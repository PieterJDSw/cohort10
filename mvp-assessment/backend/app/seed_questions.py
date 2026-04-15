from __future__ import annotations

from app.db import session_scope
from app.domain.repositories.question_repo import QuestionRepository


CODING_RUBRIC = {
    "correctness": "Returns the right result for expected and edge-case inputs",
    "code_quality": "Readable, maintainable, and idiomatic Python",
    "problem_solving": "Chooses an approach that fits the problem well",
    "efficiency": "Uses time and space proportionally to the input",
    "testing_reasoning": "Can explain edge cases and why the tests matter",
    "communication": "Explains the approach clearly",
}

THEORY_RUBRIC = {
    "conceptual_correctness": "Explains the concept accurately",
    "depth": "Covers practical details beyond a textbook definition",
    "tradeoff_reasoning": "Discusses constraints, costs, and alternatives",
    "clarity": "Keeps the explanation structured and precise",
}

ARCHITECTURE_RUBRIC = {
    "decomposition": "Breaks the system into sensible components and boundaries",
    "tradeoffs": "Explains why key choices were made",
    "scalability": "Handles growth in load, data, or team complexity",
    "reliability": "Considers failure handling and operational safety",
    "maintainability": "Keeps the system understandable and operable",
    "communication": "Communicates the design clearly",
}

CULTURE_RUBRIC = {
    "ownership": "Takes responsibility for outcomes and follow-through",
    "collaboration": "Works effectively with the people involved",
    "prioritization": "Focuses on the most important action first",
    "communication_clarity": "Communicates decisions and tradeoffs clearly",
}

AI_FLUENCY_RUBRIC = {
    "prompt_quality": "Uses prompts that are precise and task-oriented",
    "context_provided": "Provides the model enough relevant context",
    "verification_behavior": "Checks the output before trusting it",
    "correction_of_ai_errors": "Finds and corrects model mistakes",
    "effective_use": "Uses AI where it increases speed without lowering quality",
}


def coding_question(
    *,
    title: str,
    prompt: str,
    difficulty: str,
    entrypoint: str,
    tests: list[dict],
) -> dict:
    return {
        "type": "coding",
        "title": title,
        "prompt": prompt,
        "difficulty": difficulty,
        "rubric_json": CODING_RUBRIC,
        "metadata_json": {
            "entrypoint": entrypoint,
            "tests": tests,
        },
    }


def narrative_question(
    *,
    question_type: str,
    title: str,
    prompt: str,
    difficulty: str,
    rubric: dict,
) -> dict:
    return {
        "type": question_type,
        "title": title,
        "prompt": prompt,
        "difficulty": difficulty,
        "rubric_json": rubric,
        "metadata_json": {},
    }


