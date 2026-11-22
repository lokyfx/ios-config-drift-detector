import os
from dotenv import load_dotenv
from netmiko import ConnectHandler

load_dotenv()

ssh_pass = os.getenv("SHH_KEY_R1")
if not ssh_pass:
    raise ValueError("No SSH key in .env")

device = {
    "device_type": "cisco_ios",
    "host": "192.168.122.10",
    "username": "admin",
    "password": ssh_pass,
}

with ConnectHandler(**device) as connection:
    if device["secret"]:
        connection.enable()
        running_config = connection.send_command("show running-config")

with open("r1_running_config.cfg", "w", encoding="utf-8") as f:
    f.write(running_config)
    print("Config saved for R1.")
