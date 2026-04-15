"""Test fixtures: 使用内存数据库"""

import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

# 在任何 app import 之前创建测试 engine
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@pytest.fixture(scope="module", autouse=True)
def patch_db():
    """替换 core.db 模块的 engine 和 get_db"""
    import core.db as db_module

    def override_get_db():
        with Session(test_engine) as session:
            yield session

    # 替换 engine 和 get_db
    db_module.engine = test_engine
    db_module.get_db = override_get_db

    # 初始化表
    SQLModel.metadata.create_all(test_engine)

    # 覆盖 app 的依赖
    from main import app
    from api.deps import get_db
    app.dependency_overrides[get_db] = override_get_db

    yield

    app.dependency_overrides.clear()
