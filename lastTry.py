import requests
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--cookie_string", type=str, required=True)

args = parser.parse_args()
cookies = args.cookie_string

headers = {
    'authority': 'glados.rocks',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'authorization': '20924375476958375692840661964561-864-1536',
    'content-type': 'application/json;charset=UTF-8',
    # Requests sorts cookies= alphabetically
    'origin': 'https://glados.rocks',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
}

json_data = {
    'token': 'glados.one',
}

response = requests.post('https://glados.rocks/api/user/checkin', cookies=cookies, headers=headers, json=json_data)
print(response.text)