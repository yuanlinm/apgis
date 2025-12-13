## APGIS: All files and code in this repository are currently in the testing phase.

#### 1. POP_AP_MAPPING

GIS/
├── 1-中国市界行政区划/          # 城市边界Shapefile
├── 2-LandScan/                  # 2000-2021年人口栅格数据(TIFF)
├── 3-CHAP_Ozone_avgY_1K_2000_2024_V3/   # 2000-2024年臭氧数据(NetCDF)
├── 3-CHAP_PM25_avgY_1K_2000_2021_V4/    # 2000-2021年PM2.5数据(NetCDF)
├── CODE/
│   ├── 0-RUN.bash_command_all.sh        # 运行脚本
│   └── 1-triple_mapping_pipline.py      # 核心处理程序
└── OUTPUT/                      # 输出目录


# run
```bash
cd /path/to/GIS
bash CODE/0-RUN.bash_command_all.sh
```
