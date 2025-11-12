"""
意图澄清功能测试
测试clarify_intent工具是否能正确生成包含所有智能体功能的澄清问题
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent  # tests/unit/router/ -> tests/unit/ -> tests/ -> V2_0_Agent/
sys.path.insert(0, str(project_root))

from domain.router.tools import clarify_intent


def test_clarify_intent_includes_all_agents():
    """测试意图澄清是否包含所有智能体功能"""
    print("=" * 80)
    print("意图澄清功能测试")
    print("=" * 80)
    
    # 根据当前设计，clarify_intent 工具必须明确提到三种功能：
    # 1. 记录血压（或查询血压、管理血压）
    # 2. 预约复诊（或预约、复诊）
    # 3. 进行病情诊断（或诊断、诊断患者病情、健康咨询等）
    test_cases = [
        {
            "name": "简单问候",
            "query": "你好",
            "expected_keywords": {
                "血压": ["血压", "记录血压", "查询血压"],  # 必须包含血压相关关键词
                "预约": ["预约", "复诊", "挂号"],  # 必须包含预约相关关键词
                "诊断": ["诊断", "病情诊断", "健康咨询", "咨询健康", "病情", "患者诊断"]  # 必须包含诊断相关关键词（至少一个）
            }
        },
        {
            "name": "模糊查询",
            "query": "我需要帮助",
            "expected_keywords": {
                "血压": ["血压", "记录血压", "查询血压"],
                "预约": ["预约", "复诊", "挂号"],
                "诊断": ["诊断", "病情诊断", "健康咨询", "咨询健康", "病情", "患者诊断"]
            }
        },
        {
            "name": "空消息",
            "query": "",
            "expected_keywords": {
                "血压": ["血压", "记录血压", "查询血压"],
                "预约": ["预约", "复诊", "挂号"],
                "诊断": ["诊断", "病情诊断", "健康咨询", "咨询健康", "病情", "患者诊断"]
            }
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['name']}")
        print(f"查询: '{test_case['query']}'")
        print("-" * 80)
        
        try:
            # 调用澄清工具
            clarification = clarify_intent.invoke({
                "query": test_case['query'],
                "possible_intents": None
            })
            
            print(f"生成的澄清问题: {clarification}")
            
            # 检查是否包含所有类别的关键词
            # 每个类别（血压、预约、诊断）必须至少有一个关键词出现
            missing_categories = []
            for category, keywords in test_case['expected_keywords'].items():
                found = any(keyword in clarification for keyword in keywords)
                if found:
                    print(f"  ✅ {category}: 找到相关关键词")
                else:
                    print(f"  ❌ {category}: 未找到相关关键词")
                    missing_categories.append(category)
            
            if missing_categories:
                print(f"❌ 失败: 缺少类别 {missing_categories}")
                failed += 1
            else:
                print(f"✅ 通过: 包含所有必需类别（血压、预约、诊断）")
                passed += 1
            
            # 额外检查：确保澄清问题长度合理
            if len(clarification) > 100:
                print(f"⚠️  警告: 澄清问题过长（{len(clarification)}字符），建议不超过50字")
            elif len(clarification) < 10:
                print(f"⚠️  警告: 澄清问题过短（{len(clarification)}字符）")
            else:
                print(f"✅ 澄清问题长度合理（{len(clarification)}字符）")
            
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    # 汇总结果
    print("\n" + "=" * 80)
    print("测试结果汇总")
    print("=" * 80)
    print(f"总测试数: {len(test_cases)}")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"通过率: {passed / len(test_cases) * 100:.1f}%")
    
    if failed == 0:
        print("\n✅ 所有测试通过！")
        return True
    else:
        print(f"\n❌ 有 {failed} 个测试失败")
        return False


def test_clarify_intent_keywords():
    """测试澄清问题是否包含特定关键词"""
    print("\n" + "=" * 80)
    print("关键词检查测试")
    print("=" * 80)
    
    # 测试多个查询，确保澄清问题包含诊断相关关键词
    test_queries = [
        "你好",
        "在吗",
        "有什么功能",
        "我需要帮助"
    ]
    
    required_keywords = {
        "血压": ["血压", "记录血压", "查询血压"],
        "预约": ["预约", "复诊", "挂号"],
        "诊断": ["诊断", "病情诊断", "健康咨询", "咨询健康", "病情", "患者诊断"]
    }
    
    all_passed = True
    
    for query in test_queries:
        print(f"\n测试查询: '{query}'")
        try:
            clarification = clarify_intent.invoke({
                "query": query,
                "possible_intents": None
            })
            
            print(f"澄清问题: {clarification}")
            
            # 检查每个类别是否至少有一个关键词出现
            for category, keywords in required_keywords.items():
                found = any(keyword in clarification for keyword in keywords)
                if found:
                    print(f"  ✅ {category}: 找到相关关键词")
                else:
                    print(f"  ❌ {category}: 未找到相关关键词")
                    all_passed = False
            
        except Exception as e:
            print(f"  ❌ 测试失败: {str(e)}")
            all_passed = False
    
    if all_passed:
        print("\n✅ 所有关键词检查通过！")
    else:
        print("\n❌ 部分关键词检查失败")
    
    return all_passed


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("意图澄清功能完整测试")
    print("=" * 80)
    
    # 运行测试
    test1_result = test_clarify_intent_includes_all_agents()
    test2_result = test_clarify_intent_keywords()
    
    # 最终结果
    print("\n" + "=" * 80)
    print("最终测试结果")
    print("=" * 80)
    if test1_result and test2_result:
        print("✅ 所有测试通过！")
        exit(0)
    else:
        print("❌ 部分测试失败")
        exit(1)

