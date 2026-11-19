# V7 来源与取舍

整理日期：2026-11-19。这里记录本版的材料范围和核对结果，不存放用户账号、订单、真实节点或原始聊天截图。

## 指定指南和回复

- [用户指定帖子](https://x.com/Tynric_carter/status/2120755440153965007)
- [VPS 选购与搭建全流程指南](https://x.com/i/article/2120733575737929728)
- 阅读方式：X 直接访问受限，经 [FxTwitter 公开读取接口](https://api.fxtwitter.com/Tynric_carter/status/2120755440153965007) 取得文章文字；经 [公开线程镜像](https://xitter.cf/Tynric_carter/status/2120755440153965007) 读取当时展示的主帖与 24 条回复。不是登录后的完整回复导出，也不包含被折叠、删除或后来新增内容。文章中的套餐图片没有作为本版价格依据。

吸收的主题是购买前看线路证据、区分支付周期、核对资源与已有服务、按版本配置面板，以及把连通和后续维护纳入交付。回复中关于去程/回程、晚高峰和测试地址的建议，转化成有范围、有时间记录的测量流程；未采用按单一 IP 前缀判定线路的规则。

文章及评论属于经验材料。具体配置按下方项目官方文档核对，当前价格按采购当时的官方结账页核对。此包不转载全文、图片、评论全文或商家价格表。

## 官方核对与实施位置

| 来源 | 核对结果及对应文件 |
| --- | --- |
| [Xray 传输配置](https://xtls.github.io/config/transport.html) | 传输与安全层、字段/组合依版本核验；保留 xray-config 配置检查与 maintenance 的兼容排查 |
| [Hysteria 服务端](https://v2.hysteria.network/docs/advanced/Full-Server-Config/) | TLS 证书读取机制及独立拥塞控制；见 maintenance |
| [Hysteria 客户端](https://v2.hysteria.network/docs/advanced/Full-Client-Config/) | URI 输入与 TLS 固定指纹；见 hysteria2、hy2-verification |
| [Let's Encrypt 验证类型](https://letsencrypt.org/docs/challenge-types/) | HTTP-01 公网 80 与 DNS-01 的适用条件；见 purchasing、maintenance |
| [Linux IP sysctl](https://docs.kernel.org/networking/ip-sysctl.html) | TCP 默认算法及可用算法检查；见 maintenance |
| [sing-box AnyTLS](https://sing-box.sagernet.org/configuration/inbound/anytls/) | 可选扩展入口，按当前客户端能力核验；没有附带部署 AnyTLS |
| [IPPure FAQ](https://ippure.com/faq) | 保持检测时点和字段范围，不以评分代替网络/账号可用性验收 |

## 本轮实际使用经验

在旧节点检查中出现过“客户端显示 -1，但同一 VLESS 配置经独立核心请求 HTTPS 成功”的情况。把它整理为配置 → 传输 → 协议 → HTTPS → 用户客户端的分层流程，见 node-health。其余超时节点只按当次测试网络和端口报告。没有把旧节点地址、凭据、当时结果或国家写成新使用者的默认配置。

原有重装恢复、UDP 端口数字避让、独立测试与重启自启流程保留。公开包只包含空端口模板；本机升级必须保留旧集合。安装或更新技能只修改技能文件，不触发原文中的部署命令。
