import duckdb
import requests
import pandas as pd
from tqdm import tqdm
from pathlib import Path
from datetime import datetime
from joblib import Parallel, delayed
from pandas.tseries.offsets import MonthEnd

baseurl = "https://data.sifeng.site/"

def indicator_day(fields = "*",
                  begin_date = "1999-12-19",
                  end_date = datetime.now().strftime("%Y-%d-%m"),
                  stock_code = "*",
                  local_dir = Path.home() / ".sifeng/parquet/indicator_day/",
                  n_jobs = 4):
    # fetch data from COS
    def fdownload(mend):
        filename = f"INDICATOR-DAY{mend.strftime('%Y%m')}.parquet"
        update = not (local_dir / filename).exists()
        if mend.year == datetime.now().year and mend.month == datetime.now().month:
            update = True
        if update:
            resp = requests.get(baseurl + filename)
            with open(local_dir / filename, "wb") as file:
                file.write(resp.content)
    begin_date, end_date = pd.to_datetime(begin_date), pd.to_datetime(end_date)
    tasks = tqdm([delayed(fdownload)(_) for _ in pd.date_range(begin_date, end_date + MonthEnd(0), freq="M")], desc="Checking", unit="month", unit_scale=True, leave=False)
    local_dir.mkdir(parents=True, exist_ok=True)
    Parallel(n_jobs=n_jobs, verbose=0)(tasks)
    # parse data from local drive
    if fields == "*":
        fields = ['stock_code', 'trade_date', 'turnover_rate', 'turnover_rate_free', 'volume_ratio', 'pe', 'pe_ttm', 'pb', 'ps', 'ps_ttm', 'dv_ratio', 'dv_ttm', 'total_share', 'float_share', 'free_share', 'total_mv', 'circ_mv']
    if stock_code == "*":
        sql = f"SELECT {', '.join(fields)} FROM read_parquet('{local_dir / '*.parquet'}') WHERE trade_date BETWEEN '{begin_date.strftime('%Y-%m-%d')}' AND '{end_date.strftime('%Y-%m-%d')}'"
    elif isinstance(stock_code, str):
        sql = f"SELECT {', '.join(fields)} FROM read_parquet('{local_dir / '*.parquet'}') WHERE trade_date BETWEEN '{begin_date.strftime('%Y-%m-%d')}' AND '{end_date.strftime('%Y-%m-%d')}' AND stock_code = '{stock_code}'"
    else:
        connector = "', '"
        sql = f"SELECT {', '.join(fields)} FROM read_parquet('{local_dir / '*.parquet'}') WHERE trade_date BETWEEN '{begin_date.strftime('%Y-%m-%d')}' AND '{end_date.strftime('%Y-%m-%d')}' AND stock_code IN ('{connector.join(stock_code)}')"
    return duckdb.sql(sql).df()

def kline_day(fields = "*",
              begin_date = "1999-12-19",
              end_date = datetime.now().strftime("%Y-%d-%m"),
              stock_code = "*",
              local_dir = Path.home() / ".sifeng/parquet/kline_day/",
              n_jobs = 4):
    # fetch data from COS
    def fdownload(mend):
        filename = f"KLINE-DAY{mend.strftime('%Y%m')}.parquet"
        update = not (local_dir / filename).exists()
        if mend.year == datetime.now().year and mend.month == datetime.now().month:
            update = True
        if update:
            resp = requests.get(baseurl + filename)
            with open(local_dir / filename, "wb") as file:
                file.write(resp.content)
    begin_date, end_date = pd.to_datetime(begin_date), pd.to_datetime(end_date)
    tasks = tqdm([delayed(fdownload)(_) for _ in pd.date_range(begin_date, end_date + MonthEnd(0), freq="M")], desc="Checking", unit="month", unit_scale=True, leave=False)
    local_dir.mkdir(parents=True, exist_ok=True)
    Parallel(n_jobs=n_jobs, verbose=0)(tasks)
    # parse data from local drive
    if fields == "*":
        fields = ['stock_code', 'trade_date', 'open', 'high', 'low', 'close', 'vol', 'amount', 'adj_factor']
    if stock_code == "*":
        sql = f"SELECT {', '.join(fields)} FROM read_parquet('{local_dir / '*.parquet'}') WHERE trade_date BETWEEN '{begin_date.strftime('%Y-%m-%d')}' AND '{end_date.strftime('%Y-%m-%d')}'"
    elif isinstance(stock_code, str):
        sql = f"SELECT {', '.join(fields)} FROM read_parquet('{local_dir / '*.parquet'}') WHERE trade_date BETWEEN '{begin_date.strftime('%Y-%m-%d')}' AND '{end_date.strftime('%Y-%m-%d')}' AND stock_code = '{stock_code}'"
    else:
        connector = "', '"
        sql = f"SELECT {', '.join(fields)} FROM read_parquet('{local_dir / '*.parquet'}') WHERE trade_date BETWEEN '{begin_date.strftime('%Y-%m-%d')}' AND '{end_date.strftime('%Y-%m-%d')}' AND stock_code IN ('{connector.join(stock_code)}')"
    return duckdb.sql(sql).df()

def basic_info(fields = "*",
               stock_code = "*",
               local_dir = Path.home() / ".sifeng/parquet/status_charts/",
               force_update = False):
    # fetch data from COS
    local_dir.mkdir(parents=True, exist_ok=True)
    filename = "BASIC-INFO.parquet"
    update = not (local_dir / filename).exists()
    if force_update:
        update = True
    if update:
        resp = requests.get(baseurl + filename)
        with open(local_dir / filename, "wb") as file:
            file.write(resp.content)
    # parse data from local drive
    if fields == "*":
        fields = ['stock_code', 'stock_name', 'area', 'industry', 'sector', 'list_status', 'list_date', 'st_flag']
    if stock_code == "*":
        sql = f"SELECT {', '.join(fields)} FROM read_parquet('{local_dir / 'BASIC-INFO.parquet'}')"
    elif isinstance(stock_code, str):
        sql = f"SELECT {', '.join(fields)} FROM read_parquet('{local_dir / 'BASIC-INFO.parquet'}') WHERE stock_code = '{stock_code}'"
    else:
        connector = "', '"
        sql = f"SELECT {', '.join(fields)} FROM read_parquet('{local_dir / 'BASIC-INFO.parquet'}') WHERE stock_code IN ('{connector.join(stock_code)}')"
    return duckdb.sql(sql).df()
