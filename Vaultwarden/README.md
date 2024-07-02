# VaultWardenBackup
A python script to backup the important data from vaultwarden. 

This includes:
- Main database (db.sqlite3)
- Attachments folder

## Features
### Logging
Every step of the backup is logged to a backup.log file.

This includes info and error messages.

### Database backup
The database is backed up via the command

```
sqlite3 db.sqlite3 .backup [output_file]
```

in order to avoid corruption.

## Usage
```
usage: vault_warden_backup.py [-h] [-d DATA_DIR] [-b BACKUP_DIR]
                              [-m MAX_BACKUPS]

options:
  -h, --help                                 show this help message and exit
  -d DATA_DIR, --data_dir DATA_DIR
                                             Directory containing all of Vaultwarden's data
  -b BACKUP_DIR, --backup_dir BACKUP_DIR
                                             Directory to backup to
  -m MAX_BACKUPS, --max_backups MAX_BACKUPS
                                             The maximum number of backups in the backup directory.
                                             This WILL DELETE old backups
```

### Automation
This script is meant to be called with via a crontab.

In Linux:
```
crontab -e
```

Add a simple command to the bottom, such as:
```
33 03 * * * vault_warden_backup.py [optional_arguments]
```

Given that this script is located in ~/bin.

It is also recommended that you back up this backup off-site with another crontab using rclone.

### Piping
This script returns 1 when a catastrophic errors occurs.

This allows behaviors like sending a Telegram message when an error occurs:

```
vault_warden_backup.py || notify_me.py -m "Error backing up VaultWarden"
```

notify_me.py is available [here](https://github.com/oPisiti/NotifyMe)

### Customization
Under "Constants - Default values" inside the script, the following are defined:
- DATA_DIR = HOME_DIR + "/docker-Vaultwarden/vw-data/"
- BASE_BACKUP_DIR     = "/Archive/Vaultwarden-backup/"
- MAX_NUMBER_BACKUPS  = 30

These values are then overridden if the script is called with any optional command line arguments.

Therefore, to make the call simpler, you may change these values accordingly.