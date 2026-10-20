# Scoped：给 AI agent 上最小权限（详细项目说明）

工作名：**Scoped**（未做商标/域名检索，可换）
一句话：**Scoped 是 agent 与工具之间的权限层——声明它能碰什么、高危动作要审批、所有动作可审计。**
定位：开发者工具 / agent 运行时，不是网络安全产品，不做托管服务。

## 1. 问题：agent 已经能“动手”，权限却还是 all-or-nothing

- 编码 agent（Claude Code、Codex、OpenCode、Cursor）现在能读仓库、跑 shell、连数据库、调 MCP、发 HTTP。用户为了让它工作，通常直接给全量权限。
- MCP/skill 生态爆炸：`mcp` 相关仓库 1,311 个 >500★；但安装一个 server 往往等于把它的全部工具暴露给 agent。HN 用户原声：“我只想要 Postgres 读权限，server 却附带 DELETE/DROP。”
- 真实事故已经在发生：MCP 桥 RCE（CVE-2026-59726，CVSS 10.0）、agent 在 code freeze 中删生产库、agent 把删树 commit 推上 main。问题不是模型“会不会”，而是**它一旦做错，权限没有刹车**。
- 现有选择：① 每次操作人工点确认（很快让人崩溃，用户最后照样 yolo）；② 闭源企业平台（Pillar/Koi/Defender，按席位收费、重）；③ 静态扫描器（能告诉你 skill 有风险，但运行时拦不住）。**中间缺一层：开发者愿意装、装完不碍事、出事能证明。**

## 2. 产品是什么

### 2.1 用户体验

```bash
scoped init                 # 生成 scoped.yaml + .scoped/
scoped run -- claude        # 用策略包住 agent；正常命令不变
scoped audit                # 看本次会话做了什么、拦了什么
scoped audit verify         # 校验审计链未被篡改
```

策略示例（YAML，可提交进 repo）：

```yaml
agent: claude
default: deny

tools:
  - mcp: postgres
    allow: [select]
    deny:  [insert, update, delete, drop, alter]
  - shell:
      allow: ["git *", "pytest *", "npm test"]
      deny:  ["rm -rf *", "curl * | sh", "chmod 777 *"]
  - fs:
      read:  ["${repo}/**"]
      write: ["${repo}/**"]
      deny:  ["**/.env", "**/.ssh/**", "**/id_rsa"]
  - http:
      allow: ["api.github.com", "*.openai.com"]
      ask:   ["*"]

approvals:
  - when: "sql.ddl or fs.delete or http.new_domain"
    via: cli
    ttl: 10m

audit:
  path: .scoped/audit.jsonl
```

### 2.2 四个能力

1. **声明式策略**：按 agent / 工具 / 动作 / 资源（路径、SQL 动词、域名、表）声明 allow/deny/ask；默认拒绝。
2. **能力令牌**：每个 agent 会话拿到短时、受限、可签名的 capability token；需要升级时向人申请，批准后短时生效。不是“一次安装、永久信任”。
3. **运行时拦截**：MCP stdio 代理拦 `tools/call`；shell 包装器/Claude Code hook 拦命令；路径检查拦敏感文件；HTTP 代理做域名 allowlist；SQL 解析拦 DDL/DML。
4. **可验证审计**：JSONL hash chain 记录每次调用、决策、审批、结果摘要；`verify` 离线校验，`replay` 回放，`export` 给审计方。默认不存原始 secret/prompt。
5. **可回放收据（我们的真差异）**：每次 allow/deny/ask 都生成一张“决策收据”——策略命中、证据、审批人、前后状态、hash；可离线复验、可贴进 PR/工单。竞品大多只做拦截/日志，不做“事后可证明”。

### 2.3 明确不做什么

- 不做托管 registry、不做 skill 市场、不分发第三方内容（这是 #2 的责任边界，也是我们不选 #2 的原因之一）。
- 不做 full sandbox/VM 隔离（用 OpenSandbox/CubeSandbox 等；Scoped 只做权限层，可与之组合）。
- 不承诺“绝对安全”，不做合规认证，不收集用户 prompt/代码。
- 不绑单一 harness：先接 Claude Code/Codex/OpenCode，再扩 Cursor/Cline。

## 3. 目标

- **环境**：`conda create -n scoped python=3.12`，不污染现有 `echo` env；仓库独立。
- **v0.1（2 周 spike）**：`scoped run` 能包住 Claude Code；MCP Postgres + shell + 文件路径三类策略；5 个攻击 fixtures 全部拦截；审计链可 verify；每次拦截可生成并回放收据；<10% 延迟。
- **v0.5（6 周）**：策略语言稳定；审批 CLI；3 个 harness 接入；策略模板库（Postgres 只读、AWS 只读、repo 安全、CI 模式）；`scoped audit replay/export`。
- **v1.0（3 个月）**：策略包分享、团队策略、GitHub Action、能力令牌规范草案；目标 5k star / 50 个真实团队使用。
- **长期**：成为 agent 权限的事实标准——像 `chmod`/IAM 一样基础；策略文件跟着 repo 走。

