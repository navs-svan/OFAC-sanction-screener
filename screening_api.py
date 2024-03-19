import re
from datetime import datetime
import os
import pandas as pd
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker
from rapidfuzz import fuzz
from fastapi import FastAPI, Request
from postgre_logs import Base, Log
from typing import Any

# GLOBAL VARIABLES
DBHOST = os.environ.get("DBHOST")
DBPORT = os.environ.get("DBPORT")
DBUSER = os.environ.get("DBUSER")
DBNAME = os.environ.get("DBNAME")
DBPASS = os.environ.get("DBPASS")

ENGINE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=DBUSER,
    password=DBPASS,
    host=DBHOST,
    port=DBPORT,
    database=DBNAME,
)
ENGINE = create_engine(url=ENGINE_URL)


# HELPER FUNCTIONS
def get_table() -> pd.DataFrame:
    """
    Summary: Queries the consolidated_ofac table from Postgres

    Returns:
        pd.Dataframe: pandas Dataframe containing all records from
            consolidated table
    """
    with ENGINE.connect() as conn:
        df = pd.read_sql_query("SELECT * FROM consolidated_ofac;", con=conn)

    return df


def clean_name(name: str) -> str:
    """
    Summary: cleans the "name" parameter of the query. Transformations
        are the following:
            1) replace "/" and "-" with space

            2) removes all non-alphanumeric character

            3) removes consecutive and trailing spaces

            4) capitalizes the name

    Arguments:
        name (str): the string to be cleaned

    Returns
        string: cleaned string

    """
    name = re.sub("[/-]", " ", name)  # replace / and - with space
    name = re.sub("[^A-Z0-9\\s]", "", name.upper())  # extract only alpha numeric
    name = re.sub("\\s+", " ", name).strip()  # remove consecutive spaces

    return name


def get_fuzz(str1: str, str2: str, is_sorted: bool = True) -> float:
    """
    Summary: Calculates the Levenshtein Distance between two strings

    Arguments:
        str1 (str): the first string
        str2 (str): the second string
        is_sorted (bool, optional): optional parameter for sorting a string
            alphabetically. Defaults to True

    Returns:
        float: normalized Levenshtein Distance. Value ranges from 0 to 1.
    """
    if is_sorted:
        str1 = " ".join(sorted(str1.split(" ")))
        str2 = " ".join(sorted(str2.split(" ")))

    ratio = fuzz.ratio(s1=str1, s2=str2)

    return round(ratio / 100, 3)


def log_request(
    client_ip: str,
    name_query: str,
    threshold_query: float,
    response_bool: bool,
    timestamp: datetime,
) -> None:
    """
    Summary: Logs API requests to a Postgres Database

    Arguments:
        client_ip (str): client ip address taken from the request
        name_query (str): name parameter of the query
        threshold_query (float): threshold parameter of the query
        response_bool (bool): value is True if the the are potential matches
            and False if otherwise
        timestamp (datetime): timestamp when the request was made
    """
    Base.metadata.create_all(bind=ENGINE)
    Session = sessionmaker(bind=ENGINE)

    session = Session()
    log = Log(
        client_ip=client_ip,
        name_query=name_query,
        threshold_query=threshold_query,
        response=response_bool,
        timestamp=timestamp,
    )
    session.add(log)
    session.commit()


# FAST API CODE

screening_app = FastAPI()


@screening_app.get("/")
async def root():
    return {"status": "success", "response": "Welcome to OFAC Screener"}


@screening_app.get("/screen")
async def screen(
    name: str,
    request: Request,
    threshold: float = 0.75,
) -> dict[str, Any]:
    """
    Summary: "/screen" endpoint of the API

    Arguments:
        name (str): the name to be searched against the database
        request (Request): class representing the incoming request
        threshold (float, optional): Threshold for similarity between 
            name argument and names in the table. Defaults to 0.75

    Returns:
        dict[str, Any]: dictionary containing request status, client_ip, 
            and potential matches from the database
    """
    client_host = request.client.host
    print(type(client_host))
    is_sorted = False

    df = get_table()

    df["fuzz"] = df["cleaned_name"].apply(
        func=get_fuzz, args=(clean_name(name), is_sorted)
    )

    df_filtered = df[df["fuzz"] >= threshold].fillna("-").to_dict(orient="records")
    if len(df_filtered) > 0:
        status = "potential matches found"
        response_bool = 1
    else:
        status = "no matches found"
        response_bool = 0

    timestamp = datetime.now()
    log_request(
        client_ip=client_host,
        name_query=name,
        threshold_query=threshold,
        response_bool=response_bool,
        timestamp=timestamp,
    )
    response = {"status": status, "client_host": client_host, "entities": df_filtered}
    return response
