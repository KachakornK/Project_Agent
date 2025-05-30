import requests

class WebhookManager:
    def __init__(self):
        self.webhook_url = None
    
    def set_webhook_url(self, url):
        """ตั้งค่า URL และตรวจสอบความถูกต้อง"""
        if url and self._validate_url(url):
            self.webhook_url = url
            return True
        return False
    
    def _validate_url(self, url):
        """ตรวจสอบว่า URL ถูกต้อง"""
        return url.startswith(('http://', 'https://'))
    
    def send_to_webhook(self, data):
        """ส่งข้อมูลไปยัง Webhook"""
        if not self.webhook_url:
            print("ไม่มี Webhook URL ที่กำหนด")
            return False
            
        try:
            response = requests.post(
                self.webhook_url,
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"ส่งข้อมูลไม่สำเร็จ: {str(e)}")
            return False