import json
import urllib.request


BASE = "http://localhost:8000"


def api(method: str, path: str, payload: dict | None = None):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(f"{BASE}{path}", data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=120) as response:
        body = response.read().decode("utf-8")
        return json.loads(body) if body else None


def code_answer(entrypoint: str) -> str:
    entrypoint = entrypoint or "solution"
    mapping = {
        "two_sum": """
def two_sum(nums, target):
    seen = {}
    for index, value in enumerate(nums):
        needed = target - value
        if needed in seen:
            return [seen[needed], index]
        seen[value] = index
    return []
""",
        "is_palindrome": """
def is_palindrome(value):
    normalized = ''.join(ch.lower() for ch in str(value) if ch.isalnum())
    return normalized == normalized[::-1]
""",
        "fizz_buzz": """
def fizz_buzz(n):
    result = []
    for value in range(1, n + 1):
        if value % 15 == 0:
            result.append("FizzBuzz")
        elif value % 3 == 0:
            result.append("Fizz")
        elif value % 5 == 0:
            result.append("Buzz")
        else:
            result.append(str(value))
    return result
""",
        "reverse_string": """
def reverse_string(value):
    return value[::-1]
""",
        "merge_intervals": """
def merge_intervals(intervals):
    if not intervals:
        return []
    intervals = sorted(intervals, key=lambda item: item[0])
    merged = [intervals[0][:]]
    for start, end in intervals[1:]:
        last = merged[-1]
        if start <= last[1]:
            last[1] = max(last[1], end)
        else:
            merged.append([start, end])
    return merged
""",
        "max_profit": """
def max_profit(prices):
    min_price = float("inf")
    best = 0
    for price in prices:
        min_price = min(min_price, price)
        best = max(best, price - min_price)
    return best
""",
    }
    if entrypoint in mapping:
        return mapping[entrypoint].strip()
    return f"def {entrypoint}(*args, **kwargs):\n    return None"


def text_answer(question_type: str) -> str:
    answers = {
        "theory": (
            "I would define the concept clearly, explain where it fits in a production system, "
            "and then call out the operational tradeoffs. My default bias is toward predictable "
            "behavior, readability, and observability rather than clever but opaque solutions."
        ),
        "architecture": (
            "I would separate responsibilities between the request layer, domain services, and asynchronous "
            "workers, keep the API stateless, and move long running work onto queues. I would back the design "
            "with retries, idempotency, metrics, structured logs, and dead letter handling so it degrades safely."
        ),
        "culture": (
            "I would align on the outcome, constraints, and ownership first, then communicate tradeoffs directly "
            "and document the decision. If there is disagreement, I would reduce it to facts, pick the safest "
            "next step, and follow up with accountability and feedback."
        ),
        "ai_fluency": (
            "I use AI to speed up drafting, debugging, and summarization, but I do not trust outputs without verification. "
            "My process is to ask for a concrete result, validate assumptions against tests or source material, and keep "
            "a clear audit trail of what was accepted, edited, or rejected."
        ),
    }
    return answers.get(
        question_type,
        "I would answer with a direct recommendation, the reasoning behind it, and the main tradeoffs and failure modes.",
    )


started = api("POST", "/api/candidates/start", {"full_name": "queue-testobserve"})
session_id = started["session_id"]
handled = []

while True:
    question = api("GET", f"/api/sessions/{session_id}/current-question")
    if not question:
        break

    handled.append(
        {
            "sequence": question["sequence_no"],
            "type": question["type"],
            "title": question["title"],
        }
    )

    if question["type"] == "coding":
        entrypoint = (question.get("metadata") or {}).get("entrypoint", "")
        api(
            "POST",
            f"/api/sessions/{session_id}/answers/code",
            {"code": code_answer(entrypoint), "language": "python"},
        )
    else:
        api(
            "POST",
            f"/api/sessions/{session_id}/answers/text",
            {"answer": text_answer(question["type"])},
        )

    api("POST", f"/api/sessions/{session_id}/next")

report = api("POST", f"/api/sessions/{session_id}/finish")
print(
    json.dumps(
        {
            "session_id": session_id,
            "handled": handled,
            "recommendation": report.get("recommendation"),
            "overall_score": report.get("overall_score"),
        },
        indent=2,
    )
)
