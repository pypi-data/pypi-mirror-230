import requests

def verifyLicense(api_key: str, license_key: str, product_id: str):
    try:
        data = {
            'product_id': product_id,
            'key': license_key
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': api_key
        }
        response = requests.post("https://candorian.app/api/licenses/verify", json=data, headers=headers)
        json_response = response.json()
        isLicenseValid = json_response.get('success', False)
        return isLicenseValid
    except requests.exceptions.RequestException:
        print("Error: Unable to fetch license information.")
        return False

def getConfigs(api_key: str, config_id: str):
    #try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': api_key
        }
        response = requests.get(f"https://dashboard.candorservices.net/api/configs/{config_id}", headers=headers)
        json_response = response.json()
        print(json_response)
        isLicenseValid = json_response.get('success', False)
        return isLicenseValid
    #except requests.exceptions.RequestException:
    #    print("Error: Unable to fetch config information.")
    #    return False