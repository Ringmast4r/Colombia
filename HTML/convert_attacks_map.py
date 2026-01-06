#!/usr/bin/env python3
"""
Convert Attacks on Peace Signatories data to interactive choropleth map
"""

import json
import math
import os

RAW_DIR = r"C:\Users\Squir\Desktop\NARCO COUNTER OPS\COLOMBIA\RAW DOWNLOADS"
OUT_DIR = r"C:\Users\Squir\Desktop\NARCO COUNTER OPS\COLOMBIA\HTML"

def web_mercator_to_wgs84(x, y):
    """Convert Web Mercator (EPSG:3857) to WGS84 (EPSG:4326)"""
    lon = (x / 20037508.34) * 180
    lat = (math.atan(math.exp(y * math.pi / 20037508.34)) * 360 / math.pi) - 90
    return [lon, lat]

def convert_ring(ring):
    """Convert a ring of coordinates from Web Mercator to WGS84"""
    return [web_mercator_to_wgs84(coord[0], coord[1]) for coord in ring]

def load_and_convert_attacks():
    """Load attacks data and convert to GeoJSON"""
    filepath = os.path.join(RAW_DIR, "Afectaciones_Firmantes_2025.json")

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    features = []
    total_homicides = 0
    total_disappearances = 0
    total_threats = 0
    total_attempted = 0

    for feature in data.get('features', []):
        attrs = feature.get('attributes', {})
        geom = feature.get('geometry', {})

        # Get attack counts - handle encoding issues with field names
        homicides = 0
        disappearances = 0
        threats = 0
        attempted = 0
        dept_name = "Unknown"

        for key, val in attrs.items():
            if 'HOMICIDIO_FIRMANTE' in key:
                homicides = val or 0
            elif 'DESAPARIC' in key:
                disappearances = val or 0
            elif 'AMENAZAS' in key:
                threats = val or 0
            elif 'TENTATIVA' in key:
                attempted = val or 0
            elif 'DPTO_CNMBR' in key:
                dept_name = val or "Unknown"

        total_homicides += homicides
        total_disappearances += disappearances
        total_threats += threats
        total_attempted += attempted

        total_attacks = homicides + disappearances + threats + attempted

        if 'rings' in geom:
            coordinates = [convert_ring(ring) for ring in geom['rings']]
            geojson_feature = {
                "type": "Feature",
                "properties": {
                    "department": dept_name,
                    "homicides": homicides,
                    "disappearances": disappearances,
                    "threats": threats,
                    "attempted": attempted,
                    "total": total_attacks
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": coordinates
                }
            }
            features.append(geojson_feature)

    print(f"Summary:")
    print(f"  Homicides: {total_homicides}")
    print(f"  Disappearances: {total_disappearances}")
    print(f"  Attempted Homicides: {total_attempted}")
    print(f"  Threats: {total_threats}")
    print(f"  TOTAL: {total_homicides + total_disappearances + total_attempted + total_threats}")

    return {
        "type": "FeatureCollection",
        "features": features
    }, {
        "homicides": total_homicides,
        "disappearances": total_disappearances,
        "attempted": total_attempted,
        "threats": total_threats
    }

