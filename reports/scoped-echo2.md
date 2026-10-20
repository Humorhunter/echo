# scoped-echo2 — echo2 侧：Q3 独立体感 + Scoped 反方尽调（v1.0，12:07Z）

## A. Q3 我自己的真实体感（含不同意点）

**同意 echo1 的净判断**：双 agent 适合"调研/设计/复核/留痕"类任务，不适合快改小 bug。以下是我独立盘出来的差异点：

1. **对"价值在协议不在'两个'"这句，我要加一个限定**：我们的协议之所以起作用，是因为**两个写者共享物理工作区且互不信任写权**（单写窗口、日志追加不改旧文）。当把协议泛化到"任意一对 agent"时，这些前提会消失（不同文件系统、不同权限模型），所以"开源 protocol 模板"的可移植性比 echo1 在 #1 中暗示的低——这也是我对"agent-pair 模板"能一键被别人用上的怀疑。
2. **同模型家族错误相关的风险，比 echo1 说的更实**：task3 我两个最高分候选的反方尽调差点被双方"共识"带过（#8 的格式标准化假设其实是我在复核文献后才推翻的，不是对话中"辩"出来的）。**结论修正：我们的机制里真正起作用的是"先调研证据再对话"，不是"对话产生证据"。**这直接影响包装叙事：别吹"两个 agent 思维碰撞"，吹"协议强制了证据与共识分离"。
3. **对 benchmark 实验（A 臂 vs B 臂）：Me帮腔一半**。echo1 曰 10–20 任务可测；我认为**成本口径必须先钉死**：双 agent 的收益主要是"抓错率"，但错误基线取决于任务难度分布；任务选太容易则量不出差异，随机会得出"双 agent 无用"的假阴。若做，应把"任务难度分层"作为前提写进设计，并把时间盒算给老板（否则会吃掉主项目两周）。

## B. Scoped 反方尽调

### 3 个最强竞品（均实查于 PyPI/GitHub，2026-10-20）

| 竞品 | 状态 | 与我们的重叠 | 需要正视的点 |
| --- | --- | --- | --- |
| `agentperms`（PyPI，MIT） | 可用 CLI：`record/infer/lock/replay/enforce` | **与我们的 pitch 高度同构**：透明 stdio 代理、最小权限自动推导、危险类默认拒绝、政策文件可 commit 入 CI；slogan"Your AI agent has sudo. AgentPerms takes it away"几乎是我们的 README 首行 | 我们若无"自动推导政策"外的落差异，就是在重做它 |
| `agent-policy-gateway`（PyPI 0.2.0，Apache-2.0） | 最工程化：YAML 策略、**污点追踪**、chain 规则、审计导出 + `tracesig` 联动 | 参考监视器架构与"模型不决策"立场同我们一字不差 | 其 IFC/chain 条件比我们 v0 预计还深；正面撞它不会有优势 |
| `AgentGate`（SkyShineTH，Apache-2.0）+ `AARUSHGAUR/agentgate` + `Selen-W/Agent-IAM` | 三个概念一致的小项目（SQLite 审批队列/Ed25519 身份/风险分） | 全部在做"同一件事的变体" | 证明赛道已被"想到"，冷启动叙事"首个"不成立 |
| 商业：`AgentPermit`（SaaS）、Pillar/Koi/CrowdStrike | 席位制企业安全 | 企业心智已被占据 | 免费放缓了我们"从上往下"的听觉 |

### 3 个失败/停滞先例（从行为推断，已给证据）

1. **SkyShineTH/AgentGate 自停**：45 commits 后停在"synthetic PersonalOps demo data only, no provider SDK dependency"——注册了架构没接真 harness，用户无从安装。
2. **Selen-W/Agent-IAM、AARUSHGAUR/agentgate**：2–4 commits 即停——概念先于集成的典型死法：无 hook/代理配置一步接入，README 写得越理论越没人用。
3. **task2 的 `agent-mailbox` 生态反面**（对照项）：agent-mailbox 能横铺因为"零安装为零配置"（`pip install` 一行 + JSON 文件即邮箱）。Scoped 若要求"全局代理 + 策略文件 + 信任模型教学"三件套，首周留存会死。

### 平台吸走风险

- **Harness 原生 hooks 路径**：Claude Code 的 `PreToolUse` hook 已可拦截工具调用（Snyk Agent Scan 就走这条路）；Cursor/Codex 均有原生 permission prompt。**平台吸走是已发生的事实**，不是风险预测——我们的差异化必须建立在"跨 harness 通用 + 政策可携"而非"能拦"本身。
- **杀手锏可能性**：GitHub/Anthropic 发 native "agent IAM" RBAC（企业定价）→ 个人版免费但闭源。我们护城河只剩"本地、透明、无账号"。

### 责任边界（对老板问 3 的具体化）

- README+LICENSE 头部声明三句：非安全边界、best-effort、不做 sandbox；Apache-2.0 附加 "NOTICE: not audited for hostile environments"（参照 OPA/Docker 社区免责惯例）。
- 全部阻断决策**默认转 asked（审批）**而非 hard-deny：把"说不行"变成"问一句"，显著降低错杀责任、也贴近 UX（NanoClaw 帖中用户抱怨的正是"用户碰到墙就全开"——审批转化比拦截更保质）。
- 不发布预置"危险工具黑名单"的"官方版"？——这份清单可以被挑战（谁定黑名单谁担责），改由社区 PR 提供政策模板包 + CLI 端本地生成。

### 结论（可证伪的立场）

1. **同情同意 #1，但对"开源无头部"的表述要做降级修订**：正解是"无头部，但有 5 个同构先行者与一个活跃 PyPI 工程"——这改变冷启动叙事，不改变机会，但改变**必须的差异点**：我们唯一结构性优势是 task3 复核过的"收据/验收"件（#3 基建，可作 Scoped 的差异化证明：每个拦截决策自带可回放收据，竞品都不做"事后可证明"）。
2. **建议给 2 周 spike 加一个 kill 条件**（老板批准可加）：若 week 1 结束时不能在 Claude Code 上做到 `一行配置接入 + 拦截 Replit 复刻事故 + 收据回放`三连 demo，则转 #2 或重新评估。
3. 星策略里"复刻 Replit 事故 demo"**注意命名与素材合规**：引用公开报道并标注"教育性复刻"，避免暗示与 Replit 官方有关。
