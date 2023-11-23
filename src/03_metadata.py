from sqlalchemy import ForeignKey
from sqlalchemy import MetaData
from sqlalchemy import Table, Column, Integer, String
from sqlalchemy import create_engine


## 1. Setting up MetaData with Table objects

metadata_obj = MetaData()

user_table = Table(
    "user_account",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String(30)),
    Column("fullname", String),
)

# 전체 애플리케이션에 대해 단일 메타데이터 객체를 갖는 것이 가장 일반적인 경우로,
# 애플리케이션의 한 위치에 모듈 수준 변수로 표시되며, 종종 "models" 또는 "dbschema" 유형의 패키지로 표시됩니다

## 1.1. Components of Table

print(user_table.c.name)

print(user_table.c.keys())

## 1.2. Declaring Simple Constraints

print(user_table.primary_key)


address_table = Table(
    "address",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("user_id", ForeignKey("user_account.id"), nullable=False),
    Column("email_address", String, nullable=False),
)


## 1.3. Emitting DDL to the Database

engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)

metadata_obj.create_all(engine)

# 스키마 요소를 삭제하기 위해 CREATE를 삭제할 때와 역순으로 DROP 문을 출력하는 MetaData.drop_all() 메서드도 있습니다.
metadata_obj.drop_all(engine)

# Tip: 테스트, 소규모 어플리케이션, 수명이 짧은 DB에 메타 데이터의 생성/삭제 기능이 유용하지만
# 장기적으로 애플리케이션 스키마 관리를 위해 SQLAlchemy를 기반으로 하는 Alembic과 같은 스키마 관리 도구를 추천함.

# TODO: https://docs.sqlalchemy.org/en/20/tutorial/metadata.html#using-orm-declarative-forms-to-define-table-metadata
