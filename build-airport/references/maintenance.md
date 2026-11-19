# 维护：版本、面板、证书与性能

按当前任务只读相关小节。旧节点故障先做 [node-health.md](node-health.md) 的分层测试；证据不足时不以“升级全套”“关闭防火墙”“重装系统”替代定位。

## 版本兼容与回退

维护记录至少区分：客户端应用、实际客户端核心、服务端核心、面板（如有）及各自版本。面板有某个选项不代表打包核心支持它；客户端导入成功也不代表核心理解每个参数。

REALITY、HY2 等出现认证或握手变化时，先核对两端实际版本、对应发行说明和报错阶段。使用同一 URI 在独立兼容核心复测。不要固定教程中的版本为“最新版”，也不要只因更新可用就升级原本正常的服务。

确需升级时：备份当次配置、服务定义与原二进制 → 校验新发行包 → 用新核心做配置检查 → 在既有授权内切换 → 新连接 HTTPS 验证；失败可恢复原版本与配置。涉及其他业务中断、格式迁移或删除数据时先界定影响。不能仅凭 REALITY 回落行为断言全是版本问题，密钥、SNI、Short ID 和网络路径也要核对。

[Xray 官方传输配置](https://xtls.github.io/config/transport.html) · [Hysteria 发行说明](https://v2.hysteria.network/docs/changelog/)

## 3x-ui 作为可选管理方式

仅用户需要面板或实例已经使用面板时进入此分支。先确认资源与已有安装；直接核心部署成功的机器不为了教程截图再加一个面板。

1. 核对当前官方安装说明和对应版本的交互流程。先下载、检查脚本再执行，不将任意远程响应直接管道交给 shell，不根据旧截图预填菜单数字。
2. 独立规划管理入口、代理入站、SSH 的映射。服务监听内部端口，公网 URL/URI 使用外部端口；三个服务都遵守同一端口避让集合。安全组、主机防火墙和 NAT 是三个不同位置。
3. 管理访问使用可验证的 HTTPS 或 SSH 隧道。当前证书与实际 URL 协议一致；不因链接写了 https 就假定 TLS 已配置。只开放需要的管理来源，改规则前保持可用管理通道。
4. VLESS/REALITY 核对入站监听、协议与传输、安全参数及客户端关联；导出的 Flow/UUID/公钥/Short ID 与服务端相同。HY2 核对版本、UDP 监听、认证、TLS 和客户端支持的混淆。菜单名与参数以当前面板/核心为准。
5. “引用面板证书”仅复用文件路径；仍需检查证书范围、有效期、读取权限、续期后核心加载和外部验证。二维码导入不会自动创建防火墙或 NAT 规则。
6. 面板 `active`、本机 HTTP 200 和代理可用分别验收。本机 404 核对当前 webBasePath；本机 200/公网失败核对面板外部端口、路径和代理链，不把代理数据端口用作面板端口。

[3x-ui 官方安装说明](https://github.com/MHSanaei/3x-ui/blob/main/docs/content/docs/en/guide/installation.mdx)

## 证书全生命周期

先确定采用受信任 CA 还是自签固定指纹，不把 REALITY 密钥当作 TLS 证书。记录公共证书的 SAN、有效期、服务读取路径及更新机制；私钥只保存在部署需要的位置。

- **HTTP-01**：验证端从公网访问 80；只将实例内部 80 映射到任意高位外部端口不能满足验证。**DNS-01**：需要域名控制和相应 DNS 权限，可用于不开放公网 80 的环境。根据所用 CA、ACME 客户端及平台实际能力选型，不硬套教程步骤。[Let's Encrypt](https://letsencrypt.org/docs/challenge-types/)
- **加载机制**：检查实际核心文档。原生 Hysteria 的 `tls.cert/key` 文件在每次握手读取，因此文件更新后应新建连接验收；其他实现若要求 reload/restart，则仅对目标服务执行。不能把“续期命令成功”当成“运行服务已使用新证书”。[Hysteria TLS](https://v2.hysteria.network/docs/advanced/Full-Server-Config/#tls)
- **受信任证书**：到期前确认续期任务、写入权限、服务读取路径和加载方式；验证 SAN/SNI、有效期和全新 TLS/QUIC 握手。不要频繁真实签发来测试，优先采用 ACME 工具支持的检查或 staging 模式。
- **自签并固定指纹**：继续使用本次公共叶证书的 DER SHA-256。更换证书后更新 URI 和各客户端，再以最终链接新建连接。指纹不匹配不能通过去掉 pin 或单独关闭证书验证解决。[Hysteria 客户端 TLS](https://v2.hysteria.network/docs/advanced/Full-Client-Config/#tls)
- **续期证据**：记录检查时间、到期时间、公开指纹及全新连接结果；把未实际演练的自动续期标为“已配置，未演练”。不要为“长期维护”自行创建定时任务、提醒或新付费服务。

## Linux TCP BBR 与 HY2 拥塞控制

只在性能任务或需要调整的部署中评估，不把 BBR 变成每次安装的必做项。先只读：

```sh
sysctl net.ipv4.tcp_available_congestion_control
sysctl net.ipv4.tcp_congestion_control
sysctl net.core.default_qdisc
```

字段不可读、算法缺失或容器不允许修改时记录限制。不要尝试修改服务商宿主机或为单节点更换内核。需改变配置时保留原值，只写本次所需的独立配置项，验证实际生效与回退方式，避免不加判断地运行 `sysctl --system` 应用所有无关文件。

`net.ipv4.tcp_congestion_control` 控制内核 TCP 的默认拥塞算法；HY2/QUIC 有自身控制器，系统 TCP BBR 开关不能证明 HY2 已使用 BBR。HY2 的带宽设置可能影响具体控制模式，按当前核心文档和真实链路能力配置，不把商家网卡速率照填为端到端带宽。[Linux IP sysctl](https://docs.kernel.org/networking/ip-sysctl.html) · [Hysteria 拥塞控制](https://v2.hysteria.network/docs/advanced/Full-Server-Config/#congestion)

性能调整前后用同一网络、目标、流量上限和时间窗口比较。若用户只问能否连接，完成小流量 HTTPS 即可，不默认跑大流量测速或全天监控。

## AnyTLS、双协议或中转的范围

AnyTLS 是可选扩展，不因文章推荐而替换用户指定的协议。用户选择后，读取当前 [sing-box AnyTLS 入站](https://sing-box.sagernet.org/configuration/inbound/anytls/)、对应出站/TLS 与客户端分享规范，确认目标客户端支持；独立端口和服务不覆盖现有工作负载。导出对应协议格式，不包装成 VLESS 或 HY2。

同理，额外部署双协议、TUIC、CDN 或中转时先界定用户要求、资源与费用。主备各自用最终链接验收；不能用主线路成功替备用验收，也不能把某协议写成永久最优或保证不被阻断。

## 备份与可继续维护的交付

每次有实质变更，备份本次目标配置和可恢复的服务定义。管理文件记录新配置位置、版本、证书期限、续费期限、相关端口和恢复步骤；端口避让记录保留已用数字。节点使用者 TXT 与含管理凭据的资料分开保存，更新技能包时不带入这些任务文件。

重启自启按 [hy2-verification.md](hy2-verification.md) 验证实例真实重启、无需人工启动和全新客户端连接。纯健康检查、升级服务重启、实例开机自启三者分别报告，不混写。
