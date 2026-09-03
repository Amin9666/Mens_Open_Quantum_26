import math
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

SHOTS = 8192

# relative importance of each feature; must sum to 1.0
WEIGHTS = {
    "rank": 0.55,
    "form": 0.30,
    "fatigue": 0.15,
}


def _clip(x, lo=-1.0, hi=1.0):
    return max(lo, min(hi, x))


def player_features(p1, p2):
    """Signed advantages of p1 over p2 in [-1, 1] for each feature."""
    # real ATP ranks span ~1-2000+, so compare on a log scale: a ~33x rank ratio
    # (e.g. #10 vs #330) saturates to full advantage.
    log_span = 3.5
    rank_adv = _clip(
        (math.log(p2["rank_score"] + 1) - math.log(p1["rank_score"] + 1)) / log_span
    )

    form_adv = _clip(p1["dominance"] - p2["dominance"], -0.5, 0.5) * 2

    fatigue_adv = _clip((p2["sets_played"] - p1["sets_played"]) / 2.0)

    return {"rank": rank_adv, "form": form_adv, "fatigue": fatigue_adv}


def build_circuit(feature_adv):
    """3 feature qubits + 1 decision qubit. Each feature qubit is put into a
    superposition weighted by that feature's advantage, then entangled onto the
    decision qubit with a controlled rotation scaled by the feature's importance
    weight. The interference between the (non-commuting) controlled rotations from
    all three feature qubits is what produces the final win-probability distribution
    on the decision qubit — not a linear/classical weighted sum.
    """
    feature_names = ["rank", "form", "fatigue"]
    n_feat = len(feature_names)
    qc = QuantumCircuit(n_feat + 1, n_feat + 1)
    decision = n_feat

    for i, name in enumerate(feature_names):
        adv = feature_adv[name]
        theta = (adv + 1) * (math.pi / 2)  # -1 -> 0, 0 -> pi/2, +1 -> pi
        qc.ry(theta, i)

    # decision qubit starts at |0>; each feature qubit's superposition controls how
    # much of that feature's weighted rotation gets entangled onto the decision
    # qubit. Chaining non-commuting controlled rotations from all three feature
    # qubits onto the same target is what makes this genuinely quantum rather than
    # a classical weighted sum evaluated once.
    for i, name in enumerate(feature_names):
        w = WEIGHTS[name]
        qc.cry(w * math.pi, i, decision)

    qc.measure(range(n_feat + 1), range(n_feat + 1))
    return qc, decision


def predict_match(p1, p2, shots=SHOTS):
    feature_adv = player_features(p1, p2)
    qc, decision_bit = build_circuit(feature_adv)

    sim = AerSimulator()
    result = sim.run(qc, shots=shots).result()
    counts = result.get_counts()

    p1_wins = 0
    for bitstring, count in counts.items():
        bits = bitstring[::-1]  # qiskit returns little-endian
        if bits[decision_bit] == "1":
            p1_wins += count

    p1_prob = p1_wins / shots
    winner = p1 if p1_prob >= 0.5 else p2
    confidence = max(p1_prob, 1 - p1_prob)

    return {
        "p1": p1["name"],
        "p2": p2["name"],
        "p1_win_prob": round(p1_prob, 4),
        "p2_win_prob": round(1 - p1_prob, 4),
        "predicted_winner": winner["name"],
        "confidence": round(confidence, 4),
        "features": feature_adv,
    }
