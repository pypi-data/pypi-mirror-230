import requests

model_name = "ModelService"

url = f"http://localhost:8081/v2/models/{model_name}/versions/1/infer"

payload = {
  "parameters": {
    "str": "str",
    "float": 1.222,
    "bool": True
  }
}

response = requests.request("POST", url, json=payload)
print(response.text)
