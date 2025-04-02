import platform
import socket
import psutil
import os
from getmac import get_mac_address

# 1. Computer Name
computer_name = os.getenv('COMPUTERNAME') or os.getenv('HOSTNAME')

# 2. Host Name
host_name = socket.gethostname()


# 4. MAC Address
mac_address = get_mac_address()

# 5. IP Address
ip_address = socket.gethostbyname(host_name)

# 6. CPU Info
cpu = {
    "Cores": psutil.cpu_count(),
    "Frequency (MHz)": psutil.cpu_freq().current,
    "Logical cores": psutil.cpu_count(logical=True)
}

# 7. RAM Info
memory = psutil.virtual_memory()
ram = {
    "Total RAM": memory.total / (1024 ** 3),  # GB
    "Available RAM": memory.available / (1024 ** 3),  # GB
    "Used RAM": memory.used / (1024 ** 3),  # GB
    "Percentage": memory.percent
}

# 8. Hard Disk Info
disk = psutil.disk_usage('/')
hard_disk = {
    "Total": disk.total / (1024 ** 3),  # GB
    "Used": disk.used / (1024 ** 3),  # GB
    "Free": disk.free / (1024 ** 3),  # GB
    "Percentage": disk.percent
}

# 9. OS Info
os_info = platform.system() + " " + platform.release()  # e.g., Windows 10, Linux

# Display all the gathered information
print(f"Computer Name: {computer_name}")
print(f"Host Name: {host_name}")
print(f"MAC Address: {mac_address}")
print(f"IP Address: {ip_address}")
print(f"CPU Info: {cpu}")
print(f"RAM Info: {ram}")
print(f"Hard Disk Info: {hard_disk}")
print(f"OS Info: {os_info}")
