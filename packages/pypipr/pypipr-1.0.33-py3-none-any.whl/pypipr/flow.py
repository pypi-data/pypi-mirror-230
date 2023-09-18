"""
Runtutan prosedur untuk third party
"""


from .lib import *
from .ifunctions import *
from .console import *


def github_push(commit_msg=None):
    """
    Menjalankan command status, add, commit dan push

    ```py
    github_push('Commit Message')
    ```
    """

    def console_input(prompt, default):
        print_colorize(prompt, text_end="")
        if default:
            print(default)
            return default
        else:
            return input()

    print_log("Menjalankan Github Push")
    console_run("Checking files", "git status")
    msg = console_input("Commit Message if any or empty to exit : ", commit_msg)
    if msg:
        console_run("Mempersiapkan files", "git add .")
        console_run("Menyimpan files", f'git commit -m "{msg}"')
        console_run("Mengirim files", "git push")
    print_log("Selesai Menjalankan Github Push")


def github_pull():
    """
    Menjalankan command `git pull`

    ```py
    github_pull()
    ```
    """
    console_run("Git Pull", "git pull")


def github_user(email=None, name=None):
    """
    Menyimpan email dan nama user secara global sehingga tidak perlu
    menginput nya setiap saat.

    ```py
    github_user('my@emil.com', 'MyName')
    ```
    """
    if email:
        console_run("Update Github User Email", f"git config --global user.email {email}")
    if name:
        console_run("Update Github User Name", f"git config --global user.name {name}")

def pip_freeze_without_version(filename=None):
    """
    Memberikan list dari dependencies yang terinstall tanpa version.
    Bertujuan untuk menggunakan Batteries Included Python.

    ```py
    print(pip_freeze_without_version())
    ```
    """
    run = console_run("PIP Freeze", "pip list --format=freeze", capture_output=True)
    
    text = run.stdout
    if WINDOWS:
        text = text.decode()

    res = ijoin((i.split("=")[0] for i in text.splitlines()), separator="\n")
    
    if filename:
        return iopen(filename, data=res)
    
    return res


def poetry_update_version(mayor=False, minor=False, patch=True):
    """
    Update versi pada pyproject.toml menggunakan poetry

    ```py
    poetry_update_version()
    ```
    """
    if mayor:
        console_run("Update version mayor", "poetry version mayor")
    if minor:
        console_run("Update version minor", "poetry version minor")
    if patch:
        console_run("Update version patch", "poetry version patch")


def poetry_publish(token=None):
    """
    Publish project to pypi,org

    ```py
    poetry_publish()
    ```
    """
    if token:
        console_run("update token", f"poetry config pypi-token.pypi {token}")
    console_run("Build", "poetry build")
    console_run("Publish to PyPi.org", "poetry publish")


if __name__ == "__main__":
    print_colorize("Anda menjalankan module pypipr", color=colorama.Fore.RED)
