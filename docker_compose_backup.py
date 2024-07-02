#!/usr/bin/python3

import argparse
import getpass
import os
from pathlib import Path
import pwd
import re
import shutil
import subprocess


def main():
    # Parsing command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--docker-path", help="Sets the directory in which the docker files are located. Default: ~/docker-Containers")
    parser.add_argument("--output-dir", help="Sets a custom output directory. Default: ~/")
    parser.add_argument("--output-name", help="Sets a custom output file name. Default: ~/docker-compose-archive.tar.7z")
    parser.add_argument("-a", help="Appends files to archive if it already exists", action='store_true')
    parser.add_argument("-e", help="Enables encryption", action='store_true')
    parser.add_argument("-f", help="Forces creation/deletion of directories", action='store_true')
    args = parser.parse_args()

    # Configuration info
    HOME_DIR = str(Path.home())
    
    if not args.docker_path: DOCKER_FILES_DIR = HOME_DIR + "/docker-Containers/"     # ADJUST TO YOUR SETUP
    else:                    DOCKER_FILES_DIR = args.docker_path

    DOCKER_REGEX = ".*docker-compose.yml$"
    
    TMP_DIR_NAME = "docker-compose-backup.tmp/"
    TMP_DIR_PATH = f"{HOME_DIR}/{TMP_DIR_NAME}"
    
    if not args.output_dir:  OUTPUT_DIR = HOME_DIR + "/"
    else:                    OUTPUT_DIR = args.output_dir

    if not args.output_name: OUTPUT_FILE_NAME = "docker-compose-archive.tar.7z"
    else:                    OUTPUT_FILE_NAME = args.output_name + ".tar.7z"
    
    ENCRYPT    = args.e
    APPEND     = args.a
    FORCE_EXEC = args.f

    # Creating a tmp directory
    try:
        os.mkdir(TMP_DIR_PATH)
    except FileExistsError as e:
        if not FORCE_EXEC:
            confirm = input(f"File {TMP_DIR_PATH} already exists. Removing and recreate? (y/N) ")
            if confirm != "y": return        
        
        shutil.rmtree(TMP_DIR_PATH)
        
        os.mkdir(TMP_DIR_PATH)
        
    # Getting all docker-compose.yml paths
    compose_paths = subprocess.run(f"find {DOCKER_FILES_DIR} -maxdepth 2 -type f -regex '{DOCKER_REGEX}' 2>/dev/null", shell=True, text=True, stdout=subprocess.PIPE).stdout
    compose_paths = compose_paths.split("\n")
    
    # The expected number of subdirectories of a path for a top level docker-compose.yml file
    expected_size = len(DOCKER_FILES_DIR.split("/")) + 1
    
    # Cleaning the bigger paths - They include sub-sub dirs docker-compose.yml files.
    # Theses are probably for dependencies. They were NOT made by me
    # for key, value in compose_paths_dict.items():
    compose_paths_dict = dict()
    for p in compose_paths:
        dirs = p.split("/")
        if len(dirs) <= expected_size and len(dirs) != 1:
            compose_paths_dict[p] = dirs
    
    
    # Creating directories in TMP_DIR_NAME and moving docker-compose.yml files
    for path, parts in compose_paths_dict.items():
        dir_to_create = f"{TMP_DIR_PATH}{parts[-2]}"
        
        # Creating dir
        try:
            os.mkdir(dir_to_create)
        except FileExistsError as e:
            shutil.rmtree(dir_to_create)
            os.mkdir(dir_to_create)
    
        # Moving docker-compose.yml files
        subprocess.run(f"cp {path} {dir_to_create}", shell=True, text=True)
        
    # Deleting pre-existing archive is -a not set
    archive_path_full = OUTPUT_DIR + OUTPUT_FILE_NAME
    if not APPEND and os.path.exists(archive_path_full):
        print(f"File {archive_path_full} exists. Deleting")
        os.remove(archive_path_full)

    # Prompting for password
    if ENCRYPT:
        while True:
            try:
                password = getpass.getpass(prompt="Encryption password:")
                password_confirmation = getpass.getpass(prompt="Confirm password:")
            except Exception as error:
                print('ERROR', error)

            if password == password_confirmation: break
        
            print("\nPasswords do not match. Retrying")

    
    # Encrypting with password
    if ENCRYPT: subprocess.run(f"cd {HOME_DIR} && tar -cf - {TMP_DIR_NAME} | 7za a -p'{password}' -si {OUTPUT_DIR}{OUTPUT_FILE_NAME}", shell=True, text=True)    
    else:       subprocess.run(f"cd {HOME_DIR} && tar -cf - {TMP_DIR_NAME} | 7za a -si {OUTPUT_DIR}{OUTPUT_FILE_NAME}", shell=True, text=True)    
    
    # Cleaning up tmp dir
    shutil.rmtree(TMP_DIR_PATH)


if __name__ == "__main__":
    main()
