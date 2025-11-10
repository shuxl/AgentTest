"""
LangChain 回调处理器模块
用于记录所有模型交互的请求和响应日志
"""
import logging
import json
import time
from typing import Any, Dict, List, Optional
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from langchain_core.messages import BaseMessage


# 获取日志记录器
logger = logging.getLogger(__name__)


class ModelInteractionLogger(BaseCallbackHandler):
    """
    模型交互日志记录器
    记录所有 LLM 调用的请求和响应信息
    """
    
    def __init__(self, verbose: bool = True):
        """
        初始化回调处理器
        
        Args:
            verbose: 是否输出详细日志，默认为 True
        """
        super().__init__()
        self.verbose = verbose
        self.start_times: Dict[str, float] = {}
    
    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        **kwargs: Any
    ) -> None:
        """
        LLM 调用开始时触发
        
        Args:
            serialized: 序列化的 LLM 配置信息
            prompts: 输入提示词列表
            **kwargs: 其他参数
        """
        # 生成唯一标识符用于关联请求和响应
        run_id = kwargs.get("run_id", "unknown")
        self.start_times[run_id] = time.time()
        
        # 提取模型名称
        model_name = serialized.get("name", "unknown")
        if isinstance(model_name, dict):
            model_name = model_name.get("name", "unknown")
        
        # 记录请求信息
        logger.info("=" * 80)
        logger.info(f"[LLM请求开始] Run ID: {run_id}")
        logger.info(f"[LLM请求] 模型: {model_name}")
        logger.info(f"[LLM请求] 输入提示词数量: {len(prompts)}")
        
        # 记录每个提示词的内容（截断过长的内容）
        for i, prompt in enumerate(prompts):
            prompt_preview = prompt[:500] + "..." if len(prompt) > 500 else prompt
            logger.info(f"[LLM请求] 提示词[{i}]: {prompt_preview}")
        
        # 记录其他参数
        if kwargs:
            logger.debug(f"[LLM请求] 其他参数: {json.dumps(kwargs, ensure_ascii=False, default=str)}")
    
    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """
        LLM 调用结束时触发
        
        Args:
            response: LLM 响应结果
            **kwargs: 其他参数
        """
        run_id = kwargs.get("run_id", "unknown")
        start_time = self.start_times.pop(run_id, None)
        elapsed_time = time.time() - start_time if start_time else None
        
        # 记录响应信息
        logger.info(f"[LLM响应结束] Run ID: {run_id}")
        
        if elapsed_time is not None:
            logger.info(f"[LLM响应] 耗时: {elapsed_time:.2f} 秒")
        
        # 记录生成结果
        if response.generations:
            logger.info(f"[LLM响应] 生成结果数量: {len(response.generations)}")
            
            for i, generation_list in enumerate(response.generations):
                for j, generation in enumerate(generation_list):
                    if hasattr(generation, 'text'):
                        text_preview = generation.text[:500] + "..." if len(generation.text) > 500 else generation.text
                        logger.info(f"[LLM响应] 生成结果[{i}][{j}]: {text_preview}")
                    
                    # 记录工具调用（如果有）
                    if hasattr(generation, 'message') and hasattr(generation.message, 'tool_calls'):
                        if generation.message.tool_calls:
                            logger.info(f"[LLM响应] 工具调用: {json.dumps(generation.message.tool_calls, ensure_ascii=False, default=str)}")
        
        # 记录 LLM 输出信息（token 使用等）
        if hasattr(response, 'llm_output') and response.llm_output:
            logger.info(f"[LLM响应] 输出信息: {json.dumps(response.llm_output, ensure_ascii=False, default=str)}")
        
        logger.info("=" * 80)
    
    def on_llm_error(
        self,
        error: Exception,
        **kwargs: Any
    ) -> None:
        """
        LLM 调用出错时触发
        
        Args:
            error: 异常对象
            **kwargs: 其他参数
        """
        run_id = kwargs.get("run_id", "unknown")
        logger.error("=" * 80)
        logger.error(f"[LLM错误] Run ID: {run_id}")
        logger.error(f"[LLM错误] 错误类型: {type(error).__name__}")
        logger.error(f"[LLM错误] 错误信息: {str(error)}")
        logger.error("=" * 80)
        
        # 清理开始时间记录
        if run_id in self.start_times:
            del self.start_times[run_id]
    
    def on_chat_model_start(
        self,
        serialized: Dict[str, Any],
        messages: List[List[BaseMessage]],
        **kwargs: Any
    ) -> None:
        """
        聊天模型调用开始时触发（用于 ChatModel）
        
        Args:
            serialized: 序列化的模型配置信息
            messages: 消息列表（每个元素是一个消息列表）
            **kwargs: 其他参数
        """
        run_id = kwargs.get("run_id", "unknown")
        self.start_times[run_id] = time.time()
        
        # 提取模型名称
        model_name = serialized.get("name", "unknown")
        if isinstance(model_name, dict):
            model_name = model_name.get("name", "unknown")
        
        # 记录请求信息
        logger.info("=" * 80)
        logger.info(f"[ChatModel请求开始] Run ID: {run_id}")
        logger.info(f"[ChatModel请求] 模型: {model_name}")
        logger.info(f"[ChatModel请求] 消息批次数量: {len(messages)}")
        
        # 记录每个批次的消息
        for i, message_batch in enumerate(messages):
            logger.info(f"[ChatModel请求] 批次[{i}] 消息数量: {len(message_batch)}")
            
            # 记录每条消息的摘要
            for j, msg in enumerate(message_batch):
                msg_type = type(msg).__name__
                if hasattr(msg, 'content'):
                    content_preview = str(msg.content)[:200] + "..." if len(str(msg.content)) > 200 else str(msg.content)
                    logger.info(f"[ChatModel请求] 批次[{i}] 消息[{j}] ({msg_type}): {content_preview}")
        
        # 记录其他参数
        if kwargs:
            logger.debug(f"[ChatModel请求] 其他参数: {json.dumps(kwargs, ensure_ascii=False, default=str)}")
    
    def on_chat_model_end(
        self,
        response: Any,
        **kwargs: Any
    ) -> None:
        """
        聊天模型调用结束时触发
        
        Args:
            response: 模型响应
            **kwargs: 其他参数
        """
        run_id = kwargs.get("run_id", "unknown")
        start_time = self.start_times.pop(run_id, None)
        elapsed_time = time.time() - start_time if start_time else None
        
        # 记录响应信息
        logger.info(f"[ChatModel响应结束] Run ID: {run_id}")
        
        if elapsed_time is not None:
            logger.info(f"[ChatModel响应] 耗时: {elapsed_time:.2f} 秒")
        
        # 记录响应内容
        if hasattr(response, 'generations'):
            for i, generation_list in enumerate(response.generations):
                for j, generation in enumerate(generation_list):
                    if hasattr(generation, 'message'):
                        msg = generation.message
                        if hasattr(msg, 'content'):
                            content_preview = str(msg.content)[:500] + "..." if len(str(msg.content)) > 500 else str(msg.content)
                            logger.info(f"[ChatModel响应] 生成结果[{i}][{j}]: {content_preview}")
                        
                        # 记录工具调用（如果有）
                        if hasattr(msg, 'tool_calls') and msg.tool_calls:
                            logger.info(f"[ChatModel响应] 工具调用: {json.dumps(msg.tool_calls, ensure_ascii=False, default=str)}")
        
        # 记录 LLM 输出信息
        if hasattr(response, 'llm_output') and response.llm_output:
            logger.info(f"[ChatModel响应] 输出信息: {json.dumps(response.llm_output, ensure_ascii=False, default=str)}")
        
        logger.info("=" * 80)
    
    def on_chat_model_error(
        self,
        error: Exception,
        **kwargs: Any
    ) -> None:
        """
        聊天模型调用出错时触发
        
        Args:
            error: 异常对象
            **kwargs: 其他参数
        """
        run_id = kwargs.get("run_id", "unknown")
        logger.error("=" * 80)
        logger.error(f"[ChatModel错误] Run ID: {run_id}")
        logger.error(f"[ChatModel错误] 错误类型: {type(error).__name__}")
        logger.error(f"[ChatModel错误] 错误信息: {str(error)}")
        logger.error("=" * 80)
        
        # 清理开始时间记录
        if run_id in self.start_times:
            del self.start_times[run_id]


def get_model_interaction_logger() -> ModelInteractionLogger:
    """
    获取模型交互日志记录器实例
    
    Returns:
        ModelInteractionLogger: 回调处理器实例
    """
    return ModelInteractionLogger(verbose=True)

