import json
import requests
import scripts.pytest.BaseRequest as BaseRequest
import time
URL = "http://192.168.1.108:8086/"
ZONE_ID = "" 
KEY = ""

def common_gm_request(data):
    action = data["url"]
    http_url = URL + action
    request = type(action,(BaseRequest.BaseRequest,),{})()
    request.zoneId =ZONE_ID
    request.request_id = time.time().__str__()
    request.generate_sign(KEY)
    for k,v in data.items():
        setattr(request,k,v)
    json_str = json.dumps(request, default=lambda o: o.__dict__,sort_keys=True,indent=4)
    print(json_str)
    post_data = post_http_request(http_url,json_str)
    response = parse_http_response(post_data)
    print(response)
    return response

def post_http_request(url, data):
    r = requests.post(url, data)
    return r

def parse_http_response(response):
    response_text = response.text
    valid_json_str = convert_to_valid_json(response_text)
    return valid_json_str

def convert_to_valid_json(response_text):
    response_text = response_text.replace("'", '"')
    response_text = response_text.replace(': ', ':')
    try:
        parsed_response = json.loads(response_text)
        valid_json_str = json.dumps(parsed_response, ensure_ascii=False, indent=4)
        return valid_json_str
    except json.JSONDecodeError as e:
        print("JSON解析错误:", e)
        return None