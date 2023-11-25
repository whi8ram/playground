from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    bindparam,
    create_engine,
    insert,
    select,
)

metadata_obj = MetaData()

user_table = Table(
    "user_account",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String(30)),
    Column("fullname", String),
)

address_table = Table(
    "address",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("user_id", ForeignKey("user_account.id"), nullable=False),
    Column("email_address", String, nullable=False),
)

## 1. Using INSERT Statement

## 1.1. The insert() SQL Expression Construct

# 대상 테이블과 VALUES 절을 한 번에 보여주는 간단한 삽입 예제입니다:
stmt = insert(user_table).values(name="spongebob", fullname="Spongebob Squarepants")

# 대부분의 SQL 표현식은 생성되는 결과물의 일반적인 형태를 확인하기 위한 수단으로 문자열화할 수 있습니다:
print(stmt)

# 문자열화된 형식은 문에 대한 데이터베이스별 문자열 SQL 표현을 포함하는 객체의 컴파일된 형식을 생성하여 만들어지며,
# 이 객체는 ClauseElement.compile() 메서드를 사용하여 직접 획득할 수 있습니다:
compiled = stmt.compile()

print(compiled.params)


## 1.2. Executing the Statement

engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)
metadata_obj.create_all(engine)

# 이 문을 호출하면 user_table에 행을 INSERT할 수 있습니다. INSERT SQL과 번들 매개변수는 SQL 로깅에서 확인할 수 있습니다:
with engine.connect() as conn:
    result = conn.execute(stmt)
    conn.commit()

# 위의 간단한 형식에서 INSERT 문은 행을 반환하지 않으며,
# 단 하나의 행만 삽입되는 경우 일반적으로 해당 행의 INSERT 중에 생성된 열 수준의 기본값
# (가장 일반적으로 정수 기본 키 값)에 대한 정보를 반환하는 기능을 포함합니다.

print(result.inserted_primary_key)


# 1.3. INSERT usually generates the “values” clause automatically

# 실제로 Insert.values()를 사용하지 않고 "빈" 문만 출력하면 테이블의 모든 열에 대해 INSERT가 생성됩니다:
print(insert(user_table))

# 이것은 실제로 명시적인 VALUES 절을 입력하지 않고도 행을 삽입하는 데 Insert가 사용되는 일반적인 방법입니다.
# 아래 예는 매개변수 목록과 함께 두 개의 열로 구성된 INSERT 문이 한 번에 실행되는 것을 보여줍니다:
with engine.connect() as conn:
    result = conn.execute(
        insert(user_table),
        [
            {"name": "sandy", "fullname": "Sandy Cheeks"},
            {"name": "patrick", "fullname": "Patrick Star"},
        ],
    )
    conn.commit()

# 이것은 사용자 테이블 연산에서 기본 키 식별자를 애플리케이션으로 가져오지 않고도 관련 행을 추가할 수 있습니다.
# 보통 이와 같은 작업을 대신 처리해주는 ORM을 사용합니다.
scalar_subq = (
    select(user_table.c.id)
    .where(user_table.c.name == bindparam("username"))
    .scalar_subquery()
)

with engine.connect() as conn:
    result = conn.execute(
        insert(address_table).values(user_id=scalar_subq),
        [
            {
                "username": "spongebob",
                "email_address": "spongebob@sqlalchemy.org",
            },
            {"username": "sandy", "email_address": "sandy@sqlalchemy.org"},
            {"username": "sandy", "email_address": "sandy@squirrelpower.org"},
        ],
    )
    conn.commit()

# 명시적 값을 전혀 포함하지 않고 테이블의 "기본값"만 삽입하는 진정한 "빈" INSERT는 인수가 없는 Insert.values()를 지정하면 생성됩니다.
print(insert(user_table).values().compile(engine))


## 1.4. INSERT…RETURNING

# 지원되는 DB에 대해서 RETURNING 절은 마지막으로 삽입된 기본 키 값과 서버 기본값을 검색하기 위해 자동으로 사용됩니다.
# 기본값이 설정된 행에 대한 값 없이 Insert할 때 어플리케이션에서는 기본값을 모르기 때문.
insert_stmt = insert(address_table).returning(
    address_table.c.id, address_table.c.email_address
)
print(insert_stmt)

# 또한 INSERT...FROM SELECT에 명시된 예제를 기반으로 하는 아래 예제에서와 같이 Insert.from_select()와 결합할 수도 있습니다:
select_stmt = select(user_table.c.id, user_table.c.name + "@aol.com")
insert_stmt = insert(address_table).from_select(
    ["user_id", "email_address"], select_stmt
)
print(insert_stmt.returning(address_table.c.id, address_table.c.email_address))


## 1.5. INSERT…FROM SELECT

# Insert의 덜 사용되는 기능이지만, 여기서는 완전성을 위해 Insert 구문은 Insert.from_select() 메서드를 사용하여
# SELECT에서 직접 행을 가져오는 INSERT를 작성할 수 있습니다.
select_stmt = select(user_table.c.id, user_table.c.name + "@aol.com")
insert_stmt = insert(address_table).from_select(
    ["user_id", "email_address"], select_stmt
)
print(insert_stmt)
