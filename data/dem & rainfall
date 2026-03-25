"""
Script: DEM and Precipitation Data Processing
Data Sources:
- DEM: NASA NASADEM_HGT/001 (improved SRTM data, NASA & METI)
- Precipitation: CHIRPS Daily (UCSB-CHG)
"""

import ee
import geemap
import os

# Initialize GEE
try:
    ee.Initialize(project='your-project-id')
except ee.ee_exception.EEException:
    ee.Authenticate()
    ee.Initialize(project='your-project-id')

# 1. Load China boundary
# Note: Replace with your own asset path or use a public dataset
china = ee.FeatureCollection("users/your-username/China_boundary")

# 2. Load DEM data
def get_dem_data():
    """Load NASADEM data and resample to 1km resolution."""
    print("Loading DEM data...")
    dem = ee.Image("NASA/NASADEM_HGT/001").select('elevation').clip(china)
    return dem.resample('bilinear').reproject(crs='EPSG:4326', scale=1000)

# 3. Load and process precipitation data
def get_precipitation_data():
    """Load CHIRPS daily data (2015-2024), compute annual mean, and apply terrain correction."""
    print("Loading precipitation data...")
    chirps_daily = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
        .filterDate('2015-01-01', '2024-12-31') \
        .filterBounds(china) \
        .select('precipitation')
    
    annual_precip = ee.ImageCollection.fromImages(
        ee.List.sequence(2015, 2024).map(lambda year:
            chirps_daily.filterDate(
                ee.Date.fromYMD(year, 1, 1),
                ee.Date.fromYMD(year, 1, 1).advance(1, 'year')
            ).sum().set('year', year)
        )
    )
    
    mean_precip = annual_precip.mean().clip(china)
    dem = get_dem_data()
    # Terrain correction factor (0.002 per meter elevation)
    return mean_precip.add(dem.multiply(0.002)).reproject(crs='EPSG:4326', scale=1000)

def export_to_drive(image, description, folder, scale, region):
    """Export image to Google Drive."""
    task = ee.batch.Export.image.toDrive(
        image=image,
        description=description[:100],
        folder=folder,
        fileNamePrefix=description[:50],
        scale=scale,
        region=region,
        crs='EPSG:4326',
        maxPixels=1e13,
        fileFormat='GeoTIFF'
    )
    task.start()
    return task

def main():
    """Main execution function."""
    # Get data
    dem_data = get_dem_data()
    precip_data = get_precipitation_data()
    
    # Export DEM
    print("Submitting DEM export task...")
    dem_task = export_to_drive(
        image=dem_data,
        description='china_dem_1km',
        folder='GEE_Exports',
        scale=1000,
        region=china.geometry()
    )
    print(f"DEM task submitted, ID: {dem_task.id}")
    
    # Export precipitation
    print("Submitting precipitation export task...")
    precip_task = export_to_drive(
        image=precip_data,
        description='china_precip_1km_2015-2024',
        folder='GEE_Exports',
        scale=1000,
        region=china.geometry()
    )
    print(f"Precipitation task submitted, ID: {precip_task.id}")
    
    print("\nAll tasks submitted to Google Drive. Check progress at:")
    print("https://code.earthengine.google.com/tasks")
    print("\nExported files will appear in:")
    print("Google Drive > My Drive > GEE_Exports")

if __name__ == "__main__":
    main()
