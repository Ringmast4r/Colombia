#!/usr/bin/env python3
"""
Visualize ALL Colombian military/intelligence maps
Creates multiple interactive HTML maps from downloaded ArcGIS data
"""

import json
import math
import os
import glob

RAW_DIR = r"C:\Users\Squir\Desktop\NARCO COUNTER OPS\COLOMBIA\RAW DOWNLOADS"
OUT_DIR = r"C:\Users\Squir\Desktop\NARCO COUNTER OPS\COLOMBIA\HTML"

def web_mercator_to_wgs84(x, y):
    """Convert Web Mercator to WGS84"""
    lon = (x / 20037508.34) * 180
    lat = (math.atan(math.exp(y * math.pi / 20037508.34)) * 360 / math.pi) - 90
    return [lon, lat]

def convert_geometry(geom):
    """Convert ArcGIS geometry to GeoJSON"""
    if 'rings' in geom:
        coords = [[web_mercator_to_wgs84(p[0], p[1]) for p in ring] for ring in geom['rings']]
        return {"type": "Polygon", "coordinates": coords}
    elif 'paths' in geom:
        coords = [[web_mercator_to_wgs84(p[0], p[1]) for p in path] for path in geom['paths']]
        return {"type": "MultiLineString", "coordinates": coords}
    elif 'x' in geom and 'y' in geom:
        return {"type": "Point", "coordinates": web_mercator_to_wgs84(geom['x'], geom['y'])}
    return None

def load_arcgis_json(filepath):
    """Load ArcGIS JSON and convert to GeoJSON"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        features = []
        for feat in data.get('features', []):
            geom = feat.get('geometry')
            if geom:
                converted = convert_geometry(geom)
                if converted:
                    features.append({
                        "type": "Feature",
                        "properties": feat.get('attributes', {}),
                        "geometry": converted
                    })

        return {"type": "FeatureCollection", "features": features}
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def create_map_html(title, subtitle, layers, filename, center=[4.5, -74], zoom=6):
    """Create interactive Leaflet map"""

    # Build layer JavaScript
    layer_js = []
    overlay_items = []
    legend_items = []

    for name, data in layers.items():
        safe_name = name.replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '').replace('-', '_')
        color = data.get('color', '#FF0000')
        geojson = data.get('geojson', {"type": "FeatureCollection", "features": []})

        if geojson and geojson.get('features'):
            layer_js.append(f"""
        var {safe_name} = L.geoJSON({json.dumps(geojson)}, {{
            style: function(feature) {{
                return {{
                    fillColor: '{color}',
                    weight: 2,
                    opacity: 1,
                    color: '{color}',
                    fillOpacity: 0.5
                }};
            }},
            pointToLayer: function(feature, latlng) {{
                return L.circleMarker(latlng, {{
                    radius: 8,
                    fillColor: '{color}',
                    color: '#000',
                    weight: 1,
                    opacity: 1,
                    fillOpacity: 0.8
                }});
            }},
            onEachFeature: function(feature, layer) {{
                var props = feature.properties;
                var popup = '<b>{name}</b><br>';
                for (var key in props) {{
                    if (props[key] && key !== 'Shape_Length' && key !== 'Shape_Area') {{
                        popup += key + ': ' + props[key] + '<br>';
                    }}
                }}
                layer.bindPopup(popup);
            }}
        }}).addTo(map);
        """)
            overlay_items.append(f'"{name}": {safe_name}')
            legend_items.append(f'<div class="legend-item"><div class="legend-color" style="background:{color}"></div>{name} ({len(geojson["features"])})</div>')

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body {{ margin: 0; padding: 0; font-family: Arial, sans-serif; }}
        #map {{ position: absolute; top: 70px; bottom: 0; width: 100%; }}
        .header {{
            position: absolute; top: 0; left: 0; right: 0; height: 70px;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff; display: flex; align-items: center; padding: 0 20px; z-index: 1000;
        }}
        .header h1 {{ margin: 0; font-size: 22px; }}
        .header .subtitle {{ margin-left: 20px; font-size: 14px; color: #888; }}
        .legend {{
            position: absolute; bottom: 30px; left: 10px;
            background: rgba(255,255,255,0.95); padding: 15px;
            border-radius: 8px; z-index: 1000; box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            max-height: 400px; overflow-y: auto;
        }}
        .legend h4 {{ margin: 0 0 10px 0; font-size: 14px; color: #333; }}
        .legend-item {{ display: flex; align-items: center; margin: 5px 0; font-size: 12px; }}
        .legend-color {{ width: 20px; height: 20px; margin-right: 8px; border: 1px solid #333; border-radius: 3px; }}
        .info {{
            position: absolute; top: 80px; right: 10px;
            background: rgba(0,0,0,0.85); color: #fff; padding: 15px;
            border-radius: 8px; z-index: 1000; max-width: 280px; font-size: 12px;
        }}
        .info h4 {{ margin: 0 0 10px 0; color: #ffd93d; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <span class="subtitle">{subtitle}</span>
    </div>
    <div id="map"></div>
    <div class="legend">
        <h4>Layers</h4>
        {''.join(legend_items)}
    </div>
    <div class="info">
        <h4>SOURCE</h4>
        <p>ergit.presidencia.gov.co</p>
        <p>Downloaded: Jan 5, 2026</p>
        <p style="color:#ff6b6b;">NO AUTHENTICATION REQUIRED</p>
    </div>
    <script>
        var map = L.map('map').setView([{center[0]}, {center[1]}], {zoom});
        L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
            attribution: '&copy; OpenStreetMap &copy; CARTO',
            subdomains: 'abcd', maxZoom: 19
        }}).addTo(map);
        {''.join(layer_js)}
        var overlays = {{ {', '.join(overlay_items)} }};
        L.control.layers(null, overlays, {{collapsed: false}}).addTo(map);
    </script>
</body>
</html>"""

    outpath = os.path.join(OUT_DIR, filename)
    with open(outpath, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"[+] Created: {filename}")
    return outpath

