"""
Script: Land Cover Data Processing
Data Source: MODIS MCD12Q1 (NASA)
"""

import ee
import geemap

# Initialize GEE
try:
    ee.Initialize(project='your-project-id')
except ee.ee_exception.EEException:
    ee.Authenticate()
    ee.Initialize(project='your-project-id')

# 1. Load China boundary
# Note: Replace with your own asset path or use a public dataset
china = ee.FeatureCollection("users/your-username/China_boundary").geometry()

def get_landcover_data():
    """Load MODIS land cover data (MCD12Q1, 2020)."""
    # Use MODIS MCD12Q1 V6 data (500m original resolution)
    lc = ee.ImageCollection("MODIS/061/MCD12Q1") \
        .filterDate('2020-01-01', '2020-12-31') \
        .first() \
        .select('LC_Type1') \
        .clip(china)
    
    # MODIS IGBP classification scheme:
    # 1: Evergreen Needleleaf Forest    2: Evergreen Broadleaf Forest
    # 3: Deciduous Needleleaf Forest    4: Deciduous Broadleaf Forest
    # 5: Mixed Forest                   6: Closed Shrublands
    # 7: Open Shrublands                8: Woody Savannas
    # 9: Savannas                       10: Grasslands
    # 11: Permanent Wetlands            12: Croplands
    # 13: Urban and Built-up            14: Cropland/Natural Mosaic
    # 15: Snow and Ice                  16: Barren
    # 17: Water Bodies
    print("MODIS land cover classification loaded.")
    return lc

def resample_landcover(lc_img):
    """Resample land cover data to 1km resolution using mode reducer."""
    # Step 1: Aggregate to intermediate resolution (2km)
    intermediate = lc_img.reduceResolution(
        reducer=ee.Reducer.mode(),
        maxPixels=1024
    ).reproject(
        crs='EPSG:4326',
        scale=2000
    )
    
    # Step 2: Resample to target resolution (1km)
    return intermediate.reproject(
        crs='EPSG:4326',
        scale=1000
    ).rename('landcover')

def export_landcover(image):
    """Export land cover image to Google Drive."""
    task = ee.batch.Export.image.toDrive(
        image=image,
        description='china_landcover_1km_modis',
        folder='Flood_Susceptibility',
        fileNamePrefix='landcover_1km',
        scale=1000,
        region=china,
        crs='EPSG:4326',
        maxPixels=1e13,
        fileFormat='GeoTIFF'
    )
    return task

def main():
    """Main execution function."""
    print("=== China 1km Land Cover Data Generation ===")
    print("Step 1/3: Loading MODIS land cover data...")
    lc = get_landcover_data()
    
    print("Step 2/3: Resampling to 1km...")
    lc_resampled = resample_landcover(lc)
    
    print("Step 3/3: Submitting export task...")
    task = export_landcover(lc_resampled)
    task.start()
    
    print(f"""
===== Task Submitted =====
Task ID: {task.id}
Monitor: https://code.earthengine.google.com/tasks
Output: landcover_1km.tif
Properties:
- Resolution: 1000m
- Source: MODIS MCD12Q1 (2020)
- Classes: 17 IGBP classes
- CRS: WGS84
""")

if __name__ == "__main__":
    main()
