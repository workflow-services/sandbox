import sys
import json
from datetime import datetime
from s3_controller import put, get, create_bucket_if_does_not_exist

# Get file_id from command line argument
file_id = sys.argv[1]

# Current time
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Temporary local file path to store the file downloaded from Minio
downloaded_file_path = "/tmp/downloaded_output.dat"

# Step 2: Get the file using the file_id
get(file_id, downloaded_file_path)

# Step 3: Read the file into a variable
with open(downloaded_file_path, 'r') as f:
    file_content = f.read()

# Step 4: Assert that the file contains the specified content
assert "This is a very complex dataset" in file_content, "File content does not match the expected text."

# Step 5: Print the contents of the file
print("File content before modification:")
print(file_content)

# Step 6: Append new content with current time
with open(downloaded_file_path, 'a') as f:
    f.write(f"Modified at: {current_time}\n")

# Step 7: Put the modified file back to Minio
new_file_id = put(downloaded_file_path)

# Step 8: Print the new file_id
print(f"The new file_id for the modified file is: {new_file_id}")
print(json.dumps({"file_id": new_file_id}))
