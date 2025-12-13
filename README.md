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
├── triple_mapping.csv          # 像素级数据(经纬度、人口、污染物)
├── triple_mapping.nc           # NetCDF格式像素数据
├── preview.png                 # 空间分布可视化
└── stats.json                  # 统计指标
```

*Requirements:*
| 包名       | 版本        | 用途                   |
| ---------- | ----------- | ---------------------- |
| numpy      | 2.3.5+      | 数值计算和数组操作     |
| pandas     | 2.3.3+      | 数据处理和CSV输出      |
| xarray     | 2025.12.0+  | NetCDF数据读写和处理   |
| geopandas  | 1.1.1+      | 地理空间矢量数据处理   |
| matplotlib | 3.10.8+     | 数据可视化和图表生成   |
| tifffile   | 2025.12.12+ | TIFF格式栅格数据读取   |
| shapely    | 2.1.2+      | 几何对象操作和空间判断 |
| scipy      | 1.16.3+     | 科学计算和空间插值     |
| netCDF4    | 1.7.3+      | NetCDF格式支持         |


