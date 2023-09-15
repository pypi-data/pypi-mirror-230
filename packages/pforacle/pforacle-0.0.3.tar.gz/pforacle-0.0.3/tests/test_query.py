import os
from promptflow.connections import CustomConnection
from oracle.tools.query import run_query

def test_run_single_query():
    con = CustomConnection(
        configs = {
            "user": "system",
            "dsn": "localhost/xe"
        },
        secrets = {
            "password": "abcd1234",
        }
    )
    result = run_query(con, query="SELECT * FROM SYS.CUSTOMERS WHERE CUSTOMER_ID = :id", 
                       params={ "id": 6 })
    
    assert len(result) == 1

def test_run_multiple_query():
    con = CustomConnection(
        configs ={
            "user": "system",
            "dsn": "localhost/xe"
        },
        secrets = {
            "password": "abcd1234",
        }
    )
    result = run_query(con, query="SELECT * FROM SYS.CUSTOMERS WHERE MEMBERSHIP = :membership", 
                       params={ "membership": "Base" })
    
    assert len(result) == 6