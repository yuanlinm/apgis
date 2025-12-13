## APGIS: All files and code in this repository are currently in the testing phase.

#### 1. POP_AP_MAPPING
*RUNNING:*
```bash
cd /path/to/GIS
bash CODE/0-RUN.bash_command_all.sh

python3 CODE/1-POP_AP_MAPPING.py \
  --years 1990-2025 \
  --pollutant-template "PM2.5_V3/PM2.5_{year}_V3.nc" \
  --pollutant-var PM2.5 \
  --pollutant-name pm25 \
  --pop-template "LandScan/landscan-global-{year}-assets/landscan-global-{year}.tif" \
  --cities "中国市界行政区划/cities.shp" \
  --output-dir "OUTPUT/mapping"
```

*Output:*
```bash
OUTPUT/mapping/{pollutant_name}/{year}/{省}/{市}/
├── triple_mapping.csv          # 像素级数据(经纬度、人口、污染物)**# Pixel-level data (latitude and longitude, population, pollutants)
├── triple_mapping.nc           # NetCDF format pixel data
├── preview.png                 # Spatial Distribution Visualization
└── stats.json                  # Statistical Indicators
```

*Requirements:*
| package       | version        | for                   |
| ---------- | ----------- | ---------------------- |
| numpy      | 2.3.5+      | Numerical computation and array operations     |
| pandas     | 2.3.3+      | Data processing and CSV output      |
| xarray     | 2025.12.0+  | NetCDF Data Reading, Writing and Processing   |
| geopandas  | 1.1.1+      | Geospatial Vector Data Processing   |
| matplotlib | 3.10.8+     | Data visualization and chart generation   |
| tifffile   | 2025.12.12+ | Reading TIFF format raster data   |
| shapely    | 2.1.2+      | Geometric object operations and spatial judgment |
| scipy      | 1.16.3+     | Scientific computing and spatial interpolation     |
| netCDF4    | 1.7.3+      | NetCDF format support         |


