import requests


class VPStorage:
    def __init__(self):
        self.api_key = None

    def replace(self, reference, file_name, content_type, content):
        r = requests.post("https://bucket.virtualpreference.com/v1/storage", data={
            "uuid": reference
        }, files={
            "file": (file_name, content, content_type)
        }, headers={
            "Authorization": self.api_key,
        })
        match r.status_code:
            case 200:
                return True
        return False

    def destory(self, reference):
        r = requests.delete("https://bucket.virtualpreference.com/v1/storage", data={
            "uuid": reference
        }, headers={
            "Authorization": self.api_key,
        })
        match r.status_code:
            case 200:
                return True
        return False

    def push(self, file_name, content_type, content):
        r = requests.post("https://bucket.virtualpreference.com/v1/storage", data={
            "segment": "file.write"
        }, files={
            "file": (file_name, content, content_type)
        }, headers={
            "Authorization": self.api_key,
        })
        match r.status_code:
            case 201:
                j = r.json()
                return j
