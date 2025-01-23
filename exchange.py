import os
import json
import sys

def parse_input_and_generate_json(input_string, start_node, end_node):
    """
    根据输入的字符串解析每个步骤，并生成对应的 JSON 数据。
    - input_string: 通过 query.py 传递的步骤字符串。
    - start_node: 固定的起始节点信息。
    - end_node: 固定的结束节点信息。
    """
    # 分隔输入步骤
    steps = input_string.split("->")

    # 初始化 JSON 数据结构
    result = {
        "name": steps[0],  # 第一步内容作为 name
        "remarks": "",
        "node_info": {
            "node1": start_node,
            "node2": end_node
        },
        "edge_info": [],
        "local_var_data": [],
        "controller_data": {}
    }

    # 解析中间步骤，生成节点信息
    node_counter = 3  # node3 开始计数
    previous_node = "node1"  # 初始起点为 node1
    for step in steps[2:-1]:  # 跳过 DDOS 和 结束
        try:
            app_id, action_desc = step.split(" ", 1)
        except ValueError:
            raise ValueError(f"步骤 '{step}' 无法正确解析为 app_id 和 action 描述")

        # 确定 app.json 路径
        app_dir = os.path.join("./", app_id)
        app_json_path = os.path.join(app_dir, "app.json")
        print(f"检查 app.json 文件路径: {app_json_path}")  # 调试输出
        if not os.path.exists(app_json_path):
            raise FileNotFoundError(f"{app_json_path} 文件不存在")

        # 读取 app.json 文件
        with open(app_json_path, "r", encoding="utf-8") as f:
            app_config = json.load(f)

        # 构造节点信息
        node_key = f"node{node_counter}"

        # 获取动作和参数
        actions = app_config.get("action", [])
        matched_action = None
        for action in actions:
            # 完全匹配 action_desc 和 action.name
            if action_desc == action.get("name", ""):
                matched_action = action
                break

        if not matched_action:
            raise ValueError(f"未找到与 '{action_desc}' 完全匹配的动作")

        action_func = matched_action.get("func", "")
        # 根据函数名获取函数的参数
        args = app_config.get("args", {}).get(action_func, [])

        # 构建 data.temp 字段
        data_data = {
            "node_name": app_config.get("name", ""),
            "action": action_func,
            "action_name": matched_action.get("name", ""),
            "description": app_config.get("description", "")
        }

        # 添加动态参数字段
        for arg in args:
            data_data[arg.get("key", "")] = f"@({node_key}.result)"  # 假设所有的参数都是来自节点的输出

        # 添加节点信息
        result["node_info"][node_key] = {
            "app_id": app_id,
            "app_type": 1,  # 默认是 1
            "information": {
                "action": actions,
                "app_dir": app_id,
                "args": app_config.get("args", {}),
                "description": app_config.get("description", ""),
                "icon": f"{app_id}/icon.png",
                "identification": app_config.get("identification", ""),
                "is_public": app_config.get("is_public", True),
                "name": app_config.get("name", ""),
                "type": app_config.get("type", ""),
                "version": app_config.get("version", ""),
                "data": data_data
            }
        }

        # 添加边信息
        result["edge_info"].append({
            "source": {"cell": previous_node, "port": "right"},
            "target": {"cell": node_key, "port": "left"}
        })

        # 更新计数器和前置节点
        node_counter += 1
        previous_node = node_key

    # 最后补充结束节点的边信息
    result["edge_info"].append({
        "source": {"cell": previous_node, "port": "right"},
        "target": {"cell": "node2", "port": "left"}
    })

    return result


# 固定的开始和结束节点内容
start_node = {
    "app_id": "start",
    "app_type": 0,  # 修改为 0
}
end_node = {
    "app_id": "end",
    "app_type": 0,  # 修改为 0
}

# 修改 exchange.py
# 在主函数部分修改如下：
if len(sys.argv) < 2:
    print("请提供 query.py 的输出字符串作为参数")
    sys.exit(1)

input_string = sys.argv[1]  # 从命令行获取输入字符串
# 其余部分无需更改


# 调用生成 JSON
try:
    generated_json = parse_input_and_generate_json(input_string, start_node, end_node)
    output_file = "output.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(generated_json, f, ensure_ascii=False, indent=4)
    print(f"成功生成 JSON 文件：{output_file}")
except Exception as e:
    print(f"发生错误: {e}")
