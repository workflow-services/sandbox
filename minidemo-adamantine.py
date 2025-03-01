import os
import time
import requests

api_token = os.environ['API_TOKEN']

# *** Step 1: Ensure that Defiant is online (no auth necessary) ***
resp = requests.get('https://s3m.apps.olivine.ccs.ornl.gov/olcf/v1alpha/status/defiant')
print(resp.json())
if resp.json()['status'] != 'OPERATIONAL':
    print("Defiant offline! Please try again")
else:
    print("Defiant online! Continuing to submit job...")



# *** Step 2: Submit a job to Defiant (must pack Authorization header) ***
headers = {
            "Authorization": f"{api_token}",
            "Content-Type": "application/json"
            }
jobs_url = "https://s3m.apps.olivine.ccs.ornl.gov/slurm/v0.0.42/defiant/job/submit"

job_script = {
  "job": {
    "script": "#!/bin/bash --login\n echo \"testing api ${HELLO}...\"; srun bash -c \"apptainer exec --bind $(pwd):/home/adaptive-control-workspace/shared adamantine-driver_latest.sif bash run_shadow_demo.sh 4\"; ",
    "name": "DocumentationJob",
    "account": "csc266",
    "partition": "batch-gpu",
    "current_working_directory": "/lustre/polis/csc266/proj-shared/demo-intersect-apptainer/adaptive-control-driver/",
    "environment": [
      "HELLO=world"
    ],
    "nodes": "1",
    "tasks": 1,
    "time_limit": {
      "number": 30,
      "set": True
    }
  }
}

response = requests.post(jobs_url, headers=headers, json=job_script)

job_id = response.json()['job_id']

if len(response.json()['errors']) == 0:
    print(f"Job successfully submitted with ID {job_id}. Continuing...")
else:
    print("Job did not successfully submit. Terminating...")


job_status_url = f"https://s3m.apps.olivine.ccs.ornl.gov/slurm/v0.0.42/defiant/job/{job_id}"

while True:
    response = requests.get(job_status_url, headers=headers)
    status = response.json()['jobs'][0]['state']['current'][0]
    if status == "COMPLETED":
        print(f"Job with id {job_id} successfully completed! Terminating monitor loop...")
        break
    elif status == "FAILED":
        print(f"Job with id {job_id} has failed! Terminating monitor loop...")
        break
    else:
        print(status)
        print(f"Job with id {job_id} still running... sleeping...")
        time.sleep(5)
