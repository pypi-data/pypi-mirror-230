#!/bin/sh

# see https://git01.iis.fhg.de/ks-ip-lib/software/libjapi-demo/container_registry

set -e # terminate on any error

LOCAL_IMAGE="libjapi-demo:latest"
REGISTRY="git01.iis.fhg.de:5005"
GITLAB_IMAGE="ks-ip-lib/software/libjapi-demo"

docker tag $LOCAL_IMAGE $REGISTRY/$GITLAB_IMAGE
docker login $REGISTRY
docker push $REGISTRY/$GITLAB_IMAGE
docker logout $REGISTRY

