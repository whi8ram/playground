from sqlalchemy import create_engine

# 사용자 관점에서 엔진 오브젝트의 유일한 목적은 Connection이라는 데이터베이스에 대한 연결 단위를 제공하는 것
# https://docs.sqlalchemy.org/en/20/tutorial/dbapi_transactions.html#getting-a-connection
# memory와 Echo mode 설정이 초보자에게 좋은 듯!
engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)
