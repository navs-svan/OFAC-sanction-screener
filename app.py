import sys
import json
import time
import pandas as pd
import os
from pathlib import Path
from ftplib import FTP_TLS


def get_ftp() -> FTP_TLS:
    # FTP details
    FTPHOST = os.environ["FTPHOST"]
    FTPUSER = os.environ["FTPUSER"]
    FTPPASS = os.environ["FTPPASS"]
    FTPPORT = int(os.environ["FTPPORT"])

    # Log in to FTP
    ftp = FTP_TLS()
    ftp.connect(FTPHOST, FTPPORT)
    ftp.login(FTPUSER, FTPPASS)
    ftp.prot_p()

    return ftp


def read_csv(config: dict) -> pd.DataFrame:
    url = config["URL"]
    params = config["PARAMS"]
    return pd.read_csv(filepath_or_buffer=url, **params)


def upload_to_ftp(ftp: FTP_TLS, filesource: Path) -> None:
    with open(filesource, "rb") as f:
        ftp.storbinary(f"STOR {filesource.name}", f)


def pipeline():
    ftp = get_ftp()

    credentials_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(credentials_path, "r") as f:
        config = json.load(f)

    for source_name, source_config in config.items():
        # Download file from OFAC
        FILEPATH = Path(f"{source_name}.csv")
        print(f"Retrieving {FILEPATH.name} from OFAC")
        df = read_csv(source_config)
        df.to_csv(FILEPATH, index=False)
        # Upload to FTP server
        print(f"Uploading {FILEPATH.name} to FTP server")
        upload_to_ftp(ftp=ftp, filesource=FILEPATH)
        # Delete csv file in local machine
        print(f"Deleting {FILEPATH.name}")
        os.remove(FILEPATH)



if __name__ == "__main__":
    pipeline()
