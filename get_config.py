#     IMPORTANT! 
# Note for users: If targeting a newer router/image with modern SSH algorithms,
# you can safely ignore or remove the legacy KEX and host-key workaround below.

import os
import paramiko
from dotenv import load_dotenv
from netmiko import ConnectHandler
from paramiko.kex_group1 import KexGroup1
from paramiko.kex_group14 import KexGroup14

# Safely remove if requirements are met in the above section (from *** to ***)
# ***
# Map legacy SHA-1 KEX names to Paramiko KEX classes
kex_engines = {
    "diffie-hellman-group14-sha1": KexGroup14,
    "diffie-hellman-group1-sha1": KexGroup1,
}

for kex_name, kex_cls in kex_engines.items():
    # Add KEX implementation to Paramiko's registry
    if kex_name not in paramiko.Transport._kex_info:
        paramiko.Transport._kex_info = {
            **paramiko.Transport._kex_info,
            kex_name: kex_cls,
        }
    # Add KEX algorithm to client offer list
    if kex_name not in paramiko.Transport._preferred_kex:
        paramiko.Transport._preferred_kex = (
            *paramiko.Transport._preferred_kex,
            kex_name,
        )

# Allow legacy ssh-rsa host keys
for key_alg in ("ssh-rsa",):
    if key_alg not in paramiko.Transport._preferred_keys:
        paramiko.Transport._preferred_keys = (
            *paramiko.Transport._preferred_keys,
            key_alg,
        )
# Safely remove if requirements are met in the above section
# ***

# Load environment variables from .env
load_dotenv()

ssh_pass = os.getenv("SSH_KEY_R1")
if not ssh_pass:
    raise ValueError("Nincs SSH jelszó a .env fájlban (SSH_KEY_R1)")

# Target device connection parameters
device = {
    "device_type": "cisco_ios",
    "host": "192.168.122.10",
    "username": "admin",
    "password": ssh_pass,
    "secret": ssh_pass,
}

# Connect via SSH, enter enable mode, pull running-config
with ConnectHandler(**device) as connection:
    if device["secret"]:
        connection.enable()
    running_config = connection.send_command("show running-config")

# Write retrieved config to local file
with open("r1_running_config.cfg", "w", encoding="utf-8") as f:
    f.write(running_config)

print("Config saved for R1.")
