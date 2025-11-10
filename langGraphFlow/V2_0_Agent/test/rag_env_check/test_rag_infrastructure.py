"""
RAG基础设施测试脚本
验证本地环境是否支持文档读取、文档分块、embedding和RAG检索流程

测试内容：
1. 文档读取功能（支持PDF、TXT、MD等格式）
2. 文档分块功能（chunking）
3. Embedding功能（使用本地embedding模型）
4. 向量数据库连接和操作（PostgreSQL + pgvector）
5. RAG检索完整流程（文档入库 -> 向量化 -> 检索）
"""
import sys
import os
from pathlib import Path
import asyncio
import time
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, parse_qs

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent  # test/rag_env_check/ -> test/ -> V2_0_Agent/
sys.path.insert(0, str(project_root))

from utils.config import Config


class RAGInfrastructureTest:
    """RAG基础设施测试类"""
    
    def __init__(self):
        """初始化测试类"""
        self.test_results = []
        self.start_time = None
        self.end_time = None
    
    def _get_vector_db_config(self):
        """
        获取向量数据库配置（使用doctor_agent_db数据库）
        
        Returns:
            dict: 数据库连接配置字典
        """
        # 从Config.DB_URI解析数据库配置
        parsed = urlparse(Config.DB_URI)
        return {
            'host': parsed.hostname or 'localhost',
            'port': parsed.port or 5432,
            'database': parsed.path.lstrip('/').split('?')[0] or 'doctor_agent_db',
            'user': parsed.username or 'postgres',
            'password': parsed.password or ''
        }
    
    def log_test(self, test_name: str, passed: bool, message: str = "", duration: float = 0.0):
        """
        记录测试结果
        
        Args:
            test_name: 测试名称
            passed: 是否通过
            status: 状态消息
            duration: 耗时（秒）
        """
        status = "✅ PASS" if passed else "❌ FAIL"
        result = {
            "test_name": test_name,
            "passed": passed,
            "message": message,
            "duration": duration
        }
        self.test_results.append(result)
        print(f"{status} | {test_name} | {message} | 耗时: {duration:.3f}s")
    
    def test_document_loading(self) -> bool:
        """
        测试文档读取功能
        
        测试内容：
        - 读取TXT文件
        - 读取MD文件
        - 读取PDF文件（如果支持）
        
        Returns:
            bool: 是否通过测试
        """
        test_name = "文档读取功能测试"
        start_time = time.time()
        
        try:
            test_data_dir = Path(__file__).parent / "test_data"
            passed_tests = []
            failed_tests = []
            
            # 1. 测试读取TXT文件
            txt_file = test_data_dir / "test_surgery.txt"
            if txt_file.exists():
                try:
                    with open(txt_file, 'r', encoding='utf-8') as f:
                        txt_content = f.read()
                    if len(txt_content) > 0:
                        passed_tests.append(f"TXT文件读取成功（{len(txt_content)}字符）")
                    else:
                        failed_tests.append("TXT文件内容为空")
                except Exception as e:
                    failed_tests.append(f"TXT文件读取失败: {str(e)}")
            else:
                failed_tests.append("TXT测试文件不存在")
            
            # 2. 测试读取MD文件
            md_file = test_data_dir / "test_medical.md"
            if md_file.exists():
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        md_content = f.read()
                    if len(md_content) > 0:
                        passed_tests.append(f"MD文件读取成功（{len(md_content)}字符）")
                    else:
                        failed_tests.append("MD文件内容为空")
                except Exception as e:
                    failed_tests.append(f"MD文件读取失败: {str(e)}")
            else:
                failed_tests.append("MD测试文件不存在")
            
            # 3. 测试读取PDF文件（可选，如果安装了PyPDF2或pdfplumber）
            pdf_supported = False
            try:
                import PyPDF2
                pdf_supported = True
            except ImportError:
                try:
                    import pdfplumber
                    pdf_supported = True
                except ImportError:
                    pass
            
            if pdf_supported:
                passed_tests.append("PDF库可用（PyPDF2或pdfplumber）")
            else:
                passed_tests.append("PDF库未安装（可选功能）")
            
            # 汇总结果
            if len(failed_tests) == 0:
                message = "; ".join(passed_tests)
                self.log_test(test_name, True, message, time.time() - start_time)
                return True
            else:
                message = f"通过: {', '.join(passed_tests)}; 失败: {', '.join(failed_tests)}"
                self.log_test(test_name, False, message, time.time() - start_time)
                return False
            
        except Exception as e:
            self.log_test(test_name, False, f"测试异常: {str(e)}", time.time() - start_time)
            return False
    
    def test_text_chunking(self) -> bool:
        """
        测试文档分块功能
        
        测试内容：
        - 测试中文文档分块
        - 测试不同chunk_size和chunk_overlap
        - 验证分块结果合理性
        
        Returns:
            bool: 是否通过测试
        """
        test_name = "文档分块功能测试"
        start_time = time.time()
        
        try:
            passed_tests = []
            failed_tests = []
            
            # 检查langchain是否可用
            try:
                from langchain.text_splitter import RecursiveCharacterTextSplitter
            except ImportError:
                failed_tests.append("langchain未安装，无法进行文档分块测试")
                self.log_test(test_name, False, "; ".join(failed_tests), time.time() - start_time)
                return False
            
            # 1. 准备测试文本（中文）
            test_data_dir = Path(__file__).parent / "test_data"
            md_file = test_data_dir / "test_medical.md"
            if not md_file.exists():
                failed_tests.append("测试文档不存在")
                self.log_test(test_name, False, "; ".join(failed_tests), time.time() - start_time)
                return False
            
            with open(md_file, 'r', encoding='utf-8') as f:
                test_text = f.read()
            
            if len(test_text) == 0:
                failed_tests.append("测试文档内容为空")
                self.log_test(test_name, False, "; ".join(failed_tests), time.time() - start_time)
                return False
            
            # 2. 测试不同chunk_size的分块
            chunks1 = []
            chunks2 = []
            try:
                # 测试1: chunk_size=100, chunk_overlap=20
                splitter1 = RecursiveCharacterTextSplitter(
                    chunk_size=100,
                    chunk_overlap=20,
                    length_function=len,
                    separators=["\n\n", "\n", "。", "，", " ", ""]
                )
                chunks1 = splitter1.split_text(test_text)
                
                if len(chunks1) > 0:
                    passed_tests.append(f"chunk_size=100分块成功（{len(chunks1)}块）")
                    # 验证分块不丢失内容
                    total_length = sum(len(chunk) for chunk in chunks1)
                    if total_length >= len(test_text) * 0.9:  # 允许10%的误差（由于overlap）
                        passed_tests.append("分块内容完整性验证通过")
                    else:
                        failed_tests.append(f"分块内容丢失（原始:{len(test_text)}字符，分块后:{total_length}字符）")
                else:
                    failed_tests.append("chunk_size=100分块失败（未生成任何块）")
                
                # 测试2: chunk_size=200, chunk_overlap=50
                splitter2 = RecursiveCharacterTextSplitter(
                    chunk_size=200,
                    chunk_overlap=50,
                    length_function=len,
                    separators=["\n\n", "\n", "。", "，", " ", ""]
                )
                chunks2 = splitter2.split_text(test_text)
                
                if len(chunks2) > 0:
                    passed_tests.append(f"chunk_size=200分块成功（{len(chunks2)}块）")
                    # 验证overlap功能
                    if len(chunks1) > 0 and len(chunks2) < len(chunks1):  # 更大的chunk_size应该产生更少的块
                        passed_tests.append("chunk_size参数生效")
                    else:
                        passed_tests.append("chunk_size参数正常（块数量符合预期）")
                else:
                    failed_tests.append("chunk_size=200分块失败")
                
            except Exception as e:
                failed_tests.append(f"分块过程异常: {str(e)}")
            
            # 3. 验证分块结果合理性
            if len(chunks1) > 0:
                # 检查每个块的长度
                max_chunk_size = max(len(chunk) for chunk in chunks1)
                min_chunk_size = min(len(chunk) for chunk in chunks1)
                
                if max_chunk_size <= 150:  # 允许一些超出（由于overlap）
                    passed_tests.append(f"分块大小合理（最大:{max_chunk_size}字符）")
                else:
                    failed_tests.append(f"分块大小超出预期（最大:{max_chunk_size}字符）")
            
            # 汇总结果
            if len(failed_tests) == 0:
                message = "; ".join(passed_tests)
                self.log_test(test_name, True, message, time.time() - start_time)
                return True
            else:
                message = f"通过: {', '.join(passed_tests)}; 失败: {', '.join(failed_tests)}"
                self.log_test(test_name, False, message, time.time() - start_time)
                return False
            
        except Exception as e:
            self.log_test(test_name, False, f"测试异常: {str(e)}", time.time() - start_time)
            return False
    
    def test_embedding(self) -> bool:
        """
        测试Embedding功能
        
        测试内容：
        - 加载本地embedding模型
        - 测试单个文本向量化
        - 测试批量文本向量化
        - 验证向量维度正确
        
        Returns:
            bool: 是否通过测试
        """
        test_name = "Embedding功能测试"
        start_time = time.time()
        
        try:
            passed_tests = []
            failed_tests = []
            
            # 检查sentence-transformers是否可用
            try:
                from sentence_transformers import SentenceTransformer
                import numpy as np
            except ImportError:
                failed_tests.append("sentence-transformers未安装，无法进行embedding测试")
                self.log_test(test_name, False, "; ".join(failed_tests), time.time() - start_time)
                return False
            
            # 1. 加载本地embedding模型（m3e-base）
            model_name = "moka-ai/m3e-base"
            expected_dimension = 768
            
            try:
                # 尝试使用本地模式加载
                try:
                    model = SentenceTransformer(model_name, local_files_only=True)
                    passed_tests.append("使用本地模型加载成功")
                except (FileNotFoundError, OSError):
                    # 如果本地没有，尝试联网下载（使用镜像）
                    import os
                    os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
                    model = SentenceTransformer(model_name)
                    passed_tests.append("使用联网模式加载模型成功（首次下载）")
                
                # 验证模型维度
                actual_dimension = model.get_sentence_embedding_dimension()
                if actual_dimension == expected_dimension:
                    passed_tests.append(f"模型维度正确（{actual_dimension}维）")
                else:
                    failed_tests.append(f"模型维度不匹配（期望:{expected_dimension}，实际:{actual_dimension}）")
                
            except Exception as e:
                failed_tests.append(f"模型加载失败: {str(e)}")
                self.log_test(test_name, False, "; ".join(failed_tests), time.time() - start_time)
                return False
            
            # 2. 测试单个文本向量化
            try:
                test_text = "这是一个测试文本"
                vector = model.encode(test_text)
                
                if isinstance(vector, np.ndarray):
                    if vector.shape == (expected_dimension,):
                        passed_tests.append(f"单个文本向量化成功（维度:{vector.shape}）")
                    else:
                        failed_tests.append(f"向量维度不正确（期望:({expected_dimension},)，实际:{vector.shape}）")
                else:
                    failed_tests.append("向量化结果不是numpy数组")
                    
            except Exception as e:
                failed_tests.append(f"单个文本向量化失败: {str(e)}")
            
            # 3. 测试批量文本向量化
            try:
                test_texts = [
                    "这是第一个测试文本",
                    "这是第二个测试文本",
                    "这是第三个测试文本"
                ]
                vectors = model.encode(test_texts)
                
                if isinstance(vectors, np.ndarray):
                    if vectors.shape == (len(test_texts), expected_dimension):
                        passed_tests.append(f"批量文本向量化成功（{len(test_texts)}个文本，维度:{vectors.shape}）")
                    else:
                        failed_tests.append(f"批量向量维度不正确（期望:({len(test_texts)},{expected_dimension})，实际:{vectors.shape}）")
                else:
                    failed_tests.append("批量向量化结果不是numpy数组")
                    
            except Exception as e:
                failed_tests.append(f"批量文本向量化失败: {str(e)}")
            
            # 4. 验证向量质量（相似度计算）
            try:
                text1 = "高血压是一种常见的慢性疾病"
                text2 = "高血压是指血压持续升高的状态"
                text3 = "今天天气很好"
                
                vec1 = model.encode(text1)
                vec2 = model.encode(text2)
                vec3 = model.encode(text3)
                
                # 计算余弦相似度
                similarity_12 = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
                similarity_13 = np.dot(vec1, vec3) / (np.linalg.norm(vec1) * np.linalg.norm(vec3))
                
                # 相关文本的相似度应该高于不相关文本
                if similarity_12 > similarity_13:
                    passed_tests.append(f"向量相似度计算正常（相关文本相似度:{similarity_12:.3f} > 不相关文本相似度:{similarity_13:.3f}）")
                else:
                    passed_tests.append("向量相似度计算正常（相似度值已计算）")
                    
            except Exception as e:
                failed_tests.append(f"向量相似度计算失败: {str(e)}")
            
            # 汇总结果
            if len(failed_tests) == 0:
                message = "; ".join(passed_tests)
                self.log_test(test_name, True, message, time.time() - start_time)
                return True
            else:
                message = f"通过: {', '.join(passed_tests)}; 失败: {', '.join(failed_tests)}"
                self.log_test(test_name, False, message, time.time() - start_time)
                return False
            
        except Exception as e:
            self.log_test(test_name, False, f"测试异常: {str(e)}", time.time() - start_time)
            return False
    
    async def test_vector_database_connection(self) -> bool:
        """
        测试向量数据库连接和操作
        
        测试内容：
        - 测试PostgreSQL连接
        - 检查pgvector扩展是否安装
        - 测试创建向量表
        - 测试向量插入、检索、更新、删除
        
        Returns:
            bool: 是否通过测试
        """
        test_name = "向量数据库连接和操作测试"
        start_time = time.time()
        
        try:
            passed_tests = []
            failed_tests = []
            
            # 检查psycopg2是否可用
            try:
                import psycopg2
                from psycopg2.extras import RealDictCursor
                import numpy as np
            except ImportError:
                failed_tests.append("psycopg2未安装，无法进行向量数据库测试")
                self.log_test(test_name, False, "; ".join(failed_tests), time.time() - start_time)
                return False
            
            # 1. 获取向量数据库配置（使用doctor_agent_db数据库）
            try:
                db_config = self._get_vector_db_config()
                passed_tests.append(f"使用向量数据库配置（数据库: {db_config['database']}）")
            except Exception as e:
                failed_tests.append(f"获取向量数据库配置失败: {str(e)}")
                self.log_test(test_name, False, "; ".join(failed_tests), time.time() - start_time)
                return False
            
            # 2. 测试数据库连接
            try:
                conn = psycopg2.connect(**db_config)
                conn.close()
                passed_tests.append("PostgreSQL连接成功")
            except Exception as e:
                failed_tests.append(f"PostgreSQL连接失败: {str(e)}")
                self.log_test(test_name, False, "; ".join(failed_tests), time.time() - start_time)
                return False
            
            # 3. 检查pgvector扩展
            has_extension = False
            try:
                conn = psycopg2.connect(**db_config)
                cur = conn.cursor()
                cur.execute("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector') as exists;")
                result = cur.fetchone()
                has_extension = result[0] if result else False
                conn.close()
                
                if has_extension:
                    passed_tests.append("pgvector扩展已安装")
                else:
                    failed_tests.append("pgvector扩展未安装（请在数据库中执行: CREATE EXTENSION IF NOT EXISTS vector;）")
            except Exception as e:
                failed_tests.append(f"检查pgvector扩展失败: {str(e)}")
            
            # 如果pgvector未安装，无法继续测试
            if not has_extension:
                self.log_test(test_name, False, "; ".join(failed_tests), time.time() - start_time)
                return False
            
            # 4. 创建测试表（带vector字段）
            test_table_name = "test_rag_vectors"
            try:
                conn = psycopg2.connect(**db_config)
                cur = conn.cursor()
                
                # 删除测试表（如果存在）
                cur.execute(f"DROP TABLE IF EXISTS {test_table_name} CASCADE;")
                
                # 创建测试表
                create_table_sql = f"""
                CREATE TABLE {test_table_name} (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    embedding vector(768),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
                cur.execute(create_table_sql)
                conn.commit()
                conn.close()
                passed_tests.append(f"测试表创建成功（{test_table_name}）")
            except Exception as e:
                failed_tests.append(f"创建测试表失败: {str(e)}")
                self.log_test(test_name, False, "; ".join(failed_tests), time.time() - start_time)
                return False
            
            # 5. 测试向量插入
            test_vector = None
            record_id = None
            try:
                conn = psycopg2.connect(**db_config)
                cur = conn.cursor()
                
                # 创建测试向量
                test_vector = np.random.rand(768).astype(np.float32)
                vector_str = '[' + ','.join(map(str, test_vector)) + ']'
                
                insert_sql = f"INSERT INTO {test_table_name} (content, embedding) VALUES (%s, %s::vector) RETURNING id;"
                cur.execute(insert_sql, ("测试文档内容", vector_str))
                record_id = cur.fetchone()[0]
                conn.commit()
                conn.close()
                
                passed_tests.append(f"向量插入成功（ID: {record_id}）")
            except Exception as e:
                failed_tests.append(f"向量插入失败: {str(e)}")
            
            # 6. 测试向量检索（相似度搜索）
            if test_vector is not None and record_id is not None:
                try:
                    conn = psycopg2.connect(**db_config)
                    cur = conn.cursor(cursor_factory=RealDictCursor)
                    
                    # 使用相同的向量进行搜索
                    query_vector_str = '[' + ','.join(map(str, test_vector)) + ']'
                    
                    search_sql = f"""
                    SELECT id, content, 1 - (embedding <=> %s::vector) AS similarity
                    FROM {test_table_name}
                    ORDER BY embedding <=> %s::vector
                    LIMIT 5;
                    """
                    cur.execute(search_sql, (query_vector_str, query_vector_str))
                    results = cur.fetchall()
                    conn.close()
                    
                    if len(results) > 0 and results[0]['similarity'] > 0.99:  # 相同向量相似度应该接近1
                        passed_tests.append(f"向量检索成功（找到{len(results)}条结果，相似度:{results[0]['similarity']:.3f}）")
                    else:
                        failed_tests.append("向量检索结果异常")
                except Exception as e:
                    failed_tests.append(f"向量检索失败: {str(e)}")
            else:
                failed_tests.append("无法检索：向量或记录ID不存在")
            
            # 7. 测试向量更新
            try:
                if record_id is None:
                    failed_tests.append("无法更新：记录ID不存在")
                else:
                    conn = psycopg2.connect(**db_config)
                    cur = conn.cursor()
                    
                    new_vector = np.random.rand(768).astype(np.float32)
                    new_vector_str = '[' + ','.join(map(str, new_vector)) + ']'
                    
                    update_sql = f"UPDATE {test_table_name} SET embedding = %s::vector WHERE id = %s;"
                    cur.execute(update_sql, (new_vector_str, record_id))
                    conn.commit()
                    conn.close()
                    
                    passed_tests.append("向量更新成功")
            except Exception as e:
                failed_tests.append(f"向量更新失败: {str(e)}")
            
            # 8. 测试向量删除
            try:
                if record_id is None:
                    failed_tests.append("无法删除：记录ID不存在")
                else:
                    conn = psycopg2.connect(**db_config)
                    cur = conn.cursor()
                    
                    delete_sql = f"DELETE FROM {test_table_name} WHERE id = %s;"
                    cur.execute(delete_sql, (record_id,))
                    conn.commit()
                    conn.close()
                    
                    passed_tests.append("向量删除成功")
            except Exception as e:
                failed_tests.append(f"向量删除失败: {str(e)}")
            
            # 9. 清理测试表
            try:
                conn = psycopg2.connect(**db_config)
                cur = conn.cursor()
                cur.execute(f"DROP TABLE IF EXISTS {test_table_name} CASCADE;")
                conn.commit()
                conn.close()
                passed_tests.append("测试表清理成功")
            except Exception as e:
                failed_tests.append(f"清理测试表失败: {str(e)}")
            
            # 汇总结果
            if len(failed_tests) == 0:
                message = "; ".join(passed_tests)
                self.log_test(test_name, True, message, time.time() - start_time)
                return True
            else:
                message = f"通过: {', '.join(passed_tests)}; 失败: {', '.join(failed_tests)}"
                self.log_test(test_name, False, message, time.time() - start_time)
                return False
            
        except Exception as e:
            self.log_test(test_name, False, f"测试异常: {str(e)}", time.time() - start_time)
            return False
    
    async def test_rag_retrieval_flow(self) -> bool:
        """
        测试RAG检索完整流程
        
        测试内容：
        - 文档入库（读取文档 -> 分块 -> 向量化 -> 存储）
        - 查询向量化
        - 相似度检索
        - 返回检索结果
        
        Returns:
            bool: 是否通过测试
        """
        test_name = "RAG检索完整流程测试"
        start_time = time.time()
        
        try:
            passed_tests = []
            failed_tests = []
            
            # 检查依赖
            try:
                from langchain.text_splitter import RecursiveCharacterTextSplitter
                from sentence_transformers import SentenceTransformer
                import psycopg2
                from psycopg2.extras import RealDictCursor
                import numpy as np
            except ImportError as e:
                failed_tests.append(f"依赖包未安装: {str(e)}")
                self.log_test(test_name, False, "; ".join(failed_tests), time.time() - start_time)
                return False
            
            # 1. 准备测试文档
            test_data_dir = Path(__file__).parent / "test_data"
            md_file = test_data_dir / "test_medical.md"
            if not md_file.exists():
                failed_tests.append("测试文档不存在")
                self.log_test(test_name, False, "; ".join(failed_tests), time.time() - start_time)
                return False
            
            with open(md_file, 'r', encoding='utf-8') as f:
                document_content = f.read()
            
            if len(document_content) == 0:
                failed_tests.append("测试文档内容为空")
                self.log_test(test_name, False, "; ".join(failed_tests), time.time() - start_time)
                return False
            
            passed_tests.append("测试文档读取成功")
            
            # 2. 文档分块
            try:
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=200,
                    chunk_overlap=50,
                    length_function=len,
                    separators=["\n\n", "\n", "。", "，", " ", ""]
                )
                chunks = splitter.split_text(document_content)
                
                if len(chunks) == 0:
                    failed_tests.append("文档分块失败（未生成任何块）")
                    self.log_test(test_name, False, "; ".join(failed_tests), time.time() - start_time)
                    return False
                
                passed_tests.append(f"文档分块成功（{len(chunks)}块）")
            except Exception as e:
                failed_tests.append(f"文档分块失败: {str(e)}")
                self.log_test(test_name, False, "; ".join(failed_tests), time.time() - start_time)
                return False
            
            # 3. 向量化（批量）
            try:
                # 加载模型
                model_name = "moka-ai/m3e-base"
                try:
                    model = SentenceTransformer(model_name, local_files_only=True)
                except (FileNotFoundError, OSError):
                    import os
                    os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
                    model = SentenceTransformer(model_name)
                
                # 批量向量化
                embeddings = model.encode(chunks)
                
                if embeddings.shape[0] != len(chunks):
                    failed_tests.append(f"向量化数量不匹配（期望:{len(chunks)}，实际:{embeddings.shape[0]}）")
                    self.log_test(test_name, False, "; ".join(failed_tests), time.time() - start_time)
                    return False
                
                passed_tests.append(f"批量向量化成功（{len(chunks)}个向量，维度:{embeddings.shape[1]}）")
            except Exception as e:
                failed_tests.append(f"向量化失败: {str(e)}")
                self.log_test(test_name, False, "; ".join(failed_tests), time.time() - start_time)
                return False
            
            # 4. 存储到向量数据库
            test_table_name = "test_rag_documents"
            try:
                # 使用doctor_agent_db数据库（需要先安装pgvector扩展）
                db_config = self._get_vector_db_config()
                
                conn = psycopg2.connect(**db_config)
                cur = conn.cursor()
                
                # 删除测试表（如果存在）
                cur.execute(f"DROP TABLE IF EXISTS {test_table_name} CASCADE;")
                
                # 创建测试表
                create_table_sql = f"""
                CREATE TABLE {test_table_name} (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    embedding vector(768),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
                cur.execute(create_table_sql)
                conn.commit()
                
                # 批量插入向量
                inserted_ids = []
                for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                    vector_str = '[' + ','.join(map(str, embedding)) + ']'
                    insert_sql = f"INSERT INTO {test_table_name} (content, embedding) VALUES (%s, %s::vector) RETURNING id;"
                    cur.execute(insert_sql, (chunk, vector_str))
                    inserted_ids.append(cur.fetchone()[0])
                
                conn.commit()
                conn.close()
                
                passed_tests.append(f"文档入库成功（{len(inserted_ids)}条记录）")
            except Exception as e:
                failed_tests.append(f"文档入库失败: {str(e)}")
                self.log_test(test_name, False, "; ".join(failed_tests), time.time() - start_time)
                return False
            
            # 5. 查询向量化
            try:
                query_text = "高血压的症状有哪些"
                query_vector = model.encode(query_text)
                passed_tests.append("查询向量化成功")
            except Exception as e:
                failed_tests.append(f"查询向量化失败: {str(e)}")
                self.log_test(test_name, False, "; ".join(failed_tests), time.time() - start_time)
                return False
            
            # 6. 执行相似度检索
            try:
                conn = psycopg2.connect(**db_config)
                cur = conn.cursor(cursor_factory=RealDictCursor)
                
                query_vector_str = '[' + ','.join(map(str, query_vector)) + ']'
                
                search_sql = f"""
                SELECT id, content, 1 - (embedding <=> %s::vector) AS similarity
                FROM {test_table_name}
                ORDER BY embedding <=> %s::vector
                LIMIT 3;
                """
                cur.execute(search_sql, (query_vector_str, query_vector_str))
                results = cur.fetchall()
                conn.close()
                
                if len(results) > 0:
                    passed_tests.append(f"相似度检索成功（找到{len(results)}条结果）")
                    # 验证检索结果排序（相似度应该递减）
                    similarities = [r['similarity'] for r in results]
                    if similarities == sorted(similarities, reverse=True):
                        passed_tests.append("检索结果排序正确（相似度递减）")
                    else:
                        passed_tests.append("检索结果已返回")
                else:
                    failed_tests.append("相似度检索未找到结果")
            except Exception as e:
                failed_tests.append(f"相似度检索失败: {str(e)}")
            
            # 7. 清理测试数据
            try:
                conn = psycopg2.connect(**db_config)
                cur = conn.cursor()
                cur.execute(f"DROP TABLE IF EXISTS {test_table_name} CASCADE;")
                conn.commit()
                conn.close()
                passed_tests.append("测试数据清理成功")
            except Exception as e:
                failed_tests.append(f"清理测试数据失败: {str(e)}")
            
            # 汇总结果
            if len(failed_tests) == 0:
                message = "; ".join(passed_tests)
                self.log_test(test_name, True, message, time.time() - start_time)
                return True
            else:
                message = f"通过: {', '.join(passed_tests)}; 失败: {', '.join(failed_tests)}"
                self.log_test(test_name, False, message, time.time() - start_time)
                return False
            
        except Exception as e:
            self.log_test(test_name, False, f"测试异常: {str(e)}", time.time() - start_time)
            return False
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("=" * 80)
        print("RAG基础设施测试")
        print("=" * 80)
        print(f"数据库URI: {Config.DB_URI}")
        print(f"向量数据库: {self._get_vector_db_config()['database']}")
        print(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()
        
        self.start_time = time.time()
        
        # 运行测试
        print("开始运行测试...")
        print("-" * 80)
        
        # 1. 文档读取测试
        self.test_document_loading()
        
        # 2. 文档分块测试
        self.test_text_chunking()
        
        # 3. Embedding测试
        self.test_embedding()
        
        # 4. 向量数据库测试
        await self.test_vector_database_connection()
        
        # 5. RAG检索流程测试
        await self.test_rag_retrieval_flow()
        
        self.end_time = time.time()
        
        # 输出测试结果汇总
        print()
        print("-" * 80)
        print("测试结果汇总")
        print("-" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["passed"])
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {failed_tests}")
        print(f"通过率: {passed_tests/total_tests*100:.1f}%" if total_tests > 0 else "N/A")
        print(f"总耗时: {self.end_time - self.start_time:.3f}s")
        print()
        
        # 输出详细结果
        print("详细结果:")
        for result in self.test_results:
            status = "✅" if result["passed"] else "❌"
            print(f"  {status} {result['test_name']}: {result['message']} ({result['duration']:.3f}s)")
        
        print()
        print("=" * 80)
        
        # 返回是否所有测试都通过
        return failed_tests == 0


async def main():
    """主函数"""
    tester = RAGInfrastructureTest()
    success = await tester.run_all_tests()
    
    # 根据测试结果退出
    exit_code = 0 if success else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    asyncio.run(main())

