import json

# 手工维护的两个字典
field_map = {
    "suricata": {
        "log_type": "ThreatLevel"
    },
    "firewalld": {
        "host": "SourceIp",
        "port": "SourcePort",
        "target_port": "DestinationPort",
    },
    "feishu": {
        "msg": "Description"
    }
}

static_content = {
    "suricata": {
        "description": "日志分析工具",
        "node_name": "suricata",

    },
    "firewalld": {
        "passwd": 123456,
        "user": "attacker",
        "node_name": "firewalld_manager",
        "description": "防火墙管理工具",
        "zone": "trusted"
    },
    "feishu": {
        "hook_uuid": "secret-key",
        "description": "飞书通知工具"
    }
}

# 读取 JSON 文件
with open("output.json", "r", encoding="utf-8") as output_file, \
     open("group2.json", "r", encoding="utf-8") as group_file:
    output_data = json.load(output_file)
    group_data = json.load(group_file)

# 获取 node_info 部分
nodes = output_data.get("node_info", {})

# 遍历每个节点
for node_id, node_info in nodes.items():
    information = node_info.get("information", {})
    data = information.get("data", {})
    if not data:
        continue  # 如果没有 data 字段，跳过此节点

    app_id = node_info.get("app_id")
    if not app_id:
        continue  # 如果没有 app_id，跳过此节点

    # 获取对应的字段映射表和静态内容
    app_field_map = field_map.get(app_id, {})
    app_static_content = static_content.get(app_id, {})

    # 遍历当前节点 data 中的字段
    for field in data.keys():
        # 1. 尝试从 field_map 获取对应的字段内容
        if field in app_field_map:
            group_field = app_field_map[field]
            if group_field in group_data:
                data[field] = group_data[group_field]
                continue

        # 2. 如果 field_map 没有匹配，尝试从 static_content 获取静态内容
        if field in app_static_content:
            data[field] = app_static_content[field]

    # 更新信息中的 data
    information["data"] = data
    node_info["information"] = information

# 保存更新后的 JSON 文件
with open("output_updated.json", "w", encoding="utf-8") as updated_file:
    json.dump(output_data, updated_file, indent=4, ensure_ascii=False)

print("已成功填充所有节点的信息，并保存到 output_updated.json 文件中。")
