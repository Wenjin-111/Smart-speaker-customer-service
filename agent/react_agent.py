# agent/react_agent.py
from langchain.agents import create_agent
from agent.tools.middleware import monitor_tool, log_before_model, report_prompt_switch
from agent.tools.agent_tools import (
    rag_summarize, get_weather, get_user_location, get_user_id, get_current_month,
    fetch_external_data, fill_context_for_report
)
from model.factory import chat_model
from utils.prompt_loader import load_system_prompt


class ReactAgent:
    def __init__(self):
        self.agent = create_agent(
            model=chat_model,
            system_prompt=load_system_prompt(),
            tools=[
                rag_summarize, get_weather, get_user_location, get_user_id,
                get_current_month, fetch_external_data, fill_context_for_report
            ],
            middleware=[monitor_tool, log_before_model, report_prompt_switch],
        )

    def execute_stream(self, messages):
        """
        支持传入完整的消息历史，返回流式响应
        messages: list of dict，每个 dict 包含 role 和 content
        """
        input_dict = {"messages": messages}
        # 使用 stream_mode="values" 获取每个步骤后的完整状态
        for chunk in self.agent.stream(input_dict, stream_mode="values", context={"report": False}):
            latest_message = chunk["messages"][-1]
            # 只输出 AI 消息且不是工具调用的消息（即最终回答的内容）
            if hasattr(latest_message, "type") and latest_message.type == "ai" and not getattr(latest_message,
                                                                                               "tool_calls", None):
                if latest_message.content:
                    yield latest_message.content.strip() + "\n"