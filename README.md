# sandbox

This how it's expected to work:

1. This script should run in a container on the OpenShift cluster

```shell
$> python process1.py 
This is the generated file_id: abcdef    # This means that the file has been generated and successfully stored in MinIO 
{"file_id": "abcdef"} 
```

2. This script should run on the HPC system (as a job)

```shell
$> python process2.py abcdef
The new file_id for the modified file is: xyz    # This means that a new file has been generated and stored back into Minio. 
{"file_id": "xyz"} 
```
