import subprocess
import zipfile
from pathlib import Path
import os
import shutil

# Define the target folder where you want to download the dependencies
target_folder = "dependencies"

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
zip_file_name = "aws_lambda_NaverKinBotServer.zip"

# Create a list to store patterns from .gitignore
ignore_patterns = []

# Read the .gitignore file and extract patterns
with open('.gitignore', 'r') as gitignore_file:
    for line in gitignore_file:
        if not line.startswith('#') and not line.isspace():
            ignore_patterns.append(line.strip())

ignore_patterns.extend(['create_lambda_package.py', '.git', 'Setup Environment.bat', 'Start Server.bat', 'venv', '.gitignore', zip_file_name, 'requirements.txt'])

if os.path.exists(zip_file_name):
    os.remove(zip_file_name)
    print(f"Existing ZIP file '{zip_file_name}' deleted.")
    
# Create a ZIP archive while respecting the ignore patterns
with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as my_zip:
    current_directory = Path('.')
    temp_deps = Path(target_folder)

    for subdir in temp_deps.iterdir():
        if not any(subdir.match(pattern) for pattern in ignore_patterns):
            for file_path in subdir.rglob('*'):
                # Calculate the relative path to remove the 'dependencies\' prefix
                relative_path = file_path.relative_to(target_folder)
                            # Exclude __pycache__ folders and their contents
                if (
                    '__pycache__' not in file_path.parts  # Exclude __pycache__ folders
                    and not any(file_path.match(pattern) for pattern in ignore_patterns)
                ):
                    my_zip.write(file_path, arcname=relative_path)
            if not os.path.isdir(subdir):
                relative_path = subdir.relative_to(target_folder)
                my_zip.write(subdir, arcname=relative_path)

    for file_path in current_directory.rglob('*'):
        if not any(file_path.match(pattern) for pattern in ignore_patterns):
            # Exclude __pycache__ folders and their contents
            if (
                '__pycache__' not in file_path.parts  # Exclude __pycache__ folders
                and '.git' not in file_path.parts      # Exclude the .git folder
                and 'venv' not in file_path.parts
                and not any(file_path.match(pattern) for pattern in ignore_patterns)
            ):
                my_zip.write(file_path)