#!/bin/bash
set -e

IMAGE_NAME=shuttledb
if [[ -z "$IMAGE_NAME" ]]; then
  echo "The IMAGE_NAME must be set"
  exit 1
fi

DOCKER_HOST=${DOCKER_HOST:-localhost}
CONTAINER_NAME=${CONTAINER_NAME:-shuttledb}
DATA_DIR=${DATA_DIR:-$PWD/data}
BIN_CMD=${BIN_CMD:-postgres}
PGPORT=${PGPORT:=5432}

VOLUME_MOUNT=""
if [[ -n "$DATA_DIR" ]]; then
  VOLUME_MOUNT="-v $DATA_DIR:/tmp"
fi

docker run -d \
  --name $CONTAINER_NAME --rm \
  -p ${PGPORT}:5432 \
  $VOLUME_MOUNT \
  $IMAGE_NAME \
  -clog_line_prefix="%m [%p]: [%l-1] %u@%d" \
  -clog_error_verbosity=VERBOSE \
  -cshared_preload_libraries='timescaledb,pg_cron' \
  -ccron.database_name='shuttle_database'

set +e
for i in {1..10}; do
  sleep 2

  pg_isready -h $DOCKER_HOST

  if [[ $? == 0 ]] ; then
    exit 0
  fi

done
