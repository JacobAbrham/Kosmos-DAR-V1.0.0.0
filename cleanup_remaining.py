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


def cleanup_remaining():
    region = "me-central-1"

    # ECS Instances to delete
    ecs_instances = [
        "i-l4v1h5tsqcpukby0gpxz",
        "i-l4v57xfhgz3omcxf4gy8",
        "i-l4v1csya7lihah7ee73w"
    ]

    # RDS Instances to delete
    rds_instances = [
        "pgm-l4v660e6m0g9y248"
    ]

    # Disks to delete (if not auto-deleted with instance)
    disks = [
        "d-l4v57xfhgz3omcxmwzsu",
        "d-l4v1csya7lihah7anktx"
    ]

    # 1. Stop and Delete ECS Instances
    for instance_id in ecs_instances:
        print(f"Stopping ECS {instance_id}...")
        run_command(
            f"aliyun ecs StopInstance --RegionId {region} --InstanceId {instance_id} --ForceStop true")

    print("Waiting for instances to stop...")
    time.sleep(15)

    for instance_id in ecs_instances:
        print(f"Deleting ECS {instance_id}...")
        run_command(
            f"aliyun ecs DeleteInstance --RegionId {region} --InstanceId {instance_id} --Force true")

    # 2. Delete RDS Instances
    for db_instance_id in rds_instances:
        print(f"Deleting RDS {db_instance_id}...")
        run_command(
            f"aliyun rds DeleteDBInstance --RegionId {region} --DBInstanceId {db_instance_id}")

    # 3. Delete Disks (Best effort, they might be gone with ECS)
    for disk_id in disks:
        print(f"Deleting Disk {disk_id}...")
        run_command(
            f"aliyun ecs DeleteDisk --RegionId {region} --DiskId {disk_id}")


if __name__ == "__main__":
    cleanup_remaining()
