import subprocess
import os

files = [
    "tests/test_auth.py",
    "tests/test_students.py",
    "tests/test_faculty.py",
    "tests/test_workflows.py",
    "tests/test_secondary.py"
]

def run_tests():
    for f in files:
        print(f"Running {f}...")
        result = subprocess.run(
            ["python", "-m", "pytest", f, "-v", "--tb=short"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        print(result.stdout)
        if result.returncode != 0:
            print(f"FAILED {f}")
            print(result.stderr)

if __name__ == "__main__":
    run_tests()
