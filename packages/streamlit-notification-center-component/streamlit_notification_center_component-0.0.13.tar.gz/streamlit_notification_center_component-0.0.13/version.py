#!/usr/bin/env python

import re
import sys

def update_version(file_path, update_type, direction='increment'):
  # Read the content of the setup.py file
  with open(file_path, 'r') as file:
    content = file.read()

  # Extract the current version using a regular expression
  version_match = re.search(r'version="(\d+)\.(\d+)\.(\d+)"', content)
  if version_match:
    major, minor, patch = map(int, version_match.groups())

    # Increment or decrement the version based on the parameters
    if update_type == 'major':
      major = major + 1 if direction == 'increment' else max(major - 1, 0)
    elif update_type == 'minor':
      minor = minor + 1 if direction == 'increment' else max(minor - 1, 0)
    elif update_type == 'patch':
      patch = patch + 1 if direction == 'increment' else max(patch - 1, 0)

    # Replace the old version with the new version in the content
    new_version = f'version="{major}.{minor}.{patch}"'
    content = re.sub(r'version="\d+\.\d+\.\d+"', new_version, content)

    # Write the updated content back to the setup.py file
    with open(file_path, 'w') as file:
      file.write(content)

    print(f"Version updated to {major}.{minor}.{patch}")
  else:
    print("Could not find the version in the setup.py file")

def print_help():
  print("Usage: python version.py [major|minor|patch] [decrement]")
  print("Updates the version in setup.py based on the semver rules.")
  print("First argument specifies the part of the version to update.")
  print("Second argument can be 'decrement' to reduce the version.")

if __name__ == "__main__":
  if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help']:
    print_help()
  else:
    update_type = sys.argv[1]
    direction = 'decrement' if len(sys.argv) > 2 and sys.argv[2] == 'decrement' else 'increment'
    update_version('setup.py', update_type, direction)
