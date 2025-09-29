import requests

url = "https://soilhealth4.dac.gov.in/"

headers = {
    "Content-Type": "application/json",
    "Origin": "https://soilhealth.dac.gov.in",
    "Referer": "https://soilhealth.dac.gov.in/",
    "User-Agent": "Mozilla/5.0"
}

payload = {
    "operationName": "GetNutrientData",
    "variables": {
        "stateId": "KA",       # Karnataka
        "districtId": "Mysuru"
    },
    "query": """
    query GetNutrientData($stateId: String, $districtId: String) {
      getNutrientData(stateId: $stateId, districtId: $districtId) {
        ph
        nitrogen
        phosphorus
        potassium
        organicCarbon
      }
    }
    """
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
