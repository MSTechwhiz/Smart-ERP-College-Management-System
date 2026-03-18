import subprocess
import os

def run_pytest():
    # Run pytest and capture output
    result = subprocess.run(
        ["python", "-m", "pytest", "tests", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        cwd=os.getcwd()
    )
    with open("pytest_full_output.txt", "w", encoding="utf-8") as f:
        f.write(result.stdout)
        f.write("\n\nERRORS:\n")
        f.write(result.stderr)
    print("Done")

if __name__ == "__main__":
    run_pytest()
