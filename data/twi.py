"""
Script: Topographic Wetness Index (TWI)
Data Sources:
- DEM: NASA SRTM (USGS/SRTMGL1_003)
- Upstream area: MERIT-Hydro
Formula: TWI = ln(As / tan(slope))
"""

import ee

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

def calculate_twi(dem, upa):
    """
    Calculate Topographic Wetness Index.
    TWI = ln(As / tan(slope))
    where:
        As = upstream area (m²)
        slope = slope in radians
    """
    print("Calculating slope and contributing area...")
    
    # Slope (degrees -> radians)
    slope_deg = ee.Terrain.slope(dem)
    slope_rad = slope_deg.multiply(3.141592 / 180.0)
    tan_slope = slope_rad.tan()
    
    # Convert upstream area from km² to m²
    As = upa.multiply(1e6)
    
    # Avoid division by zero and log(0)
    eps = ee.Image.constant(1e-6)
    tan_slope_safe = tan_slope.max(eps)
    
    # TWI calculation
    twi = As.divide(tan_slope_safe).max(eps).log().rename("TWI")
    
    return twi.clip(china)

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
    
    # Calculate TWI
    twi = calculate_twi(dem, upa)
    
    # Export
    print("Exporting TWI data (1km resolution, CRS=EPSG:4326)...")
    task = export_to_drive(
        image=twi,
        description='china_twi_NASA_MERITHydro_1km',
        folder='Flood_Susceptibility',
        scale=1000
    )
    print(f"Task submitted, ID: {task.id}")
    print("\nTask monitoring: https://code.earthengine.google.com/tasks")

if __name__ == "__main__":
    main()
