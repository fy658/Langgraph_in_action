from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from typing import TypedDict
from dotenv import load_dotenv

load_dotenv()

# 首先，让我们创建一个包含更多状态字段的增强版子图
from typing import TypedDict

class EnhancedSubtaskState(TypedDict):
    subtask_input: str
    subtask_result: str
    city: str  # 新增城市字段
    temperature: int  # 新增温度字段

class EnhancedMainState(TypedDict):
    main_topic: str
    processed_data: str
    final_output: str
    user_location: str  # 新增用户位置字段

# 增强的子图节点函数
def enhanced_subtask_processor(state: EnhancedSubtaskState):
    """增强的子图处理节点"""
    city = state.get("city", "未知城市")
    temp = state.get("temperature", 20)
    return {
        "subtask_result": f"处理完成: {state['subtask_input']} (位置: {city}, 温度: {temp}°C) -> 子任务结果"
    }

def enhanced_subtask_formatter(state: EnhancedSubtaskState):
    """增强的子图格式化节点"""
    return {
        "subtask_result": f"[格式化] {state['subtask_result']}"
    }

# 构建增强版子图
enhanced_subgraph = StateGraph(EnhancedSubtaskState)
enhanced_subgraph.add_node("process", enhanced_subtask_processor)
enhanced_subgraph.add_node("format", enhanced_subtask_formatter)
enhanced_subgraph.add_edge(START, "process")
enhanced_subgraph.add_edge("process", "format")
enhanced_subgraph.add_edge("format", END)
compiled_enhanced_subgraph = enhanced_subgraph.compile(checkpointer=MemorySaver())

# 增强版主图节点函数
def enhanced_prepare_data(state: EnhancedMainState):
    """增强的数据准备"""
    return {
        "processed_data": f"预处理: {state['main_topic']}",
        "user_location": state.get("user_location", "默认位置")
    }

def enhanced_call_subgraph_node(state: EnhancedMainState):
    """调用增强版子图的节点"""
    subgraph_config = {"configurable": {"thread_id": f"enhanced_sub_{state['main_topic']}"}}
    
    # 调用子图处理，传递更多参数
    subgraph_input = {
        "subtask_input": state["processed_data"],
        "city": "beijing",  # 默认城市
        "temperature": 25   # 默认温度
    }
    subgraph_result = compiled_enhanced_subgraph.invoke(subgraph_input, subgraph_config)
    
    return {
        "processed_data": subgraph_result["subtask_result"]
    }

def enhanced_finalize_output(state: EnhancedMainState):
    """生成增强的最终输出"""
    return {
        "final_output": f"最终结果: {state['processed_data']} (用户位置: {state.get('user_location', '未知')})"
    }

# 构建增强版主图
enhanced_main_graph = StateGraph(EnhancedMainState)
enhanced_main_graph.add_node("prepare", enhanced_prepare_data)
enhanced_main_graph.add_node("subgraph_call", enhanced_call_subgraph_node)
enhanced_main_graph.add_node("finalize", enhanced_finalize_output)

enhanced_main_graph.add_edge(START, "prepare")
enhanced_main_graph.add_edge("prepare", "subgraph_call")
enhanced_main_graph.add_edge("subgraph_call", "finalize")
enhanced_main_graph.add_edge("finalize", END)

# 编译增强版主图
enhanced_hierarchical_graph = enhanced_main_graph.compile(checkpointer=MemorySaver())

# 运行增强版智能体并演示状态更新
print("=== 步骤 1: 运行增强版层次化智能体 ===")
enhanced_config = {"configurable": {"thread_id": "enhanced_hierarchical_thread"}}

# 初始运行
initial_result = enhanced_hierarchical_graph.invoke(
    {"main_topic": "天气分析任务", "user_location": "shanghai"}, 
    enhanced_config
)
print("初始执行结果：", initial_result)

print("\n" + "="*60)
print("=== 步骤 2: 获取当前状态 ===")

# 获取主图状态
main_state = enhanced_hierarchical_graph.get_state(enhanced_config)
print("主图当前状态：", main_state.values)

# 获取子图状态
subgraph_config = {"configurable": {"thread_id": "enhanced_sub_天气分析任务"}}
subgraph_state = compiled_enhanced_subgraph.get_state(subgraph_config)
print("子图当前状态：", subgraph_state.values)

print("\n" + "="*60)
print("=== 步骤 3: 更新主图状态 ===")

# 更新主图状态中的 user_location 字段
print("更新主图状态: user_location 从 'shanghai' 改为 'guangzhou'")
updated_main_config = enhanced_hierarchical_graph.update_state(
    enhanced_config,
    {"user_location": "guangzhou"}
)
print("主图状态更新完成，新配置：", updated_main_config)

# 查看更新后的主图状态
updated_main_state = enhanced_hierarchical_graph.get_state(updated_main_config)
print("更新后的主图状态：", updated_main_state.values)

print("\n" + "="*60)
print("=== 步骤 4: 更新子图状态 ===")

# 更新子图状态中的 city 字段（按照你的要求）
print("更新子图状态: city 从 'beijing' 改为 'la', temperature 从 25 改为 18")
updated_subgraph_config = compiled_enhanced_subgraph.update_state(
    subgraph_config,  # 将子图状态的 config 作为第一个参数传入
    {"city": "la", "temperature": 18}  # updates 参数指定要更新的状态键值对
)
print("子图状态更新完成，新配置：", updated_subgraph_config)

# 查看更新后的子图状态
updated_subgraph_state = compiled_enhanced_subgraph.get_state(updated_subgraph_config)
print("更新后的子图状态：", updated_subgraph_state.values)

print("\n" + "="*60)
print("=== 步骤 5: 从更新的状态继续执行 ===")

# 从更新的子图状态继续执行（重新处理）
print("从更新的子图状态继续执行:")
for chunk in compiled_enhanced_subgraph.stream(None, updated_subgraph_config, stream_mode="values"):
    print("子图执行结果：", chunk)