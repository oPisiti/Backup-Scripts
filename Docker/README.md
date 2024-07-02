# Docker compose backup solution

This tool finds all the docker-compose.yml fiels inside a specified directory.

It then creates an archive containing all of them, while keeping the subdirectories structure. Encryption is supported.

# Using the backup

1. Unzip `docker-compose-archive.tar.7z`
2. Copy `compose_all.sh` into the root of the compose files directories
3. Run the bash script `compose_all.sh`

This will recreate all of the docker containers for you

## Usage
```
usage: dockerComposeBackup.py [-h] [--docker-path DOCKER_PATH] [--output-dir OUTPUT_DIR] [--output-name OUTPUT_NAME] [-e] [-a]

options:
  -h, --help            show this help message and exit
  --docker-path DOCKER_PATH
                        Sets the directory in which the docker files are located. Default: ~/docker-Containers
  --output-dir OUTPUT_DIR
                        Sets a custom output directory. Default: ~/
  --output-name OUTPUT_NAME
                        Sets a custom output file name. Default: ~/docker-compose-archive.tar.7z
  -e                    Enables encryption
  -a                    Appends files to archive if it already exists
```

## Customization and encryption

If you want to call the script without the above arguments, you can customize the following.

Inside the main function, the first few lines are meant to be changed by the user.

Please change accordingly, ESPECIALLY: 

- `docker_files_dir`
- `output_dir`
- `encrypt`

If `encrypt` is set to True, a password will be prompted twice, so this option is not ideal for automatic backups

## Example

Say your containers' files are inside ~/docker-Containers/ and the structure is simmilar to:

```
├── Caddy
│   ├── Caddyfile
│   ├── docker-compose.yml
│   ├── docker-compose.yml.bak
│   └── template.env
├── Syncthing
│   ├── config
│   └── docker-compose.yml
├── Vaultwarden
│   ├── docker-compose.yml
│   └── vw-data
├── Wireguard
│   ├── config
│   └── docker-compose.yml
```

Then, a file ~/docker-compose-archive.tar.7z will be created with the following structure:

```
├── Caddy
│   ├── docker-compose.yml
├── Syncthing
│   └── docker-compose.yml
├── Vaultwarden
│   ├── docker-compose.yml
├── Wireguard
│   └── docker-compose.yml
```
