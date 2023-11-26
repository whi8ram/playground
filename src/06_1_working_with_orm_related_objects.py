from typing import Optional

from sqlalchemy import ForeignKey, String, create_engine, select
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    contains_eager,
    joinedload,
    mapped_column,
    relationship,
    selectinload,
)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[Optional[str]]
    addresses: Mapped[list["Address"]] = relationship(back_populates="user")

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


## 1.1 Persisting and Loading Relationships
u1 = User(name="pkrabs", fullname="Pearl Krabs")

# 이 객체는 변경 사항을 추적하고 이에 응답할 수 있는 기능이 있는 Python List의 SQLAlchemy 전용 버전입니다.
print(u1.addresses)
print(type(u1.addresses))

# 이 컬렉션은 그 안에 지속될 수 있는 유일한 유형의 파이썬 객체인 Address 클래스에 한정됩니다.
# list.append() 메서드를 사용하여 Address 객체를 추가할 수 있습니다:
a1 = Address(email_address="pearl.krabs@gmail.com")
u1.addresses.append(a1)

# 이 시점에서 예상대로 u1.addresses 컬렉션에 새 주소 개체가 포함됩니다:
print(u1.addresses)

# User.addresses 관계가 Address.user 관계와 동기화되어
# Address 객체에서 다시 "상위" User 객체로 이동할 수 있게 된 것입니다:
print(a1.user)

# Address 생성자에 직접 user 객체를 넣어줄 수도 있음.
a2 = Address(email_address="pearl@aol.com", user=u1)
print(u1.addresses)

# equivalent effect as a2 = Address(user=u1)
a2.user = u1


## 1.2. Cascading Objects into the Session
engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)

Base.metadata.create_all(engine)

session = Session(engine)

# 아직 진행 중인 세션을 사용하며, 리드 User 객체에 Session.add() 메서드를 적용하면
# 관련 Address 객체도 동일한 세션에 추가된다는 점에 유의하세요:
session.add(u1)
print(u1 in session)
print(a1 in session)
print(a2 in session)

# User가 실제 데이터베이스 행에 연결되지 않았으므로 객체에 PK 값이 없다.
# PK 없으니 Address 객체에 FK 값도 없다.
print(u1.id)
print(a1.user_id)

# ORM의 작업 단위 프로세스를 사용하면 트랜잭션의 모든 단계를 올바르게 출력할 수 있다.
# 예를 들어, FK의 타깃 레코드를 먼저 삽입하고 FK가 있는 레코드를 삽입한다.
session.commit()


## 1.3. Loading Relationships

# 마지막 단계에서는 트랜잭션에 대한 커밋을 내보내는 Session.commit()을 호출한 다음,
# 세션 커밋에 따라 모든 오브젝트가 만료되어 다음 트랜잭션을 위해 새로 고쳐지도록 Session.commit.expire_on_commit을 호출했습니다.

# 다음에 이러한 개체의 속성에 액세스하면 u1 개체에 대해 새로 생성된 기본 키를 볼 때와 같이
# 행의 기본 속성에 대해 SELECT가 방출되는 것을 볼 수 있습니다:
print(u1.id)

print(u1.addresses)

# 컬렉션 또는 속성이 채워지면 해당 컬렉션 또는 속성이 만료될 때까지 더 이상 SQL이 출력되지 않습니다.
print(u1.addresses)

# u1.addresses 컬렉션이 새로 고쳐졌으므로 ID 맵에 따르면
# 이들은 실제로 이미 처리한 a1 및 a2 객체와 동일한 주소 인스턴스이므로
# 이 특정 객체 그래프에서 모든 속성을 로드하는 것이 완료됩니다:
print(a1)
print(a2)


## 2. Using Relationships in Queries


## 2.1. Using Relationships to Join

# relationship()에 해당하는 클래스 바운드 속성을 Select.join()에 단일 인수로 전달할 수 있으며,
# 이 속성은 조인의 오른쪽과 ON 절을 한 번에 모두 나타내는 역할을 합니다:
print(select(Address.email_address).select_from(User).join(User.addresses))

