"""
Script: Soil Type Data Processing
Data Source: OpenLandMap SOL_TEXTURE-CLASS_USDA-TT_M (USDA soil texture classification)
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
china = ee.FeatureCollection("users/your-username/China_boundary")

# 2. Soil data processing
def get_processed_soil_data():
    """Process soil texture data and assign hydrological group weights."""
    # Use OpenLandMap soil data
    soil_raw = ee.Image("OpenLandMap/SOL/SOL_TEXTURE-CLASS_USDA-TT_M/v02")
    
    # Select classification band
    soil_class = soil_raw.select('b0')
    
    # Assign hydrological weights based on USDA texture classes
    # Weight values: higher = lower permeability, higher runoff potential
    soil_factor = (
        soil_class.eq(1).multiply(0.2)   # Sand
        .add(soil_class.eq(2).multiply(0.3))   # Sandy loam
        .add(soil_class.eq(3).multiply(0.5))   # Loam
        .add(soil_class.eq(4).multiply(0.6))   # Silt loam
        .add(soil_class.eq(5).multiply(0.7))   # Clay loam
        .add(soil_class.eq(6).multiply(0.9))   # Clay
        .rename('soil_factor')
        .clip(china)
    )
    return soil_factor

def resample_soil_data(soil_img):
    """Resample soil data to 1km resolution using mean reducer."""
    return soil_img.reduceResolution(
        reducer=ee.Reducer.mean(),
        maxPixels=1024
    ).reproject(
        crs='EPSG:4326',
        scale=1000
    )

def export_soil_factor(image):
    """Export soil factor image to Google Drive."""
    task = ee.batch.Export.image.toDrive(
        image=image,
        description='china_soil_factor_1km_final',
        folder='Flood_Susceptibility',
        fileNamePrefix='soil_factor_1km',
        scale=1000,
        region=china.geometry(),
        crs='EPSG:4326',
        maxPixels=1e13,
        fileFormat='GeoTIFF'
    )
    return task

def main():
    """Main execution function."""
    print("Processing soil data...")
    soil_data = get_processed_soil_data()
    
    print("Resampling to 1km...")
    soil_resampled = resample_soil_data(soil_data)
    
    print("Submitting export task...")
    task = export_soil_factor(soil_resampled)
    task.start()
    
    print(f"""
Export task submitted!
Task ID: {task.id}
Output path: Flood_Susceptibility/soil_factor_1km.tif
Resolution: 1km
CRS: WGS84
""")

if __name__ == "__main__":
    main()
