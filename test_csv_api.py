import requests

url = "http://127.0.0.1:8000/run_preprocessing/csv"
csv_file = r"C:\Users\Dell\OneDrive\Desktop\Pre agent\data.csv"

with open(csv_file, "rb") as f:
    files = {"file": (csv_file, f, "text/csv")}
    response = requests.post(url, files=files)

print(response.status_code)
print(response.json())
