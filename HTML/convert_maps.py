#!/usr/bin/env python3
"""
Convert ArcGIS JSON to GeoJSON and create interactive map
Colombia Armed Group Territories - OSINT Visualization
"""

import json
import math
import os

RAW_DIR = r"C:\Users\Squir\Desktop\NARCO COUNTER OPS\COLOMBIA\RAW DOWNLOADS"
OUT_DIR = r"C:\Users\Squir\Desktop\NARCO COUNTER OPS\COLOMBIA\HTML"

# Territory files to convert
TERRITORY_FILES = {
    "ELN_territories.json": {"name": "ELN", "color": "#FF0000"},
    "ClanDelGolfo_territories.json": {"name": "Clan del Golfo (AGC)", "color": "#FF8C00"},
    "Disidencias_EMC.json": {"name": "Disidencias EMC", "color": "#8B0000"},
    "SegundaMarquetalia.json": {"name": "Segunda Marquetalia", "color": "#800080"},
    "Disidencias_EMBF.json": {"name": "Disidencias EMBF", "color": "#006400"},
}

def web_mercator_to_wgs84(x, y):
    """Convert Web Mercator (EPSG:3857) to WGS84 (EPSG:4326)"""
    lon = (x / 20037508.34) * 180
    lat = (math.atan(math.exp(y * math.pi / 20037508.34)) * 360 / math.pi) - 90
    return [lon, lat]

def convert_ring(ring):
    """Convert a ring of coordinates from Web Mercator to WGS84"""
    return [web_mercator_to_wgs84(coord[0], coord[1]) for coord in ring]

def arcgis_to_geojson(arcgis_data, layer_name):
    """Convert ArcGIS JSON to GeoJSON format"""
    features = []

    for feature in arcgis_data.get('features', []):
        geom = feature.get('geometry', {})
        attrs = feature.get('attributes', {})

        # Handle polygon geometry (rings)
        if 'rings' in geom:
            coordinates = [convert_ring(ring) for ring in geom['rings']]
            geojson_feature = {
                "type": "Feature",
                "properties": {
                    "layer": layer_name,
                    **attrs
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": coordinates
                }
            }
            features.append(geojson_feature)

        # Handle point geometry
        elif 'x' in geom and 'y' in geom:
            coords = web_mercator_to_wgs84(geom['x'], geom['y'])
            geojson_feature = {
                "type": "Feature",
                "properties": {
                    "layer": layer_name,
                    **attrs
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": coords
                }
            }
            features.append(geojson_feature)

    return {
        "type": "FeatureCollection",
        "features": features
    }

def convert_all_territories():
    """Convert all territory files to GeoJSON"""
    all_layers = {}

    for filename, info in TERRITORY_FILES.items():
        filepath = os.path.join(RAW_DIR, filename)
        if os.path.exists(filepath):
            print(f"Converting {filename}...")
            with open(filepath, 'r', encoding='utf-8') as f:
                arcgis_data = json.load(f)

            geojson = arcgis_to_geojson(arcgis_data, info['name'])
            all_layers[info['name']] = {
                'geojson': geojson,
                'color': info['color'],
                'count': len(geojson['features'])
            }

            # Save individual GeoJSON
            out_file = os.path.join(OUT_DIR, f"{info['name'].replace(' ', '_')}.geojson")
            with open(out_file, 'w', encoding='utf-8') as f:
                json.dump(geojson, f)
            print(f"  -> {geojson['features'].__len__()} features saved to {out_file}")
        else:
            print(f"  [!] File not found: {filepath}")

    return all_layers

