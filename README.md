# build-airport

Codex 手动调用技能：选购、部署与维护个人 VLESS/REALITY、Hysteria 2（HY2）节点，核对线路与正常续费成本，避让历史端口，通过实际连接交付客户端链接。

**发布包 V7 · 技能版本 1.4 · 2026-11-19**

安装技能只增加操作流程。购买、部署、重装、重启或检查节点，由使用者之后的明确任务触发。本包是可公开分享的通用版本；使用者自行提供平台、地区、预算、实例和当次必要凭据。

## V7 更新

- 增加 VPS 选购表：线路证据、支付周期、正常续费、NAT/UDP、退款条件和资源可用性。
- 加入去程/回程与晚高峰的有限测量流程，区分营销标签、IPPure 和实际网站可用性。
- 增加延迟 -1 排查：配置、传输、协议、HTTPS、用户客户端逐层核验，只推荐实测通过的链接。
- 增加版本兼容、3x-ui 可选管理流程、证书续期与新握手验证，以及 TCP BBR/HY2 控制器的区别。
- 保留重装恢复、UDP 端口避让、独立测试、实例重启自启、链接 TXT 与管理文件分离交付。
- 保留仅手动调用；升级合并本机端口历史，公开包不携带个人节点记录。

具体取舍和来源见 [来源说明](build-airport/references/source-notes.md)。

## 安装

### 从 GitHub 安装

**技能目录：** [build-airport](https://github.com/CA176-web/build-airport_GitHub-_V5/tree/main/build-airport)

把下面这段发给 Codex：

> 请使用 skill-installer 从 https://github.com/CA176-web/build-airport_GitHub-_V5/tree/main/build-airport 安装 build-airport V1.4（V7）。本次只安装技能，不登录云平台、不购买 VPS、不部署或重装节点。若已安装，先备份旧版，保留并合并本机端口避让记录，再更新，保持仅手动调用。

安装后在下一轮对话使用 `$build-airport`。代码位于仓库的 `build-airport/` 目录；仓库名称中的 `_V5` 是原仓库名，当前内容版本为 V7 / 1.4。

已安装 skill-installer 的环境也可调用其脚本：

```text
python <skill-installer目录>/scripts/install-skill-from-github.py --repo CA176-web/build-airport_GitHub-_V5 --ref main --path build-airport
```

脚本位置按当前环境确定。已有同名安装时先按下方升级说明处理，不能用公开空模板覆盖个人端口历史。只安装技能不会执行任何部署。

需要离线安装时，下载 [V7 压缩包](./build-airport_VPS选购与连通排查_V7.zip)。压缩包包含同版本技能和通用安装说明；本页提供这个仓库的实际安装地址。

### 从压缩包安装

将 `build-airport` 文件夹放入当前环境的 `$CODEX_HOME/skills/`；未设置时使用 `~/.codex/skills/`。文件夹应直接包含 `SKILL.md`，不要多套一层发布包目录。下一轮对话使用 `$build-airport` 手动调用。

### 升级并保留端口历史

1. 将旧技能备份到技能目录之外，避免同时发现两个同名技能。
2. 保留旧版 `references/port-exclusions.json`、`private/port-exclusions.local.json`、用户指定的私密记录及版本副本；将历史端口排序去重合并到继续使用的本机记录。新包中的空列表不是清除历史的指令。
3. 更新通用说明、脚本和 UI 元数据；保持 `allow_implicit_invocation: false`。
4. 核对技能版本 1.4、旧端口集合仍在、引用文件可读取。分享给别人时使用本公开包，不压缩本机带私人记录的安装目录。

## 使用示例

```text
使用 $build-airport。只检查我提供的这些节点哪个还能用，分别测试真实代理 HTTPS，给出可用链接。不要修改服务器或系统代理。
```

```text
使用 $build-airport。按我提供的平台、国家、首次支付与续费预算筛选 VPS，列出线路和 UDP/NAT 限制；按我明确授权的范围购买与部署，避让提供的端口历史，最终交付实测链接和 TXT。
```

已有节点需 HY2 或重装时，明确指定实例、协议和允许操作的范围。AnyTLS、中转或双协议属于可选任务，不随安装自动创建。

## 隐私与检查

本包无云账号、密码、私钥、真实节点 URI、历史截图和个人端口记录。示例使用占位符、保留域名与文档地址；测试夹具只有合成公共证书，没有私钥。

运行附带的离线链接生成器测试：

```text
python -m unittest discover -s build-airport/scripts/tests -p "test_*.py"
```

`SHA256SUMS.txt` 列出包内文件摘要。脚本测试通过只说明离线生成行为已验证，不表示购买、部署或任意公网节点已经通过测试。

