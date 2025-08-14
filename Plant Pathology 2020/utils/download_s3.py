import boto3
import os

bucket_name = 'thesis-abiya'
prefix = 'runpod/results/'
local_dir = 'downloaded_results'

s3 = boto3.client('s3')

# List all objects under the prefix
response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

if 'Contents' in response:
    for obj in response['Contents']:
        s3_key = obj['Key']
        if s3_key.endswith('/'):  # skip directories
            continue

        # Construct local path
        relative_path = os.path.relpath(s3_key, prefix)
        local_path = os.path.join(local_dir, relative_path)

        # Create local directories if they don't exist
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        # Download the file
        s3.download_file(bucket_name, s3_key, local_path)
        print(f"Downloaded {s3_key} to {local_path}")
else:
    print("No objects found under the prefix.")
