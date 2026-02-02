import os
import re
from collections import Counter
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

NUM_RUNS_TIMES = 5

# TODO: Fill this in! Try to get as close to 100% correctness across all runs as possible.

    # Question: 과수원에는 15그루의 나무가 있어. 과수원의 일꾼들이 오늘 과수원에 나무를 심을 거야. 나무 심기가 끝나면
    # 21그루의 나무가 있을 거야. 오늘 과수원 일꾼들은 몇 그루의 나무를 심었을까?
    # Answer: 15그루로 시작합니다. 나중에 나무가 21그루가 됩니다. 그 차이가 그들이 심은 나무의 수일 것입니다.
    # 따라서 그들은 21 - 15 = 6그루의 나무를 심었어야 합니다. 정답은 6입니다.
    # Question: 주차장에 3대의 차량이 있고 2대의 차량이 더 도착하면 주차장에 몇 대의 차량이 있을까?
    # Answer: 주차장에 이미 3대의 차량이 있습니다. 2대가 더 도착합니다. 이제 3 + 2 = 5대의 차량이 있습니다. 정답은 5입니다.
    # Question: 지호는 초콜릿을 32개, 여동생은 42개를 가지고 있었어. 둘이 35개를 먹었다면 총 몇 개가 남았을까?
    # Answer: 레아는 초콜릿 32개, 레아의 여동생은 42개를 가지고 있었습니다. 즉, 원래 32개 + 42개 = 74개의
    # 초콜릿이 있었습니다. 35개를 먹었습니다. 따라서 총 74 - 35 = 39개의 초콜릿이 남아 있습니다. 정답은 39입니다.
    # Question: 선우는 막대 사탕을 20개 가지고 있었어. 그는 두리에게 막대 사탕을 몇 개 주었어. 이제 선우는 막대사탕 12개를 가지고 있어. 선우는 두리에게
    # 몇 개의 막대 사탕을 줬을까?
    # Answer: 선우는 막대 사탕 20개를 가지고 있었습니다. 이제 선우는 12개만 가지고 있으므로, 나머지는 두리에게 주었을 것입니다. 선우가 두리에게 준 막대사탕의
    # 20 - 12 = 8개의 막대 사탕을 두리에게 주었어야 합니다. 정답은 8개입니다.
    # Question: 도현이는 장난감이 다섯 개 있어. 크리스마스에 도현이는 엄마와 아빠로부터 각각 두 개의 장난감을 받았어. 도현이는 지금 몇 개의 장난감을
    # 가지고 있을까?
    # Answer: 도현이의 장난감이 5개입니다. 엄마로부터 2개를 받았으므로 5 + 2 = 7개의 장난감을 가지고 있습니다. 그리고 아빠한테서 2개를 더 받았어요.
    # 총 7 + 2 = 9 개의 장난감을 가지고 있습니다. 정답은 9입니다.

YOUR_SYSTEM_PROMPT = """
    Question: There are 15 trees in the orchard. The orchard workers are going to plant trees in the orchard today. After the tree planting is done, there will be 21 trees. How many trees did the orchard workers plant today?
    Answer: We start with 15 trees. Later there are 21 trees. The difference must be the number of trees they planted. So they must have planted 21 - 15 = 6 trees. The answer is 6.

    Question: If there are 3 cars in the parking lot and 2 more cars arrive, how many cars are in the parking lot?
    Answer: There are already 3 cars in the parking lot. 2 more cars arrive. Now there are 3 + 2 = 5 cars. The answer is 5.

    Question: Jiho had 32 chocolates and his sister had 42. If they ate 35 together, how many are left in total?
    Answer: Jiho had 32 chocolates and Jiho's sister had 42. That means there were originally 32 + 42 = 74 chocolates. They ate 35. So there are 74 - 35 = 39 chocolates left in total. The answer is 39.

    Question: Sunwoo had 20 lollipops. He gave some lollipops to Duri. Now Sunwoo has 12 lollipops. How many lollipops did Sunwoo give to Duri?
    Answer: Sunwoo had 20 lollipops. Since Sunwoo now only has 12, he must have given the rest to Duri. Sunwoo must have given 20 - 12 = 8 lollipops to Duri. The answer is 8.

    Question: Dohyun has five toys. At Christmas, Dohyun received two toys each from his mom and dad. How many toys does Dohyun have now?
    Answer: Dohyun has 5 toys. He received 2 from his mom, so he has 5 + 2 = 7 toys. And he received 2 more from his dad. He has a total of 7 + 2 = 9 toys. The answer is 9.
"""

USER_PROMPT = """
Solve this problem, then give the final answer on the last line as "Answer: <number>".

Henry made two stops during his 60-mile bike trip. He first stopped after 20
miles. His second stop was 15 miles before the end of the trip. How many miles
did he travel between his first and second stops?
"""

EXPECTED_OUTPUT = "Answer: 25"


def extract_final_answer(text: str) -> str:
    """Extract the final 'Answer: ...' line from a verbose reasoning trace.

    - Finds the LAST line that starts with 'Answer:' (case-insensitive)
    - Normalizes to 'Answer: <number>' when a number is present
    - Falls back to returning the matched content if no number is detected
    """
    matches = re.findall(r"(?mi)^\s*answer\s*:\s*(.+)\s*$", text)
    if matches:
        value = matches[-1].strip()
        num_match = re.search(r"-?\d+(?:\.\d+)?", value.replace(",", ""))
        if num_match:
            return f"Answer: {num_match.group(0)}"
        return f"Answer: {value}"
    return text.strip()


def test_your_prompt(system_prompt: str) -> bool:
    """Run the prompt NUM_RUNS_TIMES, majority-vote on the extracted 'Answer: ...' lines.

    Prints "SUCCESS" if the majority answer equals EXPECTED_OUTPUT.
    """
    answers: list[str] = []
    for idx in range(NUM_RUNS_TIMES):
        print(f"Running test {idx + 1} of {NUM_RUNS_TIMES}")
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=USER_PROMPT,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=1.0,
                thinking_config=types.ThinkingConfig(
                    thinking_level=types.ThinkingLevel.MINIMAL
                ),
            ),
        )
        output_text = response.text
        final_answer = extract_final_answer(output_text)
        print(f"Run {idx + 1} answer: {final_answer}")
        answers.append(final_answer.strip())

    if not answers:
        print("No answers produced.")
        return False

    counts = Counter(answers)
    majority_answer, majority_count = counts.most_common(1)[0]
    print(f"Majority answer: {majority_answer} ({majority_count}/{len(answers)})")

    if majority_answer.strip() == EXPECTED_OUTPUT.strip():
        print("SUCCESS")
        return True

    # Print distribution for debugging when majority does not match expected
    print(f"Expected output: {EXPECTED_OUTPUT}")
    print("Answer distribution:")
    for answer, count in counts.most_common():
        print(f"  {answer}: {count}")
    return False


if __name__ == "__main__":
    test_your_prompt(YOUR_SYSTEM_PROMPT)


