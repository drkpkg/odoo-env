import os, argparse, sys
import requests
import zipfile
import json

ODOO_VERSIONS = (("15.0", "3.8"), ("16.0", "3.9"), ("17.0", "3.10"), ("master", "3.11"))

def create_python_version_file():
    python_version_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".python-version")
    python_version = "3.7"
    with open(python_version_file, "w") as file:
        file.write(python_version)

def get_python_version():
    python_version_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".python-version")
    with open(python_version_file, "r") as file:
        return file.read().strip()

def create_odoo_version_file(version="master"):
    odoo_version_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".odoo-version")
    odoo_version = version
    with open(odoo_version_file, "w") as file:
        file.write(odoo_version)

def get_odoo_version():
    odoo_version_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".odoo-version")
    with open(odoo_version_file, "r") as file:
        return file.read().strip()

def remove_directory(path):
    if os.path.exists(path):
        for root, dirs, files in os.walk(path):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                remove_directory(os.path.join(root, dir))
        os.rmdir(path)

def remove_virtualenv():
    virtualenv_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv")
    remove_directory(virtualenv_directory)

def remove_odoo_directory():
    odoo_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "odoo")
    remove_directory(odoo_directory)

def restore_virtualenv():
    python_version = get_python_version()
    remove_virtualenv()
    os.system(f"pyenv install {python_version}")
    os.system(f"pyenv local {python_version}")
    os.system(f"python -m venv .venv")

def delete_directory(directory):
    if os.path.exists(directory):
        remove_directory(directory)

def download_odoo():
    odoo_version = get_odoo_version()
    odoo_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "odoo")
    delete_directory(odoo_directory)
    odoo_url = f"https://github.com/odoo/odoo/archive/refs/heads/{odoo_version}.zip"
    odoo_zip = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"odoo-{odoo_version}.zip")  
    download_percentage = 0
    total_percentage = 0
    with open(odoo_zip, "wb") as file:
        response = requests.get(odoo_url, stream=True)
        for data in response.iter_content(chunk_size=4096):
            file.write(data)
            download_percentage += len(data)
            total_percentage = download_percentage / 1024 / 1024
            sys.stdout.write(f"\rDownloading Odoo {odoo_version}: {total_percentage:.2f} MB")
            sys.stdout.flush()
    print("\n")
            
    try:
        with zipfile.ZipFile(odoo_zip, "r") as zip_ref:
            zip_ref.extractall(odoo_directory)
        os.remove(odoo_zip)
        sys.stdout.write(f"Odoo {odoo_version} downloaded successfully\n")
        # Move the extracted directory to the target directory
        odoo_source_directory = os.path.join(odoo_directory, f"odoo-{odoo_version}")
        odoo_target_directory = os.path.join(odoo_directory, "odoo")
        os.rename(odoo_source_directory, odoo_target_directory)
        sys.stdout.write(f"Odoo {odoo_version} moved successfully\n")
    except Exception as e:
        sys.stdout.write(f"Error: {e}\n")
        exit(1)
    
def restore_odoo():
    odoo_version = get_odoo_version()
    odoo_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "odoo")
    odoo_source_directory = os.path.join(odoo_directory, f"odoo-{odoo_version}")
    odoo_target_directory = os.path.join(odoo_directory, "odoo")
    remove_odoo_directory()
    os.rename(odoo_source_directory, odoo_target_directory)


def odoo_version_list():
    """
    Returns the list of versions of Odoo available in the repository.
    """
    odoo_versions = []
    for version, _ in ODOO_VERSIONS:
        odoo_versions.append(version)
    return odoo_versions

def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--restore", action="store_true", help="Restore Odoo and Virtualenv")
    arg_parser.add_argument("--download", action="store_true", help="Download Odoo")
    arg_parser.add_argument("--list", action="store_true", help="List available Odoo versions")
    # init v15.0
    arg_parser.add_argument("init", nargs="?", help="Initialize Odoo version")
    args = arg_parser.parse_args()
    if args.restore:
        restore_virtualenv()
        restore_odoo()
    if args.download:
        download_odoo()
    if args.list:
        print("\n".join(odoo_version_list()))
    if args.init:
        odoo_version_arg = args.init
        create_odoo_version_file(odoo_version_arg)
        create_python_version_file()
        restore_virtualenv()
        download_odoo()
        restore_odoo()
    
if __name__ == "__main__":
    main()