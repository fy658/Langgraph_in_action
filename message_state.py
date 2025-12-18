from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, trim_messages, RemoveMessage
from langgraph.graph import MessagesState, StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages.utils import count_tokens_approximately
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="Qwen/Qwen3-8B")

# 使用 trim_messages 的节点
def llm_node_with_trim(state: MessagesState):
    print("🤖 LLM节点 (使用 trim_messages)")
    message_history = state['messages']
    print(f"📥 接收到 {len(message_history)} 条消息")

    # 显示原始消息
    for i, msg in enumerate(message_history):
        content_preview = msg.content[:50] + "..." if len(msg.content) > 50 else msg.content
        print(f"  {i+1}. [{msg.__class__.__name__}] {content_preview}")

    # 使用 trim_messages 修剪消息历史
    trimmed_messages = trim_messages(
        message_history,
        max_tokens=200,  # 降低限制以便看到修剪效果
        strategy="last",
        token_counter=count_tokens_approximately,
        allow_partial=False
    )

    print(f"✂️ 修剪后保留 {len(trimmed_messages)} 条消息 (token限制: 200)")

    # 生成回复
    llm_response = llm.invoke(trimmed_messages)
    print(f"💭 生成回复: {llm_response.content}")

    return {"messages": [llm_response]}

# 使用 filter_messages 的节点 (基于 RemoveMessage)
def filter_node(state: MessagesState):
    print("\n🔧 过滤节点 (使用 RemoveMessage)")
    message_history = state['messages']
    print(f"📥 接收到 {len(message_history)} 条消息")

    remove_messages = []

    # 过滤策略：移除包含"你好"或"再见"的寒暄消息
    for msg in message_history:
        if any(greeting in msg.content.lower() for greeting in ["你好",
"再见", "hello", "bye"]):
            print(f"🗑️ 标记移除寒暄消息: {msg.content[:30]}...")
            remove_messages.append(RemoveMessage(id=msg.id))
        # 移除过长的消息
        elif len(msg.content) > 100:
            print(f"🗑️ 标记移除过长消息: {msg.content[:30]}...")
            remove_messages.append(RemoveMessage(id=msg.id))

    if remove_messages:
        print(f"📊 将移除 {len(remove_messages)} 条消息")
        return {"messages": remove_messages}
    else:
        print("✅ 没有需要移除的消息")
        return {}

# 添加用户消息的节点
def add_user_message(state: MessagesState):
    print("\n👤 添加用户消息节点")
    new_message = HumanMessage(content="我想了解人工智能的最新发展，特别是在自然语言处理方面的突破。")
    print(f"➕ 添加消息: {new_message.content}")
    return {"messages": [new_message]}

# 创建图
print("🏗️ 构建消息管理示例图...")
builder = StateGraph(MessagesState)

# 添加节点
builder.add_node("add_message", add_user_message)
builder.add_node("filter", filter_node)
builder.add_node("llm_trim", llm_node_with_trim)

# 定义边
builder.add_edge(START, "add_message")
builder.add_edge("add_message", "filter")
builder.add_edge("filter", "llm_trim")
builder.add_edge("llm_trim", END)

# 编译图
graph = builder.compile()
print("✅ 图构建完成！")

# 准备初始消息历史
print("\n=== 🚀 消息状态管理示例 ===")

initial_messages = [
    SystemMessage(content="你是一个专业的AI助手，擅长回答各种问题。"),
    HumanMessage(content="你好！很高兴见到你。"),
    AIMessage(content="你好！我也很高兴为您服务。有什么可以帮助您的吗？"),
    HumanMessage(content="这是一条很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长的测试消息，用来测试过滤功能。"),
    AIMessage(content="我明白了您的测试消息。"),
    HumanMessage(content="再见！"),
]

print("📋 初始消息历史:")
for i, msg in enumerate(initial_messages):
    content_preview = msg.content[:40] + "..." if len(msg.content) > 40 else msg.content
    print(f"  {i+1}. [{msg.__class__.__name__}] {content_preview}")

# 运行图
result = graph.invoke({"messages": initial_messages})

print(f"\n=== ✨ 最终结果 ===")
print(f"📊 最终消息历史包含 {len(result['messages'])} 条消息:")
for i, msg in enumerate(result['messages']):
    content_preview = msg.content[:50] + "..." if len(msg.content) > 50 else msg.content
    print(f"  {i+1}. [{msg.__class__.__name__}] {content_preview}")



"""
 实际工作流程：
- 添加新的用户消息
- 过滤不需要的消息
- 使用修剪后的消息生成 LLM 回复
- 展示完整的消息管理流程
"""