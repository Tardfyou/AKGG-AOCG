from loguru import logger
import asyncio

async def run_firewalld_command(host, port, user, passwd, command):
    """
    运行 firewalld 相关的命令，并捕获输出。
    """
    try:
        import socket
        import paramiko
    except:
        logger.info("[firewalld_manager] 导入 paramiko 模块失败, 请输入命令 pip install paramiko")
        return {"status": 2, "result": "缺少 paramiko 模块，请 pip install paramiko 安装"}

    try:
        # 建立ssh连接
        ssh = paramiko.SSHClient()
        key = paramiko.AutoAddPolicy()
        ssh.set_missing_host_key_policy(key)
        ssh.connect(host, int(port), user, passwd, timeout=5)

        # 将列表转换为字符串
        command_str = " ".join(command)
        
        stdin, stdout, stderr = ssh.exec_command(command_str)
    except paramiko.ssh_exception.AuthenticationException:
        return {"status": 1, "result": "认证失败"}
    except paramiko.ssh_exception.NoValidConnectionsError:
        return {"status": 1, "result": "连接失败"}
    except socket.gaierror:
        return {"status": 1, "result": "Host 不正确"}
    except Exception as e:
        logger.info("[firewalld_manager] 执行失败 ：{e}", e=e)
        return {"status": 2, "result": f"执行失败：{e}"}
    else:
        err = stderr.read()
        if err == b"":
            return {"status": 0, "result": str(stdout.read().decode("utf-8"))}
        else:
            return {"status": 2, "result": str(err.decode("utf-8"))}

    


async def add_port_to_zone(host,port,user,passwd,target_port, zone="public"):
    """
    将指定端口添加到 firewalld 的指定区域中。
    """
    command = ["firewall-cmd", "--zone", zone, "--add-port", f"{target_port}/tcp", "--permanent"]
    return await run_firewalld_command(host,port,user,passwd,command)


async def remove_port_from_zone(host,port,user,passwd,target_port, zone="public"):
    """
    从 firewalld 的指定区域中移除指定端口。
    """
    command = ["firewall-cmd", "--zone", zone, "--remove-port", f"{target_port}/tcp", "--permanent"]
    return await run_firewalld_command(host,port,user,passwd,command)


async def reload_firewalld(host,port,user,passwd):
    """
    重新加载 firewalld 的规则。
    """
    command = ["firewall-cmd", "--reload"]
    return await run_firewalld_command(host,port,user,passwd,command)


async def block_ip(host, port, user, passwd, ip_address):
    """
    禁止指定 IP 的所有流量。
    """
    # 构建完整的 rich rule 规则字符串
    rule = f"rule family='ipv4' source address='{ip_address}' reject"
    
    # 将命令作为一个完整的字符串传递
    command = [
        "firewall-cmd",
        "--permanent",
        f"--add-rich-rule=\"{rule}\""
    ]
    
    logger.info("Executing command: " + " ".join(command))  # 打印命令用于调试
    
    return await run_firewalld_command(host, port, user, passwd, command)