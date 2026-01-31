# Chain of Thought

## Task
Calculate `3^12345 mod 100` and output "Answer: 43". The model should reason through the problem step by step.

## Attempt 1

### Prompt
```
You are a mathematician. Solve problems step by step.

For modular exponentiation:
1. Find the pattern/cycle of powers mod 100
2. Determine cycle length
3. Use modular arithmetic to find the answer

Show your work clearly, then give final answer as "Answer: <number>".
```

### Result
```
Running test 1 of 5
SUCCESS
```

### Analysis
The prompt worked on the first attempt. The key was guiding the model to use the correct mathematical approach:
- Powers of 3 mod 100 follow a cycle (Euler's theorem: cycle length divides φ(100) = 40)
- The actual cycle length for 3 mod 100 is 20
- 12345 mod 20 = 5, so 3^12345 ≡ 3^5 ≡ 243 ≡ 43 (mod 100)

## Final Solution

### Prompt
```
You are a mathematician. Solve problems step by step.

For modular exponentiation:
1. Find the pattern/cycle of powers mod 100
2. Determine cycle length
3. Use modular arithmetic to find the answer

Show your work clearly, then give final answer as "Answer: <number>".
```

### Why It Works
1. **Role assignment**: "You are a mathematician" primes the model for mathematical reasoning
2. **Explicit CoT instruction**: "Solve problems step by step" triggers chain-of-thought reasoning
3. **Structured approach**: The numbered steps guide the model toward the correct algorithm (finding cycles in modular arithmetic)
4. **Output format**: "Answer: <number>" ensures the final answer is extractable by the test harness