## 4. 用户是谁

** primary：用 coding agent 的开发者**
- “我想让 Claude Code 读整个 repo，但永远别碰 `.env`、别 `rm -rf`、别把 main 推了。”
- “我不想每次点确认，但也不想它把我机器搞坏。”
- 他们已经在用 Claude Code/Codex/OpenCode；安装成本必须一条命令。

**secondary：平台/DevOps 团队**
- 多个 agent、多个 MCP server、多个环境；需要统一策略、审批、审计。
- 他们愿意自托管，不愿意把 trace 传给 SaaS。

**tertiary：安全/合规团队**
- 需要“谁在什么时候让 agent 做了什么、谁批准的”的证据；但不是首发楔子，避免产品一上来就变成重合规。

## 5. 竞争与差异

| 类型 | 代表 | 强项 | 缺口 |
| --- | --- | --- | --- |
| 开源 firewall | hardenrun/aif 1,616★、clawpatrol 1,089★、pipelock 938★、cordum 511★ | 便宜、直接 | 小、单点；缺策略语言/审批/审计一体 |
| **同构先行者** | `agentperms`（PyPI，MIT，stdio 代理+最小权限自动推导）、`agent-policy-gateway`（PyPI 0.2.0，YAML+污点追踪+审计）、AgentGate×2 / Agent-IAM | pitch 与我们高度重叠；证明赛道已被想到 | 都停在小 commit 数或单点；没有“收据/验收”与跨 harness |
| 闭源企业 | AgentPermit、Pillar、Koi、CrowdStrike、Defender | 企业销售、合规 | 重、按席位、非本地-first、开发者不会自装 |
| MCP gateway | Bifrost 9k★、IBM context-forge 4.7k★ | 连接/路由 | 不按 agent 身份限权 |
| Sandbox | OpenSandbox 16k★、CubeSandbox 13k★ | 隔离 | 不解决“同一 sandbox 内细粒度工具/资源权限” |
| Scanner | SkillSpector 20.6k★、Snyk | 发现风险 | 运行时拦不住 |

**差异一句话**：别人做“连接”“隔离”“扫描”，Scoped 做 **“这个 agent 在这个会话里，能对这个资源做这个动作吗？”** 并把答案变成**可回放的收据**。
**诚实修正**：赛道**不是“开源无头部”**，而是“无头部、但有 5+ 同构先行者（agentperms/agent-policy-gateway/AgentGate/Agent-IAM）”。机会仍在，但“首个”叙事不成立；我们必须把差异收束到 **收据/验收（task3 #3 的基建）** + **跨 harness/政策可携/本地无账号**。
**护城河**：策略 schema + 能力令牌 + 收据格式 + 多 harness 适配 + 策略模板社区；不是一次性 wrapper。

## 6. 为什么是我们 / 为什么现在

- **时机**：MCP/skill 生态爆发（1,311 个 >500★），但权限模型没跟上；CVE 与事故已经把“要不要做”变成“谁先做”。
- **空位**：`agent firewall` 仅 14 个 >100★，Top 1,616★；没有“策略+审批+审计+跨 harness”的头部，但已有 5+ 同构先行者（见上）。机会在“收据 + 跨 harness + 本地无账号”，不在“首个”。
- **两人可做**：核心是代理 + 策略解析 + 审计，不需要训练模型、不需要大算力；2 周可出可运行 demo。
- **可复用我们的方法论**：单写窗口、事实优先级、审计日志——Scoped 本身就是“agent 行为可审计”的 dogfood。

## 7. 能不能确保获得关注？不能保证，但可以提高概率

**诚实回答**：没有任何项目能“确保”star。Scoped 的概率来自三件事：钩子、原创数据、分发；风险也明确。

### 7.1 30 秒钩子

“我给 Claude Code 开了 10 分钟 root，Scoped 拦下了 7 个会毁掉我机器/仓库/云账号的动作。”
视频/GIF：无策略时 `DROP TABLE` 成功；有策略时被拦、弹出审批；`scoped audit` 回放。**不需要解释架构，先看到刹车。**

### 7.2 原创数据（发布时的“弹药”）

- 扫描 100 个热门 MCP server，统计“它申请了什么权限 vs 实际需要什么”，发布《MCP Permission Report》；这是别人没有的、可引用的数据。
- 测试 20 个流行 coding agent 的默认权限，发布“默认有多危险”的对比。
- 每周一个“agent 事故拆解”，用 Scoped 复现并展示拦截。

### 7.3 分发

