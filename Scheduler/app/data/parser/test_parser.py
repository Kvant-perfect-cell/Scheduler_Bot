import requests

url = "https://www.surpk.ru/schedule/index"

response = requests.get(url)

print("STATUS:", response.status_code)
print(response.text[:2000])  # первые 2000 символов