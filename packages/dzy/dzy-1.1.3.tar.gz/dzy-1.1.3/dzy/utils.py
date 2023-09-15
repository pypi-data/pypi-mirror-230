import gcsfs
from datetime import datetime
from yaml import safe_load


def get_today_str(date_format: str = "%Y%m%d"):
    """
    Returns today's date as string (based on UTC time).
    """
    return datetime.utcnow().strftime(date_format)


def get_unix_time():
    """
    Returns the current UTC unix time.
    """
    return datetime.utcnow().timestamp()


def read_yaml_file(
        file_path: str,
        fs: gcsfs.GCSFileSystem = None,
        bucket_name: str = None
) -> dict:
    """
    Reads in yaml file, either from locally or from GCS.

    Looks for gs://{bucket_name}/{file_path} when bucket and fs are both
    present, else tries the file_path locally.
    """
    if fs and bucket_name:
        gcs_json_path = f"{bucket_name}/{file_path}"
        with fs.open(gcs_json_path) as f:
            y = safe_load(f)
    else:
        with open(file_path, "r") as f:
            y = safe_load(f)

    f.close()

    return y
