import subprocess
import json
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


def cleanup():
    # Resources to delete
    resources = {
        "me-central-1": {
            "ecs": ["i-l4v57xfhgz3omcxf4gy7"],
            "disks": ["d-l4vcl9wtgyz6hsq5mul4", "d-l4v02q84jjxt6o7gutwr", "d-l4v57xfhgz3oldf2vzq0", "d-l4v57xfhgz3omcxmwzss"],
            "nat": ["ngw-l4vm2jux152b1vytaym1w"],
            "eip": ["eip-l4vpvpufx1w7jm61cc4if"]
        },
        "me-east-1": {
            "nat": ["ngw-eb34hvzkucmmw7lkvgvua"],
            "eip": ["eip-eb3r2nnozeqwcv64xsl3v"]
        }
    }

    # 1. Stop and Delete ECS Instances
    for region, items in resources.items():
        if "ecs" in items:
            for instance_id in items["ecs"]:
                print(f"Stopping ECS {instance_id} in {region}...")
                run_command(
                    f"aliyun ecs StopInstance --RegionId {region} --InstanceId {instance_id} --ForceStop true")

                # Wait for stopped state (simple loop)
                print(f"Waiting for {instance_id} to stop...")
                time.sleep(10)

                print(f"Deleting ECS {instance_id}...")
                run_command(
                    f"aliyun ecs DeleteInstance --RegionId {region} --InstanceId {instance_id} --Force true")

    # 2. Delete Disks
    for region, items in resources.items():
        if "disks" in items:
            for disk_id in items["disks"]:
                print(f"Deleting Disk {disk_id} in {region}...")
                run_command(
                    f"aliyun ecs DeleteDisk --RegionId {region} --DiskId {disk_id}")

    # 3. Delete NAT Gateways
    for region, items in resources.items():
        if "nat" in items:
            for nat_id in items["nat"]:
                print(f"Deleting NAT Gateway {nat_id} in {region}...")
                # Force=true deletes SNAT/DNAT entries
                run_command(
                    f"aliyun vpc DeleteNatGateway --RegionId {region} --NatGatewayId {nat_id} --Force true")

    # 4. Release EIPs
    for region, items in resources.items():
        if "eip" in items:
            for eip_id in items["eip"]:
                print(f"Releasing EIP {eip_id} in {region}...")
                run_command(
                    f"aliyun vpc ReleaseEipAddress --RegionId {region} --AllocationId {eip_id}")


if __name__ == "__main__":
    cleanup()
