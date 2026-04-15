from __future__ import annotations

from types import MappingProxyType
from typing import Any

from strands import tool


SAFE_BUILTINS = MappingProxyType(
    {
        "abs": abs,
        "all": all,
        "any": any,
        "bool": bool,
        "dict": dict,
        "enumerate": enumerate,
        "filter": filter,
        "float": float,
        "int": int,
        "len": len,
        "list": list,
        "map": map,
        "max": max,
        "min": min,
        "range": range,
        "reversed": reversed,
        "set": set,
        "sorted": sorted,
        "str": str,
        "sum": sum,
        "tuple": tuple,
        "zip": zip,
    }
)


def run_python_tests(code: str, metadata: dict) -> dict:
    namespace: dict = {"__builtins__": SAFE_BUILTINS}
    tests = metadata.get("tests", [])
    entrypoint = metadata.get("entrypoint")

    try:
        compiled = compile(code, "<candidate-code>", "exec")
        exec(compiled, namespace, namespace)
        function = namespace.get(entrypoint)
        if entrypoint and not callable(function):
            return {
                "status": "error",
                "passed": 0,
                "total": len(tests),
                "results": [
                    {
                        "name": "entrypoint",
                        "passed": False,
                        "error": "Entrypoint not found",
                    }
                ],
            }
    except Exception as exc:
        return {
            "status": "error",
            "passed": 0,
            "total": len(tests),
            "results": [{"name": "compile", "passed": False, "error": str(exc)}],
        }

    results: list[dict] = []
    passed = 0
    for index, test in enumerate(tests, start=1):
        args = test.get("input", [])
        kwargs = test.get("kwargs", {})
        expected = test.get("expected")
        try:
            if entrypoint:
                actual = function(*args, **kwargs)
            else:
                actual = namespace.get(test.get("variable"))
            ok = actual == expected
            if ok:
                passed += 1
            results.append(
                {
                    "name": test.get("name", f"test_{index}"),
                    "passed": ok,
                    "expected": expected,
                    "actual": actual,
                }
            )
        except Exception as exc:
            results.append(
                {
                    "name": test.get("name", f"test_{index}"),
                    "passed": False,
                    "error": str(exc),
                }
            )

    return {
        "status": "completed",
        "passed": passed,
        "total": len(tests),
        "results": results,
    }


def build_run_python_tests_tool(
    *,
    submission_code: str,
    metadata: dict[str, Any] | None,
):
    current_submission = submission_code or ""
    current_metadata = metadata or {}

    @tool
    def run_python_tests_tool(code: str | None = None) -> dict:
        """Run the current coding question's local Python tests against the provided code or the active submission."""
        code_to_test = current_submission if code is None else code
        return run_python_tests(code_to_test, current_metadata)

    return run_python_tests_tool
