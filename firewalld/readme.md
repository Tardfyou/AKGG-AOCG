## APP说明

**本机需要安装 firewalld 工具**

## 动作列表
### 添加端口到区域
**参数**

|  参数   | 类型  |  必填   |  备注  |
|  ----  | ----  |  ----  |  ----  |
|**port**|	text|	是	|端口号，例如 8080|
|**zone**|	text|	否	|防火墙区域，默认值为 public|
**返回值：**
```
返回 json 数据
{
  "status": 0,
  "result": "successfully added port 8080 to zone public"
}
```
### 移除端口从区域
**参数**

|  参数   | 类型  |  必填   |  备注  |
|  ----  | ----  |  ----  |  ----  |
|**port**|	text|	是	|端口号，例如 8080|
|**zone**|	text|	否	|防火墙区域，默认值为 public|
**返回值：**
```
返回 json 数据
{
  "status": 0,
  "result": "successfully removed port 8080 from zone public"
}
```
### 重新加载防火墙规则
**参数**

此操作无需参数。

**返回值：**
```
返回 json 数据
{
  "status": 0,
  "result": "firewalld rules reloaded successfully"
}
```
### 阻止IP
**参数**

|  参数   | 类型  |  必填   |  备注  |
|  ----  | ----  |  ----  |  ----  |
|**ip_address**|	text|	是	|要阻止的 IP 地址，例如 192.168.1.100|
**返回值：**

```
返回 json 数据
{
  "status": 0,
  "result": "IP address 192.168.1.100 blocked successfully"
}
```