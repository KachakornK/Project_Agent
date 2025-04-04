import requests
import json

WEBHOOK_URL = 'https://discord.com/api/webhooks/1357307846940950578/t_8qishlPcWlyrbf9f6ORGj31uf81LPMRGBUjPFNilzxoqQuKk_ffbapvBzXO0IE6Nsb'

def send_to_discord(system_info):
    try:
        message_content = f"""
        **ระบบคอมพิวเตอร์: {system_info['hostname']}**
        ```
        OS: {system_info['os']}
        CPU: {system_info['cpu']}
        RAM: {system_info['ram']} GB
        IP: {system_info['network']['ip']}
        ติดตั้งโปรแกรม: {json.dumps(system_info['installed_programs'])} โปรแกรม```
        """
        
        # print(json.encoder(system_info['installed_programs']))
        # print(json.dumps(system_info['installed_programs']))
        payload = {
            "content": message_content,
            "embeds": [{
                "title": "รายละเอียดตำแหน่งติดตั้ง",
                "fields": [
                    {"name": "สถานที่", "value": system_info['location_info']['location']},
                    {"name": "ตึก", "value": system_info['location_info']['building']},
                    {"name": "ชั้น", "value": system_info['location_info']['floor']},
                    {"name": "แผนก", "value": system_info['location_info']['department']}
                ]
            }]
        }
        
        response = requests.post(
            WEBHOOK_URL,
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}
        )

        return response.status_code == 204
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        print("Error sending message to Discord")
        return False