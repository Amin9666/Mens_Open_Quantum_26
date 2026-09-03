import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from features import load_r1_winners, build_round_matchups
from quantum_model import predict_match


def load_known_results(path):
    if not path or not Path(path).exists():
        return {}
    actual = json.loads(Path(path).read_text())
    known = {}
    for m in actual["matches"]:
        key = frozenset({m["p1"], m["p2"]})
        known[key] = m["winner"]
    return known


def main():
    ap = argparse.ArgumentParser(description="Quantum predictor for the next round.")
    ap.add_argument("draw_json", help="Path to the current round's results JSON")
    ap.add_argument("--out", default=None, help="Path to write predictions JSON")
    ap.add_argument(
        "--known-results",
        default=None,
        help="Optional JSON of already-known next-round results, for validation",
    )
    args = ap.parse_args()

    draw = json.loads(Path(args.draw_json).read_text())
    winners = load_r1_winners(draw)
    matchups = build_round_matchups(winners)
    known_results = load_known_results(args.known_results)

    predictions = []
    correct, checked = 0, 0
    for p1, p2 in matchups:
        pred = predict_match(p1, p2)
        key = frozenset({p1["name"], p2["name"]})
        actual = known_results.get(key)
        pred["actual_winner"] = actual
        if actual:
            checked += 1
            correct += int(actual == pred["predicted_winner"])
        predictions.append(pred)

    for p in predictions:
        tag = ""
        if p["actual_winner"]:
            tag = "  [MATCH]" if p["actual_winner"] == p["predicted_winner"] else "  [MISS]"
        print(
            f"{p['p1']:28s} vs {p['p2']:28s} -> {p['predicted_winner']:28s} "
            f"({p['confidence']*100:.1f}%){tag}"
        )

    if checked:
        print(f"\nValidation on known results: {correct}/{checked} correct")

    if args.out:
        Path(args.out).write_text(json.dumps(predictions, indent=2))
        print(f"\nWrote {len(predictions)} predictions to {args.out}")


if __name__ == "__main__":
    main()