# ============================================================
# MAP 1: September 2025 Military Map - All Layers
# ============================================================
print("\n=== SEPTEMBER 2025 MILITARY MAP ===")
sep_layers = {}

sep_files = {
    'CNR_SEP_2025_MIL1_layer9': ('AETCR Camps', '#00FF00'),
    'CNR_SEP_2025_MIL1_layer12': ('ELN', '#FF0000'),
    'CNR_SEP_2025_MIL1_layer15': ('Clan del Golfo', '#FF8C00'),
    'CNR_SEP_2025_MIL1_layer13': ('Disidencias EMC', '#8B0000'),
    'CNR_SEP_2025_MIL1_layer11': ('Segunda Marquetalia', '#800080'),
    'CNR_SEP_2025_MIL1_layer24': ('Disidencias EMBF', '#006400'),
    'CNR_SEP_2025_MIL1_layer16': ('ASCN', '#0000FF'),
}

for prefix, (name, color) in sep_files.items():
    # Try different filename patterns
    for pattern in [f'{prefix}.json', f'{prefix}_*.json']:
        matches = glob.glob(os.path.join(RAW_DIR, pattern))
        if matches:
            geojson = load_arcgis_json(matches[0])
            if geojson and geojson['features']:
                sep_layers[name] = {'geojson': geojson, 'color': color}
                print(f"  Loaded: {name} ({len(geojson['features'])} features)")
            break

if sep_layers:
    create_map_html(
        "CNR SEPTEMBER 2025 - MILITARY MAP",
        "All Armed Group Layers | ergit.presidencia.gov.co",
        sep_layers,
        "military_sep2025_full.html"
    )

# ============================================================
# MAP 2: July 2025 Military Map
# ============================================================
print("\n=== JULY 2025 MILITARY MAP ===")
jul_layers = {}

jul_files = {
    'CNR_julio_2025_MIL1_layer9': ('AETCR Camps', '#00FF00'),
    'CNR_julio_2025_MIL1_layer12': ('ELN', '#FF0000'),
    'CNR_julio_2025_MIL1_layer15': ('Clan del Golfo', '#FF8C00'),
    'CNR_julio_2025_MIL1_layer13': ('Disidencias EMC', '#8B0000'),
    'CNR_julio_2025_MIL1_layer11': ('Segunda Marquetalia', '#800080'),
    'CNR_julio_2025_MIL1_layer24': ('Disidencias EMBF', '#006400'),
    'CNR_julio_2025_MIL1_layer16': ('ASCN', '#0000FF'),
}

for prefix, (name, color) in jul_files.items():
    for pattern in [f'{prefix}.json', f'{prefix}_*.json']:
        matches = glob.glob(os.path.join(RAW_DIR, pattern))
        if matches:
            geojson = load_arcgis_json(matches[0])
            if geojson and geojson['features']:
                jul_layers[name] = {'geojson': geojson, 'color': color}
                print(f"  Loaded: {name} ({len(geojson['features'])} features)")
            break

if jul_layers:
    create_map_html(
        "CNR JULY 2025 - MILITARY MAP",
        "Armed Group Territories | ergit.presidencia.gov.co",
        jul_layers,
        "military_jul2025_full.html"
    )

