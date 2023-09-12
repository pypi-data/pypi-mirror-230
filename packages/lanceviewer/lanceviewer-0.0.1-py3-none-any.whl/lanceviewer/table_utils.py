import lance
import duckdb
from pathlib import Path
from lanceviewer.settings import should_download_remote_data

def load_dataset(uri):
    is_local = Path(uri).exists()
    is_bucket = uri.startswith("s3://") or uri.startswith("gs://")
    if not is_local and not is_bucket:
        raise ValueError("Invalid URI")
    if is_local or (is_bucket and not should_download_remote_data()):
        return lance.dataset(uri)
    else:
        raise NotImplementedError("Remote data download not supported yet")

def run_sql_query(dataset, query, limit=None):
    if query.rstrip().lstrip():
        table = dataset.to_table(limit=limit)  # noqa
        result = duckdb.sql(query).to_df()
        return result

def apply_transforms(df, transform):
    for key, (fn, _) in transform.items():
        if key in df.columns:
            df[key] = df[key].apply(fn)
    return df

def get_column_config(transform):
    column_config = {}
    for key, (_, config) in transform.items():
        if config is not None:
            column_config[key] = config
    return column_config
