import requests

def send_to_webhook(data):
    url = "https://webhook.site/42a5dc6b-deea-44a1-a769-b050e9c87d7d"
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(url, json=data, headers=headers)
        return response.status_code == 200
    except Exception as e:
        print(f"Webhook error: {e}")
        return False
