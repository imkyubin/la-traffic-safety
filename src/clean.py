"""Data contracts and cleaning shared by analysis, notebooks and Tableau export."""
from pathlib import Path
import hashlib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / 'data/crashes_2024_2025.csv.gz'
PERIODS = ['Late Night', 'Morning Rush', 'Midday', 'Evening Rush', 'Night']
BINARY = ['ALCOHOL_INVOLVED', 'PEDESTRIAN_ACCIDENT', 'BICYCLE_ACCIDENT',
          'MOTORCYCLE_ACCIDENT', 'TRUCK_ACCIDENT']
SOURCE_COLUMNS = [
    'CASE_ID', 'ACCIDENT_YEAR', 'COLLISION_DATE', 'COLLISION_TIME', 'DAY_OF_WEEK',
    'COLLISION_SEVERITY', 'COUNTY', 'CITY', 'PRIMARY_RD', 'SECONDARY_RD',
    'POINT_X', 'POINT_Y', 'INTERSECTION', 'STATE_HWY_IND', 'HIT_AND_RUN',
    'CONTROL_DEVICE', 'TYPE_OF_COLLISION', 'PRIMARY_COLL_FACTOR',
    'PCF_VIOL_CATEGORY', *BINARY,
]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def parse_hhmm(values):
    """Accept integral HHMM; preserve unknown/invalid values as missing."""
    n = pd.to_numeric(values, errors='coerce')
    valid = n.notna() & (n % 1 == 0) & n.between(0, 2359) & ((n % 100) < 60)
    return (n // 100).where(valid).astype('Int64'), (n % 100).where(valid).astype('Int64')


def time_period(hours):
    """Original Tableau notebook's five mutually exclusive time blocks."""
    return pd.cut(hours.astype(float), bins=[-1, 4, 9, 14, 18, 23], labels=PERIODS)


def load_crashes(path=DEFAULT_DATA):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f'Missing crash data: {path}. See data/README.md.')
    df = pd.read_csv(path, dtype='string')
    missing = set(SOURCE_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f'Missing required columns: {sorted(missing)}')
    df = df[SOURCE_COLUMNS].copy()
    for col in df:
        df[col] = df[col].str.strip().replace('', pd.NA)
    if df['CASE_ID'].isna().any() or df['CASE_ID'].duplicated().any():
        raise ValueError('CASE_ID must be present and unique: input must be one row per crash.')
    severity = pd.to_numeric(df['COLLISION_SEVERITY'], errors='coerce')
    if not severity.isin([1, 2, 3, 4]).all():
        raise ValueError('This project expects injury/fatal crashes with severity codes 1–4.')
    dates = pd.to_datetime(df['COLLISION_DATE'], format='%Y-%m-%d', errors='coerce')
    if dates.isna().any():
        raise ValueError('COLLISION_DATE contains missing or invalid dates.')
    if not df['COUNTY'].eq('LOS ANGELES').all():
        raise ValueError('This analysis expects Los Angeles County records only.')
    df['DATE'] = dates
    df['IS_SEVERE'] = severity.isin([1, 2]).astype(int)
    df['HOUR'], df['MINUTE'] = parse_hhmm(df['COLLISION_TIME'])
    df['DATETIME'] = dates + pd.to_timedelta(df['HOUR'].astype(float), unit='h') + pd.to_timedelta(df['MINUTE'].astype(float), unit='m')
    df['TIME_PERIOD'] = time_period(df['HOUR'])
    df['WEEKDAY'] = dates.dt.dayofweek
    df['IS_WEEKEND'] = (df['WEEKDAY'] >= 5).astype(int)
    for col in ['POINT_X', 'POINT_Y']:
        df[col] = pd.to_numeric(df[col], errors='coerce').astype(float)
    df['HAS_COORDINATES'] = df['POINT_X'].between(-180, 180) & df['POINT_Y'].between(-90, 90)
    quality = {
        'input_sha256': sha256(path), 'rows': len(df), 'unique_crashes': df['CASE_ID'].nunique(),
        'date_min': str(dates.min().date()), 'date_max': str(dates.max().date()),
        'severe_crashes': int(df['IS_SEVERE'].sum()), 'severe_share': float(df['IS_SEVERE'].mean()),
        'invalid_time_rows': int(df['HOUR'].isna().sum()),
        'missing_or_invalid_coordinates': int((~df['HAS_COORDINATES']).sum()),
        'weekday_mismatches': int((pd.to_numeric(df['DAY_OF_WEEK']) != df['WEEKDAY'] + 1).sum()),
        'year_counts': {str(k): int(v) for k, v in dates.dt.year.value_counts().sort_index().items()},
        'severity_counts': {str(int(k)): int(v) for k, v in severity.value_counts().sort_index().items()},
    }
    return df, quality


