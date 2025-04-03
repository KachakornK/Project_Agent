import platform
import psutil
import socket
import time
import json
import requests
import json
import subprocess
import re
from cpuinfo import get_cpu_info
from getmac import get_mac_address
import tkinter as tk
from tkinter import messagebox

CONFIG_FILE = "config.json"
# Your Discord Webhook URL
WEBHOOK_URL = 'https://discord.com/api/webhooks/1357307846940950578/t_8qishlPcWlyrbf9f6ORGj31uf81LPMRGBUjPFNilzxoqQuKk_ffbapvBzXO0IE6Nsb'

class SystemInfo:
    def __init__(self):
        self.load_config()
        # เพิ่ม try-except สำหรับการดึงข้อมูล
        try:
            self.pc_os = platform.system()
        except Exception as e:
            self.pc_os = "Unknown"
            print(f"Error fetching OS info: {e}")
        
        try:
            self.ram_info = psutil.virtual_memory()
            self.pc_ram = round(self.ram_info.total / (1024 ** 3), 2)
        except Exception as e:
            self.pc_ram = "Unknown"
            print(f"Error fetching RAM info: {e}")
        
        try:
            self.cpu_info = get_cpu_info()
        except Exception as e:
            self.cpu_info = {"brand_raw": "Unknown"}
            print(f"Error fetching CPU info: {e}")
        
        try:
            self.hostname = socket.gethostname()
        except Exception as e:
            self.hostname = "Unknown"
            print(f"Error fetching hostname: {e}")
        
        try:
            self.ip_address = socket.gethostbyname(self.hostname)
        except Exception as e:
            self.ip_address = "Unknown"
            print(f"Error fetching IP address: {e}")
        
        try:
            self.mac_address = get_mac_address()
        except Exception as e:
            self.mac_address = "Unknown"
            print(f"Error fetching MAC address: {e}")
        
        try:
            self.partitions_pc = self.get_accessible_partitions()
            self.pc_partition = self.get_partition_info()
        except Exception as e:
            self.partitions_pc = []
            self.pc_partition = {}
            print(f"Error fetching partition info: {e}")
        
        try:
            self.current_time = self.get_current_time()
        except Exception as e:
            self.current_time = "Unknown"
            print(f"Error fetching current time: {e}")
        
        try:
            self.office_expiry = self.get_office_license_info()
        except Exception as e:
            self.office_expiry = "Unknown"
            print(f"Error fetching office license info: {e}")

    def load_config(self):  
        try:
            with open(CONFIG_FILE, "r") as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {"location": "", "building": "", "floor": "", "department": ""}
        except json.JSONDecodeError as e:
            self.config = {"location": "", "building": "", "floor": "", "department": ""}
            print(f"Error decoding JSON from config file: {e}")
        except Exception as e:
            self.config = {"location": "", "building": "", "floor": "", "department": ""}
            print(f"Error loading config: {e}")

    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)

    def get_accessible_partitions(self):
        partitions = psutil.disk_partitions()
        accessible_partitions = []
        for part in partitions:
            try:
                psutil.disk_usage(part.mountpoint)
                accessible_partitions.append(part.device)
            except PermissionError:
                continue
        return accessible_partitions

    def get_partition_info(self):
        partition_info = {}
        for part in self.partitions_pc:
            disktotal = psutil.disk_usage(part)
            partition_info[part.replace(':\\', '')] = round(disktotal.total / (1024 ** 3), 2)
        return partition_info

    def get_current_time(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def get_office_license_info():
        paths = [
            r"C:\Program Files\Microsoft Office\Office16",
            r"C:\Program Files (x86)\Microsoft Office\Office16",
            r"C:\Program Files\Microsoft Office\Office19",
            r"C:\Program Files (x86)\Microsoft Office\Office19"
        ]

        for path in paths:
            ospp_path = f'{path}\\ospp.vbs'
            try:
                result = subprocess.run(["cscript", ospp_path, "/dstatus"], capture_output=True, text=True)
                output = result.stdout
                
                # ค้นหาข้อมูล "REMAINING GRACE"
                match = re.search(r"REMAINING GRACE:\s+(\d+)\s+days", output)
                if match:
                    remaining_days = match.group(1)
                    return f"Office License จะหมดอายุใน {remaining_days} วัน"
                
                # ถ้าไม่มีข้อมูล REMAINING GRACE อาจเป็นแบบถาวร (ไม่หมดอายุ)
                if "LICENSED" in output:
                    return "Office License เป็นแบบถาวร"
            
            except Exception as e:
                continue

        return "ไม่พบข้อมูล License ของ Microsoft Office"

    def get_system_info(self):
        return {
            "pc_hostname": self.hostname,
            "pc_os": self.pc_os,
            "pc_RAM": self.pc_ram,
            "pc_cpu": self.cpu_info['brand_raw'],
            "pc_hardisk": self.pc_partition,
            "pc_ip": self.ip_address,
            "pc_mac": self.mac_address,
            "current_time": self.current_time,
            "office_expiry": self.office_expiry,
            "location": self.config.get("location", ""),
            "building": self.config.get("building", ""),
            "floor": self.config.get("floor", ""),
            "department": self.config.get("department", "")
        }
    

    def save_to_file(self, filename="output.txt"):
        with open(filename, "w") as f:
            data = {
                "content": f'```PC : {self.pc_os}\n OS :{self.pc_os}\nRAM :{self.pc_ram}\nCPU : {self.cpu_info['brand_raw']}\nDisk :{self.pc_partition}```',  # Message to be sent
                "username": "PythonBot",  # Optional: Set a custom username for the bot
                "avatar_url": "https://example.com/avatar.png"  # Optional: Set an avatar for the bot
            }
            response = requests.post(WEBHOOK_URL, data=json.dumps(data), headers={'Content-Type': 'application/json'})
            if response.status_code == 200:
                print("Message sent successfully")
            else:
                print(f"Failed to send message: {response.status_code}")
            json.dump(self.get_system_info(), f)
            # print(f"pc_ip: {self.ip_address}")

class SystemInfoGUI:
    def __init__(self, root, system_info):
        self.root = root
        self.root.title("System Information")
        self.system_info = system_info
        self.create_widgets()

    def create_widgets(self):
        sys_info = self.system_info.get_system_info()

        tk.Label(self.root, text="System Information", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        tk.Label(self.root, text=f"Hostname: {sys_info['pc_hostname']}").grid(row=1, column=0, sticky="w", padx=10)
        tk.Label(self.root, text=f"OS: {sys_info['pc_os']}").grid(row=2, column=0, sticky="w", padx=10)
        tk.Label(self.root, text=f"RAM: {sys_info['pc_RAM']} GB").grid(row=3, column=0, sticky="w", padx=10)
        tk.Label(self.root, text=f"CPU: {sys_info['pc_cpu']}").grid(row=4, column=0, sticky="w", padx=10)
        tk.Label(self.root, text=f"IP Address: {sys_info['pc_ip']}").grid(row=5, column=0, sticky="w", padx=10)
        tk.Label(self.root, text=f"MAC Address: {sys_info['pc_mac']}").grid(row=6, column=0, sticky="w", padx=10)

        self.label_current_time = tk.Label(self.root, text=f"Current Time: {sys_info['current_time']}")
        self.label_current_time.grid(row=7, column=0, sticky="w", padx=10)

        tk.Label(self.root, text=f"Office License: {sys_info['office_expiry']}").grid(row=8, column=0, sticky="w", padx=10)

        

        row = 9
        tk.Label(self.root, text="Partition:").grid(row=row, column=0, sticky="w", padx=10)
        row += 1
        for partition, size in sys_info['pc_hardisk'].items():
            label_partition_info = tk.Label(self.root, text=f"{partition}: {size} GB")
            label_partition_info.grid(row=row, column=0, sticky="w", padx=20)
            row += 1


        tk.Label(self.root, text="ชื่อสถานที่:").grid(row=row, column=0, sticky="w", padx=10)
        self.entry_location = tk.Entry(self.root)
        self.entry_location.grid(row=row, column=0, columnspan=2)
        self.entry_location.insert(0, sys_info["location"])
        row += 1

        tk.Label(self.root, text="ตึก:").grid(row=row, column=0, sticky="w", padx=10)
        self.entry_building = tk.Entry(self.root)
        self.entry_building.grid(row=row, column=0, columnspan=2)
        self.entry_building.insert(0, sys_info["building"])
        row += 1
        
    

        tk.Label(self.root, text="ชั้น:").grid(row=row, column=0, sticky="w", padx=10)
        self.entry_floor = tk.Entry(self.root)
        self.entry_floor.grid(row=row, column=0, columnspan=2)
        self.entry_floor.insert(0, sys_info["floor"])
        row += 1

        tk.Label(self.root, text="แผนก:").grid(row=row, column=0, sticky="w", padx=10)
        self.entry_department = tk.Entry(self.root)
        self.entry_department.grid(row=row, column=0, columnspan=2)
        self.entry_department.insert(0, sys_info["department"])
        row += 1


       

        save_button = tk.Button(self.root, text="ส่งข้อมูล", command=self.save_to_file)
        save_button.grid(row=row, column=0, columnspan=2, pady=10)

        self.update_time()

    def update_time(self):
        self.system_info.current_time = self.system_info.get_current_time()
        self.label_current_time.config(text=f"Current Time: {self.system_info.current_time}")
        self.root.after(1000, self.update_time)

    def save_to_file(self):
        self.system_info.config["location"] = self.entry_location.get()
        self.system_info.config["building"] = self.entry_building.get()
        self.system_info.config["floor"] = self.entry_floor.get()
        self.system_info.config["department"] = self.entry_department.get()

        self.system_info.save_config()
        self.system_info.save_to_file()
        messagebox.showinfo("Success", "ข้อมูลถูกบันทึกลงใน output.txt")
        self.root.quit()

def main():
    system_info = SystemInfo()
    root = tk.Tk()
    app = SystemInfoGUI(root, system_info)
    root.mainloop()

if __name__ == "__main__":
    main()