
import time
import requests
from olcf_facility_api.clients import StatusClient, ComputeClient

# assume token is stored in ~/.s3m/s3m_tokens.json as {"API_KEY": xxx}. Replace 'xxx' with your token from myOLCF. 
status_cli = StatusClient()
compute_cli = ComputeClient()


# *** Step 1: Ensure that Defiant is online (no auth necessary) *** 
defiant_status = status_cli.get_resource_status('defiant')
if defiant_status.resource_status != 'OPERATIONAL':
    print("Defiant offline! Please try again")
else:
    print("Defiant online! Continuing to submit job...")

# *** Step 2: Submit a job to Defiant (must pack Authorization header) ***
job_script = {
 "job": {
    "script": "#!/bin/bash --login\n echo \"testing api ${HELLO}...\"; srun bash -c \"source mini-venv/bin/activate && python3 write_file.py renan-mini.txt\"; ",
    "name": "DocumentationJob",
    "account": "csc266",
    "partition": "batch-gpu",
    "current_working_directory": "/lustre/polis/csc266/proj-shared",
    "environment": ["HELLO=world"],
    "nodes": "1",
    "tasks": 16,
    "time_limit": {
        "number": 30,
        "set":    True
    }
  }
}


# Submit and snag the job_id, ensure there are no errors. 
submit = compute_cli.submit_job(payload=job_script, resource='defiant')
job_id = submit.job_id

if not submit.error:
    print(f"Job successfully submitted with ID {job_id}. Continuing...")
else:
    print("Job did not successfully submit. Terminating...") 


# *** Step 3: Iteratively scan to check job status. ***
while True: 
    job_status = compute_cli.get_job_status('defiant', job_id)

    # If completed or failed, then break
    if job_status.job_state == "COMPLETED":
        print(f"Job with id {job_id} successfully completed! Terminating monitor loop...")
        break
    elif job_status.job_state == "FAILED":
        print(f"Job with id {job_id} FAILED! Terminating monitor loop...")
        break
    else:
        print(f"Job with id {job_id} still running... sleeping...") 
        time.sleep(5)  # no client-side rate limiting, please be gentle. 

