#!/usr/bin/env python3
"""
FULL ARCGIS DUMP - STEALTH MODE
Downloads all accessible services from Colombian government ArcGIS
Via Tor SOCKS5 proxy
"""

import requests
import json
import os
import time

# Tor proxy
PROXIES = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

BASE_URL = "https://ergit.presidencia.gov.co/server/rest/services"
OUT_DIR = r"C:\Users\Squir\Desktop\NARCO COUNTER OPS\COLOMBIA\RAW DOWNLOADS"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:102.0) Gecko/20100101 Firefox/102.0'
}

def fetch(url):
    """Fetch URL via Tor"""
    try:
        r = requests.get(url, proxies=PROXIES, headers=HEADERS, timeout=60)
        return r.text
    except Exception as e:
        print(f"  [!] Error: {e}")
        return None

def save_json(data, filename):
    """Save JSON to file"""
    filepath = os.path.join(OUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        if isinstance(data, str):
            f.write(data)
        else:
            json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  [+] Saved: {filename}")

def download_feature_layer(service_url, layer_id, name_prefix):
    """Download all features from a layer"""
    query_url = f"{service_url}/{layer_id}/query?where=1%3D1&outFields=*&f=json"
    print(f"    Querying layer {layer_id}...")
    data = fetch(query_url)
    if data:
        filename = f"{name_prefix}_layer{layer_id}.json"
        save_json(data, filename)
        return True
    return False

def download_map_image(service_url, name_prefix):
    """Export map as PNG"""
    export_url = f"{service_url}/export?bbox=-9098767,-471243,-7320364,1504865&bboxSR=102100&size=1920,1080&format=png&f=image"
    print(f"    Exporting map image...")
    try:
        r = requests.get(export_url, proxies=PROXIES, headers=HEADERS, timeout=120)
        if r.status_code == 200:
            filepath = os.path.join(OUT_DIR, f"{name_prefix}.png")
            with open(filepath, 'wb') as f:
                f.write(r.content)
            print(f"  [+] Saved: {name_prefix}.png")
            return True
    except Exception as e:
        print(f"  [!] Map export error: {e}")
    return False

def process_service(service_name, service_type):
    """Process a single service"""
    print(f"\n[*] Processing: {service_name} ({service_type})")

    service_url = f"{BASE_URL}/{service_name}/{service_type}"

    # Get service info
    info_url = f"{service_url}?f=json"
    info = fetch(info_url)

    if not info:
        return

    try:
        data = json.loads(info)
    except:
        print("  [!] Invalid JSON response")
        return

    # Check for error
    if 'error' in data:
        print(f"  [!] Error: {data['error'].get('message', 'Unknown')}")
        return

    # Save metadata
    safe_name = service_name.replace('/', '_')
    save_json(data, f"{safe_name}_meta.json")

    # Get layers
    layers = data.get('layers', [])

    if service_type == 'MapServer':
        # Download map image
        download_map_image(service_url, f"{safe_name}_map")

    if service_type == 'FeatureServer' or layers:
        # Download each layer
        for layer in layers:
            layer_id = layer.get('id', 0)
            layer_name = layer.get('name', f'layer{layer_id}')
            print(f"    Layer {layer_id}: {layer_name}")
            download_feature_layer(service_url, layer_id, safe_name)
            time.sleep(0.5)  # Rate limit

def enumerate_folder(folder_name):
    """Enumerate services in a folder"""
    print(f"\n{'='*60}")
    print(f"FOLDER: {folder_name}")
    print('='*60)

    folder_url = f"{BASE_URL}/{folder_name}?f=json"
    data = fetch(folder_url)

    if not data:
        return

    try:
        folder_data = json.loads(data)
    except:
        return

    # Save folder listing
    save_json(folder_data, f"{folder_name}_folder.json")

    services = folder_data.get('services', [])

    for svc in services:
        svc_name = svc.get('name', '')
        svc_type = svc.get('type', 'MapServer')
        process_service(svc_name, svc_type)
        time.sleep(1)  # Rate limit between services

def main():
    print("="*60)
    print("FULL ARCGIS DUMP - STEALTH MODE (TOR)")
    print("Target: ergit.presidencia.gov.co")
    print("="*60)

    # First get root services
    print("\n[*] Fetching root services...")
    root = fetch(f"{BASE_URL}?f=json")

    if not root:
        print("[!] Cannot connect to target")
        return

    root_data = json.loads(root)

    # Root level services
    for svc in root_data.get('services', []):
        svc_name = svc.get('name', '')
        svc_type = svc.get('type', 'MapServer')
        process_service(svc_name, svc_type)
        time.sleep(1)

    # All folders
    folders = root_data.get('folders', [])

    for folder in folders:
        if folder in ['Utilities', 'System']:  # Skip system folders
            continue
        enumerate_folder(folder)
        time.sleep(2)  # Rate limit between folders

    print("\n" + "="*60)
    print("DUMP COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
