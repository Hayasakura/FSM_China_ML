"""
Script: Flood Detection from Sentinel-1 SAR
Data Sources:
- SAR: Sentinel-1 GRD (ESA)
- Water mask: JRC Global Surface Water
"""

import ee

class FloodDetectorSAR:
    def __init__(self):
        # Initialize GEE
        try:
            ee.Initialize(project='your-project-id')
        except ee.ee_exception.EEException:
            ee.Authenticate()
            ee.Initialize(project='your-project-id')
        
        # Area of interest
        # Note: Replace with your own asset path or use a public dataset
        self.aoi = ee.FeatureCollection('users/your-username/China_boundary')
        
        # Parameters
        self.years = list(range(2015, 2025))
        self.months = [4, 5, 6, 7, 8, 9]  # Flood season months
        self.threshold_ratio = 1.25
        self.water_mask = ee.Image('JRC/GSW1_4/GlobalSurfaceWater') \
            .select('seasonality') \
            .gte(6) \
            .clip(self.aoi)  # Permanent water mask (seasonality >= 6)

    def get_s1(self, pol):
        """Get Sentinel-1 GRD collection with specified polarization."""
        return ee.ImageCollection('COPERNICUS/S1_GRD') \
            .filter(ee.Filter.eq('instrumentMode', 'IW')) \
            .filter(ee.Filter.listContains('transmitterReceiverPolarisation', pol)) \
            .filter(ee.Filter.eq('orbitProperties_pass', 'ASCENDING')) \
            .filterBounds(self.aoi) \
            .select(pol)

    def detect_year(self, year):
        """Detect flood pixels for a given year."""
        vh = self.get_s1('VH')
        
        # Select baseline period (dry season)
        if year in (2015, 2016):
            start, end = f'{year}-11-01', f'{year}-11-30'  # November for 2015-2016
        else:
            start, end = f'{year}-03-01', f'{year}-03-31'  # March for other years
        
        b_vh = vh.filterDate(start, end).median().clip(self.aoi)
        
        # Skip if no baseline data
        if b_vh.bandNames().size().getInfo() == 0:
            print(f"⚠️ Baseline missing for year {year} ({start}--{end})")
            return None
        
        imgs = []
        for m in self.months:
            a_vh = vh.filterDate(f'{year}-{m:02d}-01', f'{year}-{m:02d}-28').max().clip(self.aoi)
            if a_vh.bandNames().size().getInfo():
                # Flood detection: VH ratio > threshold AND not permanent water
                mask = (a_vh.divide(b_vh).gt(self.threshold_ratio).And(self.water_mask.Not()))
                
                # Slope filtering (exclude areas with slope > 5°)
                mask = mask.updateMask(ee.Terrain.slope(ee.Image('NASA/NASADEM_HGT/001')).lt(5))
                
                # Connected component analysis (keep clusters >= 8 pixels)
                mask = mask.updateMask(mask.toUint8().connectedPixelCount(8, True).gte(8))
                imgs.append(mask.rename('flood'))
        
        if not imgs:
            print(f"⚠️ Year {year} has no valid monthly data")
            return None
        
        # Resample to 100m resolution
        resampled_imgs = [img.reproject(crs='EPSG:4326', scale=100) for img in imgs]
        
        # Return maximum flood extent for the year
        year_img = ee.ImageCollection(resampled_imgs).max().rename('flood')
        return year_img.setDefaultProjection(crs='EPSG:4326', scale=250)

    def run(self):
        """Run flood detection for all years and export."""
        all_imgs = []
        for y in self.years:
            print(f">>>> Year {y}")
            img = self.detect_year(y)
            if img:
                all_imgs.append(img)
        
        if not all_imgs:
            print("❌ No results.")
            return
        
        # Combine all years (max extent)
        full = ee.ImageCollection(all_imgs).max().rename('flood_binary') \
            .setDefaultProjection(crs='EPSG:4326', scale=250)
        
        # Resample to 1km for final output
        full_resampled = full.reproject(crs='EPSG:4326', scale=1000)
        
        # Export to Google Drive
        task = ee.batch.Export.image.toDrive(
            image=full_resampled.toByte(),
            description='Flood_MTB_1km',
            fileNamePrefix='cnflood_mtb_1km',
            region=self.aoi.geometry(),
            scale=1000,
            crs='EPSG:4326',
            maxPixels=1e13,
            fileFormat='GeoTIFF',
            skipEmptyTiles=True
        )
        task.start()
        print("✅ Export started. Task ID:", task.id)

if __name__ == '__main__':
    FloodDetectorSAR().run()
