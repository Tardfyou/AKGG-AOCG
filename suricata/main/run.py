from loguru import logger
import requests
import json
import sys

async def process_logs(log_type):
    """
    处理 Suricata 日志数据。
      param log_type: 日志类型，'stats' 表示监控统计信息，'alert' 表示警报信息
      return: 处理后的日志数据
    """
    
    log_file = '/var/log/suricata/eve.json'
    logger.info("Suricata APP执行参数为: {log_type}", log_type=log_type)
    
    # 读取日志文件
    try:
        with open(log_file, 'r') as f:
            log_data = f.readlines()
        
        if log_type == 'stats':
            # 处理并返回监控部分的统计信息
            stats = [json.loads(line) for line in log_data if 'event_type' in json.loads(line) and json.loads(line)['event_type'] == 'stats']
            formatted_stats = json.dumps(stats, indent=2)  # 将数据格式化为 JSON 字符串
            logger.info("[Suricata log] 执行成功:监控部分统计信息")
            return {"status": 0, "result": formatted_stats}
        
        elif log_type == 'alert':
            # 处理并返回警报信息
            alerts = [json.loads(line) for line in log_data if 'alert' in json.loads(line)]
            formatted_alerts = json.dumps(alerts, indent=2)  # 将数据格式化为 JSON 字符串
            logger.info("[Suricata log] 执行成功:警报信息.")
            return {"status": 0, "result": formatted_alerts}
        
        else:
            logger.error("[Suricata log] 执行失败:Invalid log type specified. Use 'stats' or 'alert'.")
            return {"status": 1,"result":"error: Invalid log type specified. Use 'stats' or 'alert'."}

    except FileNotFoundError:
        logger.error("[Suricata log] 执行失败:Log file not found, please confirm the file path.")
        return {"status": 2, "result":"error: Log file not found."}
    except json.JSONDecodeError:
        logger.error("[Suricata log] 执行失败:Error deoding JSON from log file.")
        return {"status": 2, "result":"error: Error deoding JSON from log file."}
     

"""
不一定需要的功能
更新 Suricata 规则集。
return: 更新结果

async def update_suricata_rules():
    # 导入模块
    try:
        import subprocess
    except ImportError:
        logger.info("[Suricata Update] 导入 subprocess 模块失败, 请输入命令 pip install subprocess")
        return {"status": 2, "result": "缺少 subprocess 模块，请 pip install subprocess 安装"}
    
    try:
        command = ['suricata-update']
        
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            logger.error(f"[Suricata Update] 执行失败: {stderr.decode('utf-8')}")
            return {"status": 2, "result": stderr.decode('utf-8')}
        
        logger.info(f"[Suricata Update] 执行成功: {stdout.decode('utf-8')}")
        return {"status": 0, "result": stdout.decode('utf-8')}

    except Exception as e:
        logger.error(f"[Suricata Update] 运行时发生异常: {str(e)}")
        return {"status": 1, "result": str(e)}

"""     
"""
# 以下用于测试
if __name__ == '__main__':
    # 导入异步库
    import asyncio

    # 测试函数
    async def test():
        result1 = await process_logs(alerts)
        print(json.dumps(result1, indent=2))
        
        #result2 = await process_logs(stats)
        #print(json.dumps(result2, indent=2))


    # 加入异步队列
    async def main(): await asyncio.gather(test())

    # 启动执行
    asyncio.run(main())
"""
