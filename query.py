#!/usr/bin/env python3
# coding: utf-8

import json
import sys
from py2neo import Graph

class IncidentQuery:
    def __init__(self, data_path="group2.json"):
        # 配置连接到 Neo4j 的参数
        self.g = Graph(
            "bolt://localhost:7687",  # Neo4j 地址
            auth=("neo4j", "cyw123857496")  # Neo4j 用户名和密码
        )
        self.data_path = data_path  # 默认路径为 group2.json

    def read_incident_name(self):
        """从 JSON 文件中读取 IncidentName 字段"""
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("IncidentName", None)
        except FileNotFoundError:
            print(f"文件 {self.data_path} 未找到", file=sys.stderr)
            return None
        except json.JSONDecodeError:
            print(f"文件 {self.data_path} 无法解析为有效的 JSON", file=sys.stderr)
            return None

    def query_configuration_solution(self, incident_name):
        """根据 IncidentName 从 Neo4j 查询 configuration_solution 字段"""
        query = f"""
        MATCH (e:SecurityEvent {{name: '{incident_name}'}})
        RETURN e.detailed_solution AS configuration_solution
        """
        try:
            result = self.g.run(query).data()
            if result:
                return result[0].get("configuration_solution", "未找到匹配的解决方案")
            return "未找到匹配的事件"
        except Exception as e:
            print(f"查询 Neo4j 发生错误: {e}", file=sys.stderr)
            return "查询失败"

    def run(self):
        """主流程"""
        # 读取 IncidentName
        incident_name = self.read_incident_name()
        if not incident_name:
            print("未能从 JSON 文件中读取到 IncidentName 字段", file=sys.stderr)
            return

        # 查询配置解决方案
        solution = self.query_configuration_solution(incident_name)
        print(solution)  # 仅输出查询结果


if __name__ == "__main__":
    # 创建实例并运行
    query_handler = IncidentQuery()
    query_handler.run()
