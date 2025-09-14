import requests

url = "https://crop-recommendation-api.p.rapidapi.com/api/predict"

payload = {
	"N": "22",
	"P": "20",
	"K": "22",
	"temperature": "25",
	"humidity": "25",
	"ph": "6.0",
	"rainfall": "25"
}
headers = {
	"x-rapidapi-key": "d4f78ff2c3msh883378ec47fdadep1f7007jsn80b045877f72",
	"x-rapidapi-host": "crop-recommendation-api.p.rapidapi.com",
	"Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print(response.json())