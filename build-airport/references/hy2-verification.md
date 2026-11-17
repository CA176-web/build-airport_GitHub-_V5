# HY2 连通测试与重启自启验收

仅在用户已要求部署或修复目标实例时执行。本文件把 HY2 的完成条件分成五步；失败就修复对应阶段，不能把监听、平台 Running 或链接生成成功写成节点验收成功。

## 1. 固定本次配置与端口

在本次私密工作目录记录实例标识、服务名、核心版本、配置路径、实际入口、UDP 内外端口和最终链接文件；不要写进技能目录。记录任务时间，方便对应前后证据。

核对三处使用同一组参数：

| 位置 | 核对项 |
| --- | --- |
| 平台转发 | 正确实例、入口地址族、协议 UDP、外部端口 → 内部端口 |
| 服务端 | UDP 监听内部端口；认证、混淆、证书路径及 SNI 与计划一致 |
| 最终 URI | 实际公网入口与外部端口；认证、混淆、SNI、pinSHA256 与服务端一致 |

新端口先按 [workflow.md](workflow.md) 与完整历史集合核对；旧 TCP 数字仍避让。使用高位端口不代表平台已经开放 UDP。若配置了防火墙，仅检查和调整本次端口所需的 UDP 规则，保留其他规则和管理通道。

## 2. 检查落盘和服务状态

先按 [recovery.md](recovery.md) 核验下载副本与最终二进制摘要。公共证书另外检查有效期与 SAN；生成器只验证格式并计算指纹。自签证书按同一 SNI 创建 DNS SAN，确认运行服务能读取证书、私钥和配置。

可用 OpenSSL 查看公共证书，不输出私钥：

```sh
openssl x509 -in /etc/hysteria/server.crt -noout -dates -ext subjectAltName -fingerprint -sha256
```

按实际单元名检查 systemd 的 `is-enabled`、`is-active`、`show` 中的 `MainPID`、`ExecMainStatus` 和启动时间，检查本次服务 journal 和内部端口的 UDP 监听。OpenRC 使用对应运行级别和服务状态检查。配置加载失败、权限错误或反复崩溃时先修复，不继续生成“已验证”结果。

