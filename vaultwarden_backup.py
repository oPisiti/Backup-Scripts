#!/usr/bin/python3

import argparse
import glob
import logging
import os
import re
import subprocess
import sys

from datetime import datetime
from pathlib import Path


def main():

    # Command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data_dir",    help="Directory containing all of Vaultwarden's data", type=str)
    parser.add_argument("-b", "--backup_dir",  help="Directory to backup to", type=str)
    parser.add_argument("-m", "--max_backups", help="The maximum number of backups in the backup directory. This WILL DELETE old backups", type=int)
    args = parser.parse_args()

    # Constants - Default values
    HOME_DIR = str(Path.home())
    DATA_DIR = HOME_DIR + "/docker-Containers/Vaultwarden/vw-data/"
    BASE_BACKUP_DIR         = "/Archive/Vaultwarden-backup/"
    BACKUP_FILE_INIT_STRING = "backup-"
    MAX_NUMBER_BACKUPS      = 30

    # Constants - Updated
    if args.data_dir    is not None: DATA_DIR = args.data_dir + ("/" if args.data_dir[-1] != "/" else "")
    if args.backup_dir  is not None: BASE_BACKUP_DIR = args.backup_dir + ("/" if args.backup_dir[-1] != "/" else "")
    if args.max_backups is not None: MAX_NUMBER_BACKUPS = args.max_backups

    # Setting up the logger
    logging.basicConfig(
        filename = f"{BASE_BACKUP_DIR}backup.log", 
        format   = '%(levelname)s %(asctime)s - %(message)s', 
        datefmt  = '%d-%b-%y %H:%M:%S', 
        level    = logging.INFO)

    logging.info("----- Starting Backup -----")

    now = datetime.now()

    # Getting the newest and oldest directories in BASE_BACKUP_DIR: https://stackoverflow.com/questions/10983705/how-to-get-the-newest-directory-in-python/10983925
    # CHANGE IN CASE OF MODIFICATION OF BACKUP FOLDERS NAMES (specially BACKUP_FILE_INIT_STRING)
    logging.info(f"Getting newest and oldest directories in {BASE_BACKUP_DIR}")

    directories_list = [f"{BASE_BACKUP_DIR}{d}" for d in os.listdir(f"{BASE_BACKUP_DIR}") if os.path.isdir(f"{BASE_BACKUP_DIR}{d}")]
    directories_list = [dir for dir in directories_list if BACKUP_FILE_INIT_STRING in dir]      
    directories_list.sort(key=lambda x: os.path.getmtime(x), reverse=True)

    # In case there are no matching backup directories
    try:               newest_dir = directories_list[0]
    except IndexError: newest_dir = None                    
    try:               oldest_dir = directories_list[-1]
    except IndexError: oldest_dir = None                

    logging.info(f"Latest backup:   {re.findall('backup-.*', newest_dir)[0] if newest_dir is not None else 'None'}")
    logging.info(f"Oldest backup:   {re.findall('backup-.*', oldest_dir)[0] if newest_dir is not None else 'None'}")

    # Creating the backup folder
    backup_dir = BASE_BACKUP_DIR + BACKUP_FILE_INIT_STRING + now.strftime("%Y.%m.%d-%Hh.%Mmin.%Ss") + "/"
    logging.info(f"Creating backup: {re.findall(f'{BACKUP_FILE_INIT_STRING}.*', backup_dir)[0][:-1]}")
    mkdir_backup_result = subprocess.run(["mkdir", "-p", backup_dir])
    
    if mkdir_backup_result.returncode == 0:
        logging.info("Success")
    else:
        logging.error(f"Failed to create directory {backup_dir}. Aborting ...")
        sys.exit(1)

    # sqlite database
    logging.info("Backing up sqlite3 database")
    database_name = "db.sqlite3"
    database_path = DATA_DIR + database_name
    db_backup_results = subprocess.run(["sqlite3", database_path, f".backup {backup_dir}{database_name}"])
    
    if db_backup_results.returncode == 0:
        logging.info("Success")
    else:
        logging.error(f"Failed to backup database to {backup_dir}. Aborting ...")
        sys.exit(1)

    # Attachments directory
    logging.info("Backing up attachments directory")
    attachments_name = "attachments/"
    attachments_dir = DATA_DIR + attachments_name
    attachments_backup_results = subprocess.run(["cp", "-r", attachments_dir, backup_dir + attachments_name])
    
    if attachments_backup_results.returncode == 0:
        logging.info("Success")
    else:
        logging.error(f"Failed to backup attachments directory to {backup_dir}")
        sys.exit(1)

    # Checking if the latest directory is the same as the newly created one: https://www.tecmint.com/compare-find-difference-between-two-directories-in-linux/
    if newest_dir is not None:
        diff = subprocess.run(["diff", "-qr", newest_dir, backup_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Deleting new backup in case it is the same as latest backup
        if diff.stdout == b'':              
            logging.info("New backup is the same as the latest backup. Deleting new backup")
            del_new_backup_results = subprocess.run(["rm", "-r", backup_dir])                       
            
            if del_new_backup_results.returncode == 0:
                logging.info("Success")
            else:
                logging.error("Failed")

    # Deleting oldest backup directory in case of more than MAX_NUMBER_BACKUPS backups
    if oldest_dir is not None and len(directories_list) > MAX_NUMBER_BACKUPS:
        logging.info(f"There are more than {MAX_NUMBER_BACKUPS} backups. Removing the oldest one: {re.findall(f'{BACKUP_FILE_INIT_STRING}.*', oldest_dir)[0]}")
        del_too_many_results = subprocess.run(["rm", "-r", oldest_dir])
        
        if del_too_many_results.returncode == 0:
            logging.info("Success")
        else:
            logging.error(f"Failed")

    logging.info("")

if __name__ == "__main__":
    main()
