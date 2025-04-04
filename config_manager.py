import json

class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
    
    def load(self):
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "location": "",
                "building": "",
                "floor": "",
                "department": ""
            }
    
    def save(self, data):
        with open(self.config_file, "w") as f:
            json.dump(data, f, indent=4)