"""
Script: NDVI Data Processing
Data Source: MODIS MOD13Q1 (NASA)
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
china = ee.FeatureCollection("users/your-username/China_boundary")

def get_ndvi_data():
    """Load MODIS NDVI data (2015-2024) and normalize."""
    print("Loading MODIS NDVI data...")
    
    # Use MODIS MOD13Q1 dataset
    modis_ndvi = ee.ImageCollection("MODIS/061/MOD13Q1") \
        .filterDate('2015-01-01', '2024-12-31') \
        .filterBounds(china) \
        .select('NDVI')
    
    # Compute annual mean
    ndvi_mean = modis_ndvi.mean().clip(china)
    
    # Normalize NDVI (MODIS NDVI is scaled by 0.0001)
    ndvi_normalized = ndvi_mean.multiply(0.0001)
    
    return ndvi_normalized

def export_to_drive(image, description, folder, scale=1000):
    """Export image to Google Drive."""
    task = ee.batch.Export.image.toDrive(
        image=image,
        description=description[:100],
        folder=folder,
        fileNamePrefix=description[:50],
        scale=scale,
        region=china.geometry(),
        crs='EPSG:4326',
        maxPixels=1e13,
        fileFormat='GeoTIFF',
        formatOptions={'cloudOptimized': True}
    )
    task.start()
    return task

def main():
    """Main execution function."""
    # Get and normalize NDVI data
    ndvi_data = get_ndvi_data()
    
    # Resample to 1km resolution
    ndvi_resampled = ndvi_data.reproject(crs='EPSG:4326', scale=1000)
    
    # Export
    print("Exporting normalized NDVI data at 1km resolution...")
    task = export_to_drive(
        image=ndvi_resampled,
        description='china_normalized_ndvi_2015-2024_1km',
        folder='Flood_Susceptibility'
    )
    print(f"Task submitted, ID: {task.id}")
    print("\nTask monitoring: https://code.earthengine.google.com/tasks")

if __name__ == "__main__":
    main()
