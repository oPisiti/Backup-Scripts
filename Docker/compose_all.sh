#!/usr/bin/bash

export COMPOSE_FILES="$(find . 2>/dev/null | grep "\.\/[a-zA-Z\-]*\/docker-compose.yml")"

for COMPOSE_FILE in $COMPOSE_FILES
do
    docker-compose -f $COMPOSE_FILE up -d --build
done