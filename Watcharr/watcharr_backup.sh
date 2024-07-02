#!/bin/bash

# Variables
CONTAINER_DIR=~/docker-Containers/Watcharr/
BACKUP_DIR=/Archive/Watcharr_Backup/

# Get current date and time
datestamp=$(date +'%Y-%m-%d')
timestamp=$(date +'%H%M')

# Creating the backup folder if it does not exist
mkdir -p $BACKUP_DIR

# Execute pg_dump command to dump the database
sqlite3 $CONTAINER_DIR"data/watcharr.db" ".backup $BACKUP_DIR"watcharr_"$datestamp"_"$timestamp".sql""