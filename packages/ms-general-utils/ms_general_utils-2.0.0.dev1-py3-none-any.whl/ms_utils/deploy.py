import errno
import shutil

import click
import os


@click.command()
def generate():
    call_path = os.getcwd()
    devops_path = os.path.join(os.path.dirname(__file__), "devops")
    for file_name in os.listdir(devops_path):
        print(f"Copy: {file_name}")
        source = os.path.join(devops_path,file_name)
        if os.path.isdir(source):
            shutil.copytree(source, os.path.join(call_path,file_name), dirs_exist_ok=True)
        else:
            shutil.copy2(source, call_path)


if __name__ == "__main__":
    generate()
