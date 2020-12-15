#!/usr/bin/env python3

import os, pwd, grp
import subprocess
from dotenv import load_dotenv
import sys
import json

load_dotenv()

# Constants

UNPRIVILEGED_USER = os.getenv("UNPRIVILEGED_USER")
# path to change the current working directory to
CHDIR_PATH = os.getenv("CHDIR_PATH")

# Helper functions

def drop_privileges(uid_name="nobody", gid_name="nogroup"):
    if os.getuid() != 0:
        return

    # Get the uid/gid from the name
    running_uid = pwd.getpwnam(uid_name).pw_uid
    running_gid = grp.getgrnam(gid_name).gr_gid

    # Remove group privileges
    os.setgroups([])

    # Try setting the new uid/gid
    os.setgid(running_gid)
    os.setuid(running_uid)

    # Ensure a very conservative umask
    os.umask(0o077)

# run a shell command
def run(cmd):
    # print(f"cmd: {cmd}")
    with subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as p:
        stdout, stderr = map(bytes.decode, p.communicate())
        return p.returncode, stdout, stderr

# encrypt data using password
# returns encrypted data
# on error, returns None and error message
def encrypt_data(data, password):
    cmd = f"echo -n '{data}' | openssl enc -aes-256-cbc -pbkdf2 -pass pass:'{password}' -a"
    exit_code, out, err = run(cmd)
    if exit_code != 0:
        return None, err.rstrip()
    return out.rstrip(), None

# decrypt data using password
# returns decrypted data
# on error, returns None and error message
def decrypt_data(data, password):
    cmd = f"echo -n '{data}' | base64 -d | openssl enc -aes-256-cbc -pbkdf2 -pass pass:'{password}' -d"
    exit_code, out, err = run(cmd)
    if exit_code != 0:
        return None, err.rstrip()
    return out.rstrip(), None

if __name__ == "__main__":
    drop_privileges(uid_name=UNPRIVILEGED_USER, gid_name=UNPRIVILEGED_USER)
    os.chdir(CHDIR_PATH)

    while True:
        try:

            json_data = json.loads(input())

            if json_data["action"] == "encrypt":
                enc_data, err = encrypt_data(json_data["data"], json_data["password"])
                if err:
                    print(json.dumps({"error": err}))
                    sys.stdout.flush()
                else:
                    print(json.dumps({"data": enc_data}))
                    sys.stdout.flush()
            elif json_data["action"] == "decrypt":
                dec_data, err = decrypt_data(json_data["data"], json_data["password"])
                if err:
                    print(json.dumps({"error": err}))
                    sys.stdout.flush()
                else:
                    print(json.dumps({"data": dec_data}))
                    sys.stdout.flush()
            else:
                print(json.dumps({"parse_error": "invalid action"}))
                sys.stdout.flush()

        except Exception as e:
            print(json.dumps({"parse_error": str(e)}))
            sys.stdout.flush()
