I don't know anything about tennis. But here's how I predicted every Round 2 winner at the 2026 US Open anyway.

Round 1 just wrapped, and instead of watching matches, I built a quantum circuit to predict Round 2.

Not "quantum" as a buzzword, an actual parameterized circuit run on a quantum simulator (Qiskit). For every matchup, I encode each player's ATP ranking, how dominant they were in Round 1, and how many sets it took them to win, each as a rotation on its own qubit. Those three qubits get entangled onto a "decision" qubit through chained controlled rotations, so the factors interfere with each other instead of just averaging out like a spreadsheet would. Run it a few thousand times on the simulator, count how often the decision qubit says "player A," and that's the win probability.

The best part: my first version of this was completely broken. A bad gate choice made it predict almost the same ~78% confidence for every match regardless of who was playing, it was just confidently guessing. Found it with a simple sanity check, fixed the circuit, and reran everything.

Some Round 2 matches had already actually been played by the time I pulled the draw, but the program only ever saw Round 1 results, so every prediction was a genuine blind guess, not a lookback. I checked it against the real bracket a few days later: 20 of the 32 Round 2 matches had been decided, and the model called 16 of them correctly. 80%, having never watched a single point.

Highest confidence picks: Alcaraz (93%), Medvedev (94%), Learner Tien (86%), all correct. The two closest coin flips (right around 50%) split one right, one wrong, which is exactly what a well-calibrated coin flip should do.

Code, circuit, and full predictions are open on GitHub: https://github.com/Amin9666/Mens_Open_Quantum_26

Next week the actual Round 2 results go back in and the same circuit predicts Round 3.

#QuantumComputing #Qiskit #MachineLearning #Tennis #USOpen #BuildInPublic
