#!/usr/bin/env python3
# coding: utf-8

import json
import sys
from py2neo import Graph
from sentence_transformers import SentenceTransformer, util

class IncidentQuery:
    def __init__(self, data_path):
        # 配置连接到 Neo4j
        self.g = Graph(
            "bolt://localhost:7687",  
            auth=("neo4j", "cyw123857496")  
        )
        self.data_path = data_path  # 通过传递的路径指定读取的 JSON 文件
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # 语义匹配模型

    def read_incident_name(self):
        """从 JSON 读取 IncidentName"""
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("IncidentName", None)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"读取 JSON 失败: {e}", file=sys.stderr)
            return None

    def query_exact_match(self, incident_name):
        """精确匹配事件名称"""
        query = f"""
        MATCH (e:SecurityEvent {{name: '{incident_name}'}})
        RETURN e.detailed_solution AS configuration_solution
        """
        try:
            result = self.g.run(query).data()
            return result[0]["configuration_solution"] if result else None
        except Exception as e:
            print(f"Neo4j 查询错误: {e}", file=sys.stderr)
            return None

    def query_fuzzy_match(self, incident_name):
        """模糊匹配事件名称"""
        query = f"""
        MATCH (e:SecurityEvent)
        WHERE toLower(e.name) CONTAINS toLower('{incident_name}')
        RETURN e.name AS event_name, e.detailed_solution AS configuration_solution
        """
        try:
            result = self.g.run(query).data()
            return result[0] if result else None
        except Exception as e:
            print(f"Neo4j 模糊查询错误: {e}", file=sys.stderr)
            return None

    def query_semantic_match(self, incident_name):
        """语义匹配事件名称"""
        query = """
        MATCH (e:SecurityEvent)
        RETURN e.name AS event_name, e.detailed_solution AS configuration_solution
        """
        try:
            events = self.g.run(query).data()
            if not events:
                return None

            # 计算事件名称的向量
            event_names = [e["event_name"] for e in events]
            event_embeddings = self.model.encode(event_names, convert_to_tensor=True)
            query_embedding = self.model.encode(incident_name, convert_to_tensor=True)

            # 计算余弦相似度
            similarities = util.cos_sim(query_embedding, event_embeddings).squeeze(0)
            best_idx = similarities.argmax().item()

            # 返回最匹配的事件
            if similarities[best_idx] > 0.7:  # 设定相似度阈值
                return events[best_idx]
            return None
        except Exception as e:
            print(f"Neo4j 语义查询错误: {e}", file=sys.stderr)
            return None

    def query_configuration_solution(self, incident_name):
        """先精准匹配，再模糊匹配，最后语义匹配"""
        # 1. 精确匹配
        exact_match = self.query_exact_match(incident_name)
        if exact_match:
            return exact_match

        # 2. 模糊匹配
        fuzzy_match = self.query_fuzzy_match(incident_name)
        if fuzzy_match:
            return fuzzy_match["configuration_solution"]

        # 3. 语义匹配
        semantic_match = self.query_semantic_match(incident_name)
        if semantic_match:
            return semantic_match["configuration_solution"]

        return "未找到匹配的事件"

    def run(self):
        """主流程"""
        incident_name = self.read_incident_name()
        if not incident_name:
            print("未能从 JSON 读取到 IncidentName", file=sys.stderr)
            return

        solution = self.query_configuration_solution(incident_name)
        print(solution)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("请提供 JSON 文件路径作为参数！", file=sys.stderr)
        sys.exit(1)

    data_path = sys.argv[1]  # 获取命令行传递的文件路径
    query_handler = IncidentQuery(data_path)
    query_handler.run()
