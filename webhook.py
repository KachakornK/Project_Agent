import requests

class WebhookManager:
    def __init__(self):
        self.webhook_urls = {
            "Default": "https://webhook.site/124198c3-ba4b-4596-9e85-e3f761262150",
            "Backup": "https://webhook-test.com/a6acc63c1a85a1cc35fbce2da7d7a992"
        }
        self.selected_url = None

    def set_webhook_url(self, url):
        self.selected_url = url

    def send_to_webhook(self, data):
        if not self.selected_url:
            return False
            
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.post(self.selected_url, json=data, headers=headers)
            return response.status_code == 200
        except Exception as e:
            print(f"Webhook error: {e}")
            return False

    def get_webhook_urls(self):
        return self.webhook_urls