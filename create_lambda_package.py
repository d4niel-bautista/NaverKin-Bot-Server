import subprocess
import zipfile
from pathlib import Path
import os
import shutil

# Define the target folder where you want to download the dependencies
target_folder = "python"

if os.path.isdir(target_folder):
    shutil.rmtree(target_folder)

# Define a list of Python packages you want to download
with open("requirements.txt", "r") as file:
    dependencies = [i.strip() for i in file.readlines()]

# Iterate through the list of dependencies and download them to the target folder
for package in dependencies:
    print(f"Downloading {package} to {target_folder}...")
    subprocess.run(["pip", "install", "--target", target_folder, "--platform", "manylinux_2_17_x86_64", "--only-binary=:all:", package])
print(f"Dependencies downloaded to {target_folder}")

# Define the name of the ZIP file you want to create
zip_base_dependencies = "base_dependencies_layer.zip"
http_handler_zip = "naver_kin_bot_server-http.zip"
websocket_handler_zip = "naver_kin_bot_server-websocket.zip"
second_layer_dependencies = ['database', 'services', 'utils']
second_layer_zip_filename = 'database-services-utils.zip'

# Create a list to store patterns from .gitignore
ignore_patterns = []

# Read the .gitignore file and extract patterns
with open('.gitignore', 'r') as gitignore_file:
    for line in gitignore_file:
        if not line.startswith('#') and not line.isspace():
            ignore_patterns.append(line.strip())

if os.path.exists(http_handler_zip):
    os.remove(zip_base_dependencies)
    os.remove(http_handler_zip)
    print(f"Existing ZIP file '{http_handler_zip}' deleted.")

if os.path.exists(second_layer_zip_filename):
    os.remove(second_layer_zip_filename)
    print(f"Existing ZIP file '{second_layer_zip_filename}' deleted.")

if os.path.exists(websocket_handler_zip):
    os.remove(websocket_handler_zip)
    print(f"Existing ZIP file '{websocket_handler_zip}' deleted.")

# Create a ZIP archive for base dependencies
with zipfile.ZipFile(zip_base_dependencies, 'w', zipfile.ZIP_DEFLATED) as my_zip:
    temp_deps = Path(target_folder)

    for subdir in temp_deps.iterdir():
        if not any(subdir.match(pattern) for pattern in ignore_patterns):
            for file_path in subdir.rglob('*'):
                # Exclude __pycache__ folders and their contents
                if (
                    '__pycache__' not in file_path.parts  # Exclude __pycache__ folders
                    and not any(file_path.match(pattern) for pattern in ignore_patterns)
                ):
                    my_zip.write(file_path)
            if not os.path.isdir(subdir):
                my_zip.write(subdir)
    shutil.rmtree(target_folder)

shutil.copytree('database', os.path.join(target_folder, 'database'))
shutil.copytree('services', os.path.join(target_folder, 'services'), dirs_exist_ok=True)
shutil.copytree('utils', os.path.join(target_folder, 'utils'), dirs_exist_ok=True)

# Create a ZIP archive for second dependencies layer
with zipfile.ZipFile(second_layer_zip_filename, 'w', zipfile.ZIP_DEFLATED) as my_zip:
    temp_deps = Path(target_folder)
    
    for subdir in temp_deps.iterdir():
        if not any(subdir.match(pattern) for pattern in ignore_patterns):
            for file_path in subdir.rglob('*'):
                # Exclude __pycache__ folders and their contents
                if (
                    '__pycache__' not in file_path.parts  # Exclude __pycache__ folders
                    and not any(file_path.match(pattern) for pattern in ignore_patterns)
                ):
                    my_zip.write(file_path)
            if not os.path.isdir(subdir):
                my_zip.write(subdir)
    shutil.rmtree(target_folder)

ignore_patterns.extend(['create_lambda_package.py', '.git', 'Setup Environment.bat', 'Start Server.bat', 'venv', '.gitignore', http_handler_zip, 'requirements.txt', zip_base_dependencies, 'test.py', 'database', 'services', 'utils', second_layer_zip_filename])
    
# Create a ZIP archive while respecting the ignore patterns
with zipfile.ZipFile(http_handler_zip, 'w', zipfile.ZIP_DEFLATED) as my_zip:
    current_directory = Path('.')

    for file_path in current_directory.rglob('*'):
        if not any(file_path.match(pattern) for pattern in ignore_patterns):
            # Exclude __pycache__ folders and their contents
            if (
                '__pycache__' not in file_path.parts  # Exclude __pycache__ folders
                and '.git' not in file_path.parts      # Exclude the .git folder
                and 'venv' not in file_path.parts
                and 'database' not in file_path.parts
                and 'services' not in file_path.parts
                and 'utils' not in file_path.parts
                and 'websocket_handler' not in file_path.parts
                and not any(file_path.match(pattern) in file_path.parts for pattern in ignore_patterns)
            ):
                my_zip.write(file_path)

ignore_patterns.extend(['main.py', http_handler_zip, websocket_handler_zip])

with zipfile.ZipFile(websocket_handler_zip, 'w', zipfile.ZIP_DEFLATED) as my_zip:
    websocket_handler_dir = Path('websocket_handler')
    
    for file_path in websocket_handler_dir.rglob('*'):
        if not any(file_path.match(pattern) for pattern in ignore_patterns):
            # Exclude __pycache__ folders and their contents
            if (
                '__pycache__' not in file_path.parts  # Exclude __pycache__ folders
                and '.git' not in file_path.parts      # Exclude the .git folder
                and 'venv' not in file_path.parts
                and 'database' not in file_path.parts
                and 'services' not in file_path.parts
                and 'utils' not in file_path.parts
                and 'http_handler' not in file_path.parts
                and 'networking' not in file_path.parts
                and not any(file_path.match(pattern) in file_path.parts for pattern in ignore_patterns)
            ):
                arcname = file_path.relative_to(websocket_handler_dir)
                my_zip.write(file_path, arcname=arcname)