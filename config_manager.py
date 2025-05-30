import json
import os

class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        # ตรวจสอบและสร้างไฟล์ config ถ้ายังไม่มี
        if not os.path.exists(self.config_file):
            self._create_default_config()
    
    def _create_default_config(self):
        default_config = {
            "location": "",
            "building": "",
            "floor": "",
            "department": "",
            "webhook_url": ""  # เพิ่ม webhook_url ใน config เริ่มต้น
        }
        with open(self.config_file, "w") as f:
            json.dump(default_config, f, indent=4)
    
    def load(self):
        try:
            with open(self.config_file, "r", encoding='utf-8') as f:
                config_data = json.load(f)
                # ตรวจสอบว่า config มี webhook_url หรือไม่ (สำหรับกรณีอัพเกรดจากเวอร์ชันเก่า)
                if 'webhook_url' not in config_data:
                    config_data['webhook_url'] = ""
                    self.save(config_data)
                return config_data
        except (FileNotFoundError, json.JSONDecodeError):
            self._create_default_config()
            return self.load()
    
    def save(self, data):
        # อ่าน config เดิมก่อนเพื่อเก็บ webhook_url ถ้ามี
        current_config = self.load()
        if 'webhook_url' in current_config:
            data['webhook_url'] = current_config['webhook_url']
        
        with open(self.config_file, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    
    def save_webhook_url(self, url):
        """บันทึกเฉพาะ Webhook URL"""
        config = self.load()
        config['webhook_url'] = url
        with open(self.config_file, "w", encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    
    def get_webhook_url(self):
        """ดึง URL และตรวจสอบความถูกต้อง"""
        config = self.load()
        url = config.get('webhook_url', '')
        if url and isinstance(url, str) and url.startswith(('http://', 'https://')):
            return url
        return ''