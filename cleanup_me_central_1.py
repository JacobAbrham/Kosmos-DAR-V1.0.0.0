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


def cleanup_me_central_1():
    region = "me-central-1"

    # 1. Delete Key Pairs
    key_pairs = ["kosmos-production-k3s"]
    for kp in key_pairs:
        print(f"Deleting KeyPair {kp}...")
        run_command(
            f"aliyun ecs DeleteKeyPairs --RegionId {region} --KeyPairNames '[\"{kp}\"]'")

    # 2. Delete Security Groups
    # Note: Must delete rules or ensure no instances attached. We already deleted instances.
    security_groups = [
        "sg-l4v1csya7lih7okrvref",  # kosmos-production-rds-sg
        "sg-l4vcl9wtgyz6fzm9u27y"  # kosmos-production-k3s-sg
    ]
    for sg in security_groups:
        print(f"Deleting Security Group {sg}...")
        run_command(
            f"aliyun ecs DeleteSecurityGroup --RegionId {region} --SecurityGroupId {sg}")

    # 3. Delete VSwitches
    vswitches = [
        "vsw-l4v53luycftlmr9a6jn13",
        "vsw-l4vb4z692ar06lqxlxuxk",
        "vsw-l4vx3bdqa4czpzyc08zxm"
    ]
    for vsw in vswitches:
        print(f"Deleting VSwitch {vsw}...")
        run_command(
            f"aliyun vpc DeleteVSwitch --RegionId {region} --VSwitchId {vsw}")

    # 4. Delete VPC
    vpc_id = "vpc-l4v4xolaclyyauvdzc3bj"
    print(f"Deleting VPC {vpc_id}...")
    run_command(f"aliyun vpc DeleteVpc --RegionId {region} --VpcId {vpc_id}")


if __name__ == "__main__":
    cleanup_me_central_1()
