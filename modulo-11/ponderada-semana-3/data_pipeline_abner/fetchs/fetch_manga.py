import requests

def fetch_manga_data(url):
    try:
        payload = {}
        headers = {}

        response = requests.get(url, headers=headers, data=payload)

        response.raise_for_status()  # Isso vai levantar um erro para códigos de status >= 400

        return response.json()  # Retorna a resposta em formato JSON
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None