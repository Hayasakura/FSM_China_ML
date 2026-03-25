"""
Script: Sediment Transport Index (STI) - Log-transformed version
Data Sources:
- DEM: NASA SRTM (USGS/SRTMGL1_003)
- Upstream area: MERIT-Hydro
Formula: STI = (log(As + 1) / 22.13)^0.4 * (sin(slope) / 0.0896)^1.3
"""

import ee
import math

# Initialize GEE
try:
    ee.Initialize(project='your-project-id')
except ee.ee_exception.EEException:
    ee.Authenticate()
    ee.Initialize(project='your-project-id')

# 1. Load China boundary
# Note: Replace with your own asset path or use a public dataset
china_raw = ee.FeatureCollection("users/your-username/China_boundary")
china = china_raw.geometry()

def get_nasa_merit_data():
    """Load NASA SRTM DEM and MERIT-Hydro upstream area."""
    print("Loading NASA SRTM DEM and MERIT-Hydro...")
    dem = ee.Image("USGS/SRTMGL1_003").select('elevation').clip(china)
    upa = ee.Image("MERIT/Hydro/v1_0_1").select('upa').clip(china)  # Upstream area (km²)
    return dem, upa

def calculate_sti(dem, upa):
    """
    Calculate Sediment Transport Index with log transformation.
    STI = (log(As + 1) / 22.13)^0.4 * (sin(slope) / 0.0896)^1.3
    where:
        As = upstream area (m²)
        slope = slope in radians
    """
    print("Calculating slope and contributing area...")
    
    # Slope (degrees -> radians)
    slope_rad = ee.Terrain.slope(dem).multiply(math.pi / 180.0)
    sin_slope = slope_rad.sin()
    
    # Convert upstream area from km² to m²
    As_m2 = upa.multiply(1e6)
    
    # Log transformation to enhance non-channel areas
    As_log = As_m2.add(1).log()
    
    # STI formula
    part1 = As_log.divide(22.13).pow(0.4)
    part2 = sin_slope.divide(0.0896).pow(1.3)
    sti = part1.multiply(part2).rename("STI")
    
    return sti.clip(china)

def export_to_drive(image, description, folder, scale=1000):
    """Export image to Google Drive."""
    task = ee.batch.Export.image.toDrive(
        image=image,
        description=description[:100],
        folder=folder,
        fileNamePrefix=description[:50],
        scale=scale,
        region=china,
        crs="EPSG:4326",
        maxPixels=1e13,
        fileFormat='GeoTIFF',
        formatOptions={'cloudOptimized': True}
    )
    task.start()
    return task

def main():
    """Main execution function."""
    # Load data
    dem, upa = get_nasa_merit_data()
    
    # Calculate STI (log-transformed version)
    sti = calculate_sti(dem, upa)
    
    # Export
    print("Exporting STI data (1km resolution, CRS=EPSG:4326)...")
    task = export_to_drive(
        image=sti,
        description='china_sti_log_transformed_1km',
        folder='Flood_Susceptibility',
        scale=1000
    )
    print(f"Task submitted, ID: {task.id}")
    print("\nTask monitoring: https://code.earthengine.google.com/tasks")

if __name__ == "__main__":
    main()
