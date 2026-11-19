# HY2：UDP 部署、指纹链接与验收

用于用户明确要求 Hysteria 2 / HY2，或同意把旧节点切换成 HY2 的任务。资源和重装问题先读 [recovery.md](recovery.md)。

## 1. 确认 UDP 路径和核心

在当前实例创建实际协议为 **UDP** 的映射：公网外部端口 → 实例内部监听端口。两个新数字都避让历史集合；客户端填外部端口。备注写“UDP”而协议列仍为 TCP 的规则无效。无需为 HY2 数据连接再开同端口 TCP；SSH 管理仍可使用 TCP。

从 [Hysteria 官方发行页](https://github.com/apernet/hysteria/releases) 获取适合服务器架构、客户端支持的稳定版本。读取当次发行说明和官方摘要；下载后、复制至最终路径后分别校验。公开 GitHub 下载遵循当前环境的下载技能，凭据不经过公共下载代理。不要把历史成功版本固定为永久最新版。

使用独立 `hysteria` 服务账号。生成新的高熵认证密码和 Salamander 混淆密码，记录在本次私密工作文件中。密码不沿用 root 密码，不写入技能。已有成功配置仅需修复映射时，保留原认证资料。

## 2. TLS 与配置

有可用域名和受信任证书时正常验证 TLS。无域名时可生成带 DNS SAN 的自签证书，用独立的本地 SNI 名称和固定证书指纹。SNI 必须与该证书匹配，不照搬旧 REALITY 的伪装域名。

以下 YAML 是字段结构，尖括号内容需替换；也可使用等价 JSON。配置能力以 [官方服务端配置](https://v2.hysteria.network/docs/advanced/Full-Server-Config/) 为准。

```yaml
listen: ":<NEW_INTERNAL_UDP_PORT>"
tls:
  cert: /etc/hysteria/server.crt
  key: /etc/hysteria/server.key
  sniGuard: strict
auth:
  type: password
  password: "<NEW_AUTH_PASSWORD>"
obfs:
  type: salamander
  salamander:
    password: "<NEW_OBFS_PASSWORD>"
```

证书与客户端 SNI 一起生成；证书有效期要覆盖实际维护周期。私钥及认证配置只授予服务账号所需读取权限，例如目录 `0750`、私密文件 `0640 root:hysteria`。私钥只留在服务器或用户要求的私密备份中，生成链接只需公共证书。

自签路径采用 `insecure=1` **并固定本次证书的 `pinSHA256`**。指纹取 DER 编码证书的 SHA-256，不是 PEM 文本的文件摘要，也不是私钥摘要。可在服务器交叉核对：

```sh
openssl x509 -in /etc/hysteria/server.crt -noout -fingerprint -sha256
```

重签或更换证书后必须重新生成链接。尽量从实际公共证书文件计算，不抄截图。必须通过终端转录时按短行分组核对，并以客户端握手验证最终值；遇到指纹错误不能删除指纹来“修好”。相关字段见 [官方客户端配置](https://v2.hysteria.network/docs/advanced/Full-Client-Config/)。

证书续期和服务加载按 [maintenance.md](maintenance.md) 核验。原生 Hysteria 读取证书的行为与面板打包的其他核心可能不同；不将“自动续期成功”当成运行中的新连接已经使用新证书。

核对目标客户端导入后确实保留并执行固定指纹验证。若客户端丢弃 `pinSHA256`，不能交付成仅 `insecure=1` 的配置；改用该客户端支持的受信任证书/自定义 CA 或兼容的客户端方案，再重新验收。

## 3. 服务与资源

按 PID 1 选服务管理器。systemd 环境可采用以下单元；先创建账号和配置目录，再启用。Alpine/OpenRC 使用对应服务脚本，不直接运行 systemctl。

```ini
[Unit]
Description=Hysteria 2 server
Wants=network-online.target
After=network-online.target

[Service]
User=hysteria
Group=hysteria
ExecStart=/usr/local/bin/hysteria server --config /etc/hysteria/config.yaml
Restart=on-failure
RestartSec=3
NoNewPrivileges=true
UMask=0077

[Install]
WantedBy=multi-user.target
```

高位端口不需要额外低端口绑定权限。256 MB 等小实例优先直接运行核心；按实际内存压力调整 Go 内存目标和 QUIC 缓冲参数，不安装无关面板或套用大带宽模板。`GOMEMLIMIT` 是软目标，不能代替系统内存检查。

写入单元后 daemon-reload、enable、start，并检查退出状态、journal 和 UDP 监听。这些检查是部署阶段证据，最终仍需外部客户端测试。

## 4. 生成可导入链接

按 [官方 URI 规范](https://v2.hysteria.network/docs/developers/URI-Scheme/) 使用 `hysteria2://`（别名 `hy2://`）。认证、查询参数和备注分别做 URL 编码；不要把 VLESS UUID、公钥或 flow 拼进 HY2。

```text
hysteria2://<ENCODED_AUTH>@<PUBLIC_HOST>:<EXTERNAL_UDP_PORT>/?sni=<SNI>&insecure=1&pinSHA256=<CERT_SHA256>&obfs=salamander&obfs-password=<ENCODED_OBFS_PASSWORD>#<ENCODED_NAME>
```

自签且使用 Salamander 时，优先运行随技能附带的离线生成器。先把下面的结构存入本次私密工作目录，填入真实部署参数；示例值不是节点：

```json
{
  "host": "example.com",
  "external_port": 50001,
  "auth": "replace-with-new-auth",
  "sni": "hy2-node.local",
  "obfs_password": "replace-with-new-obfs",
  "name": "HY2-node"
}
```

```text
python scripts/hy2_link.py --settings task-private.json --certificate server.crt --output HY2节点链接_V1.txt
```

脚本仅使用 Python 3 标准库，验证公共证书可解析、计算证书指纹、编码链接并创建新 TXT；已有输出文件会拒绝覆盖。证书有效期、SAN 与 SNI 是否匹配须另行检查。它不登录、不联网、不部署，也不证明连通。不要把填好密码的输入文件或生成链接放回技能目录。

## 5. 用同一个交付链接验证

按 [hy2-verification.md](hy2-verification.md) 完成配置核对、外部握手、HTTPS 与重启自启验收。该流程以最终 URI 文件为唯一测试输入，分别保存重启前、重启后结果；修复了认证、端口或证书时，重新生成并测试最终链接。

| 结果 | 下一步 |
| --- | --- |
| 收到证书或 pinSHA256 错误 | UDP 已有回应，核对实际证书、指纹、SNI、目标是否为本实例 |
| 认证失败 | 核对密码、URI 编码、服务端实际加载配置 |
| QUIC 握手超时 | 核对 UDP 映射、监听、混淆参数、网络路径；不能只凭一次超时宣布整个 IP 被封 |
| 握手成功但 HTTPS 失败 | 检查服务端 DNS、出站、请求是否经过测试代理 |
| CLI 能用但 v2rayN 导入失败 | 核对 v2rayN 与其核心兼容性、URI 字符和协议；不能伪装成 vless:// |
