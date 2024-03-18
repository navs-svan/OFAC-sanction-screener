import re
import datetime
import os
import pandas as pd
from sqlalchemy import URL, Table, MetaData
from sqlalchemy import create_engine, insert
from rapidfuzz import fuzz
from fastapi import FastAPI

screening_app = FastAPI()


# Helper functions
def get_table() -> pd.DataFrame:
    DBHOST = os.environ.get("DBHOST")
    DBPORT = os.environ.get("DBPORT")
    DBUSER = os.environ.get("DBUSER")
    DBNAME = os.environ.get("DBNAME")
    DBPASS = os.environ.get("DBPASS")

    # Create sqlalchemy connection url
    url = URL.create(
        drivername="postgresql+psycopg2",
        username=DBUSER,
        password=DBPASS,
        host=DBHOST,
        port=DBPORT,
        database=DBNAME,
    )
    engine = create_engine(url=url)

    with engine.connect() as conn:
        df = pd.read_sql_query("SELECT * FROM consolidated_ofac;", con=conn)

    return df


def clean_name(name: str) -> str:

    name = re.sub("[/-]", " ", name)  # replace / and - with space
    name = re.sub("[^A-Z0-9\\s]", "", name.upper())  # extract only alpha numeric
    name = re.sub("\\s+", " ", name).strip()  # remove consecutive spaces

    return name


def get_fuzz(str1: str, str2: str, is_sorted=True) -> float:

    if is_sorted:
        str1 = " ".join(sorted(str1.split(" ")))
        str2 = " ".join(sorted(str2.split(" ")))

    ratio = fuzz.ratio(s1=str1, s2=str2)

    return round(ratio / 100, 3)


def log_request(): ...


@screening_app.get("/")
async def root():
    return {"status": "success", "response": "Welcome to OFAC Screener"}


@screening_app.get("/screen")
async def screen(name: str, threshold: float = 0.75):
    is_sorted = True

    df = get_table()

    df["jaro-winkler"] = df["cleaned_name"].apply(
        func=get_fuzz, args=(clean_name(name), is_sorted)
    )

    df_filtered = (
        df[df["jaro-winkler"] >= threshold].fillna("-").to_dict(orient="records")
    )

    response = {"status": "success", "BODY": df_filtered}
    return response
