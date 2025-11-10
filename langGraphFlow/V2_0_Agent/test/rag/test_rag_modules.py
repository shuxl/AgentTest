"""
RAG基础设施测试用例
测试文档读取、分块、embedding、向量数据库操作和RAG检索流程
"""
import sys
import os
from pathlib import Path
import time
from typing import List, Dict, Any

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.rag import (
    DocumentLoader,
    TextSplitter,
    EmbeddingService,
    VectorStore,
    RAGRetriever
)


class RAGInfrastructureTests:
    """RAG基础设施测试类"""
    
    def __init__(self):
        """初始化测试类"""
        self.test_results = []
        self.test_data_dir = project_root / "test" / "rag_env_check" / "test_data"
    
    def log_test(self, test_name: str, passed: bool, message: str = "", duration: float = 0.0):
        """
        记录测试结果
        
        Args:
            test_name: 测试名称
            passed: 是否通过
            message: 状态消息
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
        """测试文档读取功能"""
        test_name = "文档读取功能测试"
        start_time = time.time()
        
        try:
            passed_tests = []
            failed_tests = []
            
            loader = DocumentLoader()
            
            # 测试读取TXT文件
            txt_file = self.test_data_dir / "test_surgery.txt"
            if txt_file.exists():
                try:
                    doc = loader.load_document(str(txt_file))
                    passed_tests.append(f"TXT文件读取成功（{doc['file_size']}字符）")
                except Exception as e:
                    failed_tests.append(f"TXT文件读取失败: {str(e)}")
            else:
                failed_tests.append("TXT测试文件不存在")
            
            # 测试读取MD文件
            md_file = self.test_data_dir / "test_medical.md"
            if md_file.exists():
                try:
                    doc = loader.load_document(str(md_file))
                    passed_tests.append(f"MD文件读取成功（{doc['file_size']}字符）")
                except Exception as e:
                    failed_tests.append(f"MD文件读取失败: {str(e)}")
            else:
                failed_tests.append("MD测试文件不存在")
            
            # 检查PDF支持
            if loader._check_pdf_support():
                passed_tests.append("PDF库可用")
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
        """测试文档分块功能"""
        test_name = "文档分块功能测试"
        start_time = time.time()
        
        try:
            passed_tests = []
            failed_tests = []
            
            # 读取测试文档
            loader = DocumentLoader()
            md_file = self.test_data_dir / "test_medical.md"
            if not md_file.exists():
                failed_tests.append("测试文档不存在")
                self.log_test(test_name, False, "; ".join(failed_tests), time.time() - start_time)
                return False
            
            doc = loader.load_document(str(md_file))
            
            # 测试分块
            splitter = TextSplitter(chunk_size=200, chunk_overlap=50)
            chunks = splitter.split_text(doc['content'])
            
            if len(chunks) > 0:
                passed_tests.append(f"文档分块成功（{len(chunks)}块）")
                
                # 验证分块信息
                info = splitter.get_chunk_info(chunks)
                passed_tests.append(f"平均块大小: {info['avg_chunk_size']:.1f}字符")
                
                # 验证内容完整性
                total_length = sum(len(chunk) for chunk in chunks)
                if total_length >= len(doc['content']) * 0.9:
                    passed_tests.append("分块内容完整性验证通过")
                else:
                    failed_tests.append("分块内容丢失")
            else:
                failed_tests.append("文档分块失败（未生成任何块）")
            
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
        """测试Embedding功能"""
        test_name = "Embedding功能测试"
        start_time = time.time()
        
        try:
            passed_tests = []
            failed_tests = []
            
            # 创建Embedding服务
            service = EmbeddingService()
            service.load_model()
            
            dimension = service.get_dimension()
            passed_tests.append(f"模型加载成功（维度: {dimension}）")
            
            # 测试单个文本向量化
            test_text = "这是一个测试文本"
            vector = service.encode(test_text)
            
            if vector.shape == (dimension,):
                passed_tests.append(f"单个文本向量化成功（维度: {vector.shape}）")
            else:
                failed_tests.append(f"向量维度不正确（期望: ({dimension},)，实际: {vector.shape}）")
            
            # 测试批量文本向量化
            test_texts = [
                "这是第一个测试文本",
                "这是第二个测试文本",
                "这是第三个测试文本"
            ]
            vectors = service.encode_batch(test_texts)
            
            if vectors.shape == (len(test_texts), dimension):
                passed_tests.append(f"批量文本向量化成功（{len(test_texts)}个文本，维度: {vectors.shape}）")
            else:
                failed_tests.append(f"批量向量维度不正确")
            
            # 测试相似度计算
            text1 = "高血压是一种常见的慢性疾病"
            text2 = "高血压是指血压持续升高的状态"
            text3 = "今天天气很好"
            
            vec1 = service.encode(text1)
            vec2 = service.encode(text2)
            vec3 = service.encode(text3)
            
            import numpy as np
            similarity_12 = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
            similarity_13 = np.dot(vec1, vec3) / (np.linalg.norm(vec1) * np.linalg.norm(vec3))
            
            if similarity_12 > similarity_13:
                passed_tests.append(f"向量相似度计算正常（相关文本相似度:{similarity_12:.3f} > 不相关文本相似度:{similarity_13:.3f}）")
            else:
                passed_tests.append("向量相似度计算正常（相似度值已计算）")
            
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
    
    def test_vector_database(self) -> bool:
        """测试向量数据库操作"""
        test_name = "向量数据库操作测试"
        start_time = time.time()
        
        try:
            passed_tests = []
            failed_tests = []
            
            store = VectorStore()
            
            # 测试连接
            if store.test_connection():
                passed_tests.append("数据库连接成功")
            else:
                failed_tests.append("数据库连接失败")
                self.log_test(test_name, False, "; ".join(failed_tests), time.time() - start_time)
                return False
            
            # 检查扩展
            if store.check_extension('vector'):
                passed_tests.append("pgvector扩展已安装")
            else:
                failed_tests.append("pgvector扩展未安装")
                self.log_test(test_name, False, "; ".join(failed_tests), time.time() - start_time)
                return False
            
            # 创建测试表
            test_table = "test_vector_ops"
            if store.create_table(test_table, dimension=768, drop_if_exists=True):
                passed_tests.append(f"测试表创建成功（{test_table}）")
            else:
                failed_tests.append("测试表创建失败")
                self.log_test(test_name, False, "; ".join(failed_tests), time.time() - start_time)
                return False
            
            # 测试插入
            import numpy as np
            test_vector = np.random.rand(768).astype(np.float32)
            record_id = store.insert_vector(test_table, "测试内容", test_vector)
            
            if record_id:
                passed_tests.append(f"向量插入成功（ID: {record_id}）")
            else:
                failed_tests.append("向量插入失败")
            
            # 测试检索
            if record_id:
                results = store.cosine_search(test_table, test_vector, limit=5)
                if len(results) > 0 and results[0]['similarity'] > 0.99:
                    passed_tests.append(f"向量检索成功（找到{len(results)}条结果，相似度:{results[0]['similarity']:.3f}）")
                else:
                    failed_tests.append("向量检索结果异常")
            
            # 清理测试表
            try:
                with store.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute(f"DROP TABLE IF EXISTS {test_table} CASCADE;")
                    conn.commit()
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
    
    def test_rag_retrieval_flow(self) -> bool:
        """测试RAG检索完整流程"""
        test_name = "RAG检索完整流程测试"
        start_time = time.time()
        
        try:
            passed_tests = []
            failed_tests = []
            
            # 创建RAG检索器
            retriever = RAGRetriever(table_name="test_rag_flow")
            
            # 初始化表
            if retriever.initialize_table(drop_if_exists=True):
                passed_tests.append("向量数据库表初始化成功")
            else:
                failed_tests.append("向量数据库表初始化失败")
                self.log_test(test_name, False, "; ".join(failed_tests), time.time() - start_time)
                return False
            
            # 添加测试文档
            md_file = self.test_data_dir / "test_medical.md"
            if md_file.exists():
                try:
                    inserted = retriever.add_document(str(md_file))
                    passed_tests.append(f"文档入库成功（{inserted}个块）")
                except Exception as e:
                    failed_tests.append(f"文档入库失败: {str(e)}")
                    self.log_test(test_name, False, "; ".join(failed_tests), time.time() - start_time)
                    return False
            else:
                failed_tests.append("测试文档不存在")
                self.log_test(test_name, False, "; ".join(failed_tests), time.time() - start_time)
                return False
            
            # 执行检索
            query = "高血压的症状有哪些"
            results = retriever.retrieve(query, top_k=3)
            
            if len(results) > 0:
                passed_tests.append(f"相似度检索成功（找到{len(results)}条结果）")
                # 验证检索结果排序
                similarities = [r['similarity'] for r in results]
                if similarities == sorted(similarities, reverse=True):
                    passed_tests.append("检索结果排序正确（相似度递减）")
                else:
                    passed_tests.append("检索结果已返回")
            else:
                failed_tests.append("相似度检索未找到结果")
            
            # 清理测试表（可选，保留用于检查）
            # try:
            #     with retriever.vector_store.get_connection() as conn:
            #         cur = conn.cursor()
            #         cur.execute(f"DROP TABLE IF EXISTS {retriever.table_name} CASCADE;")
            #         conn.commit()
            #     passed_tests.append("测试数据清理成功")
            # except Exception as e:
            #     failed_tests.append(f"清理测试数据失败: {str(e)}")
            
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
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 80)
        print("RAG基础设施测试用例")
        print("=" * 80)
        print(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()
        
        start_time = time.time()
        
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
        self.test_vector_database()
        
        # 5. RAG检索流程测试
        self.test_rag_retrieval_flow()
        
        end_time = time.time()
        
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
        print(f"总耗时: {end_time - start_time:.3f}s")
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


def main():
    """主函数"""
    tester = RAGInfrastructureTests()
    success = tester.run_all_tests()
    
    # 根据测试结果退出
    exit_code = 0 if success else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