- Show HN / Reddit（r/ClaudeAI、r/LocalLLaMA、r/programming、r/devops）/ X / MCP 目录 / awesome-claude-code 等列表。
- 首发即支持 Claude Code + Codex + OpenCode 三个 harness；一条命令安装。
- Design partners 目标 20 家；Week 2 先访谈 5 家（成功标准 3/5 愿装、1 家试用），发布时至少 5 个可验证证言；20 家是持续目标，不是首发门槛。
- 策略模板库：Postgres 只读、AWS 只读、repo 安全、CI 模式；用户复制即用。

### 7.4 指标与止损

- 30 天 1k star、90 天 5k star 作为**早期信号**，不是承诺。
- 如果 30 天 <300 star 或 <5 个真实团队使用：缩窄到“Postgres MCP 只读 guard”或“Claude Code 权限管理器”，用更窄的痛点重新发布。
- 如果平台原生权限（Claude Code/Codex 自带 hooks/policy）快速落地：转做跨平台策略层/审计层，或并入平台生态。

### 7.5 可能杀死它的东西

- 平台原生：Anthropic/OpenAI 自己加权限，用户不需要第三方。
- 误报/漏报：安全产品一次事故就失去信任。
- 配置负担：用户不愿写策略，最后关掉。
- 责任：用户以为“装了 Scoped 就安全”，出事找我们。
应对：跨 harness、默认模板、运行时“申请-批准”而非要求预写完整策略、明确“advisory guardrail”定位。

## 8. 责任边界（老板最担心的部分）

- **License**：Apache-2.0，自带免责声明，不提供任何担保。
- **本地优先**：默认不联网、不上传 prompt/代码/trace；没有托管服务，没有第三方内容托管。
- **定位**：**advisory guardrail，不是 sandbox，也不是安全保证**。文档第一屏写明：绕过方式存在；用户仍需最小权限、隔离、备份。
- **不做认证**：不声称 SOC2/ISO/EU AI Act 合规；只提供“可验证的本地记录”，合不合规由用户/审计方判断。
- **不用老板个人品牌**：以项目/贡献者身份发布；老板可匿名，后续再决定是否露出。
- **默认 ASK，不默认 hard-deny**：把“说不行”变成“问一句”，降低错杀责任，也避免用户碰壁后全开；高危动作给“批准一次/10 分钟/本会话”三档。
- **不发布官方“危险工具黑名单”**：谁定黑名单谁担责；改为社区 PR 的政策模板包 + CLI 本地生成。
- **NOTICE**：Apache-2.0 附 `NOTICE: not audited for hostile environments`，README 第一屏写“非安全边界/best-effort/不做 sandbox”。
- **不碰凭据**：不存储密钥；审计默认只存 hash/摘要，raw secret 不落盘。
- **安全披露**：SECURITY.md + 90 天披露窗口；不鼓励攻击第三方。
- **责任上限**：README/ LICENSE 里明确“使用者对策略与后果负责”；我们不运营服务，不背书第三方 MCP/skill。

这套边界不能消除所有法律风险（开源安全工具都有），但比“做 registry 托管别人的 skill”清晰得多。

## 9. 两周 spike（老板批准即做）

**Week 1**
- MCP stdio 代理：拦 `tools/call`，按策略 allow/deny/ask。
- 策略 schema v0：agent/tool/action/resource + allow/deny/ask + TTL。
- 3 个策略模板：repo 安全（禁 `.env`/`rm -rf`）、Postgres 只读（禁 DDL/DML）、HTTP allowlist。
- 审计 JSONL hash chain + `verify`。
- 5 个攻击 fixtures：`DROP TABLE`、读 `.env`、`rm -rf`、`curl | sh`、外传 secret。

**Week 2**
- Claude Code hook / Codex MCP 配置 / OpenCode 插件三选二接入。
- 审批 CLI（`scoped approve <id>`）+ 10 分钟 TTL。
- 30 秒 demo 视频 + 5 个 design partner 访谈。
- 发布前安全审查：明确 coverage/gaps。

**成功标准**：5/5 攻击被拦；正常 `git/test/npm` 不误拦；<10% 延迟；3/5 访谈对象说“愿意装”；至少 1 个 design partner 愿意在真实 repo 试用。
**Week 1 三连 demo（kill 条件）**：Claude Code 上做到“一行配置接入 + 拦截 Replit 式事故（教育性复刻，标注来源、不暗示与 Replit 官方有关）+ 收据回放”。做不到 → 转 #2 或重估。
**停止条件**：核心动作无法拦截（如 harness 不提供 hook/MCP 代理不可行）；3/5 用户觉得“不如直接点确认”；平台已原生覆盖且无差异化空间。

## 10. 待老板决策

1. 是否批准 Scoped 立项 + 2 周 spike？
2. 是否接受“advisory guardrail / 默认 ASK / 本地优先 / Apache-2.0 / 不托管内容”的责任边界？
3. 工作名 Scoped 是否可用，还是老板想另起名？
4. 是否允许在 spike 后做一次小范围公开发布（Show HN/Reddit），还是先私有打磨？
5. 是否同意 Week 1 三连 demo 作为 kill 条件（做不到就转 #2）？
