import subprocess
import time
import re
import sys
import uuid
import argparse

PLAYER_IMAGE_TAG = "player_exploit_server"
VICTIM_IMAGE_TAG = "quay.io/curl/curl:latest"
TIMEOUT_SECONDS = 5

def run_command(cmd):
    """Helper to run shell commands - catch errors, etc ..."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        return result
    except Exception as e:
        print(f"Syscall failed: {e}")
        return None


def build_player_submission(path_to_submission):
    print(f"Building player submission from {path_to_submission}...")
    # Podman build command
    cmd = ["podman", "build", "-t", PLAYER_IMAGE_TAG, path_to_submission]
    res = run_command(cmd)

    if res.returncode != 0:
        print(f"Build Failed:\n{res.stderr}")
        return False
    return True


def analyze_crash(logs):
    """
    Parses logs for ASAN/Segfaults.
    """
    # Check for Sanitizer Errors
    if "AddressSanitizer" in logs or "Segmentation fault" in logs:
        print("\nCRITICAL: Curl Crashed!")

        # Extract Stack Trace
        # Regex for ASAN stack trace: #0 0x... in FunctionName
        match = re.search(r'#0\s+0x[0-9a-f]+\s+in\s+([a-zA-Z0-9_]+)', logs)

        if match:
            crash_func = match.group(1)
            print(f"Crash Location: {crash_func}")
            return {"crashed": True, "location": crash_func}
        else:
            return {"crashed": True, "location": "unknown"}

    return {"crashed": False}


def run_trial(target_port, curl_command_template):
    # Generate a unique ID for this run so we can parallelize later if needed
    run_id = str(uuid.uuid4())[:8]
    pod_name = f"frizzing_{run_id}"
    player_name = f"malice_{run_id}"
    victim_name = f"victim_{run_id}"

    # Format the curl command with the target port
    final_curl_args = curl_command_template.format(port=target_port)

    try:
        # Create the Pod
        # We don't publish ports to the host (-p) to keep it isolated.
        run_command(["podman", "pod", "create", "--name", pod_name])

        # Start Player Container (Inside the Pod)
        # Note: We don't map ports because they share the pod's localhost
        run_command([
            "podman", "run", "-d",
            "--pod", pod_name,
            "--name", player_name,
            PLAYER_IMAGE_TAG
        ])

        # Give the server a moment to spin up
        time.sleep(2)

        # Start Victim Container (Inside the Pod)
        print(f"Launching Victim ({VICTIM_IMAGE_TAG})")
        print(f"Curl Args: {final_curl_args}")

        # Construct the full podman run command
        # Note: We split the curl args into a list so subprocess doesn't treat them as one filename
        victim_cmd = [
                         "podman", "run",
                         "--pod", pod_name,
                         "--name", victim_name,
                         "--cap-add", "SYS_PTRACE",  # Needed for ASAN
                         VICTIM_IMAGE_TAG
                     ] + final_curl_args.split()

        # We use subprocess.TimeoutExpired to handle hangs
        try:
            victim_proc = subprocess.run(
                victim_cmd,
                capture_output=True,
                text=True,
                timeout=TIMEOUT_SECONDS
            )
            logs = victim_proc.stderr + victim_proc.stdout

        except subprocess.TimeoutExpired:
            print("Curl victim timed out (Infinite loop?)")
            logs="TIMEOUT"
            # Kill the victim container manually if it hung
            run_command(["podman", "kill", victim_name])

        # Cleanup
        # 'podman pod rm -f' kills and removes all containers in the pod
        run_command(["podman", "pod", "rm", "-f", pod_name])

        # Analyze
        return analyze_crash(logs)

    except Exception as e:
        print(f"Error: {e}")
        # Emergency Cleanup
        run_command(["podman", "pod", "rm", "-f", pod_name])
        return {"crashed": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="The Frizzing Dome: A Curl CTF Judge")

    # Required argument: Path to the player's submission folder
    parser.add_argument("submission", help="Path to player's submission directory containing submission.")

    # Optional arguments
    parser.add_argument("--port", type=int, default=8080,
                        help="Port the malicious server listens on inside the container (default: 8080)")
    parser.add_argument("--timeout", type=int, default=10,
                        help="Timeout in seconds before killing the trial (default: 10)")
    parser.add_argument("--victim", default="quay.io/curl/curl:latest",
                        help="Docker image for the victim curl (default: quay.io/curl/curl:latest)")
    parser.add_argument("--tag", default="player_exploit_server",
                        help="Tag name for the built player image (default: player_exploit_server)")
    parser.add_argument("--command", default="-v http://localhost:{port}/exploit",
                        help="Arguments passed to curl inside the container. Use {port} to inject the port number. (default: '-v http://localhost:{port}/exploit')")

    args = parser.parse_args()

    # Update global config with command line args
    TIMEOUT_SECONDS = args.timeout
    VICTIM_IMAGE_TAG = args.victim
    PLAYER_IMAGE_TAG = args.tag
    submission_path = args.submission

    print("******************************* Frizzing curl **************************************")
    print(f"Target: {submission_path}")
    print(f"Curl victim image: {VICTIM_IMAGE_TAG}")
    print("************************************************************************************")

    if build_player_submission(submission_path):
        result = run_trial(target_port=args.port, curl_command_template=args.command)

        if result["crashed"]:
            print(f"WINNER! you crashed curl !!!!!!!!!!!!!!!!!! {{podman_crusher_{result['location']}}}")
            sys.exit(0)
        else:
            print("Curl survived.")
            sys.exit(0)