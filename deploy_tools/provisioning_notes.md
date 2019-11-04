# Provisioning a new site

## Required packages:

- nginx
- Python 3.6
- Pip & Pipenv
- Git

### On Ubuntu

    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt update
    sudo apt install nginx git python3.6
    python -m pip install pip
    python3.6 -m pip install pip

## NginX Virtual Host config

- see `nginx.template.conf`
- replace DOMAIN with `goat-staging.ddns.net` (for example)

## Systemd service

- see `gunicornd-systemd.template.service`
- replace DOMAIN with `goat-staging.ddns.net`

## Folder structure

Assume we have a user account at /home/USERNAME

/home/USERNAME
└── sites
│   ├── DOMAIN1
│   │   └──...
│   ├── DOMAIN2
│   │   └──...
...
