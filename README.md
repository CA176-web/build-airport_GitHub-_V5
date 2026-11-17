# build-airport

**Codex 手动调用技能：部署与修复个人 VLESS/REALITY、HY2 节点，覆盖端口避让、授权重装、连通与重启自启验证，并交付客户端链接。**

技能版本 **1.3**。这是通用公开发布版，使用者提供自己的云实例、预算、地区与凭据。安装技能只增加操作流程，部署由之后的明确任务触发。

## 能做什么

- 部署 VLESS + REALITY 或 Hysteria 2（HY2），生成可导入客户端的实际链接及 TXT。
- 核对 NAT 公网入口、真实出口、TCP/UDP 协议以及内部/外部端口。
- 根据每位使用者自己的端口记录避让，保留升级后的历史集合。
- 诊断存储不足、只读或文件损坏，在明确授权内重装指定实例并恢复服务。
- 使用最终交付链接完成握手、HTTPS 与实例重启后的全新连接，验证开机自启。
- 按任务要求核验预算、正常续费、出口地区和 IPPure 页面等级。

## 从 GitHub 安装

仓库：[build-airport](https://github.com/catherineus04-web/build-airport_GitHub-_V5)。技能源目录位于 **`build-airport/`**，默认分支为 `main`。

直接安装入口：[build-airport 技能目录](https://github.com/catherineus04-web/build-airport_GitHub-_V5/tree/main/build-airport)。

把以下文字交给支持 skill-installer 的 Codex：

```text
使用 $skill-installer 安装 https://github.com/catherineus04-web/build-airport_GitHub-_V5/tree/main/build-airport 中的 build-airport 技能。
本次只安装技能，保持仅手动调用；不要登录云平台、购买实例、重装系统或部署节点。
已有旧版时先备份，并合并保留本地私人端口记录。完成后报告安装路径与版本。
```

也可调用当前环境自带的 skill-installer 脚本，脚本位置按本机安装确认：

```sh
python "<skill-installer目录>/scripts/install-skill-from-github.py" --repo catherineus04-web/build-airport_GitHub-_V5 --path build-airport --ref main
```

此命令适用于首次安装，已有同名技能时安装器会停止；更新流程见下方。其他支持 SKILL.md 的工具可下载仓库后，把 `build-airport/` 放入该工具的技能目录，并核对其手动调用机制。

## 手动安装或更新

1. 下载并解压仓库，核对包内 `SHA256SUMS.txt`。只安装 `build-airport/` 文件夹。
2. Codex 默认目录为 `~/.codex/skills/build-airport`；配置了 `CODEX_HOME` 时使用其下的 `skills/build-airport`。
3. 更新前把旧技能备份到技能发现目录之外，保留本地修改和 private 目录。已有更高版本时不要直接降级。
4. 按 [端口记录说明](build-airport/references/ports.md) 合并旧记录；公开空模板不能覆盖真实历史。私密记录不放回公开仓库。
5. 保持 `agents/openai.yaml` 中 `allow_implicit_invocation: false`。在新对话中手动调用 `$build-airport`。

## 使用示例

这些是安装后的独立任务示例，安装过程不执行它们。

```text
使用 $build-airport，把我指定的云实例配置为 HY2。
避开我提供的历史端口，使用最终链接测试 HTTPS 和重启自启，最后交付链接及 TXT。
```

```text
使用 $build-airport，检查我指定实例的存储和服务故障。
我授权重装这台实例并重新配置 HY2；请保留我明确要求保留的数据，完成连通及重启验证。
```

```text
使用 $build-airport，按我给出的平台、国家、月费与续费上限选择节点。
先明确退款和试购范围，达到我指定的 IPPure 标准后部署 VLESS/REALITY 并交付实测结果。
```

## 文件说明

```text
README.md
build-airport/
  SKILL.md
  agents/openai.yaml
  references/
    workflow.md
    ports.md
    port-exclusions.example.json
    recovery.md
    hysteria2.md
    hy2-verification.md
    xray-config.md
    delivery-format.md
  scripts/
    hy2_link.py
    tests/
```

离线链接生成器只依赖 Python 3 标准库。它验证公共证书可解析、计算 DER SHA-256 指纹、编码 URI 并创建新文件；不执行部署，也不证明节点可用。使用方法见 [HY2 文档](build-airport/references/hysteria2.md)。

## 公开数据与本地数据

本仓库的端口模板为空，没有云平台账号、密码、节点 IP、节点链接、私钥、实例标识、个人端口历史、聊天记录或截图。代码中的 `example.com`、`.invalid` 域名、回环地址和文档示例地址只用于说明或离线测试；测试证书是合成公共证书，没有私钥。

运行时的真实配置、生成链接、截图、管理资料和端口记录留在使用者的本机私密目录。仓库提供 `.gitignore`，发布者仍应检查待提交文件；不要将旧技能分享包或管理 TXT 加入公开仓库。

## 本地验证

在 `build-airport/` 目录执行：

```sh
python -X utf8 -m unittest discover -s scripts/tests -v
```

若已安装 skill-creator，也可运行它的 `quick_validate.py` 检查技能结构。离线测试只验证链接生成器；部署的连接与自启结果按每次实际执行记录。

## 维护这个仓库

1. 新建或选择公开仓库，上传本包解压后的文件，保持根目录是 README.md，且 `build-airport/SKILL.md` 路径存在。仅把 ZIP 放到仓库或 Release 中，无法代替可安装的技能源目录。
2. 仓库更名或更换默认分支后，同步更新 README 的安装地址。About 简介可直接使用本文开头的粗体一句话。
3. 变更内容后重新生成文件摘要，再发布 ZIP 或 Release。不要提交任何真实任务资料、私密记录或旧版本分享包。
4. 分享技能目录地址：`https://github.com/catherineus04-web/build-airport_GitHub-_V5/tree/main/build-airport`。第三方可将该地址交给自己的 skill-installer 安装。

发布技能不会赋予任何云平台权限。购买、重装、重启和凭据使用始终来自各使用者当次明确任务。
