#!/usr/bin/env python3
"""Fix DDHH Human Rights Map - Data is already in WGS84"""

import json
import os

RAW_DIR = r"C:\Users\Squir\Desktop\NARCO COUNTER OPS\COLOMBIA\RAW DOWNLOADS"
OUT_DIR = r"C:\Users\Squir\Desktop\NARCO COUNTER OPS\COLOMBIA\HTML"

def convert_arcgis_to_geojson(data):
    """Convert ArcGIS JSON to GeoJSON - NO coordinate conversion for WGS84"""
    features = []
    for feat in data.get('features', []):
        geom = feat.get('geometry')
        if not geom:
            continue

        if 'rings' in geom:
            geojson_geom = {'type': 'Polygon', 'coordinates': geom['rings']}
        elif 'paths' in geom:
            geojson_geom = {'type': 'MultiLineString', 'coordinates': geom['paths']}
        elif 'x' in geom and 'y' in geom:
            geojson_geom = {'type': 'Point', 'coordinates': [geom['x'], geom['y']]}
        else:
            continue

        features.append({
            'type': 'Feature',
            'properties': feat.get('attributes', {}),
            'geometry': geojson_geom
        })

    return {'type': 'FeatureCollection', 'features': features}

def load_file(filename):
    filepath = os.path.join(RAW_DIR, filename)
    if not os.path.exists(filepath):
        print(f"  File not found: {filename}")
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if 'error' in data:
            print(f"  Error in {filename}: {data['error']}")
            return None
        geojson = convert_arcgis_to_geojson(data)
        print(f"  Loaded: {filename} ({len(geojson['features'])} features)")
        return geojson
    except Exception as e:
        print(f"  Error loading {filename}: {e}")
        return None

print("Loading DDHH data files...")
layers = {}

# Load each layer
files_to_load = [
    ('DDHH_DDHH_Fiscalia_L0.json', 'Fiscalia (Prosecutor)', '#FF0000'),
    ('DDHH_Medicina_legal_L0_data.json', 'Medicina Legal', '#00FF00'),
    ('DDHH_DDHH_Fecolper_L0.json', 'Fecolper (Journalists)', '#FF8C00'),
    ('DDHH_DDHH_CensoObservatorios_Survey123_L0.json', 'Census Observatories', '#800080'),
]

for filename, name, color in files_to_load:
    geojson = load_file(filename)
    if geojson and geojson['features']:
        layers[name] = {'geojson': geojson, 'color': color}

print(f"\nTotal layers: {len(layers)}")
total_features = sum(len(l['geojson']['features']) for l in layers.values())
print(f"Total features: {total_features}")

# Build JavaScript for layers
layer_js = []
overlay_items = []
legend_items = []

for name, data in layers.items():
    safe_name = name.replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '').replace('-', '_')
    color = data['color']
    geojson = data['geojson']

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
                    radius: 6,
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
                    if (props[key] && key !== 'Shape_Length' && key !== 'Shape_Area' && key !== 'OBJECTID') {{
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
    <title>Human Rights Data (DDHH) - Colombia</title>
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
        <h1>HUMAN RIGHTS DATA (DDHH)</h1>
        <span class="subtitle">Protection & Victim Data | ergit.presidencia.gov.co</span>
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
        <p><strong>{total_features}</strong> total features</p>
    </div>
    <script>
        var map = L.map('map').setView([4.5, -74], 6);
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

outpath = os.path.join(OUT_DIR, 'ddhh_human_rights_map.html')
with open(outpath, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"\nCreated: ddhh_human_rights_map.html")
print(f"File size: {os.path.getsize(outpath)/1024/1024:.1f} MB")