QUESTION_BANK = [
    coding_question(
        title="Pair Sum",
        prompt="Write a Python function `pair_sum(nums, target)` that returns the indices of the two values that add up to `target`. Return the first valid pair you find.",
        difficulty="easy",
        entrypoint="pair_sum",
        tests=[
            {"name": "basic", "input": [[2, 7, 11, 15], 9], "expected": [0, 1]},
            {"name": "late_pair", "input": [[3, 2, 4], 6], "expected": [1, 2]},
        ],
    ),
    coding_question(
        title="Palindrome Check",
        prompt="Write a Python function `is_palindrome(text)` that returns `True` when the string reads the same forwards and backwards after ignoring spaces and letter casing.",
        difficulty="easy",
        entrypoint="is_palindrome",
        tests=[
            {"name": "phrase", "input": ["Never odd or even"], "expected": True},
            {"name": "negative", "input": ["Assessment"], "expected": False},
        ],
    ),
    coding_question(
        title="Frequency Counter",
        prompt="Write `count_words(text)` that returns a dictionary of lowercase word counts using whitespace splitting.",
        difficulty="easy",
        entrypoint="count_words",
        tests=[
            {"name": "counts", "input": ["One two two"], "expected": {"one": 1, "two": 2}},
            {"name": "empty", "input": [""], "expected": {}},
        ],
    ),
    coding_question(
        title="Valid Parentheses",
        prompt="Write `is_valid_parentheses(text)` that returns `True` when the input contains balanced `()`, `[]`, and `{}` brackets.",
        difficulty="easy",
        entrypoint="is_valid_parentheses",
        tests=[
            {"name": "balanced", "input": ["([]){}"], "expected": True},
            {"name": "mismatch", "input": ["([)]"], "expected": False},
        ],
    ),
    coding_question(
        title="Binary Search Insert Position",
        prompt="Write `search_insert(nums, target)` that returns the index of `target` in a sorted list, or the index where it should be inserted to keep the list sorted.",
        difficulty="easy",
        entrypoint="search_insert",
        tests=[
            {"name": "found", "input": [[1, 3, 5, 6], 5], "expected": 2},
            {"name": "insert_middle", "input": [[1, 3, 5, 6], 2], "expected": 1},
        ],
    ),
    coding_question(
        title="Longest Common Prefix",
        prompt="Write `longest_common_prefix(words)` that returns the shared starting prefix across all input strings.",
        difficulty="easy",
        entrypoint="longest_common_prefix",
        tests=[
            {"name": "shared", "input": [["flower", "flow", "flight"]], "expected": "fl"},
            {"name": "none", "input": [["dog", "racecar", "car"]], "expected": ""},
        ],
    ),
    coding_question(
        title="First Unique Character",
        prompt="Write `first_unique_char(text)` that returns the index of the first non-repeating character, or `-1` if none exists.",
        difficulty="easy",
        entrypoint="first_unique_char",
        tests=[
            {"name": "first_unique", "input": ["leetcode"], "expected": 0},
            {"name": "missing", "input": ["aabb"], "expected": -1},
        ],
    ),
    coding_question(
        title="Roman Numeral Parser",
        prompt="Write `roman_to_int(text)` that converts a Roman numeral string into an integer.",
        difficulty="medium",
        entrypoint="roman_to_int",
        tests=[
            {"name": "simple", "input": ["III"], "expected": 3},
            {"name": "subtractive", "input": ["MCMXCIV"], "expected": 1994},
        ],
    ),
    coding_question(
        title="Rotate Array",
        prompt="Write `rotate_right(nums, k)` that returns a new list rotated right by `k` steps.",
        difficulty="medium",
        entrypoint="rotate_right",
        tests=[
            {"name": "basic", "input": [[1, 2, 3, 4, 5], 2], "expected": [4, 5, 1, 2, 3]},
            {"name": "wraparound", "input": [[1, 2, 3], 4], "expected": [3, 1, 2]},
        ],
    ),
    coding_question(
        title="Merge Intervals",
        prompt="Write `merge_intervals(intervals)` that merges overlapping inclusive intervals and returns them sorted by start position.",
        difficulty="medium",
        entrypoint="merge_intervals",
        tests=[
            {"name": "overlap", "input": [[[1, 3], [2, 6], [8, 10], [15, 18]]], "expected": [[1, 6], [8, 10], [15, 18]]},
            {"name": "touching", "input": [[[1, 4], [4, 5]]], "expected": [[1, 5]]},
        ],
    ),
    coding_question(
        title="Top K Frequent Elements",
        prompt="Write `top_k_frequent(nums, k)` that returns the `k` most frequent integers in descending order of frequency. Break ties by smaller number first.",
        difficulty="medium",
        entrypoint="top_k_frequent",
        tests=[
            {"name": "basic", "input": [[1, 1, 1, 2, 2, 3], 2], "expected": [1, 2]},
            {"name": "tie_break", "input": [[4, 4, 1, 1, 2], 2], "expected": [1, 4]},
        ],
    ),
    coding_question(
        title="Group Anagrams",
        prompt="Write `group_anagrams(words)` that groups words that are anagrams. Return the groups sorted internally and sorted by the first word in each group.",
        difficulty="medium",
        entrypoint="group_anagrams",
        tests=[
            {
                "name": "basic",
                "input": [["eat", "tea", "tan", "ate", "nat", "bat"]],
                "expected": [["ate", "eat", "tea"], ["bat"], ["nat", "tan"]],
            },
            {"name": "single", "input": [["abc"]], "expected": [["abc"]]},
        ],
    ),
    coding_question(
        title="Sliding Window Max Sum",
        prompt="Write `max_window_sum(nums, k)` that returns the largest sum of any contiguous subarray of length `k`.",
        difficulty="medium",
        entrypoint="max_window_sum",
        tests=[
            {"name": "basic", "input": [[2, 1, 5, 1, 3, 2], 3], "expected": 9},
            {"name": "all_negative", "input": [[-4, -2, -7, -1], 2], "expected": -6},
        ],
    ),
    coding_question(
        title="Product Except Self",
        prompt="Write `product_except_self(nums)` that returns a list where each position contains the product of every other element in the input list.",
        difficulty="medium",
        entrypoint="product_except_self",
        tests=[
            {"name": "basic", "input": [[1, 2, 3, 4]], "expected": [24, 12, 8, 6]},
            {"name": "includes_zero", "input": [[-1, 1, 0, -3, 3]], "expected": [0, 0, 9, 0, 0]},
        ],
    ),
    coding_question(
        title="Queue Using Stacks",
        prompt="Write a class `QueueWithStacks` with methods `push(x)`, `pop()`, `peek()`, and `empty()`. Also write `run_queue_ops(ops)` where `ops` is a list of operations like `['push', 3]` or `['peek']` and return the collected outputs of non-push operations.",
        difficulty="medium",
        entrypoint="run_queue_ops",
        tests=[
            {
                "name": "queue_flow",
                "input": [[["push", 1], ["push", 2], ["peek"], ["pop"], ["empty"]]],
                "expected": [1, 1, False],
            },
            {
                "name": "empties",
                "input": [[["push", 5], ["pop"], ["empty"]]],
                "expected": [5, True],
            },
        ],
    ),
    coding_question(
        title="Min Stack Operations",
        prompt="Write a class `MinStack` with `push(x)`, `pop()`, `top()`, and `get_min()`. Also write `run_min_stack_ops(ops)` which executes operations and returns outputs from `pop`, `top`, and `get_min` calls.",
        difficulty="medium",
        entrypoint="run_min_stack_ops",
        tests=[
            {
                "name": "min_tracking",
                "input": [[["push", -2], ["push", 0], ["push", -3], ["get_min"], ["pop"], ["top"], ["get_min"]]],
                "expected": [-3, -3, 0, -2],
            }
        ],
    ),
    coding_question(
        title="Meeting Rooms Needed",
        prompt="Write `min_meeting_rooms(intervals)` that returns the minimum number of meeting rooms required so all meetings can happen without overlap.",
        difficulty="medium",
        entrypoint="min_meeting_rooms",
        tests=[
            {"name": "overlap", "input": [[[0, 30], [5, 10], [15, 20]]], "expected": 2},
            {"name": "reuse", "input": [[[7, 10], [2, 4]]], "expected": 1},
        ],
    ),
    coding_question(
        title="Spiral Matrix Traversal",
        prompt="Write `spiral_order(matrix)` that returns the values of a matrix in spiral order.",
        difficulty="medium",
        entrypoint="spiral_order",
        tests=[
            {"name": "square", "input": [[[1, 2, 3], [4, 5, 6], [7, 8, 9]]], "expected": [1, 2, 3, 6, 9, 8, 7, 4, 5]},
            {"name": "rectangular", "input": [[[1, 2, 3, 4], [5, 6, 7, 8]]], "expected": [1, 2, 3, 4, 8, 7, 6, 5]},
        ],
    ),
    coding_question(
        title="Linked List Cycle Detection",
        prompt="Write `has_cycle(values, pos)` that builds a linked list from `values`, connects the tail to the node at index `pos` when `pos >= 0`, and returns whether the resulting list contains a cycle.",
        difficulty="medium",
        entrypoint="has_cycle",
        tests=[
            {"name": "cycle", "input": [[3, 2, 0, -4], 1], "expected": True},
            {"name": "no_cycle", "input": [[1, 2], -1], "expected": False},
        ],
    ),
    coding_question(
        title="Grid Shortest Path",
        prompt="Write `shortest_path(grid)` that returns the minimum number of moves from the top-left cell to the bottom-right cell in a grid of `0`s and `1`s, where `0` is open and `1` is blocked. Return `-1` if unreachable.",
        difficulty="hard",
        entrypoint="shortest_path",
        tests=[
            {"name": "reachable", "input": [[[0, 0, 0], [1, 1, 0], [0, 0, 0]]], "expected": 4},
            {"name": "blocked", "input": [[[0, 1], [1, 0]]], "expected": -1},
        ],
    ),
    coding_question(
        title="Kth Largest Element",
        prompt="Write `kth_largest(nums, k)` that returns the kth largest value from the list.",
        difficulty="medium",
        entrypoint="kth_largest",
        tests=[
            {"name": "basic", "input": [[3, 2, 1, 5, 6, 4], 2], "expected": 5},
            {"name": "duplicates", "input": [[3, 2, 3, 1, 2, 4, 5, 5, 6], 4], "expected": 4},
        ],
    ),
    narrative_question(
        question_type="theory",
        title="Database Indexes",
        prompt="Explain when you would add an index to a relational database table and what tradeoffs come with it.",
        difficulty="medium",
        rubric=THEORY_RUBRIC,
    ),
    narrative_question(
        question_type="theory",
        title="REST vs RPC",
        prompt="Compare REST and RPC APIs for an internal service ecosystem and explain where each fits better.",
        difficulty="medium",
        rubric=THEORY_RUBRIC,
    ),
    narrative_question(
        question_type="theory",
        title="Transaction Isolation Levels",
        prompt="Explain the common transaction isolation levels in relational databases and how they affect correctness and throughput.",
        difficulty="medium",
        rubric=THEORY_RUBRIC,
    ),
    narrative_question(
        question_type="theory",
        title="Caching Strategy",
        prompt="Explain the difference between cache-aside, write-through, and write-behind caching, including when each is a good fit.",
        difficulty="medium",
        rubric=THEORY_RUBRIC,
    ),
    narrative_question(
        question_type="theory",
        title="Authentication vs Authorization",
        prompt="Explain the difference between authentication and authorization and outline how they work together in a typical web application.",
        difficulty="easy",
        rubric=THEORY_RUBRIC,
    ),
    narrative_question(
        question_type="theory",
        title="Feature Flags",
        prompt="Explain what feature flags are, what problems they solve, and the operational risks they introduce.",
        difficulty="medium",
        rubric=THEORY_RUBRIC,
    ),
    narrative_question(
        question_type="theory",
        title="Horizontal vs Vertical Scaling",
        prompt="Compare horizontal and vertical scaling for a backend service and explain when you would choose each option.",
        difficulty="easy",
        rubric=THEORY_RUBRIC,
    ),
    narrative_question(
        question_type="theory",
        title="Event-Driven Systems",
        prompt="Explain the benefits and tradeoffs of event-driven architecture compared with synchronous request-response communication.",
        difficulty="medium",
        rubric=THEORY_RUBRIC,
    ),
    narrative_question(
        question_type="architecture",
        title="Assessment Platform Design",
        prompt="Design a service that runs developer assessments, stores answers, scores responses, and shows reports to hiring teams.",
        difficulty="hard",
        rubric=ARCHITECTURE_RUBRIC,
    ),
    narrative_question(
        question_type="architecture",
        title="Background Processing",
        prompt="How would you separate synchronous user actions from asynchronous evaluation work in this MVP?",
        difficulty="hard",
        rubric=ARCHITECTURE_RUBRIC,
    ),
    narrative_question(
        question_type="architecture",
        title="Multi-Tenant Reporting",
        prompt="Design a reporting layer for multiple customers where each customer must only see their own candidate data and analytics.",
        difficulty="hard",
        rubric=ARCHITECTURE_RUBRIC,
    ),
    narrative_question(
        question_type="architecture",
        title="Webhook Ingestion Pipeline",
        prompt="Design a webhook ingestion system that receives external events, validates them, stores them safely, and processes them downstream.",
        difficulty="hard",
        rubric=ARCHITECTURE_RUBRIC,
    ),
    narrative_question(
        question_type="architecture",
        title="Search Service Design",
        prompt="Design a search service for assessment results where recruiters can filter by role, score, date, and recommendation with low latency.",
        difficulty="hard",
        rubric=ARCHITECTURE_RUBRIC,
    ),
    narrative_question(
        question_type="architecture",
        title="Rate-Limited AI Integration",
        prompt="Design how you would integrate with an external LLM provider that enforces strict rate limits and sometimes returns slow or failed responses.",
        difficulty="hard",
        rubric=ARCHITECTURE_RUBRIC,
    ),
    narrative_question(
        question_type="culture",
        title="Production Incident",
        prompt="A release breaks candidate session creation in production. How do you respond in the first hour?",
        difficulty="medium",
        rubric=CULTURE_RUBRIC,
    ),
    narrative_question(
        question_type="culture",
        title="Disagreement on Scope",
        prompt="A product manager wants more features before launch, but the team is already late. How do you handle it?",
        difficulty="medium",
        rubric=CULTURE_RUBRIC,
    ),
    narrative_question(
        question_type="culture",
        title="Weak Pull Request",
        prompt="A teammate opens a pull request that works but has shaky tests and messy structure. How do you handle the review?",
        difficulty="medium",
        rubric=CULTURE_RUBRIC,
    ),
    narrative_question(
        question_type="culture",
        title="Junior Engineer Blocked",
        prompt="A junior engineer has been blocked for two days on a task you delegated. What do you do next?",
        difficulty="medium",
        rubric=CULTURE_RUBRIC,
    ),
    narrative_question(
        question_type="culture",
        title="Missed Delivery Date",
        prompt="Your team is going to miss a delivery date that leadership already communicated externally. How do you handle it?",
        difficulty="medium",
        rubric=CULTURE_RUBRIC,
    ),
    narrative_question(
        question_type="culture",
        title="Ambiguous Requirements",
        prompt="You start implementing a feature and realize the requirements are too ambiguous to proceed safely. What do you do?",
        difficulty="easy",
        rubric=CULTURE_RUBRIC,
    ),
    narrative_question(
        question_type="ai_fluency",
        title="Using AI Safely",
        prompt="Describe how you would use an AI assistant to speed up implementation while avoiding subtle correctness issues.",
        difficulty="medium",
        rubric=AI_FLUENCY_RUBRIC,
    ),
    narrative_question(
        question_type="ai_fluency",
        title="AI for Debugging",
        prompt="Describe how you would use an AI tool to debug a failing production issue without leaking sensitive data or trusting the first answer.",
        difficulty="medium",
        rubric=AI_FLUENCY_RUBRIC,
    ),
    narrative_question(
        question_type="ai_fluency",
        title="Prompting for Code Review",
        prompt="Explain how you would prompt an AI assistant to review a pull request so that the output is concrete, testable, and useful.",
        difficulty="medium",
        rubric=AI_FLUENCY_RUBRIC,
    ),
    narrative_question(
        question_type="ai_fluency",
        title="Verifying Generated SQL",
        prompt="An AI assistant proposes a migration and a complex SQL query. Explain how you would validate both before shipping them.",
        difficulty="medium",
        rubric=AI_FLUENCY_RUBRIC,
    ),
    narrative_question(
        question_type="ai_fluency",
        title="Trust Boundaries for AI Output",
        prompt="Explain which kinds of AI-generated engineering output you would trust least by default and how that changes your verification approach.",
        difficulty="medium",
        rubric=AI_FLUENCY_RUBRIC,
    ),
]


def seed_questions_if_empty() -> int:
    repo = QuestionRepository()
    with session_scope() as db:
        existing_titles = repo.fetch_titles(db)
        missing_questions = [
            payload for payload in QUESTION_BANK if payload["title"] not in existing_titles
        ]
        if not missing_questions:
            return 0
        repo.seed_questions(db, missing_questions)
        return len(missing_questions)


if __name__ == "__main__":
    created = seed_questions_if_empty()
    print(f"Questions seeded: {created}")
