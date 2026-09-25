# Exercise 03

## 0.1

1. Does sampled receive the old or the new value of value?
- The old value (0)

2. Which of the two clocked processes appears to execute first?

value is blocking. sampled is non-blocking. 
meaning value blocks so executes immediately on posedge.
sampled computes right hand side, but only writes at negedge.
Meaning sampled saves the old value. Meaning the second process (sampled) starts executing first (by saving old value). But the first process (value) finishes first.

Although it appears that for value negedge it executes before the sample.

3. Is the observed result guaranteed to be the same with another Verilog simulator?
- No. These races are up to the programmer of the simulator.

4. Why might repeated runs with the same simulator still produce the same waveform even though the code contains a race?
- Because the simulator is usually made deterministic

5. How could the module be rewritten to remove the race?
- If both were blocking?
- If both are non-blocking
    - I don't get why
    - negation should be slower than fetching?
    - Does the simulator create a dependency?

