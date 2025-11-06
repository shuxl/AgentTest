"""
路由功能单元测试
测试路由智能体的核心功能
"""
import asyncio
import sys
import os
from langchain_core.messages import HumanMessage, AIMessage

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))  # 回到项目根目录
sys.path.insert(0, project_root)

from utils.router_state import RouterState, IntentResult
from utils.router import router_node, route_decision, clarify_intent_node
from utils.tools.router_tools import identify_intent, clarify_intent


def test_router_state():
    """测试RouterState数据结构"""
    print("=" * 50)
    print("测试 RouterState 数据结构")
    print("=" * 50)
    
    state: RouterState = {
        "messages": [HumanMessage(content="我想记录血压")],
        "current_intent": None,
        "current_agent": None,
        "need_reroute": False,
        "session_id": "test_session_001",
        "user_id": "test_user_001"
    }
    
    assert isinstance(state["messages"], list)
    assert state["session_id"] == "test_session_001"
    assert state["user_id"] == "test_user_001"
    
    print("✓ RouterState 数据结构测试通过")
    return True


def test_intent_result():
    """测试IntentResult数据结构"""
    print("\n" + "=" * 50)
    print("测试 IntentResult 数据结构")
    print("=" * 50)
    
    result = IntentResult(
        intent_type="blood_pressure",
        confidence=0.9,
        entities={},
        need_clarification=False,
        reasoning="用户明确提到记录血压"
    )
    
    assert result.intent_type == "blood_pressure"
    assert result.confidence == 0.9
    assert not result.need_clarification
    
    print("✓ IntentResult 数据结构测试通过")
    return True


async def test_identify_intent_tool():
    """测试identify_intent工具，包括意图识别和路由决策验证"""
    print("\n" + "=" * 50)
    print("测试 identify_intent 工具（含路由决策验证）")
    print("=" * 50)
    
    # 测试明确的意图
    test_cases = [
        ("我想记录血压", "blood_pressure"),
        ("查询我的血压记录", "blood_pressure"),
        ("我想预约复诊", "appointment"),
        ("查询我的预约", "appointment"),
        ("查询患者病历", "doctor_assistant"),
        ("开具处方", "doctor_assistant"),
        ("你好", "unclear"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for query, expected_intent in test_cases:
        try:
            # 1. 测试意图识别
            result_dict = identify_intent.invoke({
                "query": query,
                "conversation_history": None,
                "current_intent": None
            })
            
            result = IntentResult(**result_dict)
            intent_type = result.intent_type
            
            # 2. 验证返回的意图类型是否在允许的范围内
            assert intent_type in ["blood_pressure", "appointment", "doctor_assistant", "unclear"]
            assert 0.0 <= result.confidence <= 1.0
            
            # 3. 验证识别出的意图是否等于期望的意图（精确验证）
            if intent_type == expected_intent:
                intent_match = True
            else:
                # 对于unclear意图，如果置信度低也认为是合理的
                intent_match = (intent_type == expected_intent) or (expected_intent == "unclear" and result.confidence < 0.7)
            
            # 4. 测试路由决策：根据识别出的意图验证路由决策是否正确
            state: RouterState = {
                "messages": [HumanMessage(content=query)],
                "current_intent": intent_type,
                "current_agent": None,
                "need_reroute": False,
                "session_id": "test",
                "user_id": "test"
            }
            
            route = route_decision(state)
            
            # 5. 验证路由决策：路由目标应该等于意图类型（对于unclear，路由目标也是unclear）
            expected_route = expected_intent
            route_match = (route == expected_route)
            
            if intent_match and route_match:
                print(f"  ✓ '{query}' -> intent={intent_type} (置信度: {result.confidence:.2f}), route={route}")
                passed += 1
            else:
                print(f"  ✗ '{query}' -> intent={intent_type} (期望: {expected_intent}), route={route} (期望: {expected_route})")
            
        except Exception as e:
            print(f"  ✗ '{query}' -> 失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print(f"\n✓ identify_intent 工具测试通过: {passed}/{total}")
    return passed == total


async def test_clarify_intent_tool():
    """测试clarify_intent工具"""
    print("\n" + "=" * 50)
    print("测试 clarify_intent 工具")
    print("=" * 50)
    
    test_cases = [
        "你好",
        "在吗",
        "有什么功能",
    ]
    
    passed = 0
    total = len(test_cases)
    
    for query in test_cases:
        try:
            clarification = clarify_intent.invoke({
                "query": query,
                "possible_intents": None
            })
            
            assert isinstance(clarification, str)
            assert len(clarification) > 0
            
            print(f"  ✓ '{query}' -> 澄清问题: {clarification[:50]}...")
            passed += 1
            
        except Exception as e:
            print(f"  ✗ '{query}' -> 失败: {str(e)}")
    
    print(f"\n✓ clarify_intent 工具测试通过: {passed}/{total}")
    return passed == total


def test_route_decision():
    """测试route_decision函数"""
    print("\n" + "=" * 50)
    print("测试 route_decision 函数")
    print("=" * 50)
    
    test_cases = [
        ("blood_pressure", "blood_pressure"),
        ("appointment", "appointment"),
        ("doctor_assistant", "doctor_assistant"),
        ("unclear", "unclear"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for intent, expected_route in test_cases:
        state: RouterState = {
            "messages": [],
            "current_intent": intent,
            "current_agent": None,
            "need_reroute": False,
            "session_id": "test",
            "user_id": "test"
        }
        
        route = route_decision(state)
        
        assert route == expected_route
        print(f"  ✓ intent={intent} -> route={route}")
        passed += 1
    
    print(f"\n✓ route_decision 函数测试通过: {passed}/{total}")
    return passed == total


async def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 50)
    print("路由功能单元测试")
    print("=" * 50)
    
    results = []
    
    # 测试数据结构
    try:
        results.append(("RouterState数据结构", test_router_state()))
    except Exception as e:
        print(f"✗ RouterState数据结构测试失败: {str(e)}")
        results.append(("RouterState数据结构", False))
    
    try:
        results.append(("IntentResult数据结构", test_intent_result()))
    except Exception as e:
        print(f"✗ IntentResult数据结构测试失败: {str(e)}")
        results.append(("IntentResult数据结构", False))
    
    # 测试路由决策函数（纯数据解析，不依赖LLM，在工具测试之前）
    try:
        results.append(("route_decision函数", test_route_decision()))
    except Exception as e:
        print(f"✗ route_decision函数测试失败: {str(e)}")
        results.append(("route_decision函数", False))
    
    # 测试工具（需要LLM API）
    # identify_intent工具测试中已包含路由决策验证
    try:
        results.append(("identify_intent工具（含路由决策）", await test_identify_intent_tool()))
    except Exception as e:
        print(f"✗ identify_intent工具测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        results.append(("identify_intent工具（含路由决策）", False))
    
    try:
        results.append(("clarify_intent工具", await test_clarify_intent_tool()))
    except Exception as e:
        print(f"✗ clarify_intent工具测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        results.append(("clarify_intent工具", False))
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓" if result else "✗"
        print(f"{status} {test_name}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("✓ 所有测试通过！")
    else:
        print(f"✗ {total - passed} 个测试失败")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)