# ============================================================
# MAP 3: Case 03 Military Map
# ============================================================
print("\n=== CASE 03 MILITARY MAP ===")
caso_layers = {}

caso_files = {
    'Mapa_Caso_03_MIL1_layer9': ('AETCR Camps', '#00FF00'),
    'Mapa_Caso_03_MIL1_layer31': ('ELN', '#FF0000'),
    'Mapa_Caso_03_MIL1_layer33': ('Clan del Golfo', '#FF8C00'),
    'Mapa_Caso_03_MIL1_layer32': ('Frente 33 EMBF', '#006400'),
    'Mapa_Caso_03_MIL1_layer34': ('ASCN', '#0000FF'),
    'Mapa_Caso_03_MIL1_layer21': ('Firmantes Presence', '#FFFF00'),
}

for prefix, (name, color) in caso_files.items():
    for pattern in [f'{prefix}.json', f'{prefix}_*.json']:
        matches = glob.glob(os.path.join(RAW_DIR, pattern))
        if matches:
            geojson = load_arcgis_json(matches[0])
            if geojson and geojson['features']:
                caso_layers[name] = {'geojson': geojson, 'color': color}
                print(f"  Loaded: {name} ({len(geojson['features'])} features)")
            break

if caso_layers:
    create_map_html(
        "CASE 03 MILITARY MAP",
        "Special Investigation Zones | ergit.presidencia.gov.co",
        caso_layers,
        "military_caso03.html"
    )

# ============================================================
# MAP 4: AT Zones Map
# ============================================================
print("\n=== AT ZONES MAP ===")
at_layers = {}

at_files = {
    'Mapa_AT_MIL1_layer0': ('Departments', '#3388ff'),
    'Mapa_AT_MIL1_layer1': ('AT Municipalities 2025', '#ff7800'),
    'Mapa_AT_MIL1_layer2': ('PEP Municipalities', '#00ff00'),
}

for prefix, (name, color) in at_files.items():
    for pattern in [f'{prefix}.json', f'{prefix}_*.json']:
        matches = glob.glob(os.path.join(RAW_DIR, pattern))
        if matches:
            geojson = load_arcgis_json(matches[0])
            if geojson and geojson['features']:
                at_layers[name] = {'geojson': geojson, 'color': color}
                print(f"  Loaded: {name} ({len(geojson['features'])} features)")
            break

if at_layers:
    create_map_html(
        "AT ZONES MAP",
        "Administrative Territories | ergit.presidencia.gov.co",
        at_layers,
        "at_zones_map.html"
    )

# ============================================================
# MAP 5: AETCR Camps Only (Points)
# ============================================================
print("\n=== AETCR CAMPS MAP ===")
aetcr_layers = {}

aetcr_file = os.path.join(RAW_DIR, 'CNR_SEP_2025_MIL1_layer9.json')
if os.path.exists(aetcr_file):
    geojson = load_arcgis_json(aetcr_file)
    if geojson and geojson['features']:
        aetcr_layers['AETCR Reintegration Camps'] = {'geojson': geojson, 'color': '#00FF00'}
        print(f"  Loaded: AETCR Camps ({len(geojson['features'])} camps)")

if aetcr_layers:
    create_map_html(
        "AETCR REINTEGRATION CAMPS",
        "Former FARC Camp Locations | CRITICAL TARGET DATA",
        aetcr_layers,
        "aetcr_camps_map.html",
        zoom=6
    )

# ============================================================
# MAP 6: Human Rights Data
# ============================================================
print("\n=== HUMAN RIGHTS DATA MAP ===")
ddhh_layers = {}

ddhh_files = glob.glob(os.path.join(RAW_DIR, 'DDHH_*.json'))
colors = ['#FF0000', '#00FF00', '#0000FF', '#FF8C00', '#800080', '#008080']
for i, f in enumerate(ddhh_files[:6]):
    geojson = load_arcgis_json(f)
    if geojson and geojson['features']:
        name = os.path.basename(f).replace('.json', '').replace('DDHH_', '').replace('_', ' ')[:30]
        ddhh_layers[name] = {'geojson': geojson, 'color': colors[i % len(colors)]}
        print(f"  Loaded: {name} ({len(geojson['features'])} features)")

if ddhh_layers:
    create_map_html(
        "HUMAN RIGHTS DATA (DDHH)",
        "Protection & Victim Data | ergit.presidencia.gov.co",
        ddhh_layers,
        "ddhh_human_rights_map.html"
    )

print("\n" + "="*60)
print("MAP VISUALIZATION COMPLETE")
print("="*60)
