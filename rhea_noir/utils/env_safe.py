import os
import shutil
from typing import Optional

ENV_PATH = ".env"
BACKUP_PATH = ".env.bak"

def safe_update_env(key: str, value: str):
    """
    Safely updates or adds a key-value pair to the .env file.
    Creates a backup first. Preserves comments and existing structure.
    """
    if not os.path.exists(ENV_PATH):
        print(f"Creating new {ENV_PATH}")
        with open(ENV_PATH, "w") as f:
            f.write(f"{key}={value}\n")
        return

    # 1. Create Backup
    try:
        shutil.copy2(ENV_PATH, BACKUP_PATH)
        print(f"Backup created at {BACKUP_PATH}")
    except IOError as e:
        print(f"Error creating backup: {e}")
        return

    # 2. Read existing content
    with open(ENV_PATH, "r") as f:
        lines = f.readlines()

    new_lines = []
    key_found = False
    
    for line in lines:
        # Check if line starts with key=
        clean_line = line.strip()
        if clean_line.startswith(f"{key}="):
            new_lines.append(f"{key}={value}\n")
            key_found = True
            print(f"Updating existing key: {key}")
        else:
            new_lines.append(line)

    if not key_found:
        # Append if new
        if new_lines and not new_lines[-1].endswith("\n"):
            new_lines[-1] += "\n"
        new_lines.append(f"{key}={value}\n")
        print(f"Adding new key: {key}")

    # 3. Write safely
    try:
        with open(ENV_PATH, "w") as f:
            f.writelines(new_lines)
        print(f"Successfully updated {ENV_PATH}")
    except IOError as e:
        print(f"Error writing .env: {e}")
        # Restore backup
        shutil.copy2(BACKUP_PATH, ENV_PATH)
        print("Restored backup due to write error.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python env_safe.py KEY VALUE")
    else:
        safe_update_env(sys.argv[1], sys.argv[2])
