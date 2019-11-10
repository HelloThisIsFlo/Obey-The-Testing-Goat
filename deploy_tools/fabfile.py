import random
from fabric.contrib.files import append, exists
from fabric.api import cd, env, local, run, sudo

REPO_URL = 'git@github.com:FlorianKempenich/Obey-The-Testing-Goat.git'


def deploy():
    # # 'env.host' is the address of the server specified when
    # # using the cli
    site_folder = f'/home/{env.user}/sites/{env.host}'
    _prompt_for_sudo_password()
    run(f'mkdir -p {site_folder}')
    with cd(site_folder):
        _get_latest_source()
        _update_pipenv_virtualenv()
        _create_or_update_dotenv()
        _update_static_files()
        _update_database()
    _restart_service()


def _prompt_for_sudo_password():
    sudo('echo "Sudo password ok"')

def _get_latest_source():
    if exists('.git'):
        run('git fetch')
    else:
        run(f'git clone {REPO_URL} .')
    current_commit = local('git log -n 1 --format=%H', capture=True)
    run(f'git reset --hard {current_commit}')


def _update_pipenv_virtualenv():
    run('pipenv sync')


def _create_or_update_dotenv():
    def append_secret_key():
        current_contents = run('cat .env')
        if 'DJANGO_SECRET_KEY' not in current_contents:
            new_secret = ''.join(random.SystemRandom().choices(
                'abcdefghijklmnopqrstuvwxyz0123456789', k=50
            ))
            append('.env', f'DJANGO_SECRET_KEY={new_secret}')

    append('.env', 'DJANGO_DEBUG_FALSE=y')
    append('.env', f'SITENAME={env.host}')
    append_secret_key()


def _update_static_files():
    run('pipenv run python manage.py collectstatic --noinput')


def _update_database():
    run('pipenv run python manage.py migrate --noinput')

def _restart_service():
    sudo(f'systemctl restart gunicorn-{env.host}')
