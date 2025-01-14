from datetime import datetime
import json
from s3_controller import put, get, create_bucket_if_does_not_exist

current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

file_path = "/tmp/output.dat"

with open(file_path, 'w') as f:
    f.write(f"This is a very complex dataset.\n")
    f.write(f"Written at: {current_time}\n")

print("Going to send this file to Minio.")

create_bucket_if_does_not_exist()
file_id = put(file_path)
print(f"This is the generated file_id: {file_id}")
print(json.dumps({"file_id": file_id}))