# 매핑에 ORM relationship()이 있는 경우 Select.join() 또는 Select.join_from()은
# relationship()이 있는 속성을 지정하지 않으면 ON 절을 추론하는 데 사용되지 않습니다.
print(select(Address.email_address).join_from(User, Address))


## 2.2. Loader Strategies

# 무엇보다도 ORM 지연 로딩을 효과적으로 사용하기 위한 첫 번째 단계는 애플리케이션을 테스트하고
# SQL 에코를 켜고 방출되는 SQL을 관찰하는 것입니다.
# 훨씬 더 효율적으로 하나로 통합할 수 있는 것처럼 보이는 중복된 SELECT 문이 많은 경우,
# 세션에서 분리된 객체에 대해 부적절하게 로드가 발생하는 경우 로더 전략 사용을 검토해야 할 때입니다.

# 로더 전략은 Select.options() 메서드를 사용하여 SELECT 문과 연결할 수 있는 객체로 표시됩니다
for user_obj in session.execute(
    select(User).options(selectinload(User.addresses))
).scalars():
    user_obj.addresses  # access addresses collection already loaded


# relationship.lazy 옵션을 사용하여 relationship()의 기본값으로 구성할 수도 있습니다:
# class User(Base):
#     __tablename__ = "user_account"

#     addresses: Mapped[list["Address"]] = relationship(
#         back_populates="user", lazy="selectin"
#     )


# 각 로더 전략 객체는 나중에 세션이 다양한 어트리뷰트를 로드하거나 액세스할 때
# 어떻게 동작할지 결정할 때 사용할 문에 몇 가지 정보를 추가합니다.

## 2.3. Selectin Load

# 최신 SQLAlchemy에서 가장 유용한 로더는 selectinload() 로더 옵션입니다.
# selectinload()는 단일 쿼리를 사용하여 전체 개체 시리즈에 대한 특정 컬렉션을 미리 로드하도록 합니다
stmt = select(User).options(selectinload(User.addresses)).order_by(User.id)
for row in session.execute(stmt):
    print(
        f"{row.User.name}  ({', '.join(a.email_address for a in row.User.addresses)})"
    )

## 2.4. Joined Load

# joinedload() 에지 로드 전략은 SQLAlchemy에서 가장 오래된 에지 로드 전략으로,
# 데이터베이스에 전달되는 SELECT 문을 JOIN(옵션에 따라 외부 조인 또는 내부 조인일 수 있음)으로 보강한
# 다음 관련 개체를 로드할 수 있습니다.
# JOINLOAD() 전략은 어떤 경우에도 가져올 기본 엔터티 행에 추가 열만 추가하면 되므로 관련 다대일 객체를 로드하는 데 가장 적합합니다.
stmt = (
    select(Address)
    .options(joinedload(Address.user, innerjoin=True))
    .order_by(Address.id)
)
for row in session.execute(stmt):
    print(f"{row.Address.email_address} {row.Address.user.name}")


## 2.5. Explicit Join + Eager load

# Select.join()과 같은 메서드를 사용하여 사용자 계정 테이블에 조인하는 동안 Address 행을 로드하여 조인을 렌더링하는 경우,
# 해당 조인을 활용하여 반환된 각 Address 객체에 대해 Address.user 특성의 내용을 eagerly load할 수도 있습니다
stmt = (
    select(Address)
    .join(Address.user)
    .where(User.name == "pkrabs")
    .options(contains_eager(Address.user))
    .order_by(Address.id)
)
for row in session.execute(stmt):
    print(f"{row.Address.email_address} {row.Address.user.name}")


# user_account.name에 있는 행을 필터링하고 user_account의 행을 반환된 행의 Address.user 속성으로 로드했습니다.
# joinedload()를 별도로 적용했다면 불필요하게 두 번 조인하는 SQL 쿼리가 생성되었을 것입니다:
stmt = (
    select(Address)
    .join(Address.user)
    .where(User.name == "pkrabs")
    .options(joinedload(Address.user))
    .order_by(Address.id)
)
print(stmt)  # SELECT has a JOIN and LEFT OUTER JOIN unnecessarily
