from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)

## 1. Getting a Connection

# Connection은 데이터베이스에 대한 개방형 리소스를 나타내므로 이 객체의 사용 범위를 항상 특정 컨텍스트로 제한하고 싶으며,
# 이를 위한 가장 좋은 방법은 with 문이라고도 하는 Python 컨텍스트 관리자 형식을 사용하는 것
with engine.connect() as conn:
    result = conn.execute(text("select 'hello world'"))
    print(result.all())

## 2. Committing Changes

# "commit as you go" 스타일
with engine.connect() as conn:
    conn.execute(text("CREATE TABLE some_table (x int, y int)"))
    conn.execute(
        text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
        [{"x": 1, "y": 1}, {"x": 2, "y": 4}],
    )
    conn.commit()

# "begin once" 스타일
with engine.begin() as conn:
    conn.execute(
        text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
        [{"x": 6, "y": 8}, {"x": 9, "y": 10}],
    )

## 3. Basics of Statement Execution

## 3.1. Fetching Rows
with engine.connect() as conn:
    result = conn.execute(text("SELECT x, y FROM some_table"))
    for row in result:
        print(f"x: {row.x}  y: {row.y}")

## 3.2. Sending Parameters
with engine.connect() as conn:
    result = conn.execute(text("SELECT x, y FROM some_table WHERE y > :y"), {"y": 2})
    for row in result:
        print(f"x: {row.x}  y: {row.y}")

## 3.3. Sending Multiple Parameters

# executemany 스타일:
with engine.connect() as conn:
    conn.execute(
        text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
        [{"x": 11, "y": 12}, {"x": 13, "y": 14}],
    )
    conn.commit()

# "execute"와 "executemany"의 주요 동작 차이점은 후자는 문에 RETURNING 절이 포함되어 있더라도 결과 행의 반환을 지원하지 않는다는 것

## 4. Executing with an ORM Session

# ORM을 사용할 때 기본적인 트랜잭션/데이터베이스 대화형 객체를 Session이라고 합니다.
# 최신 SQLAlchemy에서 이 객체는 Connection과 매우 유사한 방식으로 사용되며,
# 실제로 Session이 사용될 때 내부적으로 SQL을 방출하는 데 사용하는 Connection을 참조합니다.

stmt = text("SELECT x, y FROM some_table WHERE y > :y ORDER BY x, y")
with Session(engine) as session:
    result = session.execute(stmt, {"y": 6})
    for row in result:
        print(f"x: {row.x}  y: {row.y}")

# Commit as you go 스타일 사용 가능
with Session(engine) as session:
    result = session.execute(
        text("UPDATE some_table SET y=:y WHERE x=:x"),
        [{"x": 9, "y": 11}, {"x": 13, "y": 15}],
    )
    session.commit()
