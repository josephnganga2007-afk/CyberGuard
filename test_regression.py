import subprocess
import sys


TEST_SUITES = [
    "test_risk_language_attacks.py",
    "test_risk_false_positives.py",
    "test_risk_account_ambiguity.py"
]


print("=" * 75)
print("CYBERGUARD — REGRESSION GATE")
print("=" * 75)

passed = 0
failed = 0


for suite in TEST_SUITES:

    print()
    print("=" * 75)
    print(f"RUNNING: {suite}")
    print("=" * 75)

     
    result = subprocess.run(
    [sys.executable, suite],
    capture_output=True,
    text=False
)

    stdout = result.stdout.decode("cp1252", errors="replace")
    stderr = result.stderr.decode("cp1252", errors="replace")

    print(stdout)

    if stderr:
        print("ERROR OUTPUT:")
    print(stderr)
    if result.stderr:
        print("ERROR OUTPUT:")
        print(result.stderr)

    if result.returncode == 0:
        print(f"RESULT: PASS — {suite}")
        passed += 1
    else:
        print(f"RESULT: FAIL — {suite}")
        failed += 1


print()
print("=" * 75)
print("CYBERGUARD REGRESSION SUMMARY")
print("=" * 75)

print(f"TOTAL SUITES: {len(TEST_SUITES)}")
print(f"PASSED: {passed}")
print(f"FAILED: {failed}")

print("=" * 75)

if failed == 0:
    print("STATUS: REGRESSION GATE PASSED")
else:
    print("STATUS: REGRESSION DETECTED")