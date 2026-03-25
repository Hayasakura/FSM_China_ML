# FSM_China_ML

## The `data` folder

**dem & rainfall.py**: DEM data (NASADEM) and precipitation data (CHIRPS 2015-2024) for the study area.

**soil_type.py**: Soil type data (OpenLandMap SOL_TEXTURE-CLASS_USDA-TT_M).

**ndvi.py**: NDVI data (MODIS MOD13Q1 2015-2024).

**land cover land use.py**: Land cover data (MODIS MCD12Q1 2020).

**distance to water.py**: Terrain-adjusted distance to water (JRC Global Surface Water + NASADEM).

**twi.py**: Topographic Wetness Index (SRTM + MERIT-Hydro).

**spi.py**: Stream Power Index (SRTM + MERIT-Hydro).

**sti.py**: Sediment Transport Index (SRTM + MERIT-Hydro).

**flood point.py**: Flood points detected from Sentinel-1 SAR (2015-2024).

---

## Factors processed in ArcGIS

**Slope, Aspect, Profile Curvature**: Derived from NASADEM.

**Lithology**: Global Lithological Map (GLiM) – https://www.geo.uni-hamburg.de/en/geologie/forschung/aquatische-geochemie/glim.html

---

## The `flood_susceptibility.py` file

**flood_susceptibility.py**: Main Python script. Construct 7 machine learning models (RFC, CNN, GBDT, SVC, KNC, LR, GNB) for flood susceptibility mapping, evaluate model performance, perform SHAP analysis, and output flood susceptibility prediction.

---

## Training data generation (ArcGIS)

All factor rasters were processed using **Reclassify**, **Raster to Point**, and **Spatial Join** tools, then exported as a single table.

**Output**: `training_data.dbf` – Input for `flood_susceptibility.py`

---

## License

BSD 3-Clause. See `LICENSE` file.
