import subprocess
import time
import json


def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return None


def get_eip_status(region, eip_id):
    output = run_command(
        f"aliyun vpc DescribeEipAddresses --RegionId {region} --AllocationId {eip_id}")
    if output:
        try:
            data = json.loads(output)
            if data["EipAddresses"]["EipAddress"]:
                return data["EipAddresses"]["EipAddress"][0]["Status"]
        except:
            pass
    return None


def release_eips():
    eips = {
        "me-central-1": "eip-l4vpvpufx1w7jm61cc4if",
        "me-east-1": "eip-eb3r2nnozeqwcv64xsl3v"
    }

    for region, eip_id in eips.items():
        print(f"Checking EIP {eip_id} in {region}...")
        for _ in range(30):  # Try for 5 minutes
            status = get_eip_status(region, eip_id)
            print(f"Status: {status}")

            if status == "Available":
                print(f"Releasing {eip_id}...")
                run_command(
                    f"aliyun vpc ReleaseEipAddress --RegionId {region} --AllocationId {eip_id}")
                print("Released.")
                break
            elif status is None:
                print("EIP not found (maybe already released).")
                break

            time.sleep(10)


if __name__ == "__main__":
    release_eips()
