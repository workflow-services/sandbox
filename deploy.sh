#!/bin/bash

# Help function
show_help() {
    echo "Usage: ./deploy.sh [delete|-h]"
    echo ""
    echo "Arguments:"
    echo "  delete   Delete the resources defined in the YAML files instead of applying them."
    echo "  -h       Show this help message."
    exit 0
}

# Check if -h is passed
if [[ "$1" == "-h" ]]; then
    show_help
fi

# Determine the action: apply or delete
action="apply"
if [[ "$1" == "delete" ]]; then
    action="delete"
    oc delete pod process1-container 2>/dev/null || true
fi

# List of files to process
files=("imagestream.yaml" "buildconfig.yaml")

# Loop through the files and apply/delete them
for file in "${files[@]}"; do
    echo "$file"
    oc $action -f "$file" || { echo "Failed to $action $file"; exit 1; }
done
echo "Waiting a bit..."
sleep 5
# Additional steps if not deleting
if [[ "$action" == "apply" ]]; then
    echo "Starting build for process1 with current code..."
    oc start-build process1 --from-dir=. || { echo "Failed to start build"; exit 1; }
    echo "Waiting a bit..."
    sleep 5
    echo "Running the pod using run_pod.sh..."
    ./run_pod.sh || { echo "Failed to run pod"; exit 1; }
fi

echo "Script completed successfully."
