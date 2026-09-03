# I don't know anything about tennis, so I built a quantum computer to predict it

I couldn't tell you who won last year's US Open. I'm not sure I could name five active
ATP players off the top of my head. But the 2026 US Open men's draw was underway,
Round 1 had just finished, and I had a genuinely dumb idea: what if I predicted every
Round 2 match using an actual quantum circuit instead of watching a single point of
tennis?

Not "quantum" as a buzzword slapped on a spreadsheet. An actual parameterized quantum
circuit, run on a simulator, that outputs a win probability for each match.

## Where the data comes from

No vibes, no gut feelings — just the official USTA draw sheet. I pulled the real PDF
straight from usopen.org rather than trusting scraped summaries (which, it turns out,
contradict each other constantly — one source told me the same player had both won
and lost the same match). The draw sheet lists 64 Round 1 results: who won, the score,
and whether they were a seed, a qualifier, a wildcard, or a lucky loser.

## Turning a tennis match into a quantum circuit

For every Round 2 matchup, I built a small circuit with three "feature" qubits and one
"decision" qubit:

- **Rank** — each player's real ATP ranking, pulled from public ATP ranking data (a
  seed number alone doesn't tell you much about the 96 unseeded players)
- **Form** — how dominant they were in their Round 1 win (games won vs. lost)
- **Fatigue** — how many sets it took them to get through Round 1

Each feature gets encoded as a rotation angle on its own qubit — the bigger the
advantage for player A, the more that qubit's superposition leans toward representing
"A is stronger." Then all three feature qubits get entangled onto the decision qubit
through a chain of controlled rotations, so the features interfere with each other
rather than just getting averaged like a spreadsheet formula would. Run it through
Qiskit's Aer simulator for a few thousand shots, count how often the decision qubit
collapses to "player A wins," and that's your probability.

## The part where it was completely broken

My first version of the circuit put every decision qubit through a Hadamard gate
before entangling the features onto it. I ran a sanity check — sweep one feature from
"massively favors player A" to "massively favors player B" and watch the output
probability move.

It didn't move. At all. Every single prediction landed around 78%, no matter what I
fed it. I'd built a circuit that was completely blind to its own inputs and just
confidently, uselessly guessing "whoever's listed first."

Turns out the math was hiding a `sin(x)` term that had saturated near its peak, and
the Hadamard was injecting a huge amount of baseline bias that swamped everything
else. Dropped the Hadamard, started the decision qubit at a clean |0⟩, and reran the
sweep — it moved smoothly and symmetrically from 17% to 84% exactly where it should.
Every prediction in this article is from the fixed version.

## Then I found out I already had a real answer key

One Round 2 match — Auger-Aliassime vs. Khachanov — had already been played by the
time I pulled the draw. My very first (buggy) circuit predicted Auger-Aliassime with
90% confidence. He lost. After fixing the circuit and adding real ATP rankings instead
of guessing at unseeded players' strength, the corrected model called it 50.4% in
Khachanov's favor — essentially a coin flip, which is exactly what that match actually
was.

## Grading it against reality

A few days later I pulled the live ESPN bracket data to see how the predictions were
actually holding up — and caught a second bug in the process: I'd transcribed one
Round 1 result backwards (had Brooksby beating Faria; it was the other way around),
which had quietly fed the wrong player into a Round 2 matchup. Fixed the source data,
reran everything.

By that point 20 of the 32 Round 2 matches had actually been decided. The model,
having only ever seen Round 1 results, called **16 of those 20 correctly — 80%**.
The four misses were all closer matches (Nakashima vs. Michelsen, Merida vs. Rublev,
Berrettini vs. Navone, Harris vs. Tsitsipas) rather than confident calls it whiffed on.

## The predictions

Highest-confidence calls: Alcaraz (93%), Medvedev (94%), Learner Tien (86%), and
Etcheverry (84%) — all of which turned out correct. The closest coin flips: Harris
vs. Tsitsipas and Auger-Aliassime vs. Khachanov, both sitting right around 50%
(one right, one wrong — which is exactly what you'd want from a well-calibrated
coin flip).

Full predictions, code, and the circuit itself:
[github.com/Amin9666/Mens_Open_Quantum_26](https://github.com/Amin9666/Mens_Open_Quantum_26)

Next week, real Round 2 results go back in as input, and the same circuit predicts
Round 3. I still don't know anything about tennis. The qubits don't either — they just
do it with better math.
