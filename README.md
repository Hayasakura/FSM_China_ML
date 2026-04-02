# FSM_China_ML

### Overview

This Python script implements 7 machine learning algorithms to evaluate flood susceptibility. It processes environmental factors extracted via GIS, performs comprehensive model validation (AUC-ROC), and generates interpretable SHAP analysis to quantify factor contributions.

**The code implements:**

- **Data Extraction & Frequency Ratio (FR) Encoding:** Automatic calculation of FR values for 13 environmental factors to handle categorical and continuous variables.
- **Ensemble Modeling:** Implementation and comparison of 7 algorithms: Random Forest (RFC), Convolutional Neural Network (CNN/MLP), Gradient Boosting (GBDT), Support Vector Machine (SVC), K-Nearest Neighbors (KNC), Logistic Regression (LR), and Gaussian Naive Bayes (GNB).
- **Statistical Validation:** Multicollinearity diagnosis (VIF) and performance evaluation (Accuracy, Precision, Recall, F1-score).
- **Interpretability Engine:** Global and local feature contribution analysis using SHAP (Shapley Additive explanations).
- **Geospatial Mapping:** Generation of pixel-level susceptibility scores for integration back into GIS environments.

### Sample Dataset

To ensure reproducibility, a **ready-to-run sample dataset** is provided in the /sample folder.

- **Region:** Chongqing, China.
- **File:** Chongqing_sample.dbf.
- **Description:** This file contains pre-processed attributes for all 13 environmental factors and binary flood labels.
- **Usage:** Users can directly run the flood_susceptibility.py script using this sample file to verify the workflow and generate outputs immediately.

### Requirements

- **Python 3.9**

- **Dependencies:** All required libraries are listed in requirements.txt. You can install them in one click using:

  ```bash
  pip install -r requirements.txt
  ```

### Data Preparation & Workflow

**Step 1: GIS Preprocessing (ArcMap/ArcGIS Pro)**

1. Collect 13 conditioning factors (Elevation, Slope, NDVI, TWI, etc.).
2. Use **Raster to Point** and **Spatial Join** to aggregate attributes into a single table.
3. Export as a .dbf file (ensure the last column is the binary flood label).

**Step 2: Susceptibility Modeling (Python)**

1. Configure the file paths in flood_susceptibility.py:
   - dbfroad: Path to your input .dbf.
   - yfxroad: Output directory for the result .dbf.
2. Run the script to execute the training and validation loop.

**Step 3: Outputs & Visualization**
The script generates the following in the yfxroad directory:

- **combined_ROC.png**: ROC curves and AUC scores for all 7 models.
- **{Model}_shap_summary_plot.jpg**: Feature importance and influence direction.
- **{Model}_classification_metrics.csv**: Detailed pr
- **Output DBF**: Susceptibility probability scores (0.0–1.0) for every pixel.

**Step 4: Mapping Results**

1. Join the output .dbf back to your point shapefile in ArcMap.
2. Use **Feature to Raster** to generate the final Flood Susceptibility

### Data Sources & Acquisition

The input data were processed using Google Earth Engine (GEE) and ArcGIS. Scripts for data acquisitio/data folder:

- **Google Earth Engine Scripts (available in /data):**
  - dem_&_rainfall.py
  - soil_type.py: OpenLandMap soil type data.
  - ndvi.py: MODIS MOD13Q1 (2015-2024) data.
  - land_cover_land_use.py: MODIS MCD12Q1 (2020) data.
  - distance_to_water.py: Terrain-adjusted
  - twi.py, spi.py, sti.py: Topographic Wetness, Stream Power, and Sediment Transport indices.
  - flood_point.py: Flood points detected from Sentinel-1 SAR (2015-2024).
- **Factors processed in ArcGIS:**
  - **Slope, Aspect, Profile Curvature:** Derived from NASADEM.
  - **Lithology:** [https://www.geo.uni-hamburg.de/en/geologie/forschung/aquatische-geochemie/glim.html](https://www.google.com/url?sa=E&q=https%3A%2F%2Fwww.geo.uni-hamburg.de%2Fen%2Fgeologie%2Fforschung%2Faquatische-geochemie%2Fglim.html)
- **Future Climate Data (CMIP6):**
  Future precipitation projections are obtained from the NEX-GDDP-CMIP6 dataset.
  - **Data Source:** [https://nex-gddp-cmip6.s3.us-west-2.amazonaws.com/index.html#NEX-GDDP-CMIP6](https://www.google.com/url?sa=E&q=https%3A%2F%2Fnex-gddp-cmip6.s3.us-west-2.amazonaws.com%2Findex.html%23NEX-GDDP-CMIP6%2FGFDL-ESM4%2F)
  - **Model:** GFDL-ESM4
  - **Years:** 2031–2100
  - **Scenarios:** SSP1-2.6, SSP3-7.0, SSP5-8.5
  - **Resolution:** 0.25°

### License

BSD 3-Clause. See `LICENSE` file.
