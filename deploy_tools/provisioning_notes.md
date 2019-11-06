# Provisioning a new site

## Required packages:

```
- nginx
- Python 3.6
- Pip & Pipenv
- Git
```

### On Ubuntu

    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt update
    sudo apt install nginx git python3.6
    python -m pip install pip
    python3.6 -m pip install pip

## NginX Virtual Host config

- See `nginx.template.conf`
- Replace DOMAIN with `goat-staging.ddns.net` (for example) and copy to `/etc/nginx/sites-available/goat-staging.ddns.net`

  ```bash
  cat ./deploy_tools/nginx.template.conf \
  | sed 's/DOMAIN/goat-staging.ddns.net/g' \
  | sudo tee /etc/nginx/sites-available/goat-staging.ddns.net
  ```

- Enable site by creating symlink

  ```bash
  cd /etc/nginx/sites-enabled
  sudo ln -s /etc/nginx/sites-available/goat-staging.ddns.net goat-staging.ddns.net
  ```

## Systemd service

- See `gunicornd-systemd.template.service`
- Replace DOMAIN with `goat-staging.ddns.net` (for example) and copy to `/etc/systemd/system/gunicorn-goat-staging.ddns.net.service`

  ```bash
  # Get the location of 'gunicorn' with 'pipenv run which gunicorn'
  # and update in second 'sed' command

  cat ./deploy_tools/gunicorn-systemd.template.service  \
  | sed 's/DOMAIN/goat-staging.ddns.net/g' \
  | sed "s|GUNICORN|/home/floriank/.local/share/virtualenvs/goat-staging.ddns.net-1KJo9bu7/bin/gunicorn|g" \
  | sudo tee /etc/systemd/system/gunicorn-goat-staging.ddns.net.service
  ```

## Restart/Reload everything

```bash
sudo systemctl daemon-reload
sudo systemctl reload nginx
sudo systemctl enable gunicorn-goat-staging.ddns.net.service
sudo systemctl start gunicorn-goat-staging.ddns.net.service
```

## Folder structure

Assume we have a user account at /home/USERNAME

```
/home/USERNAME
└── sites
│   ├── DOMAIN1
│   │ └──...
│   ├── DOMAIN2
│   │ └──...
...
```
