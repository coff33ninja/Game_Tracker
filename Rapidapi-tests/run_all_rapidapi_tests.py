import os
import subprocess
import sys

def run_script(script_path) -> int:
    """Runs a single Python script and prints its output."""
    print(f"\n--- Running {os.path.basename(script_path)} ---")
    try:
        # Use sys.executable to ensure the script runs with the same Python interpreter
        # Capture stdout and stderr to display them
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True, # Decode output as text
            check=False # Don't raise an exception for non-zero exit codes
        )
        print("--- STDOUT ---")
        print(result.stdout)
        if result.stderr:
            print("--- STDERR ---")
            print(result.stderr)
        print(f"--- Finished {os.path.basename(script_path)} (Exit Code: {result.returncode}) ---")
        return result.returncode
    except FileNotFoundError:
        print("Error: Python interpreter not found. Make sure Python is in your PATH.")
        return -1 # Indicate failure to launch
    except Exception as e:
        print(f"An error occurred while trying to run {os.path.basename(script_path)}: {e}")
        return -1 # Indicate failure to launch

if __name__ == "__main__":
    test_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Looking for test scripts in: {test_dir}")

    # List all files in the directory
    all_files = os.listdir(test_dir)

    # Filter for Python files, excluding this runner script itself
    test_scripts = [
        f for f in all_files
        if f.endswith(".py") and f != os.path.basename(__file__)
    ]

    if not test_scripts:
        print("No other Python test scripts found in the directory.")
    else:
        # Optional: Sort the scripts alphabetically for consistent order
        test_scripts.sort()

        print(f"Found {len(test_scripts)} test scripts: {', '.join(test_scripts)}")
        print("-" * 30)

        passed_count = 0
        failed_count = 0

        for script_name in test_scripts:
            script_path = os.path.join(test_dir, script_name)
            exit_code = run_script(script_path)
            if exit_code == 0:
                passed_count += 1
            else:
                failed_count += 1
            # Optional: Add a small delay between runs
            # time.sleep(1)

        print("\n--- All test scripts finished ---")
        total_scripts = len(test_scripts)
        print("\n--- Summary ---")
        print(f"Total scripts run: {total_scripts}")
        print(f"  Passed: {passed_count}")
        print(f"  Failed: {failed_count}")