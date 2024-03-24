from sqlalchemy import Column, Integer
from sqlalchemy.dialects.postgresql import INET, VARCHAR, NUMERIC, BOOLEAN, TIMESTAMP
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Log(Base):
    """
    Class representing the Postgre table where logs will be stored

    Attributes:
        __tablename__: name of table
        log_id: SERIAL column for the primary key/id 
        client_ip: INET column for the client ip of the requester 
        name_query: VARCHAR(250) column for the name parameter of the request 
        threshold_query: NUMERIC column for the threshold parameter of the request
        response: BOOLEAN columns for the response type 
        timestamp: TIMESTAMP column for the timestamp when the request was made 
    """

    __tablename__ = "request_logs"

    log_id = Column("id", Integer, primary_key=True)
    client_ip = Column("client_ip", INET)
    name_query = Column("name", VARCHAR(350))
    threshold_query = Column("threshold", NUMERIC)
    response = Column("reponse_result", BOOLEAN)
    timestamp = Column("timestamp", TIMESTAMP)

    def __init__(self, client_ip, name_query, threshold_query, response, timestamp):
        self.client_ip = client_ip
        self.name_query = name_query
        self.threshold_query = threshold_query
        self.response = response
        self.timestamp = timestamp

    def __repr__(self):
        return f"Request: {self.name_query} - {self.threshold_query_query}\nResponse: {self.response}\nTime:{self.timestamp}"
