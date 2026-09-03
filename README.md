# Mens Open Quantum 26

A quantum-computing predictor for the US Open 2026 men's singles draw. Feed it a
completed round's results, it predicts the next round using a Qiskit circuit — not
a classical model with quantum branding.

## How it works

For each next-round matchup, three player-vs-player feature advantages are computed
from the completed round(s):

- **rank** — real current ATP ranking (falls back to seed number, then entry status, if a player isn't found in the rankings data)
- **form** — share of games won in their last match
- **fatigue** — sets played to get through their last match

Each feature is encoded as a rotation angle on its own qubit (`RY`), placing that
qubit in a superposition weighted by how strongly it favors player 1. Those three
feature qubits are then entangled onto a decision qubit via chained controlled
rotations (`CRY`), with rotation weights `rank=0.55, form=0.30, fatigue=0.15`. The
circuit is run on Qiskit's Aer simulator for 8192 shots; the fraction of shots
where the decision qubit collapses to `1` is player 1's predicted win probability.

See [`src/quantum_model.py`](src/quantum_model.py) for the circuit.

## Usage

```bash
source venv/bin/activate
python src/predict.py data/draws/2026_ms_r1.json --out output/round2_predictions.json
```

Each week: drop in the newly completed round's results as JSON (same shape as
`data/draws/2026_ms_r1.json`), point `predict.py` at it, and it predicts the next
round's matchups by pairing up adjacent bracket winners.

## Data

`data/draws/` holds the official USTA draw PDFs and the results parsed out of them.
Round 1 results for the 2026 draw are in `data/draws/2026_ms_r1.json`.

`data/atp_rankings.json` holds real ATP rankings (name -> rank), sourced from the
Sackmann tennis-atp dataset. The snapshot in use is dated in the file's `as_of`
field — refresh it periodically for best accuracy, since a stale snapshot won't
reflect recent ranking moves.

## Status

As of this run, Round 2 has only one completed match in the official draw sheet
(Khachanov d. Auger-Aliassime) — the rest of these are genuine predictions, not
backtests. `predict.py` checks any known results automatically for calibration.
