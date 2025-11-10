"""
批量构建所有诊断科室知识库脚本
用于一次性构建所有科室的知识库
"""
import sys
import asyncio
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.build_internal_medicine_kb import build_internal_medicine_knowledge_base
from scripts.build_surgery_kb import build_surgery_knowledge_base
from scripts.build_pediatrics_kb import build_pediatrics_knowledge_base
from scripts.build_gynecology_kb import build_gynecology_knowledge_base
from scripts.build_cardiology_kb import build_cardiology_knowledge_base
from scripts.build_general_kb import build_general_knowledge_base


async def build_all_diagnosis_knowledge_bases():
    """批量构建所有诊断科室知识库"""
    print("=" * 60)
    print("批量构建所有诊断科室知识库")
    print("=" * 60)
    
    departments = [
        ("内科", build_internal_medicine_knowledge_base),
        ("外科", build_surgery_knowledge_base),
        ("儿科", build_pediatrics_knowledge_base),
        ("妇科", build_gynecology_knowledge_base),
        ("心血管科", build_cardiology_knowledge_base),
        ("通用诊断", build_general_knowledge_base),
    ]
    
    results = {}
    
    for dept_name, build_func in departments:
        print(f"\n{'=' * 60}")
        print(f"开始构建 {dept_name} 知识库...")
        print(f"{'=' * 60}")
        
        try:
            success = await build_func()
            results[dept_name] = "成功" if success else "失败"
        except Exception as e:
            print(f"❌ {dept_name} 知识库构建出错: {e}")
            results[dept_name] = f"错误: {str(e)}"
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("构建结果汇总")
    print("=" * 60)
    for dept_name, result in results.items():
        status_icon = "✅" if result == "成功" else "❌"
        print(f"{status_icon} {dept_name}: {result}")
    
    success_count = sum(1 for r in results.values() if r == "成功")
    print(f"\n总计: {success_count}/{len(departments)} 个知识库构建成功")
    print("=" * 60)
    
    return success_count == len(departments)


if __name__ == "__main__":
    asyncio.run(build_all_diagnosis_knowledge_bases())

