import platform
import psutil
import socket
import time
import json
from datetime import datetime
from cpuinfo import get_cpu_info
from getmac import get_mac_address
from installed_programs import get_installed_software
from config_manager import ConfigManager

class SystemInfo:
    def __init__(self):
        self.config = ConfigManager()
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._load_system_info()
        self._load_dynamic_info()

    def _load_system_info(self):
        # คำนวณพื้นที่ฮาร์ดดิสก์ทั้งหมด (GB)
        total_disk = sum(disk['total'] for disk in self._get_disk_info().values())
        
        self.system_data = {
            'pc_info': { 
                'host_name': socket.gethostname(),
                'mac_address': get_mac_address(),
                'ip_address': socket.gethostbyname(socket.gethostname()),
                'cpu': get_cpu_info().get('brand_raw', 'Unknown'),
                'ram': self._get_ram_info(),
                'hard_disk': round(total_disk, 2),
                'os': f"{platform.system()} {platform.release()}",
                'created_at': self.created_at
            },
            'installed_software': self._get_installed_software_info(),  
            'location_info': self.config.load()
        }

    def _get_ram_info(self):
        try:
            ram_bytes = psutil.virtual_memory().total
            return round(ram_bytes / (1024 ** 3))  # แปลงเป็น GB และปัดเศษ
        except:
            return 0

    def _get_disk_info(self):
        disks = {}
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                disks[part.device] = {
                    'total': usage.total / (1024 ** 3),  # แปลงเป็น GB
                    'used': usage.used / (1024 ** 3),
                    'free': usage.free / (1024 ** 3)
                }
            except:
                continue
        return disks

    def _get_installed_software_info(self):
        programs = get_installed_software()
        return [{
            'name': p.get('name', 'Unknown'),
            'version': p.get('version', 'Unknown'),
            'publisher': p.get('publisher', 'Unknown'),
            'license_expiry': p.get('license_expiry', ''),
            'install_date': p.get('install_date', ''),
            'last_patch_update': p.get('last_patch_update', '')
        } for p in programs]

    def _load_dynamic_info(self):
        # อัปเดตข้อมูล location จาก config
        self.system_data['location_info'] = self.config.load()

    def get_all_info(self):
        return {
            'pc_info': self.system_data['pc_info'],
            'installed_software': self.system_data['installed_software'],
            'location_info': self.system_data['location_info']
        }

    def save_config(self, location_info):
        self.config.save(location_info)

    def save_to_json_file(self, filename='output.txt'):
        """บันทึกข้อมูลทั้งหมดลงไฟล์ JSON"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.get_all_info(), f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Error saving to JSON file: {e}")
            return False

    def save_config(self, location_info):
        """บันทึกการตั้งค่าและส่งออกข้อมูล"""
        self.config.save(location_info)
        # บันทึกเป็น JSON เมื่อมีการบันทึก config
        self.save_to_json_file()

    