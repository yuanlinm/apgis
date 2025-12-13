import argparse
import json
import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd
import matplotlib.pyplot as plt
from pathlib import Path
from tifffile import TiffFile
from shapely.geometry import Point
from scipy.ndimage import map_coordinates

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Heiti TC', 'STHeiti', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

# --------------------------------------------------------------
# Helpers
# --------------------------------------------------------------

def safe_name(name: str) -> str:
    return name.replace('/', '-').replace(' ', '')

def parse_years(years_arg: str):
    years_arg = years_arg.strip()
    if '-' in years_arg:
        start, end = years_arg.split('-')
        return list(range(int(start), int(end) + 1))
    if ',' in years_arg:
        return [int(y) for y in years_arg.split(',')]
    return [int(years_arg)]

def load_population(pop_path: Path):
    with TiffFile(pop_path) as tif:
        pop_data = tif.pages[0].asarray()
        tiepoint = tif.pages[0].tags.get(33922).value
        pixelscale = tif.pages[0].tags.get(33550).value
        lon_origin, lat_origin = tiepoint[3], tiepoint[4]
        lon_res, lat_res = pixelscale[0], pixelscale[1]
        lat_max = lat_origin
    return pop_data, lon_origin, lat_max, lon_res, lat_res

def load_pollutant(nc_path: Path, var_name: str):
    ds = xr.open_dataset(nc_path)
    data = ds[var_name].values
    lons = ds['lon'].values
    lats = ds['lat'].values
    return ds, data, lons, lats

def interpolate_pollutant(data, lons, lats, lon, lat):
    lon_idx = (lon - lons[0]) / (lons[1] - lons[0])
    lat_idx = (lat - lats[0]) / (lats[1] - lats[0])
    if not (0 <= lon_idx < data.shape[1] and 0 <= lat_idx < data.shape[0]):
        return np.nan
    if lon_idx < data.shape[1]-1 and lat_idx < data.shape[0]-1:
        pm_val = map_coordinates(data, [[lat_idx], [lon_idx]], order=1, mode='constant', cval=np.nan)[0]
    else:
        pm_val = np.nan
    if np.isnan(pm_val):
        pm_val = map_coordinates(data, [[lat_idx], [lon_idx]], order=0, mode='nearest')[0]
    return pm_val

def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------
# Core processing per city
# --------------------------------------------------------------

