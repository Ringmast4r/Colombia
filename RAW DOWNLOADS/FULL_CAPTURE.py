#!/usr/bin/env python3
"""
FULL CAPTURE MODE - COLOMBIAN ARCGIS DUMP
Downloads EVERYTHING from ergit.presidencia.gov.co
"""

import requests
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "https://ergit.presidencia.gov.co/server/rest/services"
ROOT_DIR = r"C:\Users\Squir\Desktop\NARCO COUNTER OPS\COLOMBIA\RAW DOWNLOADS"

# Organized output directories
DIRS = {
    'military': os.path.join(ROOT_DIR, 'MILITARY_MAPS'),
    'ddhh': os.path.join(ROOT_DIR, 'DDHH_HUMAN_RIGHTS'),
    'victims': os.path.join(ROOT_DIR, 'VICTIMS'),
    'armed': os.path.join(ROOT_DIR, 'ARMED_GROUPS'),
    'peace': os.path.join(ROOT_DIR, 'PEACE_PROCESS'),
    'indigenous': os.path.join(ROOT_DIR, 'INDIGENOUS'),
    'hosted': os.path.join(ROOT_DIR, 'HOSTED_SERVICES'),
    'root': ROOT_DIR
}

# Create all dirs
for d in DIRS.values():
    os.makedirs(d, exist_ok=True)

def categorize_service(name):
    """Determine which folder to save to"""
    name_lower = name.lower()
    if 'mil1' in name_lower or 'militar' in name_lower:
        return 'military'
    elif 'ddhh' in name_lower or 'fiscalia' in name_lower or 'flip' in name_lower or 'fecolper' in name_lower:
        return 'ddhh'
    elif 'victim' in name_lower or 'mujeres' in name_lower:
        return 'victims'
    elif 'agc' in name_lower or 'eln' in name_lower or 'disidencia' in name_lower or 'farc' in name_lower or 'clan' in name_lower:
        return 'armed'
    elif 'paz' in name_lower or 'acuerdo' in name_lower or 'firmante' in name_lower or 'reinteg' in name_lower or 'aetcr' in name_lower:
        return 'peace'
    elif 'resguardo' in name_lower or 'indigena' in name_lower or 'etnic' in name_lower:
        return 'indigenous'
    elif 'hosted' in name_lower:
        return 'hosted'
    return 'root'

def fetch_json(url):
    """Fetch JSON from URL"""
    try:
        r = requests.get(url, timeout=60)
        return r.json()
    except:
        return None

def save_file(data, filepath):
    """Save data to file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        if isinstance(data, (dict, list)):
            json.dump(data, f, indent=2, ensure_ascii=False)
        else:
            f.write(str(data))

def download_map_image(service_name, out_dir):
    """Export map as PNG"""
    url = f"{BASE_URL}/{service_name}/MapServer/export?bbox=-9098767,-471243,-7320364,1504865&bboxSR=102100&size=1920,1080&format=png&f=image"
    try:
        r = requests.get(url, timeout=120)
        if r.status_code == 200 and len(r.content) > 1000:
            fname = service_name.replace('/', '_') + '.png'
            filepath = os.path.join(out_dir, fname)
            with open(filepath, 'wb') as f:
                f.write(r.content)
            return f"MAP: {fname} ({len(r.content)} bytes)"
    except Exception as e:
        return f"MAP ERROR: {e}"
    return None

def download_layer_data(service_name, stype, layer_id, out_dir):
    """Download all features from a layer"""
    url = f"{BASE_URL}/{service_name}/{stype}/{layer_id}/query?where=1%3D1&outFields=*&f=json&resultRecordCount=10000"
    try:
        r = requests.get(url, timeout=120)
        if r.status_code == 200:
            fname = f"{service_name.replace('/', '_')}_{stype}_L{layer_id}.json"
            filepath = os.path.join(out_dir, fname)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(r.text)
            return f"DATA: {fname}"
    except Exception as e:
        return f"LAYER ERROR: {e}"
    return None

def process_service(service_name, stype):
    """Process a single service"""
    results = []
    category = categorize_service(service_name)
    out_dir = DIRS[category]

    # Get service metadata
    url = f"{BASE_URL}/{service_name}/{stype}?f=json"
    data = fetch_json(url)

    if not data or 'error' in data:
        return results

    # Save metadata
    fname = f"{service_name.replace('/', '_')}_{stype}_meta.json"
    save_file(data, os.path.join(out_dir, fname))
    results.append(f"META: {fname}")

    # Export map if MapServer
    if stype == 'MapServer':
        result = download_map_image(service_name, out_dir)
        if result:
            results.append(result)

    # Download all layers
    layers = data.get('layers', [])
    for layer in layers:
        lid = layer.get('id', 0)
        result = download_layer_data(service_name, stype, lid, out_dir)
        if result:
            results.append(result)

    return results

def main():
    print("="*70)
    print("FULL CAPTURE MODE - COLOMBIAN GOVERNMENT ARCGIS")
    print("Target: ergit.presidencia.gov.co")
    print("="*70)

    # Get root listing
    print("\n[*] Fetching service catalog...")
    root_data = fetch_json(f"{BASE_URL}?f=json")

    if not root_data:
        print("[!] Cannot connect!")
        return

    all_services = []

    # Root services
    for svc in root_data.get('services', []):
        all_services.append((svc['name'], svc['type']))

    # Folder services
    folders = root_data.get('folders', [])
    print(f"[*] Found {len(folders)} folders")

    for folder in folders:
        if folder in ['Utilities', 'System']:
            continue

        folder_data = fetch_json(f"{BASE_URL}/{folder}?f=json")
        if folder_data:
            for svc in folder_data.get('services', []):
                all_services.append((svc['name'], svc['type']))

    print(f"[*] Total services to download: {len(all_services)}")

    # Process all services
    total = len(all_services)
    downloaded = 0

    for i, (svc_name, svc_type) in enumerate(all_services):
        print(f"\n[{i+1}/{total}] {svc_name} ({svc_type})")
        results = process_service(svc_name, svc_type)
        for r in results:
            print(f"  {r}")
            downloaded += 1
        time.sleep(0.3)  # Rate limit

    print("\n" + "="*70)
    print(f"CAPTURE COMPLETE: {downloaded} files downloaded")
    print("="*70)

if __name__ == "__main__":
    main()
