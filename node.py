import operator
import sqlite3
import random
import time
from typing import Annotated, Sequence
from typing_extensions import TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.types import RetryPolicy

# 模拟数据库类
class MockSQLDatabase:
    def __init__(self):
        self.connection_stable = False
        self.call_count = 0

    def run(self, query):
        self.call_count += 1
        print(f"🗄️ 数据库查询 (第{self.call_count}次): {query}")

        # 模拟不稳定的数据库连接 - 前2次调用会失败
        if self.call_count <= 2:
            print(f"❌ 数据库连接失败 (模拟错误)")
            raise sqlite3.OperationalError("数据库连接超时")

        print(f"✅ 数据库查询成功")
        return "艺术家数据: Van Gogh, Picasso, Da Vinci, Monet, Renoir"

# 模拟 LLM 类
class MockChatOpenAI:
    def __init__(self, model="mock-model"):
        self.model = model
        self.call_count = 0

    def invoke(self, messages):
        self.call_count += 1
        print(f"🤖 LLM调用 (第{self.call_count}次)")

        # 模拟 LLM 偶尔失败 - 30% 概率失败
        if random.random() < 0.3:
            print(f"❌ LLM服务暂时不可用 (模拟错误)")
            raise ConnectionError("LLM服务连接失败")

        last_message = messages[-1] if messages else None
        content = f"基于查询结果，我为您找到了相关的艺术家信息。这是第{self.call_count}次成功调用的响应。"
        print(f"✅ LLM响应生成成功")
        return AIMessage(content=content)

# 初始化模拟组件
db = MockSQLDatabase()
model = MockChatOpenAI(model="Mock-GPT-4")

# 定义图的状态
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

def query_database(state):
    """查询数据库节点 - 配置了特定异常重试"""
    print(f"\n📊 执行数据库查询节点...")
    query_result = db.run("SELECT * FROM Artist LIMIT 10;")
    return {"messages": [AIMessage(content=f"数据库查询结果: {query_result}")]}

def call_model(state):
    """调用模型节点 - 配置了最大重试次数"""
    print(f"\n🧠 执行模型调用节点...")
    response = model.invoke(state["messages"])
    return {"messages": [response]}

def user_input_node(state):
    """用户输入节点"""
    print(f"\n👤 添加用户输入...")
    user_message = HumanMessage(content="请帮我查询一些著名艺术家的信息")
    print(f"📝 用户问题: {user_message.content}")
    return {"messages": [user_message]}

# 定义图 builder
print("🏗️ 构建带重试策略的 LangGraph...")
builder = StateGraph(AgentState)

# 添加用户输入节点
builder.add_node("user_input", user_input_node)

# 为 call_model 节点配置重试策略: 最大重试 5 次，包含退避策略
builder.add_node(
    "model",
    call_model,
    retry=RetryPolicy(
        max_attempts=5,           # 最大重试5次
        initial_interval=0.5,     # 初始重试间隔0.5秒
        backoff_factor=2.0,       # 退避因子2.0 (指数退避)
        max_interval=8.0,         # 最大重试间隔8秒
        jitter=True              # 添加随机抖动
    )
)

# 为 query_database 节点配置重试策略: 针对 sqlite3.OperationalError 异常进行重试
builder.add_node(
    "query_database",
    query_database,
    retry=RetryPolicy(
        retry_on=sqlite3.OperationalError,  # 只对数据库操作错误重试
        max_attempts=4,                     # 最大重试4次
        initial_interval=1.0,               # 初始间隔1秒
        backoff_factor=1.5                  # 较小的退避因子
    )
)

# 定义边
builder.add_edge(START, "user_input")
builder.add_edge("user_input", "model")
builder.add_edge("model", "query_database")
builder.add_edge("query_database", END)

# 编译图
graph = builder.compile()
print("✅ 图构建完成！")

# 测试运行
print("\n=== 🚀 重试策略演示 ===")
print("📋 测试场景:")
print("  - 数据库节点: 前2次调用会失败，第3次成功")
print("  - 模型节点: 30% 概率失败，会自动重试")
print("  - 两个节点都配置了不同的重试策略\n")

try:
    # 运行图
    result = graph.invoke({"messages": []})

    print(f"\n=== ✨ 执行完成 ===")
    print(f"📊 最终消息数量: {len(result['messages'])}")
    for i, msg in enumerate(result['messages']):
        print(f"  {i+1}. [{msg.__class__.__name__}] {msg.content[:60]}...")

    print(f"\n=== 📈 重试统计 ===")
    print(f"🗄️ 数据库调用次数: {db.call_count}")
    print(f"🤖 模型调用次数: {model.call_count}")

except Exception as e:
    print(f"\n❌ 执行失败: {e}")
    print(f"🗄️ 数据库调用次数: {db.call_count}")
    print(f"🤖 模型调用次数: {model.call_count}")