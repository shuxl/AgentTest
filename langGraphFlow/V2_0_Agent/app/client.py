"""
前端客户端（命令行界面）
实现用户输入和显示功能，与后端API通信，支持会话管理和对话历史显示
"""
import uuid
import requests
import json
import traceback
from typing import Optional
import time
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.markdown import Markdown
from rich.theme import Theme
from rich.progress import Progress

# 创建自定义主题
custom_theme = Theme({
    "info": "cyan bold",
    "warning": "yellow bold",
    "success": "green bold",
    "error": "red bold",
    "heading": "magenta bold underline",
    "highlight": "blue bold",
})

# 初始化Rich控制台
console = Console(theme=custom_theme)

# 后端API地址
API_BASE_URL = "http://localhost:8001"


def chat_with_agent(user_id: str, session_id: str, message: str) -> dict:
    """
    调用后端API进行对话
    
    Args:
        user_id: 用户ID
        session_id: 会话ID
        message: 用户消息
        
    Returns:
        服务端返回的结果
    """
    payload = {
        "message": message,
        "session_id": session_id,
        "user_id": user_id
    }
    
    console.print("[info]正在发送请求到智能体，请稍候...[/info]")
    
    try:
        with Progress() as progress:
            task = progress.add_task("[cyan]处理中...", total=None)
            response = requests.post(f"{API_BASE_URL}/api/chat", json=payload, timeout=60)
            progress.update(task, completed=100)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API调用失败: {response.status_code} - {response.text}")
    except requests.exceptions.Timeout:
        raise Exception("请求超时，请稍后重试")
    except requests.exceptions.ConnectionError:
        raise Exception(f"无法连接到后端服务 ({API_BASE_URL})，请确保后端服务已启动")


def check_backend_health() -> bool:
    """检查后端服务健康状态"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def display_chat_response(response: dict):
    """
    显示对话响应
    
    Args:
        response: 后端返回的响应数据
    """
    if not response:
        console.print("[error]收到空响应[/error]")
        return
    
    # 显示智能体回复
    response_text = response.get("response", "")
    current_intent = response.get("current_intent", "unknown")
    current_agent = response.get("current_agent", "none")
    
    # 显示回复内容
    if response_text:
        console.print(Panel(
            Markdown(response_text),
            title="[success]智能体回复[/success]",
            border_style="green"
        ))
    
    # 显示路由信息（调试用）
    intent_display = {
        "blood_pressure": "血压记录",
        "appointment": "复诊管理",
        "doctor_assistant": "医生助手",
        "unclear": "意图不明确"
    }
    intent_name = intent_display.get(current_intent, current_intent)
    
    agent_display = {
        "blood_pressure_agent": "血压记录智能体",
        "appointment_agent": "复诊管理智能体",
        "doctor_assistant_agent": "医生助手智能体",
        None: "路由智能体"
    }
    agent_name = agent_display.get(current_agent, current_agent or "路由智能体")
    
    console.print(f"[info]当前意图: {intent_name} | 当前智能体: {agent_name}[/info]")


def main():
    """主函数，运行客户端"""
    console.print(Panel(
        "多智能体路由系统前端客户端",
        title="[heading]ReAct Agent智能体交互演示系统[/heading]",
        border_style="magenta"
    ))
    
    # 检查后端服务健康状态
    console.print("[info]正在检查后端服务状态...[/info]")
    if not check_backend_health():
        console.print(Panel(
            f"无法连接到后端服务 ({API_BASE_URL})\n"
            "请确保后端服务已启动：\n"
            "  python app/main.py",
            title="[error]连接失败[/error]",
            border_style="red"
        ))
        return
    
    console.print("[success]后端服务连接正常[/success]\n")
    
    # 输入用户ID
    default_user_id = f"user_{int(time.time())}"
    user_id = Prompt.ask(
        "[info]请输入用户ID[/info] (新ID将创建新用户，已有ID将恢复使用该用户)",
        default=default_user_id
    )
    
    # 创建或使用会话ID
    session_id = str(uuid.uuid4())
    console.print(f"[info]当前会话ID: {session_id}[/info]")
    console.print("[info]提示: 使用相同的用户ID和会话ID可以恢复对话历史[/info]\n")
    
    # 主交互循环
    while True:
        try:
            # 获取用户输入
            console.print("[info]请输入您的问题[/info]")
            console.print("[info]命令提示: 'exit' 退出 | 'new' 开始新会话 | 'help' 显示帮助[/info]")
            query = Prompt.ask("", default="你好")
            
            # 处理特殊命令
            if query.lower() == 'exit':
                console.print("[info]感谢使用，再见！[/info]")
                break
            
            elif query.lower() == 'new':
                session_id = str(uuid.uuid4())
                console.print(f"[info]已创建新会话，会话ID: {session_id}[/info]")
                continue
            
            elif query.lower() == 'help':
                console.print(Panel(
                    "可用命令：\n"
                    "  exit  - 退出程序\n"
                    "  new   - 创建新会话\n"
                    "  help  - 显示帮助信息\n\n"
                    "对话示例：\n"
                    "  - 我想记录血压\n"
                    "  - 查询我的血压记录\n"
                    "  - 我想预约复诊\n"
                    "  - 查询患者病历",
                    title="[info]帮助信息[/info]",
                    border_style="cyan"
                ))
                continue
            
            # 调用后端API
            response = chat_with_agent(user_id, session_id, query)
            
            # 显示响应
            display_chat_response(response)
            
            # 添加分隔线
            console.print("\n" + "=" * 60 + "\n")
            
        except KeyboardInterrupt:
            console.print("\n[warning]用户中断，正在退出...[/warning]")
            console.print("[info]会话状态已保存，可以在下次使用相同用户ID和会话ID恢复[/info]")
            break
        except Exception as e:
            console.print(Panel(
                f"发生错误: {str(e)}\n\n"
                "可能的原因：\n"
                "  1. 后端服务未启动\n"
                "  2. 网络连接问题\n"
                "  3. 后端服务处理出错\n\n"
                "请检查后端服务日志或重试。",
                title="[error]错误[/error]",
                border_style="red"
            ))
            console.print(traceback.format_exc())
            continue


if __name__ == "__main__":
    main()

