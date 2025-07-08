import os
import subprocess
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser(description='Download live stream and optionally upload to S3')
parser.add_argument('-d', '--directory', type=str, help='Directory to save the video (skips S3 upload)')
args = parser.parse_args()

# Check if the required environment variables are set (only if not using local directory)
if not args.directory:
    required_env_vars = ["S3_ENDPOINT", "S3_ACCESS_KEY", "S3_SECRET_KEY", "S3_BUCKET", "LIVE_ID"]
    for var in required_env_vars:
        if var not in os.environ:
            print(f"{var} is not set")
            exit(1)
else:
    # For local directory mode, only LIVE_ID is required
    if "LIVE_ID" not in os.environ:
        print("LIVE_ID is not set")
        exit(1)

print(f"LIVE_ID: {os.environ['LIVE_ID']}")

# Setup Minio Client (only if not using local directory)
if not args.directory:
    subprocess.run(["mc", "alias", "set", "minio", os.environ["S3_ENDPOINT"], os.environ["S3_ACCESS_KEY"], os.environ["S3_SECRET_KEY"]])
    subprocess.run(["mc", "mb", "--ignore-existing", f"minio/{os.environ['S3_BUCKET']}"])

# Set the base directory for saving files
base_dir = args.directory if args.directory else "/data"
work_dir = f"{base_dir}/{os.environ['LIVE_ID']}"

# Download the live stream
os.makedirs(work_dir, exist_ok=True)
os.chdir(work_dir)
subprocess.run(["yt-dlp", "--live-from-start", f"https://www.youtube.com/watch?v={os.environ['LIVE_ID']}"], check=False)
os.chdir(base_dir)

# Convert the live stream to an mp4
out = os.listdir(work_dir)[0]
first_part = next((file for file in os.listdir(work_dir) if file.endswith(".part")), None)
if first_part:
    out = first_part.replace(".part", "")
    subprocess.run(["ffmpeg", "-i", f"{work_dir}/*.part", f"{work_dir}/{out}"])

print(f"{out} created")

# Upload the mp4 to S3 and remove the directory (only if not using local directory)
if not args.directory:
    subprocess.run(["mc", "cp", f"{work_dir}/{out}", f"minio/{os.environ['S3_BUCKET']}/{out}"])
    subprocess.run(["rm", "-rf", work_dir])
else:
    print(f"Video saved to: {work_dir}/{out}")
