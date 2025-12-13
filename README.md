## APGIS: All files and code in this repository are currently in the testing phase.

#### 1. POP_AP_MAPPING

# run
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
