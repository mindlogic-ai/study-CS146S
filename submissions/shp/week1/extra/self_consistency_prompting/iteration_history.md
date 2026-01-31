# Self-Consistency Prompting

## Task
Solve a word problem: "Henry made two stops during his 60-mile bike trip. He first stopped after 20 miles. His second stop was 15 miles before the end of the trip. How many miles did he travel between his first and second stops?"

Expected answer: 25 miles. The test runs 5 times and uses majority voting.

## Attempt 1

### Prompt
```
You are a careful math problem solver.

For word problems:
1. Identify all given information
2. Draw out the scenario if helpful
3. Set up the calculation step by step
4. Double-check your arithmetic

Always end with "Answer: <number>".
```

### Result
```
Running test 1 of 5
Run 1 answer: Answer: 25
Running test 2 of 5
Run 2 answer: Answer: 25
Running test 3 of 5
Run 3 answer: Answer: 25
Running test 4 of 5
Run 4 answer: Answer: 25
Running test 5 of 5
Run 5 answer: Answer: 25
Majority answer: Answer: 25 (5/5)
SUCCESS
```

### Analysis
The prompt achieved 100% consistency across all 5 runs. The problem is relatively straightforward:
- Total trip: 60 miles
- First stop: mile 20
- Second stop: 60 - 15 = mile 45
- Distance between stops: 45 - 20 = 25 miles

The structured approach ("identify information", "step by step", "double-check") led to consistent reasoning across runs.

## Final Solution

### Prompt
```
You are a careful math problem solver.

For word problems:
1. Identify all given information
2. Draw out the scenario if helpful
3. Set up the calculation step by step
4. Double-check your arithmetic

Always end with "Answer: <number>".
```

### Why It Works
1. **Role priming**: "careful math problem solver" encourages methodical thinking
2. **Structured steps**: Breaking down the process reduces variance in reasoning paths
3. **Verification step**: "Double-check your arithmetic" adds a self-review layer
4. **Consistent format**: "Answer: <number>" ensures all runs produce extractable answers
5. **Self-consistency benefit**: Even with temperature=1.0, the clear methodology leads to the same answer across runs, making majority voting trivial (5/5 agreement)

---

## Extra Tests Iteration

### Attempt 1
All 8 test cases passed with 100% consistency (40/40 individual runs correct).

Test cases included:
- Basic arithmetic word problems
- Tricky wording ("all but 9 run away" → 9 remain)
- Tricky logic ("you take away 4" → you have 4)
- Multi-step calculations

The original prompt handles all these cases effectively.
