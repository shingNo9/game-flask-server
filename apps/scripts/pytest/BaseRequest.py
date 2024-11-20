import hashlib
import json

class BaseRequest:
    def generate_sign(self, key):
        sign_str = self.request_id + key
        self.sign = hashlib.md5(sign_str.encode()).hexdigest().lower()
        return self.sign

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def __str__(self):
        return self.to_json()

    def __repr__(self):
        return self.to_json()

class CommonRequest(BaseRequest):

    def __init__(self):
        pass