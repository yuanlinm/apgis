
source .venv/bin/activate && python3 code/1-triple_mapping_pipline.py \
	--years 2000 \
	--pollutant-template "data/3.1-CHAP_PM25_avgY_1K_2000_2021_V3/CHAP_PM2.5_Y1K_{year}_V4.nc" \
	--pollutant-var PM2.5 \
	--pollutant-name pm25 \
	--pop-template "data/2-LandScan/landscan-global-{year}-assets/landscan-global-{year}.tif" \
	--cities "data/1-中国市界行政区划/cities.shp" \
	--output-dir "output/mapping"
