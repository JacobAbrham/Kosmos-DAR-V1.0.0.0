import subprocess


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


def delete_buckets():
    buckets = [
        "oss://kosmos-production-artifacts-33e51c92",
        "oss://kosmos-production-backups-33e51c92",
        "oss://kosmos-production-mlflow-33e51c92"
    ]

    region = "me-central-1"

    for bucket in buckets:
        print(f"Cleaning bucket {bucket}...")
        # Remove all objects (-r recursive, -f force) with region
        run_command(f"aliyun ossutil rm {bucket} -rf --region {region}")

        print(f"Deleting bucket {bucket}...")
        # Remove bucket (rb) with region. -f to force without confirmation
        run_command(f"aliyun ossutil rb {bucket} -f --region {region}")


if __name__ == "__main__":
    delete_buckets()
