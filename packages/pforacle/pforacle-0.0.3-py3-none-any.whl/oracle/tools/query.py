import oracledb
from promptflow import tool
from promptflow.connections import CustomConnection


@tool
def run_query(connection: CustomConnection, query: str, params: dict[str, any]) -> list:
    # check custom connection for Oracle configuration
    assert connection.configs["user"] != None, "Oracle user is not set"
    assert connection.secrets["password"] != None, "Oracle password is not set"
    assert connection.configs["dsn"] != None, "Oracle dsn is not set"

    # establish connection
    con = oracledb.connect(user=connection.configs["user"],
                           password=connection.secrets["password"],
                           dsn=connection.configs["dsn"])

    # create cursor
    with con.cursor() as cur:
        # execute parameterized query
        # query would be SELECT * FROM table WHERE id = :id
        # params would be {'id': 1}
        cur.execute(query, **params)
        cols = [c[0] for c in cur.description]
        result = cur.fetchall()
        items =[dict(zip(cols, row)) for row in result] 
        
    return items
