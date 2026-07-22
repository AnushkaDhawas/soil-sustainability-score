"""
Generate an interactive HTML map showing soil sustainability scores by
location, using the geocoded dataset from geocode_villages.py.

Run with: python src/gis/generate_map.py

Output: outputs/reports/soil_sustainability_map.html
Open this file in any web browser to view/interact with the map.
"""

import pandas as pd
import folium
from pathlib import Path

GEOCODED_DATA_PATH = Path("data/processed/akola_soil_scored_geocoded.csv")
MAP_OUTPUT_PATH = Path("outputs/reports/soil_sustainability_map.html")

# Color coding per sustainability category
CATEGORY_COLORS = {
    "Highly Sustainable": "green",
    "Moderately Sustainable": "blue",
    "Needs Improvement": "orange",
    "Unsustainable": "red",
}


def build_popup_html(row) -> str:
    """Build the HTML content shown when a marker is clicked."""
    return f"""
    <div style="font-family: Arial, sans-serif; font-size: 13px; min-width: 200px;">
        <b>{row.get('Village', 'Unknown')}</b><br>
        {row.get('Block', '')}, {row.get('District', '')}, {row.get('State', '')}<br>
        <hr style="margin:4px 0;">
        <b>SSS Score:</b> {row['sss']}<br>
        <b>Category:</b> {row['category']}<br>
        <b>Chemical Health:</b> {row['chemical_health_score']}<br>
        <b>Physical Health:</b> {row['physical_health_score']}<br>
        <hr style="margin:4px 0;">
        pH: {row.get('ph', '-')} | EC: {row.get('ec', '-')}<br>
        OC: {row.get('organic_carbon', '-')} | N: {row.get('nitrogen', '-')}<br>
        P: {row.get('phosphorus', '-')} | K: {row.get('potassium', '-')}
    </div>
    """


def main():
    df = pd.read_csv(GEOCODED_DATA_PATH)
    print(f"Loaded {len(df)} profiles")

    df = df.dropna(subset=["latitude", "longitude"])
    print(f"{len(df)} profiles have valid coordinates and will be mapped")

    if df.empty:
        print("No geocoded profiles found — run src/gis/geocode_villages.py first.")
        return

    center_lat = df["latitude"].mean()
    center_lon = df["longitude"].mean()

    m = folium.Map(location=[center_lat, center_lon], zoom_start=10,
                    tiles="OpenStreetMap")

    for _, row in df.iterrows():
        color = CATEGORY_COLORS.get(row["category"], "gray")
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=8,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            popup=folium.Popup(build_popup_html(row), max_width=300),
            tooltip=f"{row.get('Village', 'Unknown')} \u2014 {row['category']}",
        ).add_to(m)

    # Legend
    legend_html = """
    <div style="position: fixed; bottom: 30px; left: 30px; z-index: 1000;
                background: white; padding: 12px 16px; border-radius: 6px;
                box-shadow: 0 1px 4px rgba(0,0,0,0.3); font-family: Arial, sans-serif; font-size: 13px;">
        <b>Sustainability Category</b><br>
        <span style="color:green;">&#9679;</span> Highly Sustainable<br>
        <span style="color:blue;">&#9679;</span> Moderately Sustainable<br>
        <span style="color:orange;">&#9679;</span> Needs Improvement<br>
        <span style="color:red;">&#9679;</span> Unsustainable
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    MAP_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    m.save(str(MAP_OUTPUT_PATH))
    print(f"Map saved to {MAP_OUTPUT_PATH}")
    print("Open this file in a web browser to view the interactive map.")


if __name__ == "__main__":
    main()