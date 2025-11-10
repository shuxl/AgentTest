"""
构建内科知识库脚本
用于初始化内科知识库并批量导入测试文档
"""
import sys
import asyncio
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.rag.knowledge_base_manager import KnowledgeBaseManager


async def build_internal_medicine_knowledge_base():
    """构建内科知识库"""
    print("=" * 60)
    print("构建内科知识库")
    print("=" * 60)
    
    # 创建知识库管理器
    kb_manager = KnowledgeBaseManager(
        department="internal_medicine",
        chunk_size=300,
        chunk_overlap=50
    )
    
    # 初始化知识库（创建表和索引）
    print("\n1. 初始化知识库...")
    if kb_manager.initialize_knowledge_base(drop_if_exists=True):
        print("✅ 知识库初始化成功")
    else:
        print("❌ 知识库初始化失败")
        return False
    
    # 从目录批量导入文档
    doc_dir = Path(__file__).parent.parent / "data" / "medical_docs" / "internal_medicine"
    print(f"\n2. 从目录导入文档: {doc_dir}")
    
    if not doc_dir.exists():
        print(f"❌ 文档目录不存在: {doc_dir}")
        return False
    
    result = kb_manager.build_knowledge_base_from_directory(
        str(doc_dir),
        file_extensions=['.md', '.txt']
    )
    
    print(f"\n导入结果:")
    print(f"  总文件数: {result['total_files']}")
    print(f"  成功文件数: {result['success_files']}")
    print(f"  失败文件数: {result['failed_files']}")
    print(f"  总文档块数: {result['total_chunks']}")
    
    # 验证知识库
    print(f"\n3. 验证知识库...")
    doc_count = kb_manager.get_document_count()
    print(f"✅ 知识库中共有 {doc_count} 个文档块")
    
    # 测试检索
    print(f"\n4. 测试检索功能...")
    test_queries = [
        "高血压的症状有哪些",
        "如何诊断糖尿病",
        "冠心病的治疗方法"
    ]
    
    for query in test_queries:
        print(f"\n查询: {query}")
        results = kb_manager.retrieve_knowledge(query, top_k=3)
        print(f"  找到 {len(results)} 条相关结果")
        if results:
            print(f"  最相关结果相似度: {results[0].get('similarity', 0):.3f}")
    
    print("\n" + "=" * 60)
    print("✅ 内科知识库构建完成！")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    asyncio.run(build_internal_medicine_knowledge_base())