def summarize(df, keys):
    """Always publish the denominator beside the severe count and share."""
    result = df.groupby(keys, observed=True, dropna=False)['IS_SEVERE'].agg(
        crashes='size', severe_crashes='sum').reset_index()
    result['severe_share'] = result['severe_crashes'] / result['crashes']
    return result


def tableau_export(df):
    """Rebuild the original export schema, retaining crash identity internally.

    Keep one row per CASE_ID throughout preparation. Require valid time and
    coordinates only for this geographic export; retain other rows for EDA.
    """
    view = df.loc[df['HOUR'].notna() & df['HAS_COORDINATES']].copy()
    for col in BINARY:
        view[col] = view[col].eq('Y').fillna(False).astype(int)
    view['COLLISION_TIME'] = (view['HOUR'] * 100 + view['MINUTE']).astype(str).str.zfill(4)
    view['hour'] = view['HOUR']
    view['time_period'] = view['TIME_PERIOD']
    view['collision_severity_binary'] = view['IS_SEVERE']
    columns = ['CITY', 'POINT_X', 'POINT_Y', 'COLLISION_TIME', 'hour', 'DAY_OF_WEEK',
               'time_period', 'collision_severity_binary', 'TYPE_OF_COLLISION',
               'PRIMARY_COLL_FACTOR', 'INTERSECTION', 'PCF_VIOL_CATEGORY', *BINARY]
    return view[columns]


def model_frame(df):
    """Keep the original model's required fields and flag definitions."""
    required = ['CASE_ID', 'COLLISION_DATE', 'COLLISION_TIME', 'DAY_OF_WEEK',
                'COLLISION_SEVERITY', 'INTERSECTION', 'STATE_HWY_IND',
                'HIT_AND_RUN', 'CONTROL_DEVICE', 'DATETIME']
    cdf = df.dropna(subset=required).copy()
    cdf['HOUR'] = cdf['HOUR'].astype(int)
    cdf['MONTH'] = cdf['DATE'].dt.month
    cdf['DAY_OF_MONTH'] = cdf['DATE'].dt.day
    cdf['DAY_OF_WEEK_NUM'] = cdf['WEEKDAY']
    cdf['IS_EVENING_PEAK'] = cdf['HOUR'].isin([17, 18, 19, 20, 21]).astype(int)
    cdf['IS_LATE_NIGHT'] = cdf['HOUR'].isin([20, 21, 22, 23, 0]).astype(int)
    for new, old, value in [
        ('IS_INTERSECTION', 'INTERSECTION', 'Y'),
        ('IS_SURFACE_STREET', 'STATE_HWY_IND', 'N'),
        ('IS_NO_CONTROL', 'CONTROL_DEVICE', 'D'),
        ('IS_FELONY_HR', 'HIT_AND_RUN', 'F'),
    ]:
        cdf[new] = cdf[old].eq(value).astype(int)
    for field, period, prefix in [('HOUR', 24, 'HOUR'), ('WEEKDAY', 7, 'DOW'), ('MONTH', 12, 'MONTH')]:
        cdf[f'{prefix}_SIN'] = np.sin(2 * np.pi * cdf[field] / period)
        cdf[f'{prefix}_COS'] = np.cos(2 * np.pi * cdf[field] / period)
    return cdf
