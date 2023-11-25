from typing import List, Optional

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# SQLAlchemy에서 데이터베이스 메타데이터의 가장 일반적인 기본 개체는 Metadata, Table 및 Column로 알려져 있습니다.

# ORM 사용자는 두 가지 관점에서 이러한 객체에 익숙해지는 것이 가장 좋습니다.
# 여기서 설명하는 Table 객체는 ORM을 사용할 때 보다 간접적인(그리고 완전히 파이썬으로 타입이 지정된) 방식으로 선언되지만,
# 여전히 ORM의 구성 내에 Table 객체가 존재합니다.


## 1. Setting up MetaData with Table objects

# 관계형 데이터베이스로 작업할 때 쿼리하는 데이터베이스의 기본 데이터 보유 구조를 테이블이라고 합니다.
# SQLAlchemy에서 데이터베이스 "테이블"은 궁극적으로 Table이라는 유사한 이름의 Python 객체로 표현됩니다.

# 어떤 접근 방식을 사용하든 항상 Metadata 객체라고 하는 컬렉션으로 시작합니다.
# 여기에 Table 객체들을 배치합니다.
# 이 객체는 기본적으로 문자열 이름으로 키가 지정된 일련의 테이블 객체를 저장하는 Python 사전을 둘러싼 파사드입니다.
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

# 서로 연관된 Table 객체 그룹의 경우, 실제로는 단일 메타데이터 컬렉션 내에 설정하는 것이
# 선언하는 관점뿐만 아니라 DDL(즉, CREATE 및 DROP) 문이 올바른 순서로 실행되는 관점에서도 훨씬 더 간단합니다.

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

## 2. Using ORM Declarative Forms to Define Table Metadata

## 2.1. Establishing a Declarative Base


# ORM을 사용하는 경우 메타데이터 컬렉션(metadata)은 계속 존재합니다.
# 메타데이터 컬렉션 자체는 일반적으로 Declarative Base라고 하는 ORM 전용 구조와 연결됩니다.
# Base에는 registry, metadata, type_annotation_map을 속성으로 추가하여 설정할 수 있다.
class Base(DeclarativeBase):
    pass


# Declarative Base는 외부에서 메타데이터를 제공하지 않았다고 가정할 때 자동으로 생성되는 메타데이터 컬렉션을 의미합니다.
print(Base.metadata)

# Declarative Base은 또한 레지스트리라는 컬렉션을 의미하며, 이 컬렉션은 SQLAlchemy ORM의 중앙 "매퍼 구성" 단위입니다.
print(Base.registry)

## 2.2. Declaring Mapped Classes


# 아래의 두 클래스인 User 및 Address는 이제 ORM Mapped Classes라고 불립니다.
class User(Base):
    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[Optional[str]]
    addresses: Mapped[List["Address"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"


class Address(Base):
    __tablename__ = "address"
    id: Mapped[int] = mapped_column(primary_key=True)
    email_address: Mapped[str]
    user_id = mapped_column(ForeignKey("user_account.id"))
    user: Mapped[User] = relationship(back_populates="addresses")

    def __repr__(self) -> str:
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"


# 각 클래스는 선언적 매핑 프로세스의 일부로 생성된 Table 객체를 참조하며,
# 이 객체의 이름은 DeclarativeBase.__tablename__ 속성에 문자열을 할당하여 지정합니다.
print(Address.__tablename__)

# 클래스가 생성되면 이 생성된 테이블은 DeclarativeBase.__table__ 속성에서 사용할 수 있습니다.
print(Address.__table__)

# 단순한 데이터 유형이 있고 다른 옵션이 없는 열의 경우,
# int 및 str과 같은 간단한 Python 유형을 사용하여 정수 및 문자열을 의미하는 Mapped type annotation만 표시할 수 있습니다.
# 즉, mapped_column을 표시하지 않아도 됩니다. Declarative가 자동으로 빈 mapped_column()을 생성합니다.

# 명시적 타이핑 어노테이션(Mapped)의 사용은 완전히 선택 사항입니다. 어노테이션 없이 mapped_column()을 사용할 수도 있습니다.

# 기본 키워드 값을 가진 인자뿐만 아니라 위치 인자를 제공하는
# 모든 기능을 갖춘 __init__() 메서드를 자동으로 생성하려면
# Declarative Dataclass Mapping의 데이터 클래스 기능을 사용할 수 있습니다. ex. MappedAsDataclass
# _declarative_constructor
sandy = User(name="sandy", fullname="Sandy Cheeks")


## 2.3 Emitting DDL to the database from an ORM mapping

# ORM 매핑된 클래스는 메타데이터 컬렉션에 포함된 테이블 객체를 참조하므로,
# 선언적 기반이 주어졌을 때 DDL을 내보낼 때는 앞서 데이터베이스에 DDL 내보내기에서 설명한 것과 동일한 프로세스를 사용합니다.
Base.metadata.create_all(engine)


## 3. Table Reflection
# 이 섹션은 테이블 반영과 관련된 주제 또는 기존 데이터베이스에서 테이블 객체를 자동으로 생성하는 방법에 대한 간략한 소개입니다.

# 이전 섹션에서는 파이썬으로 테이블 객체를 선언한 다음 해당 스키마를 생성하기 위해 데이터베이스에 DDL을 내보내는 옵션을 사용했지만,
# Reflection 프로세스에서는 이 두 단계를 역순으로 수행하여 기존 데이터베이스에서 시작하여
# 해당 데이터베이스 내의 스키마를 나타내는 파이썬 내 데이터 구조를 생성합니다.

# Table 객체를 생성한 다음 개별 Column 및 Constraint 객체를 나타내는 대신 Table.autoload_with 파라미터를 사용하여 대상 엔진에 전달합니다:

reflected_address_table = Table("address", Base.metadata, autoload_with=engine)

# 프로세스가 끝나면 table 객체에는 이제 테이블에 있는 열 객체에 대한 정보가 포함되며,
# 이 객체는 명시적으로 선언한 테이블과 정확히 동일한 방식으로 사용할 수 있습니다:
print(reflected_address_table)
