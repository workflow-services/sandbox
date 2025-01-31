import json
import logging
import os

import yaml
from typing import Dict
from olcf_facility_api.clients import StatusClient, ComputeClient
import time
from intersect_sdk import (
    HierarchyConfig,
    IntersectBaseCapabilityImplementation,
    IntersectService,
    IntersectServiceConfig,
    default_intersect_lifecycle_loop,
    intersect_message,
    intersect_status,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class S3MIntersectCapability(IntersectBaseCapabilityImplementation):
    """Rudimentary capability implementation example.

    All capability implementations are required to have an @intersect_status decorated function,
    but we do not use it here.

    The operation we are calling is `say_hello_to_name` , so the message being sent will need to have
    an operationId of `say_hello_to_name`. The operation expects a string sent to it in the payload,
    and will send a string back in its own payload.
    """

    intersect_sdk_capability_name = 'IntersectS3M'

    @intersect_status()
    def status(self) -> str:
        """Basic status function which returns a hard-coded string."""
        return 'Up'

    @intersect_message()
    def run_compute_job(self, job_script_str: str) -> str:
        """Takes in a string parameter and says 'Hello' to the parameter!"""
        job_script = json.loads(job_script_str)
        compute_cli = ComputeClient()
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

        return f'Everything went well with this script: \n\n{job_script}\n\nSUCCESS\o/!!!'


if __name__ == '__main__':
    """
    step one: create configuration class, which handles validation - see the IntersectServiceConfig class documentation for more info

    In most cases, everything under from_config_file should come from a configuration file, command line arguments, or environment variables.
    """
    home_path = os.path.expanduser("~")
    intersect_config_file = os.path.join(home_path, ".intersect/settings.yaml")
    with open(intersect_config_file) as config_reader:
        config_raw = yaml.safe_load(config_reader)

    config = IntersectServiceConfig(
        hierarchy=HierarchyConfig(**config_raw["hierarchy"]),
        data_stores=config_raw["data_stores"],
        brokers=config_raw["brokers"],
    )
    """
    step two - create your own capability implementation class.

    You have complete control over how you construct this class, as long as it has decorated functions with
    @intersect_message and @intersect_status, and that these functions are appropriately type-annotated.
    """
    capability = S3MIntersectCapability()

    """
    step three - create service from both the configuration and your own capability
    """
    service = IntersectService([capability], config)

    """
    step four - start lifecycle loop. The only necessary parameter is your service.
    with certain applications (i.e. REST APIs) you'll want to integrate the service in the existing lifecycle,
    instead of using this one.
    In that case, just be sure to call service.startup() and service.shutdown() at appropriate stages.
    """
    logger.info('Starting hello_service, use Ctrl+C to exit.')
    default_intersect_lifecycle_loop(
        service,
    )

    """
    Note that the service will run forever until you explicitly kill the application (i.e. Ctrl+C)
    """
