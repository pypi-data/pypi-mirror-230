import requests

def get_geo_info(ip_address):
    url = f"https://ipinfo.io/{ip_address}/json"
    response = requests.get(url)
    data = response.json()
    return data

ip_address = "46.196.85.67"  # İlgilenilen IP adresini burada belirtin
geo_info = get_geo_info(ip_address)

print("IP Adresi:", geo_info["ip"])
print("Şehir:", geo_info.get("city", "Bilinmiyor"))
print("Ülke:", geo_info.get("country", "Bilinmiyor"))
print("Koordinatlar:", geo_info.get("loc", "Bilinmiyor"))
