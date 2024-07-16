import os
import subprocess

# Check if the required environment variables are set
required_env_vars = ["S3_ENDPOINT", "S3_ACCESS_KEY", "S3_SECRET_KEY", "S3_BUCKET", "LIVE_ID"]
for var in required_env_vars:
    if var not in os.environ:
        print(f"{var} is not set")
        exit(1)

print(f"LIVE_ID: {os.environ['LIVE_ID']}")

# Setup Minio Client
subprocess.run(["mc", "alias", "set", "minio", os.environ["S3_ENDPOINT"], os.environ["S3_ACCESS_KEY"], os.environ["S3_SECRET_KEY"]])
subprocess.run(["mc", "mb", "--ignore-existing", f"minio/{os.environ['S3_BUCKET']}"])

# Download the live stream
os.makedirs(f"/data/{os.environ['LIVE_ID']}", exist_ok=True)
os.chdir(f"/data/{os.environ['LIVE_ID']}")
subprocess.run(["yt-dlp", "--live-from-start", f"https://www.youtube.com/watch?v={os.environ['LIVE_ID']}"], check=False)
os.chdir("/data")

# Convert the live stream to an mp4
out = os.listdir(f"/data/{os.environ['LIVE_ID']}")[0]
first_part = next((file for file in os.listdir(f"/data/{os.environ['LIVE_ID']}") if file.endswith(".part")), None)
if first_part:
    out = first_part.replace(".part", "")
    subprocess.run(["ffmpeg", "-i", f"/data/{os.environ['LIVE_ID']}/*.part", f"/data/{os.environ['LIVE_ID']}/{out}"])

print(f"{out} created")

# Upload the mp4 to S3 and remove the directory
subprocess.run(["mc", "cp", f"/data/{os.environ['LIVE_ID']}/{out}", f"minio/{os.environ['S3_BUCKET']}/{out}"])
subprocess.run(["rm", "-rf", f"/data/{os.environ['LIVE_ID']}"])