def create_html_map(layers):
    """Create interactive HTML map with Leaflet"""

    # Build layer data for JavaScript
    layer_js = []
    for name, data in layers.items():
        layer_js.append(f"""
        // {name}
        var {name.replace(' ', '_').replace('(', '').replace(')', '')} = L.geoJSON({json.dumps(data['geojson'])}, {{
            style: function(feature) {{
                return {{
                    fillColor: '{data['color']}',
                    weight: 2,
                    opacity: 1,
                    color: '{data['color']}',
                    fillOpacity: 0.4
                }};
            }},
            onEachFeature: function(feature, layer) {{
                layer.bindPopup('<b>{name}</b><br>Features: {data["count"]}');
            }}
        }});
        """)

    # Layer control
    overlay_layers = ",\n            ".join([
        f'"{name}": {name.replace(" ", "_").replace("(", "").replace(")", "")}'
        for name in layers.keys()
    ])

    # Add all layers to map
    add_layers = "\n        ".join([
        f'{name.replace(" ", "_").replace("(", "").replace(")", "")}.addTo(map);'
        for name in layers.keys()
    ])

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Colombia Armed Groups - Territory Map (OSINT)</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body {{ margin: 0; padding: 0; font-family: Arial, sans-serif; }}
        #map {{ position: absolute; top: 60px; bottom: 0; width: 100%; }}
        .header {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 60px;
            background: #1a1a2e;
            color: #fff;
            display: flex;
            align-items: center;
            padding: 0 20px;
            z-index: 1000;
        }}
        .header h1 {{
            margin: 0;
            font-size: 18px;
        }}
        .header .subtitle {{
            margin-left: 20px;
            font-size: 12px;
            color: #888;
        }}
        .legend {{
            position: absolute;
            bottom: 30px;
            left: 10px;
            background: rgba(255,255,255,0.95);
            padding: 15px;
            border-radius: 5px;
            z-index: 1000;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }}
        .legend h4 {{ margin: 0 0 10px 0; font-size: 14px; }}
        .legend-item {{
            display: flex;
            align-items: center;
            margin: 5px 0;
            font-size: 12px;
        }}
        .legend-color {{
            width: 20px;
            height: 20px;
            margin-right: 8px;
            border: 1px solid #333;
        }}
        .info-box {{
            position: absolute;
            top: 70px;
            right: 10px;
            background: rgba(0,0,0,0.8);
            color: #fff;
            padding: 15px;
            border-radius: 5px;
            z-index: 1000;
            max-width: 300px;
            font-size: 12px;
        }}
        .info-box h4 {{ margin: 0 0 10px 0; color: #ff6b6b; }}
        .warning {{ color: #ffd93d; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>COLOMBIA ARMED GROUP TERRITORIES</h1>
        <span class="subtitle">Source: CNR_SEP_2025_MIL1 (Colombian Military Intelligence) | Downloaded: Jan 5, 2026</span>
    </div>

    <div id="map"></div>

    <div class="legend">
        <h4>Armed Groups</h4>
        {"".join([f'<div class="legend-item"><div class="legend-color" style="background:{data["color"]}"></div>{name} ({data["count"]} zones)</div>' for name, data in layers.items()])}
    </div>

    <div class="info-box">
        <h4>INTELLIGENCE ASSESSMENT</h4>
        <p><b>Source:</b> ergit.presidencia.gov.co</p>
        <p><b>Date:</b> September 2025</p>
        <p class="warning"><b>WARNING:</b> This map shows Colombian military intelligence assessment of armed group territorial control.</p>
        <p>Data was publicly accessible without authentication - major OPSEC failure.</p>
    </div>

    <script>
        // Initialize map centered on Colombia
        var map = L.map('map').setView([4.5, -74.0], 6);

        // Dark tile layer
        L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
            subdomains: 'abcd',
            maxZoom: 19
        }}).addTo(map);

        // Territory layers
        {"".join(layer_js)}

        // Add all layers to map
        {add_layers}

        // Layer control
        var overlayMaps = {{
            {overlay_layers}
        }};

        L.control.layers(null, overlayMaps, {{collapsed: false}}).addTo(map);

    </script>
</body>
</html>
"""

    output_path = os.path.join(OUT_DIR, "armed_groups_map.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\n[+] Interactive map saved to: {output_path}")
    return output_path

if __name__ == "__main__":
    print("=" * 60)
    print("CONVERTING ARCGIS DATA TO INTERACTIVE MAP")
    print("=" * 60)

    layers = convert_all_territories()

    if layers:
        html_path = create_html_map(layers)
        print("\n[+] Conversion complete!")
        print(f"[+] Open {html_path} in browser to view")
    else:
        print("[!] No layers converted")
