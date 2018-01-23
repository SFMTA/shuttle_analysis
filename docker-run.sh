#!/bin/bash
set -e

WORK_DIR=${WORK_DIR:-$PWD}

VOLUME_MOUNT=""
CONTAINER_NAME=${CONTAINER_NAME:-shuttlenb}
if [[ -n "$WORK_DIR" ]]; then
    VOLUME_MOUNT="-v $WORK_DIR:/home/jovyan/work"
fi

# using jupyter/base-notebook will fetch the base image and run it
#IMAGE_NAME=jupyter/base-notebook
IMAGE_NAME=shuttlenb

docker run -it \
  --name $CONTAINER_NAME --rm \
  -p 8888:8888 \
  $VOLUME_MOUNT \
  $IMAGE_NAME 