自签证书固定指纹时，以实际证书 DER SHA-256 为准。不要为消除报错移除 pinSHA256；旧指纹与重签后的证书不能混用。证书与 SNI 的关系见 [官方 TLS 配置](https://v2.hysteria.network/docs/advanced/Full-Server-Config/#tls)。

## 3. 从外部使用最终 URI

在用户授权的测试机启动独立 Hysteria 客户端，使用本次专属配置和空闲回环端口，记录准确 PID 与启动时间。以最终链接 TXT 的整行为输入，构造以下 YAML 或等价 JSON；程序生成配置以避免引号、反斜杠和特殊字符被 shell 改写：

```yaml
server: "<EXACT_DELIVERY_URI>"
socks5:
  listen: "127.0.0.1:<FREE_LOCAL_TEST_PORT>"
```

URI 已包含认证、TLS 和混淆参数时，不在其他字段重复覆盖。此方式见 [官方客户端 server 配置](https://v2.hysteria.network/docs/advanced/Full-Client-Config/#server-address)。Windows 辅助进程隐藏启动；不覆盖现有 v2rayN 配置，不开 TUN，不修改系统代理。

确认本次日志中的握手/认证成功，再经该 SOCKS 请求 HTTPS。启动客户端命令以当前版本 `--help` 为准。只看到本地 SOCKS 监听不算上游握手通过。

下面是 HTTPS 探测的参数传递示例；作为 Python 文件运行并传入本次已确认的本地测试端口。`--disable` 放在第一个选项以忽略默认 curl 配置；空 `--noproxy` 保留为独立参数，避免被 shell 丢掉后意外直连。`socks5h` 由代理路径解析目标域名。

```python
import os
import shutil
import subprocess
import sys

port = int(sys.argv[1])
if not 1 <= port <= 65535:
    raise SystemExit("Invalid local test port")
curl = shutil.which("curl.exe" if os.name == "nt" else "curl")
if curl is None:
    raise SystemExit("curl is required")
result = subprocess.run(
    [curl, "--disable", "--noproxy", "",
     "--proxy", f"socks5h://127.0.0.1:{port}",
     "--connect-timeout", "10", "--max-time", "20",
     "--silent", "--show-error", "--fail",
     "--output", os.devnull, "--write-out", "%{http_code}",
     "https://www.gstatic.com/generate_204"],
    shell=False, capture_output=True, text=True, timeout=25,
    creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
)
print(f"curl_exit={result.returncode}; HTTP={result.stdout.strip()}")
if result.returncode != 0 or result.stdout.strip() != "204":
    raise SystemExit("HTTPS test failed; inspect the task client/server logs")
```

保留探测时间、退出码、HTTP 状态、对应客户端握手和所用配置文件摘要。这个 HTTPS 请求在 HY2 隧道内承载 TCP 业务，客户端到节点的外层连接仍为 UDP/QUIC。公网 TCP 端口测试不能代替这个验证。curl 选项以 [官方手册](https://curl.se/docs/manpage.html) 为准。

需要出口国家或 IPPure 验收时，复用该代理路径查询并核对页面；本次没有出口检测授权或要求时不额外查询测试机的直接 IP。原生客户端通过而尚未实际导入 v2rayN 时，交付写“HY2 实测通过，附 v2rayN 导入步骤”，不写“已在 v2rayN 验证”。

## 4. 重启后建立全新连接

对本次新建、已授权重装或已获准重启的实例进行验证。有其他需保留工作负载且重启范围未明确时，先说明具体影响；安装技能不授权任何重启。

1. 保存重启前的服务状态、正式二进制/公共证书摘要和上述 HTTPS 结果。记录最终 URI 文件摘要，用于确认重启前后测试输入相同。
2. 记录目标实例和发起时间，执行一次实例/容器重启；服务进程 restart 不能替代实例开机自启验证。平台返回“受理”后继续等待实际恢复，短周期查看状态并保持进度更新。
3. 通过服务启动时间、平台任务完成记录和控制台重新可用等证据核实确实重启。容器可能共享宿主机 boot ID/uptime，不能只用该值判断实例没有重启或已经重启。
4. **不手工 start 服务**，读取自启配置、运行状态、UDP 监听和重启后的服务日志。确认持久文件存在，二进制及公共证书摘要与预期一致。平台保留的转发规则再次核对。
5. 结束本次旧测试客户端，按准确 PID 及启动时间确认后清理；以相同最终 URI 启动新客户端，重新完成握手和 HTTPS。必要时再次核验本次要求的出口指标。不能沿用旧连接或旧日志作证。

重启后启动失败需要修复时，可以修复并手工启动以定位问题，但这轮不计为自启通过。修复后重新完成一次获授权的实例重启和全新连接验证；重启次数保持必要且有界。同类故障复现且没有新线索时，停止循环重启，报告具体故障。

## 5. 验收记录和结束条件

每次填写实际结果，未执行写“未验证”：

| 检查 | 通过依据 |
| --- | --- |
| 端口避让 | 新端口与历史集合无交集，平台实际 UDP 映射与计划一致 |
| 文件完整性 | 下载和最终副本摘要匹配，重启后正式文件仍符合预期 |
| 初次连通 | 最终 URI 握手成功，同次代理 HTTPS 退出码 0、预期 HTTP 状态 |
| 自启 | 实例真实重启；无需人工启动服务，全新客户端连接及 HTTPS 通过 |
| 按需出口验收 | 从目标节点取得本次要求的国家/IPPure 结果，记录时间 |
| 交付一致性 | TXT 中 URI 与通过测试的 URI 相同；管理资料另存 |

只关闭本次进程、浏览器会话和临时文件。服务已部署但某项失败时按 [delivery-format.md](delivery-format.md) 标明阶段；保留可继续定位的证据，不把失效链接标为“可用”。确认成功后将所有本次实际占用过的云端端口按 [ports.md](ports.md) 追加到本地私密避让记录，即使后来撤回映射，也保留历史数字。