def process_city(city_row, pop_data, lon_origin, lat_max, lon_res, lat_res, pollutant_data, pollutant_lons, pollutant_lats, year, out_city_dir):
    city_name = city_row['市']
    province = city_row['省']
    geom = city_row.geometry
    if geom is None or geom.is_empty:
        return None

    minx, miny, maxx, maxy = geom.bounds
    col_start = max(0, int((minx - lon_origin) / lon_res))
    col_end = min(pop_data.shape[1], int((maxx - lon_origin) / lon_res) + 1)
    row_start = max(0, int((lat_max - maxy) / lat_res))
    row_end = min(pop_data.shape[0], int((lat_max - miny) / lat_res) + 1)

    records = []
    total_pop_pixels = 0
    matched_pixels = 0
    total_pop = 0.0
    matched_pop = 0.0
    pm_sum = 0.0
    pm_weighted_sum = 0.0

    for row in range(row_start, row_end):
        for col in range(col_start, col_end):
            pop_val = pop_data[row, col]
            if pop_val <= 0 or pop_val == -2147483647:
                continue
            lon = lon_origin + (col + 0.5) * lon_res
            lat = lat_max - (row + 0.5) * lat_res
            if not geom.contains(Point(lon, lat)):
                continue
            total_pop_pixels += 1
            total_pop += pop_val
            pm_val = interpolate_pollutant(pollutant_data, pollutant_lons, pollutant_lats, lon, lat)
            if np.isnan(pm_val):
                continue
            matched_pixels += 1
            matched_pop += pop_val
            pm_sum += pm_val
            pm_weighted_sum += pm_val * pop_val
            records.append({
                '省': province,
                '市': city_name,
                'lon': lon,
                'lat': lat,
                'population': float(pop_val),
                'pollutant': float(pm_val),
                'year': year
            })

    mapping_rate = matched_pixels / total_pop_pixels if total_pop_pixels > 0 else 0.0
    pop_coverage = matched_pop / total_pop if total_pop > 0 else 0.0
    pm_mean = pm_sum / matched_pixels if matched_pixels > 0 else np.nan
    pm_weighted = pm_weighted_sum / matched_pop if matched_pop > 0 else np.nan

    stats = {
        'province': province,
        'city': city_name,
        'year': int(year),
        'population_pixels': int(total_pop_pixels),
        'matched_pixels': int(matched_pixels),
        'mapping_rate': float(mapping_rate),
        'population_sum': float(total_pop),
        'matched_population': float(matched_pop),
        'population_coverage': float(pop_coverage),
        'pm_mean': float(pm_mean) if not np.isnan(pm_mean) else None,
        'pm_weighted': float(pm_weighted) if not np.isnan(pm_weighted) else None
    }

    ensure_dir(out_city_dir)

    if records:
        df = pd.DataFrame(records)
        csv_path = out_city_dir / 'triple_mapping.csv'
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        ds = xr.Dataset({
            'population': ('pixel', df['population'].values.astype(np.float32)),
            'pollutant': ('pixel', df['pollutant'].values.astype(np.float32))
        }, coords={
            'lon': ('pixel', df['lon'].values.astype(np.float32)),
            'lat': ('pixel', df['lat'].values.astype(np.float32)),
            'year': ('pixel', df['year'].values.astype(np.int16))
        })
        ds.to_netcdf(out_city_dir / 'triple_mapping.nc')
        # Preview scatter
        fig, ax = plt.subplots(figsize=(7, 6))
        scatter = ax.scatter(df['lon'], df['lat'], c=df['pollutant'], s=np.clip(df['population'] / 50, 5, 120),
                             cmap='YlOrRd', alpha=0.7, edgecolors='none')
        plt.colorbar(scatter, ax=ax, label='浓度')
        ax.set_title(f"{province}-{city_name} {year}")
        ax.set_xlabel('经度')
        ax.set_ylabel('纬度')
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        fig.savefig(out_city_dir / 'preview.png', dpi=150, bbox_inches='tight')
        plt.close(fig)
    # Stats JSON
    with open(out_city_dir / 'stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    return stats

# --------------------------------------------------------------
# Main
# --------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description='Triple mapping pipeline (population - pollutant) with per-city outputs')
    parser.add_argument('--years', default='2000-2021', help='年份，例如 2000 或 2000-2021 或 2000,2005,2010')
    parser.add_argument('--pollutant-template', default='data/3.1-CHAP_PM25_avgY_1K_2000_2021_V3/CHAP_PM2.5_Y1K_{year}_V4.nc', help='污染物NC路径模板，使用{year}占位符，例如 data/.../CHAP_PM2.5_Y1K_{year}_V4.nc')
    parser.add_argument('--pollutant-var', default='PM2.5', help='NC变量名，PM2.5或Ozone变量名')
    parser.add_argument('--pollutant-name', default='pm25', help='输出使用的污染物名称，用于文件夹命名，如 pm25 或 ozone')
    parser.add_argument('--pop-template', default='data/2-LandScan/landscan-global-{year}-assets/lsglobal_{year}.tif', help='人口数据TIF模板，使用{year}占位符')
    parser.add_argument('--cities', default='data/1-中国市界行政区划/cities.shp', help='城市边界shp路径')
    parser.add_argument('--output-dir', default='output/mapping', help='输出根目录')
    args = parser.parse_args()

    years = parse_years(args.years)
    cities = gpd.read_file(args.cities)
    out_root = Path(args.output_dir) / args.pollutant_name
    ensure_dir(out_root)

    for year in years:
        print(f"\n=== 处理年份 {year} ===")
        pop_path = Path(args.pop_template.format(year=year))
        pollutant_path = Path(args.pollutant_template.format(year=year))
        if not pop_path.exists():
            print(f"  跳过：人口数据缺失 {pop_path}")
            continue
        if not pollutant_path.exists():
            print(f"  跳过：污染物数据缺失 {pollutant_path}")
            continue
        pop_data, lon_origin, lat_max, lon_res, lat_res = load_population(pop_path)
        pol_ds, pol_data, pol_lons, pol_lats = load_pollutant(pollutant_path, args.pollutant_var)

        year_dir = out_root / str(year)
        ensure_dir(year_dir)
        summary_rows = []

        for _, city_row in cities.iterrows():
            province = city_row['省']
            city_name = city_row['市']
            city_dir = year_dir / safe_name(province) / safe_name(city_name)
            stats = process_city(city_row, pop_data, lon_origin, lat_max, lon_res, lat_res,
                                 pol_data, pol_lons, pol_lats, year, city_dir)
            if stats:
                summary_rows.append(stats)

        pol_ds.close()

        if summary_rows:
            df_sum = pd.DataFrame(summary_rows)
            df_sum.to_csv(year_dir / 'year_summary.csv', index=False, encoding='utf-8-sig')
            with open(year_dir / 'year_summary.json', 'w', encoding='utf-8') as f:
                json.dump(summary_rows, f, ensure_ascii=False, indent=2)
            print(f"  年度汇总: {len(summary_rows)} 城市 -> year_summary.csv/json")
        else:
            print("  年度无数据")

if __name__ == '__main__':
    main()
