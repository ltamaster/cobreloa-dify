#!/usr/bin/env python3
"""
Smoke/regression tests for the Cobreloa Dify chatflow.

Usage:
    export DIFY_API_KEY="app-..."             # API key of the published app; never commit it
    export DIFY_BASE_URL="https://<tu-instancia>/v1"   # e.g. http://localhost/v1 for the local stack
    python3 test_chatflow.py [--case NAME] [--verbose]

Reads test cases from cases.json (same directory) so new cases don't require
touching this script.
"""
import json
import os
import sys
import time
import urllib.request
import urllib.error

BASE_URL = os.environ.get("DIFY_BASE_URL")
API_KEY = os.environ.get("DIFY_API_KEY")

if not API_KEY or not BASE_URL:
    print("ERROR: set DIFY_API_KEY and DIFY_BASE_URL env vars (never hardcode them in files).", file=sys.stderr)
    sys.exit(1)


def send_message(query, user="test-debug-session", conversation_id="", inputs=None):
    payload = {
        "inputs": inputs or {},
        "query": query,
        "response_mode": "blocking",
        "user": user,
        "conversation_id": conversation_id,
    }
    req = urllib.request.Request(
        f"{BASE_URL}/chat-messages",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return {"ok": True, "status": resp.status, "latency": time.time() - t0, "body": body}
    except urllib.error.HTTPError as e:
        return {"ok": False, "status": e.code, "latency": time.time() - t0, "body": e.read().decode("utf-8")}
    except Exception as e:
        return {"ok": False, "status": None, "latency": time.time() - t0, "body": str(e)}


def load_cases():
    cases_path = os.path.join(os.path.dirname(__file__), "cases.json")
    with open(cases_path, encoding="utf-8") as f:
        return json.load(f)


def run_case(case, verbose=False):
    name = case["name"]
    turns = case["turns"]
    conversation_id = ""
    user = f"test-{name}"
    print(f"\n=== {name} ===")
    print(f"  {case.get('description', '')}")
    all_passed = True
    for i, turn in enumerate(turns):
        query = turn["query"]
        if "repeat" in turn:
            query = query * turn["repeat"]
        result = send_message(query, user=user, conversation_id=conversation_id)
        if not result["ok"]:
            print(f"  [{i}] Q: {query!r}")
            print(f"      FAIL status={result['status']} body={result['body']}")
            return False
        body = result["body"]
        conversation_id = body.get("conversation_id", conversation_id)
        answer = body.get("answer", "")
        expect_contains = turn.get("expect_contains")
        expect_not_contains = turn.get("expect_not_contains")
        passed = True
        if expect_contains and expect_contains.lower() not in answer.lower():
            passed = False
        if expect_not_contains and expect_not_contains.lower() in answer.lower():
            passed = False
        status_tag = "PASS" if passed else "CHECK"
        print(f"  [{i}] ({result['latency']:.1f}s, {status_tag}) Q: {query!r}")
        print(f"      A: {answer[:300]}{'...' if len(answer) > 300 else ''}")
        if verbose:
            usage = body.get("metadata", {}).get("usage", {})
            print(f"      tokens={usage.get('total_tokens')} price={usage.get('total_price')}")
        if not passed:
            expect_msg = f"expect_contains={expect_contains!r}" if expect_contains else f"expect_not_contains={expect_not_contains!r}"
            print(f"      >>> did not match {expect_msg}")
            all_passed = False
    return all_passed


def main():
    verbose = "--verbose" in sys.argv
    only = None
    if "--case" in sys.argv:
        only = sys.argv[sys.argv.index("--case") + 1]

    cases = load_cases()
    if only:
        cases = [c for c in cases if c["name"] == only]
        if not cases:
            print(f"No case named {only!r}", file=sys.stderr)
            sys.exit(1)

    all_passed = True
    for case in cases:
        if not run_case(case, verbose=verbose):
            all_passed = False

    if not all_passed:
        print("\nAlgunos casos no cumplieron sus expectativas (ver 'CHECK' arriba).", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
