"""
Script: Terrain-Adjusted Distance to Water
Data Sources:
- Water bodies: JRC Global Surface Water (occurrence > 50%)
- Elevation: NASADEM
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

def get_water_data():
    """Get permanent water bodies (occurrence > 50%) from JRC dataset."""
    water = ee.Image("JRC/GSW1_4/GlobalSurfaceWater") \
        .select('occurrence') \
        .gt(50) \
        .clip(china)
    print("JRC water data loaded.")
    return water

def get_topography():
    """Load elevation and slope data from NASADEM."""
    nasadem = ee.Image("NASA/NASADEM_HGT/001").select('elevation').clip(china)
    slope = ee.Terrain.slope(nasadem).clip(china)
    print("NASADEM elevation and slope loaded.")
    return nasadem, slope

def calculate_terrain_adjusted_distance(water, elevation, slope):
    """Calculate distance to water with terrain-based cost factors."""
    print("Calculating terrain-adjusted distance to water...")
    
    # (1) Base Euclidean distance (max radius 5km)
    base_distance = water.distance(ee.Kernel.euclidean(radius=5000, units='meters'))
    
    # (2) Slope cost factor (steeper slopes increase distance cost)
    # Slope cost ranges from 1 to 3 (1 at 0°, 3 at 45°)
    slope_cost = slope.expression(
        "1 + (slope / 45)",
        {'slope': slope}
    ).clamp(1, 3)
    
    # (3) Elevation adjustment factor (depressions increase flood potential)
    # Calculate relative elevation (difference from local minimum within 500m)
    min_elevation = elevation.focal_min(radius=500, units='meters')
    elevation_diff = elevation.subtract(min_elevation)
    elevation_cost = elevation_diff.expression(
        "1 + (elev_diff / 100)",  # +100m doubles cost
        {'elev_diff': elevation_diff}
    ).clamp(1, 2)
    
    # (4) Combined terrain-adjusted distance
    adjusted_distance = base_distance \
        .multiply(slope_cost) \
        .multiply(elevation_cost) \
        .rename('adjusted_water_distance')
    
    return adjusted_distance.clip(china)

def export_water_data(image):
    """Export terrain-adjusted distance to water to Google Drive."""
    task = ee.batch.Export.image.toDrive(
        image=image,
        description='china_water_distance_terrain_adjusted_1km',
        folder='Flood_Susceptibility',
        fileNamePrefix='water_distance_terrain_1km',
        scale=1000,
        region=china,
        crs='EPSG:4326',
        maxPixels=1e13,
        fileFormat='GeoTIFF',
        formatOptions={'noData': -9999}
    )
    return task

def main():
    """Main execution function."""
    print("=== China 1km Terrain-Adjusted Distance to Water ===")
    
    print("Step 1/4: Loading water data...")
    water = get_water_data()
    
    print("Step 2/4: Loading elevation and slope data...")
    elevation, slope = get_topography()
    
    print("Step 3/4: Calculating terrain-adjusted distance...")
    water_distance = calculate_terrain_adjusted_distance(water, elevation, slope)
    
    print("Step 4/4: Submitting export task...")
    task = export_water_data(water_distance)
    task.start()
    
    print(f"""
===== Task Submitted =====
Task ID: {task.id}
Monitor: https://code.earthengine.google.com/tasks
Output: water_distance_terrain_1km.tif
Properties:
- Resolution: 1000m
- Water source: JRC GSW (occurrence > 50%)
- DEM source: NASADEM
- Method: Terrain-adjusted distance (slope cost + elevation adjustment)
- CRS: WGS84
- NoData: -9999
""")

if __name__ == "__main__":
    main()