def create_attacks_map(geojson, stats):
    """Create choropleth map of attacks"""

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Attacks on Peace Signatories - Colombia 2025</title>
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
            background: #8B0000;
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
            color: #ffcccc;
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
            width: 30px;
            height: 15px;
            margin-right: 8px;
            border: 1px solid #333;
        }}
        .stats-box {{
            position: absolute;
            top: 70px;
            right: 10px;
            background: rgba(139,0,0,0.95);
            color: #fff;
            padding: 15px;
            border-radius: 5px;
            z-index: 1000;
            min-width: 200px;
        }}
        .stats-box h4 {{ margin: 0 0 15px 0; color: #fff; border-bottom: 1px solid #ff6b6b; padding-bottom: 10px; }}
        .stat-item {{
            display: flex;
            justify-content: space-between;
            margin: 8px 0;
            font-size: 14px;
        }}
        .stat-value {{
            font-weight: bold;
            color: #ff6b6b;
        }}
        .stat-total {{
            border-top: 2px solid #fff;
            margin-top: 10px;
            padding-top: 10px;
            font-size: 16px;
        }}
        .context-box {{
            position: absolute;
            bottom: 30px;
            right: 10px;
            background: rgba(0,0,0,0.85);
            color: #fff;
            padding: 15px;
            border-radius: 5px;
            z-index: 1000;
            max-width: 280px;
            font-size: 11px;
        }}
        .context-box h4 {{ margin: 0 0 10px 0; color: #ffd93d; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>ATTACKS ON PEACE SIGNATORIES - First Half 2025</h1>
        <span class="subtitle">Source: CNR_SEP_2025_MIL1 - Afectaciones Firmantes | Downloaded: Jan 5, 2026</span>
    </div>

    <div id="map"></div>

    <div class="stats-box">
        <h4>ATTACK STATISTICS (H1 2025)</h4>
        <div class="stat-item">
            <span>Homicides:</span>
            <span class="stat-value">{stats['homicides']}</span>
        </div>
        <div class="stat-item">
            <span>Forced Disappearances:</span>
            <span class="stat-value">{stats['disappearances']}</span>
        </div>
        <div class="stat-item">
            <span>Attempted Homicides:</span>
            <span class="stat-value">{stats['attempted']}</span>
        </div>
        <div class="stat-item">
            <span>Threats:</span>
            <span class="stat-value">{stats['threats']}</span>
        </div>
        <div class="stat-item stat-total">
            <span>TOTAL INCIDENTS:</span>
            <span class="stat-value">{stats['homicides'] + stats['disappearances'] + stats['attempted'] + stats['threats']}</span>
        </div>
    </div>

    <div class="legend">
        <h4>Total Attacks by Department</h4>
        <div class="legend-item"><div class="legend-color" style="background:#fee5d9"></div>0 attacks</div>
        <div class="legend-item"><div class="legend-color" style="background:#fcae91"></div>1-3 attacks</div>
        <div class="legend-item"><div class="legend-color" style="background:#fb6a4a"></div>4-6 attacks</div>
        <div class="legend-item"><div class="legend-color" style="background:#de2d26"></div>7-10 attacks</div>
        <div class="legend-item"><div class="legend-color" style="background:#a50f15"></div>10+ attacks</div>
    </div>

    <div class="context-box">
        <h4>WHO ARE "FIRMANTES"?</h4>
        <p>"Firmantes" = Signatories of the 2016 Peace Agreement</p>
        <p>Former FARC guerrillas who demobilized, surrendered weapons, and entered reintegration programs.</p>
        <p><b>~1 killing per week</b> in H1 2025</p>
        <p style="color:#ff6b6b;">Since 2016: 400+ former FARC killed</p>
    </div>

    <script>
        var map = L.map('map').setView([4.5, -74.0], 6);

        L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
            attribution: '&copy; OpenStreetMap &copy; CARTO',
            subdomains: 'abcd',
            maxZoom: 19
        }}).addTo(map);

        function getColor(total) {{
            return total > 10 ? '#a50f15' :
                   total > 6  ? '#de2d26' :
                   total > 3  ? '#fb6a4a' :
                   total > 0  ? '#fcae91' :
                               '#fee5d9';
        }}

        function style(feature) {{
            return {{
                fillColor: getColor(feature.properties.total),
                weight: 2,
                opacity: 1,
                color: '#333',
                fillOpacity: 0.7
            }};
        }}

        function onEachFeature(feature, layer) {{
            var p = feature.properties;
            var popup = '<b>' + p.department + '</b><br>' +
                        '<table style="font-size:12px;">' +
                        '<tr><td>Homicides:</td><td><b>' + p.homicides + '</b></td></tr>' +
                        '<tr><td>Disappearances:</td><td><b>' + p.disappearances + '</b></td></tr>' +
                        '<tr><td>Attempted:</td><td><b>' + p.attempted + '</b></td></tr>' +
                        '<tr><td>Threats:</td><td><b>' + p.threats + '</b></td></tr>' +
                        '<tr><td colspan="2" style="border-top:1px solid #ccc;"><b>Total: ' + p.total + '</b></td></tr>' +
                        '</table>';
            layer.bindPopup(popup);
        }}

        var attacksData = {json.dumps(geojson)};

        L.geoJSON(attacksData, {{
            style: style,
            onEachFeature: onEachFeature
        }}).addTo(map);

    </script>
</body>
</html>
"""

    output_path = os.path.join(OUT_DIR, "attacks_on_signatories_map.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\n[+] Attacks map saved to: {output_path}")
    return output_path

if __name__ == "__main__":
    print("=" * 60)
    print("CONVERTING ATTACKS DATA TO CHOROPLETH MAP")
    print("=" * 60)

    geojson, stats = load_and_convert_attacks()

    # Save GeoJSON
    geojson_path = os.path.join(OUT_DIR, "attacks_signatories.geojson")
    with open(geojson_path, 'w', encoding='utf-8') as f:
        json.dump(geojson, f)
    print(f"\n[+] GeoJSON saved to: {geojson_path}")

    html_path = create_attacks_map(geojson, stats)
    print("[+] Conversion complete!")
