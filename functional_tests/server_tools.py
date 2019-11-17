from fabric.api import run, cd
from fabric.context_managers import settings, shell_env

SERVER_USER = 'floriank'


def _run_manage_py_command(host, cmd):
    with settings(host_string=f'{SERVER_USER}@{host}'):
        with cd(f'~/sites/{host}'):
            return run(f'pipenv run python manage.py {cmd}')


def reset_database(host):
    _run_manage_py_command(host, 'flush --noinput')


def create_session_on_server(host, email):
    stdout = _run_manage_py_command(host, f'create_session {email}')
    session_key = stdout.splitlines()[-1]
    return session_key