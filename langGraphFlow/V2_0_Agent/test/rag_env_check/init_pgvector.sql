-- init_pgvector.sql
-- 在doctor_agent_db数据库中初始化pgvector扩展
-- 
-- 使用方法：
-- psql -h localhost -p 5433 -U postgres -d doctor_agent_db -f init_pgvector.sql
-- 或
-- docker exec -it <postgres_container_name> psql -U postgres -d doctor_agent_db -f init_pgvector.sql

-- 启用pgvector扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 验证扩展版本
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';

-- 显示扩展信息
\dx vector

-- 测试创建包含vector类型的表（可选）
-- CREATE TABLE test_vector_table (
--     id SERIAL PRIMARY KEY,
--     content TEXT,
--     embedding vector(768)
-- );

-- 测试插入向量数据（可选）
-- INSERT INTO test_vector_table (content, embedding) 
-- VALUES ('test', '[0.1,0.2,0.3]'::vector(768));

-- 测试查询（可选）
-- SELECT * FROM test_vector_table;

-- 清理测试表（可选）
-- DROP TABLE IF EXISTS test_vector_table;

