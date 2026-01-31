# RAG (Retrieval-Augmented Generation)

## Task
Generate a Python function `fetch_user_name(user_id: str, api_key: str) -> str` that calls an API to fetch a user by ID and returns the user's name.

The function must use information from the provided API docs context:
- Base URL: `https://api.example.com/v1`
- Endpoint: `GET /users/{id}`
- Auth header: `X-API-Key`

Required snippets: `def fetch_user_name(`, `requests.get`, `/users/`, `X-API-Key`, `return`

## Attempt 1

### System Prompt
```
You are a Python developer. Write code using ONLY the information provided in the context.
Follow the documented API exactly. Output a single fenced Python code block.
```

### Context Provider
```python
def YOUR_CONTEXT_PROVIDER(corpus: List[str]) -> List[str]:
    return [corpus[0]]  # Return the API docs
```

### Result
```python
import requests

def fetch_user_name(user_id: str, api_key: str) -> str:
    base_url = "https://api.example.com/v1"
    url = f"{base_url}/users/{user_id}"
    headers = {
        "X-API-Key": api_key
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    data = response.json()
    return data["name"]
```
SUCCESS

### Analysis
The prompt worked on the first attempt. The model correctly:
- Used the base URL from the docs
- Constructed the `/users/{id}` endpoint
- Set the `X-API-Key` header as documented
- Used `requests.get` to make the API call
- Returned only the name string

## Final Solution

### System Prompt
```
You are a Python developer. Write code using ONLY the information provided in the context.
Follow the documented API exactly. Output a single fenced Python code block.
```

### Context Provider
```python
def YOUR_CONTEXT_PROVIDER(corpus: List[str]) -> List[str]:
    return [corpus[0]]  # Return the API docs
```

### Why It Works
1. **RAG principle**: The context provider supplies the API documentation as grounding context
2. **Constraint**: "ONLY the information provided" prevents hallucinating API details
3. **Exactness**: "Follow the documented API exactly" ensures correct URL, endpoint, and headers
4. **Output format**: "single fenced Python code block" matches the expected output format
5. **Retrieval selection**: `corpus[0]` contains the API docs - the only relevant document for this task

---

## Extra Tests Iteration

### Attempt 1
All 4 test cases passed with 100% consistency (12/12 runs correct).

Test cases included:
- Original `fetch_user_name` function
- Variant returning full user dict
- Variant checking if user exists (returns bool)
- Variant verifying correct base URL usage

The original prompt and context provider handle all variations effectively.
