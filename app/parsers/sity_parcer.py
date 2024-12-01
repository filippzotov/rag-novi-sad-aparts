import requests
import json
import time
import urllib.parse

# URL для получения подробной информации
base_url = "https://cityexpert.rs/api/PropertyView/{}/r"


# Функция для получения списка квартир
def fetch_apartments(page=1):
    url = "https://cityexpert.rs/api/Search"
    # JSON structure for the request
    req_data = {
        "cityId": 2,
        "rentOrSale": "r",
        "currentPage": page,
        "searchSource": "regular",
        "sort": "datedsc",
    }
    # Compact JSON encoding
    compact_json = json.dumps(req_data, separators=(",", ":"))

    # URL encoding
    encoded_req = urllib.parse.quote(compact_json)

    # Print the full URL for testing
    full_url = f"{url}?req={encoded_req}"
    print(f"Testing Encoded URL: {full_url}")

    # Make the request
    response = requests.get(f"{url}?req={encoded_req}")

    if response.status_code == 200:
        return response.json().get("result", [])
    else:
        print(f"Ошибка запроса: {response.status_code}")
        print(f"Response content: {response.text}")
        return []


# Функция для получения подробной информации по квартире
def fetch_apartment_details(prop_id):
    url = base_url.format(prop_id)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка получения деталей квартиры {prop_id}: {response.status_code}")
        return None


def generate_url(params):
    base_url = "https://cityexpert.rs/izdavanje-nekretnina/"

    # Map cityId to city name
    city_mapping = {2: "novi-sad"}
    city = city_mapping.get(params.get("cityId"))
    if not city:
        raise ValueError(f"Invalid or missing cityId: {params.get('cityId')}")

    city = city.lower().replace(" ", "-")

    # Map structure to readable format
    structure_mapping = {
        "0.5": "garsonjera",
        "1.0": "jednosoban-stan",
        "1.5": "jednoiposoban-stan",
        "2.0": "dvosoban-stan",
        "2.5": "dvoiposoban-stan",
        "3.0": "trosoban-stan",
        "3.5": "troiposoban-stan",
        "4.0": "cetvorosoban-stan",
        "4.5": "cetvoroiposoban-stan",
        "5+": "petosoban-ili-veci-stan",
        "OTHER": "ostalo",
    }
    structure = structure_mapping.get(params.get("structure"))
    if not structure:
        raise ValueError(f"Invalid or missing structure: {params.get('structure')}")

    structure = structure.lower()

    # Format street name
    street = params.get("street")
    if not street:
        raise ValueError(f"Missing street name: {params.get('street')}")

    street = (
        street.lower()
        .replace(" ", "-")
        .replace("đ", "dj")
        .replace("š", "s")
        .replace("č", "c")
        .replace("ć", "c")
        .replace("ž", "z")
    )

    # Generate URL
    prop_id = params.get("propId")
    if not prop_id:
        raise ValueError(f"Missing property ID: {params.get('propId')}")

    url = f"{base_url}{city}/{prop_id}/{structure}-{street}-{city}"
    return url


# Основной скрипт
def get_all_apartments():
    current_page = 1
    all_apartments = []
    detailed_data = []

    # Получение всех квартир
    while True:
        print(f"Получение данных со страницы {current_page}...")
        apartments = fetch_apartments(page=current_page)
        if not apartments:
            break
        all_apartments.extend(apartments)
        current_page += 1
        time.sleep(1)

    print(
        f"\nНайдено {len(all_apartments)} квартир. Получение подробной информации...\n"
    )

    # Получение подробной информации по каждой квартире
    for apartment in all_apartments[:]:
        # Generate URL
        url = generate_url(apartment)

        prop_id = apartment.get("propId")
        if prop_id:
            print(f"Получение деталей для квартиры ID {prop_id}...")
            details = fetch_apartment_details(prop_id)
            if details:
                # Add the URL to the detailed data
                details["url"] = url
                detailed_data.append(details)
            # Пауза между запросами, чтобы не перегружать сервер
            time.sleep(1)

    return detailed_data


# Запуск скрипта
if __name__ == "__main__":
    detailed_data = get_all_apartments()
    print(detailed_data)
    print(len(detailed_data))
