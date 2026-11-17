# Xray 配置、服务和连接模板

本文件提供结构示例。全部占位符由本次生成的值替换，端口要写为 JSON 整数。选择当前 Xray 版本后核对官方文档，服务端和测试客户端均执行该版本的配置检查。

## 配置前准备

| 参数 | 来源与用途 |
| --- | --- |
| UUID | 本次新生成，服务端用户与客户端相同 |
| X25519 私钥 | 当前 Xray 生成，只写服务端 |
| X25519 公钥 | 与私钥配对，写客户端与 URI 的 pbk |
| Short ID | 安全随机生成，通常用 8 字节的 16 个十六进制字符 |
| Target | 经过服务器实际测试的 TLS 目标，例如 `www.microsoft.com:443` |
| SNI | 目标证书覆盖、服务端允许的域名，正常域名文本，不加反斜杠 |
| 内部端口 | 实例 Xray 监听，使用新选定的端口 |
| 公网入口与外部端口 | 服务商 TCP 映射入口，客户端必须连接这里 |
| 本地测试端口 | 电脑回环地址上本次空闲端口 |

可以用当前版本支持的 `xray uuid`、`xray x25519` 生成所需值。不要重用历史截图或教程中的 UUID、私钥、Short ID。

## 服务端结构

```json
{
  "log": { "loglevel": "warning" },
  "inbounds": [{
    "tag": "vless-reality",
    "listen": "0.0.0.0",
    "port": "__PROXY_INTERNAL_PORT_AS_INTEGER__",
    "protocol": "vless",
    "settings": {
      "clients": [{ "id": "__NEW_UUID__", "flow": "xtls-rprx-vision" }],
      "decryption": "none"
    },
    "streamSettings": {
      "network": "tcp",
      "security": "reality",
      "realitySettings": {
        "show": false,
        "target": "__TARGET_HOST__:443",
        "xver": 0,
        "serverNames": ["__SNI__"],
        "privateKey": "__PRIVATE_KEY__",
        "shortIds": ["__SHORT_ID__"]
      }
    }
  }],
  "outbounds": [{ "protocol": "freedom", "tag": "direct" }]
}
```

生成真实配置时，用语言的 JSON 序列化器处理数值与字符串，不用不受控的 shell 字符串拼接。不要把私钥配置放入技能目录。

常用安装布局：

```text
/usr/local/bin/xray
/usr/local/etc/xray/config.json
/var/log/xray/
```

创建专用服务账号与必要目录，保证服务账号可读配置、可写日志。配置含私钥，限制权限，例如所有者 xray、模式 600。然后运行：

```sh
/usr/local/bin/xray run -test -config /usr/local/etc/xray/config.json
```

## 服务管理

以下仅适用于已确认使用 OpenRC 的实例。先安装当前系统需要的服务管理组件，保证监督程序可用，不把 systemd 命令用于 Alpine/OpenRC。

`/etc/init.d/xray` 的结构：

```sh
#!/sbin/openrc-run
name="xray"
description="Private VLESS REALITY service"
command="/usr/local/bin/xray"
command_args="run -config /usr/local/etc/xray/config.json"
command_user="xray:xray"
supervisor="supervise-daemon"
respawn_delay=3
respawn_max=0
output_log="/var/log/xray/service.log"
error_log="/var/log/xray/error.log"
```

文件设为可执行后，用 `rc-update add xray default`、`rc-service xray start`、`rc-service xray status` 管理。检查实际监听，随后重启新实例验证持久化和自启。

若 PID 1 为 systemd，则创建适合该环境的 systemd unit，指定服务账号、ExecStart 和 Restart，并启用自启。其他容器初始化方式按宿主提供的持久启动机制处理。每次以实际重启后的结果验收。

## 独立测试客户端结构

仅监听回环，使用真实公网入口及**外部端口**。这是测试核心配置，不覆盖用户现有 v2rayN 配置。

```json
{
  "log": { "loglevel": "warning" },
  "inbounds": [{
    "listen": "127.0.0.1",
    "port": "__LOCAL_TEST_PORT_AS_INTEGER__",
    "protocol": "socks",
    "settings": { "auth": "noauth", "udp": false }
  }],
  "outbounds": [{
    "protocol": "vless",
    "settings": {
      "vnext": [{
        "address": "__PUBLIC_INGRESS__",
        "port": "__PROXY_EXTERNAL_PORT_AS_INTEGER__",
        "users": [{
          "id": "__NEW_UUID__",
          "encryption": "none",
          "flow": "xtls-rprx-vision"
        }]
      }]
    },
    "streamSettings": {
      "network": "tcp",
      "security": "reality",
      "realitySettings": {
        "serverName": "__SNI__",
        "fingerprint": "chrome",
        "publicKey": "__PUBLIC_KEY__",
        "shortId": "__SHORT_ID__",
        "spiderX": "/__RANDOM_PATH__"
      }
    }
  }]
}
```

上述字段为配置结构示例。当前版本若使用 `password` 等字段名，按该版本官方说明调整并再次配置检查；不要在同一配置中堆叠互相矛盾的别名。

客户端启动后显式经过本地 SOCKS 请求 HTTPS 与 IPPure。参数采用结构化传参，避免 PowerShell 的空字符串转义导致 NO_PROXY 选项失效。不要从直接出口取得结果冒充节点检测。

## URI 结构

```text
vless://<UUID>@<PUBLIC_INGRESS>:<PROXY_EXTERNAL_PORT>?encryption=none&flow=xtls-rprx-vision&fp=chrome&pbk=<PUBLIC_KEY>&security=reality&sid=<SHORT_ID>&sni=<SNI>&spx=<ENCODED_PATH>&type=tcp#<ENCODED_NAME>
```

使用 URI 库编码查询值和名称，保留一整行。IPv6 入口使用方括号。`pbk` 使用对应公钥，不是私钥；`sid` 是服务端允许的一个 Short ID。

如目标和所用客户端确认支持，再附加 `support-x25519mlkem768=true`。普通部署不需要凭空添加额外加密或 MLDSA 参数。

导出前以解析器核对 scheme、hostname、外部 port、UUID、flow、fp、pbk、sid、sni、type，并与当次服务端和映射逐项比较。格式检查通过后还必须执行真实协议连接。
