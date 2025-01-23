#!/usr/bin/env python3
# coding: utf-8

import os
import json
from py2neo import Graph, Node, Relationship

class SecurityGraph:
    def __init__(self):
        # 获取当前目录的路径
        cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        self.data_path = os.path.join(cur_dir, 'data/cyber_security.json')  # 使用 god.json 作为数据文件
        self.export_dir = os.path.join(cur_dir, 'dict')  # 数据导出目录

        # 使用 bolt 协议连接 Neo4j 数据库
        self.g = Graph(
            "bolt://localhost:7687",  # Neo4j 数据库的地址和端口
            auth=("neo4j", "cyw123857496")  # 数据库的用户名和密码
        )

        # 创建导出目录
        os.makedirs(self.export_dir, exist_ok=True)

    '''读取数据'''
    def read_data(self):
        with open(self.data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data

    '''创建节点'''
    def create_node(self, label, nodes, properties, color):
        for node_name in nodes:
            node_properties = properties.get(node_name, {})
            node = Node(label, name=node_name, color=color, **node_properties)
            self.g.create(node)

    '''创建关系'''
    def create_relationship(self, start_node, end_node, edges, rel_type):
        for edge in edges:
            p = edge[0]
            q = edge[1]
            query = f"""
            MATCH (a:{start_node}),(b:{end_node})
            WHERE a.name='{p}' AND b.name='{q}'
            CREATE (a)-[r:{rel_type}]->(b)
            """
            self.g.run(query)

    '''导出数据到文本文件'''
    def export_data(self, data):
        entities = {
            'security_events': set(),
            'maintenance_methods': set(),
            'check_items': set(),
            'device_software_ids': set(),
            'vendor_names': set(),
            'harm_names': set(),
        }

        # 处理数据
        for item in data:
            event_name = item['event_name']
            entities['security_events'].add(event_name)

            if 'maintenance_method' in item:
                methods = item['maintenance_method'].split(',')
                entities['maintenance_methods'].update(method.strip() for method in methods)

            if 'check_item' in item:
                checks = item['check_item'].split(',')
                entities['check_items'].update(check.strip() for check in checks)

            if 'device_software_id' in item:
                software_ids = item['device_software_id'].split(',')
                entities['device_software_ids'].update(software.strip() for software in software_ids)

            if 'vendor_name' in item:
                vendors = item['vendor_name'].split(',')
                entities['vendor_names'].update(vendor.strip() for vendor in vendors)

            if 'harm_name' in item:
                harms = item['harm_name'].split(',')
                entities['harm_names'].update(harm.strip() for harm in harms)

        # 导出每种实体到不同的文件
        for entity_name, entity_values in entities.items():
            with open(os.path.join(self.export_dir, f'{entity_name}.txt'), 'w', encoding='utf-8') as f:
                for value in entity_values:
                    f.write(value + '\n')

    '''创建知识图谱'''
    def create_graph(self):
        # 清空图谱
        self.clear_graph()

        # 读取数据并处理
        data = self.read_data()
        events = set()
        maintenance_methods = set()
        check_items = set()
        device_software_ids = set()
        vendor_names = set()
        harm_names = set()

        event_method_rels = []
        event_device_rels = []
        vendor_device_rels = []
        event_check_rels = []
        event_harm_rels = []

        node_properties = {}

        # 处理数据
        for item in data:
            event_name = item['event_name']
            events.add(event_name)

            # 保存节点属性
            node_properties[event_name] = {
                'description': item.get('description', ''),
                'preventive_measures': item.get('prevention_measures', ''),
                'attack_reason': item.get('attack_cause', ''),
                'defective_software': item.get('defective_device_software', ''),
                'detailed_solution': item.get('configuration_solution', ''),
            }

            if 'maintenance_method' in item:
                methods = item['maintenance_method'].split(',')
                maintenance_methods.update(method.strip() for method in methods)
                event_method_rels.extend([(event_name, method.strip()) for method in methods])

            if 'check_item' in item:
                checks = item['check_item'].split(',')
                check_items.update(check.strip() for check in checks)
                event_check_rels.extend([(event_name, check.strip()) for check in checks])

            if 'device_software_id' in item:
                software_ids = item['device_software_id'].split(',')
                device_software_ids.update(software.strip() for software in software_ids)
                event_device_rels.extend([(event_name, software.strip()) for software in software_ids])

            if 'vendor_name' in item:
                vendors = item['vendor_name'].split(',')
                vendor_names.update(vendor.strip() for vendor in vendors)
                vendor_device_rels.extend([(vendor.strip(), software.strip()) for vendor in vendors for software in software_ids])

            if 'harm_name' in item:
                harms = item['harm_name'].split(',')
                harm_names.update(harm.strip() for harm in harms)
                event_harm_rels.extend([(event_name, harm.strip()) for harm in harms])

        # 创建节点
        self.create_node('SecurityEvent', events, node_properties, 'red')
        self.create_node('MaintenanceMethod', maintenance_methods, {}, 'blue')
        self.create_node('CheckItem', check_items, {}, 'green')
        self.create_node('DeviceSoftware', device_software_ids, {}, 'yellow')
        self.create_node('Vendor', vendor_names, {}, 'purple')
        self.create_node('Harm', harm_names, {}, 'orange')

        # 创建关系
        self.create_relationship('SecurityEvent', 'MaintenanceMethod', event_method_rels, 'USES')
        self.create_relationship('SecurityEvent', 'DeviceSoftware', event_device_rels, 'AFFECTS')
        self.create_relationship('Vendor', 'DeviceSoftware', vendor_device_rels, 'PROVIDES')
        self.create_relationship('SecurityEvent', 'CheckItem', event_check_rels, 'REQUIRES')
        self.create_relationship('SecurityEvent', 'Harm', event_harm_rels, 'CAUSES')

        # 导出数据
        self.export_data(data)

        # 输出如何查看图谱的查询语句
        print("图谱构建完成！")
        print("您可以使用以下查询语句来查看图知识库：")
        print("MATCH (n)-[r]->(m)")
        print("RETURN n, r, m")

    '''清空图谱'''
    def clear_graph(self):
        print("清空现有图谱...")
        self.g.run("MATCH (n) DETACH DELETE n")

if __name__ == '__main__':
    handler = SecurityGraph()
    handler.create_graph()
