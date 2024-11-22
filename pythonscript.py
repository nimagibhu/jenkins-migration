import subprocess
import os

namespace = "acc"
source_pod_name = "sjenkins-57f55b945d-xmksc"  # Source Jenkins pod
destination_pod_name = "djenkins-65dbdc545d-6jq4b"  # Destination Jenkins pod
kubectl_path = "/tmp/kubectl"  # Path to download kubectl
source_directory = "/var/jenkins_home/jobs"
local_directory = "/tmp/jenkins_jobs"  # Local directory where the jobs will be copied

def download_kubectl():
    """Download kubectl binary if not already available."""
    if not os.path.exists(kubectl_path):
        print("Downloading kubectl...")
        download_command = f"curl -Lo {kubectl_path} https://storage.googleapis.com/kubernetes-release/release/v1.20.5/bin/linux/amd64/kubectl"
        chmod_command = f"chmod +x {kubectl_path}"
        try:
            subprocess.run(download_command, shell=True, check=True)
            subprocess.run(chmod_command, shell=True, check=True)
            print("kubectl downloaded successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error downloading kubectl: {e}")
            exit(1)
    else:
        print("kubectl already exists.")

def run_kubectl_command(command):
    """Run a kubectl command."""
    full_command = f"{kubectl_path} {command}"
    try:
        result = subprocess.run(full_command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Command succeeded: {result.stdout}")
        else:
            print(f"Command failed: {result.stderr}")
            exit(1)
    except Exception as e:
        print(f"An error occurred while running kubectl: {e}")
        exit(1)

def main():
    # Step 1: Download kubectl
    download_kubectl()

    try:
        # Step 2: Copy jobs from source pod to local machine
        command_cp_from_pod = f"cp {namespace}/{source_pod_name}:{source_directory} {local_directory}"
        print(f"Copying jobs from source pod to local machine...")
        run_kubectl_command(command_cp_from_pod)

        # Step 3: Copy jobs from local machine to destination pod
        command_cp_to_pod = f"cp {local_directory}/. {namespace}/{destination_pod_name}:{source_directory}"
        print(f"Copying jobs to destination pod...")
        run_kubectl_command(command_cp_to_pod)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        exit(1)

if __name__ == "__main__":
    main()
