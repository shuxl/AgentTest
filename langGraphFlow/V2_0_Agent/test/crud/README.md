# CRUD 操作测试

本目录包含CRUD基类的单元测试。

## 测试文件

- `test_crud_operations.py` - CRUD 基类单元测试

## 测试范围

- CRUD create 操作测试
- CRUD get 操作测试（按ID和过滤条件）
- CRUD get_multi 操作测试（分页、排序、过滤）
- CRUD update 操作测试
- CRUD delete 操作测试
- CRUD count 操作测试
- QueryBuilder 查询构建器测试

## 运行方式

```bash
cd langGraphFlow/V2_0_Agent
conda run -n py_311_rag python test/crud/test_crud_operations.py
```

## 测试特点

- 验证 CRUD 基类的所有功能
- 测试查询构建器的灵活性
- 验证错误处理和事务管理
- 单元测试，需要数据库连接

## 前置条件

- 已安装 SQLAlchemy 2.0+ 和 greenlet
- 数据库连接配置正确（Config.DB_URI）
- 数据库服务正在运行

## 相关文档

- `utils/db/crud.py` - CRUD 基类实现
- `utils/db/base.py` - Base 类和数据库引擎管理
- `docs/数据库使用指南.md` - 数据库使用文档

