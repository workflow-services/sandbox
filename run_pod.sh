export $(cat cluster.env | xargs) # This will load the .env file into environment variables

img_registry=$(oc get is process1 -o jsonpath='{.status.dockerImageRepository}')

oc run process1-container --image=$img_registry:latest --restart=Never \
  --env "MINIO_URI=${MINIO_URI}" \
  --env "MINIO_ROOT_USER=${MINIO_ROOT_USER}" \
  --env "MINIO_ROOT_PASSWORD=${MINIO_ROOT_PASSWORD}"

echo "Now run 'oc logs -f process1-container' to see the logs."
