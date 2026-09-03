# Mens Open Quantum 26

A quantum-computing predictor for the US Open 2026 men's singles draw. Feed it a
completed round's results, it predicts the next round using a Qiskit circuit — not
a classical model with quantum branding.

Writeup: [I don't know anything about tennis, so I built a quantum computer to predict it](ARTICLE.md)

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
python src/predict.py data/draws/2026_ms_r1.json --out output/round2_predictions.json \
  --known-results data/draws/2026_ms_r2_actual.json
```

`--known-results` is optional — pass it a JSON file of already-decided next-round
results (same shape as `data/draws/2026_ms_r2_actual.json`) to grade the
predictions as they come in.

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

Predictions were made blind, using only Round 1 results. Checked against real
Round 2 results (ESPN) after the fact: 20 of the 32 Round 2 matches have finished,
and the model got **16 of 20 (80%) correct**. See `data/draws/2026_ms_r2_actual.json`
and pass `--known-results` to `predict.py` to reproduce this check.
