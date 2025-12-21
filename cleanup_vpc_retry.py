import subprocess
import time


def run_command(command):
    print(f"Running: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        return False


def cleanup_vpc_retry():
    region = "me-central-1"
    vpc_id = "vpc-l4v4xolaclyyauvdzc3bj"

    # 1. Delete VSwitches (Retry, just in case)
    # The previous error said "DependencyViolation.VSwitch", meaning VSwitches still existed or were being deleted.
    # But DescribeVSwitches returned 0. This suggests they might have been in "Pending" deletion state.
    # We will wait a bit and try deleting the VPC again.

    print("Waiting for VSwitch deletion to propagate...")
    time.sleep(10)

    print(f"Deleting VPC {vpc_id}...")
    run_command(f"aliyun vpc DeleteVpc --RegionId {region} --VpcId {vpc_id}")


if __name__ == "__main__":
    cleanup_vpc_retry()
