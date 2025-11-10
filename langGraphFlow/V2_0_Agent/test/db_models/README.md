# 数据模型测试

本目录包含SQLAlchemy数据模型和Alembic配置的验证测试。

## 测试文件

- `test_db_models.py` - 数据模型和 Alembic 配置验证测试

## 测试范围

- SQLAlchemy 数据模型导入和定义验证
- 数据库引擎创建和连接测试
- Alembic 迁移配置验证

## 测试用例

1. **测试1**: 验证数据模型导入
   - 检查 `BloodPressureRecord` 和 `Appointment` 模型是否正确导入
   - 验证表名定义是否正确
   - 检查 `Base.metadata` 是否包含所有表

2. **测试2**: 验证数据库引擎创建
   - 测试 SQLAlchemy 异步引擎创建
   - 测试数据库连接是否正常
   - 验证引擎关闭功能

3. **测试3**: 验证 Alembic 配置
   - 检查 `alembic/` 目录结构是否存在
   - 检查 `alembic.ini` 配置文件是否存在
   - 检查迁移脚本是否存在

## 运行方式

```bash
cd langGraphFlow/V2_0_Agent
conda run -n py_311_rag python test/db_models/test_db_models.py
```

## 测试特点

- 验证 SQLAlchemy ORM 模型定义是否正确
- 验证数据库引擎配置是否正确
- 验证 Alembic 迁移工具配置是否正确
- 为数据库迁移和 CRUD 重构做准备

## 前置条件

- 已安装 SQLAlchemy 2.0+ 和 greenlet
- 已安装 Alembic
- 数据库连接配置正确（Config.DB_URI）
- 数据库服务正在运行

## 相关文档

- `utils/db/models/` - SQLAlchemy 数据模型定义
- `utils/db/base.py` - Base 类和数据库引擎管理
- `alembic/` - Alembic 迁移配置
- `docs/数据库使用指南.md` - 数据库使用文档

