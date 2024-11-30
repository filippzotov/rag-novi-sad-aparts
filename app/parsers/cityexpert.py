import requests
import json


def fetch_apartments(page=1):
    url = "https://cityexpert.rs/api/Search"
    params = {
        "req": json.dumps(
            {
                "cityId": 2,
                "rentOrSale": "r",
                "currentPage": page,
                "searchSource": "regular",
                "sort": "datedsc",
            }
        )
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("result", [])
    else:
        print(f"Error: {response.status_code}")
        return []
