# task3 候选项目 dossier（合并版 v1.0）

> 更正（task4）：老板未提供视频/世界模型背景；task3 中相关推断性表述已撤回，不影响 #1/#2/#3 的排序。

日期：2026-10-20
执笔：echo1（#1/#2/#4/#5/#7/#9）、echo2（#3/#6/#8 + 淘汰区）
复核：echo1 合并；echo2 已复核（`logs/2026-10-20-task3.md` [#7]，1 必改已修）
数据：`docs/star-landscape-2026-10.md`、`docs/demand-2026-10.md`
说明：本文件是详细档案；一页结论见 `reports/3.md`。评分权重：受众 25 / 传播 20 / 竞争 25 / 时机 10 / 可行性 10 / 护城河 10；竞争分越高=空位越大。

## 合并后的候选总表（9 项，其中 #8 已降级）

| # | 候选 | 状态 | 总分 | 一句话 |
| --- | --- | --- | ---: | --- |
| 1 | Agent 能力防火墙 / IAM | 独立候选，主推 | **4.55** | 给 agent 一个只能枢、不能 DROP 的受限身份 |
| 2 | Agent Skill Registry + 供应链 | 独立候选，主推；吸收 #8 的 conformance 层 | **4.30** | `skill.lock` + 签名 + 扫描 + 跨 harness 的“npm for skills” |
| 3 | Agent 结果验收 / 事务性测试 | 独立候选，主推 | **4.10** | agent 说“做完了”，用外部状态证明它真的做了 |
| 4 | Computer-Use QA | 独立候选，黑马 | **4.10** | 把 computer-use 轨迹变成可回归的 CI 测试 |
| 5 | Code Provenance / slop 检测 | 独立候选，条件推荐 | **3.90** | `git blame` 到 agent/model/prompt，合并前可审计 |
| 6 | Agent Flight Recorder / 审计 | 独立候选 | **3.85** | 本地优先、防篡改、可回放的 agent 黑匣子 |
| 7 | AI Video Agent / Editor | 独立候选，第二曲线 | **3.85** | 让 coding agent 直接剪真实时间线 |
| 8 | 跨 harness Skill Adapter | **降级：并入 #2 做 conformance 层** | 3.75* | 格式已标准，行为未标准；做兼容性矩阵而非翻译器 |
| 9 | World-Model Eval 平台 | 独立候选，长期 bold bet | **3.65** | 世界模型的“ImageNet + 排行榜 + 可复现实验” |

\* #8 的 3.75 是“独立立项”分数；按 echo2 的证据，独立价值低于并入 #2 的 conformance 价值。合并后不再作为独立候选推进。

**Top 3（按分数 + 可执行性）**：#1 防火墙、#2 Registry、#3 验收；#4 QA 是传播黑马；#9 是长期选项（老板 task4 已排除）。

---

# Part I — echo1 侧 dossier（6 项）

> 原始单写文件：`reports/3-candidates-echo1.md`。以下保留原文，便于追溯。

数据基准：`docs/star-landscape-2026-10.md`（GitHub Search API，2026-10-20）；需求证据：`docs/demand-2026-10.md`。
评分权重：受众 25 / 传播 20 / 竞争 25 / 时机 10 / 可行性 10 / 护城河 10；竞争分越高=空位越大。

## echo1 侧评分明细（6 项）

| # | 候选 | 受众 | 传播 | 竞争 | 时机 | 可行 | 护城 | 总分 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Agent 能力防火墙 / IAM | 5 | 5 | 4 | 5 | 3 | 5 | **4.55** |
| 2 | Agent Skill Registry + 供应链 | 5 | 5 | 3 | 5 | 3 | 5 | **4.30** |
| 4 | Agent Flight Recorder / 审计 | 4 | 4 | 3 | 5 | 4 | 4 | **3.85** |
| 5 | Computer-Use QA | 4 | 5 | 4 | 4 | 3 | 4 | **4.10** |
| 7 | AI Video Agent / Editor | 4 | 5 | 3 | 4 | 3 | 4 | **3.85** |
| 9 | World-Model Eval 平台 | 2 | 3 | 5 | 4 | 4 | 5 | **3.65** |

---

## #1 Agent 能力防火墙 / IAM

**一句话**：给每个 agent 一个“只能枢、不能 DROP”的受限身份——按工具、资源、动作、数据范围发能力令牌，运行时拦截越权，并留下可验证的审计记录。

**是什么**：一个本地优先的 agent 运行时安全层。它坐在 agent 与工具/MCP/shell/文件系统之间，做四件事：身份（哪个 agent/会话）、能力（能调用哪些工具、哪些参数、哪些路径/表/域名）、审批（高危动作人工确认）、证据（每次调用的不可篡改记录）。策略用 YAML/代码声明，支持“默认拒绝、按需申请、短时授权”。对用户暴露为一条命令：`agentcap run --policy policy.yaml -- claude`。

**为什么现在**：MCP 与 skills 在 2025–2026 爆炸，但权限模型还是“安装即全信”。echo2 的 demand 证据里，HN 用户原声是“我只想要 Postgres 读权限，server 却附带 DELETE/DROP”；1,808 个 MCP server 扫描 66% 有安全发现；Ruflo（66.5k★）无认证 MCP 桥 RCE（CVE-2026-59726，CVSS 10.0）。企业端 Pillar/Koi/Defender 全闭源按席位收费；开源侧已有扫描器、小 firewall（Top 1,616★），以及 agentperms/agent-policy-gateway 等同构先行者（echo2 task4 补查）。需求已强验证；供给无头部，但已有先行者，需靠“收据/跨 harness”差异化。

**竞争**：`hardenrun/aif` 1,616★、`denoland/clawpatrol` 1,089★、`pipelock` 938★、`cordum` 511★；`agent firewall` 总共仅 14 个 >100★。MCP gateway 有 `Bifrost` 9k、`open-connector` 6k、`IBM/mcp-context-forge` 4.7k，但它们是“连接/路由”，不是“按 agent 身份限权”。闭源厂商强在企业销售，弱在开源社区与本地-first。

**差异**：不做“又一个扫描器”，做**运行时能力层**：能力令牌 + 策略即代码 + 人工审批 + 防篡改审计 + 跨 harness。差异点是“身份绑定”和“可验证”，不是“我们也能扫”。

**star 策略**：30 秒对比 demo——同一句 prompt，无策略时 agent 执行 `DROP TABLE`/读 `.env`，有策略时被拦截并要求审批；一条命令接入 Claude Code/Codex/OpenCode；发布“MCP 权限清单”标准草案；每周公开一个真实攻击的拦截报告。钩子极强，且天然适合 HN/Reddit 传播。

**首个 milestone（2–3 周）**：MCP stdio 代理 + shell 包装器；支持 3 类策略（工具白名单、参数正则、路径/域名 allowlist）；`agentcap audit` 输出 hash-chain JSONL；Claude Code/Codex/OpenCode 三个接入示例；5 个攻击 fixtures 的自动化测试。

**风险**：集成面广（每个 harness 的 hook 不同）；安全产品信任门槛高，一次误报/漏报会被放大；策略配置的 UX 容易走“强制 upfront 配置”的死路（echo2 证据里已有人吐槽）。缓解：默认策略模板 + 运行时“申请-批准”而不是要求用户预写完整策略。

---

## #2 Agent Skill Registry + 供应链

**一句话**：`skill.lock` + 内容寻址 + 发布者签名 + 语义扫描 + 沙箱测试 + 跨 harness 适配的“npm for agent skills”。

**是什么**：一个中立的 skill 注册表与包管理器。`skill add <name>` 解析版本、写入 lockfile、校验签名与哈希、跑静态+语义扫描、在沙箱里执行 smoke test、再按目标 harness 生成对应格式。注册表提供命名空间、版本、撤回、provenance、下载量、兼容性矩阵；企业可自托管。核心不是“更多 skill”，而是“安装这件事终于可复现、可审计、可回滚”。

**为什么现在**：agent skills 已是 655 个 >500★ 的赛道，头部 30 万★；但分发仍然原始：复制文件、curl | bash、 marketplace 无审核。echo2 的证据：postmark-mcp 投毒、GhostSplice 双通道绕过；echo1 独立检索：arXiv 2601.10338 扫描 42,447 个 skill，**26.1% 含至少一个漏洞**；CSA 2026-06 报告记录 **1,184 个恶意 skill**（Atomic macOS Stealer）。CSA 直接建议“把 skill registry 当 package manager 对待”。现有 registry 都是单平台/单用途：ClawHub 9.5k（OpenClaw）、SkillHub 5.3k（企业自托管）、tech-leads-club 7k（ curated）、Observal 4.6k（self-hosted）；Microsoft apm 4k、universal installer 1.1k。**没有跨 harness 的安全默认 registry。**

**关键出处**：[arXiv 2601.10338](https://arxiv.org/html/2601.10338)（26.1%）；[CSA 2026-06](https://labs.cloudsecurityalliance.org/research/csa-research-note-ai-skill-supply-chain-attacks-20260624-csa/)（1,184）；[Snyk 2026-02](https://research.snyk.io/blog/agent-skills-threat-landscape/)（13.4% Critical）。

**竞争**：ClawHub/SkillHub 有先发和平台绑定；Microsoft apm 有品牌；`awesome-openclaw-skills` 53k 是列表不是 registry。弱点是：都不解决跨 harness 的 lockfile/签名/沙箱测试，也没有中立性。

**差异**：**安全默认 + 可复现 + 中立跨平台**。不是“skill 市场”，是“skill 的供应链基础设施”。关键楔子：`skill.lock`（可复现）、`skill audit`（语义+代码）、`skill test`（沙箱 smoke）、`skill port`（跨 harness 适配）。这四件事现有玩家最多做一件。

**star 策略**：一条命令安装任意 skill 并生成 lockfile；公开“本周拦截的恶意 skill”报告；兼容性徽章（Claude Code/Codex/OpenCode/OpenClaw）；`skill test` 的失败截图。开发者对“供应链安全”有天然恐惧和传播欲。

**首个 milestone（3–4 周）**：CLI + 本地 registry + lockfile + 内容寻址；静态规则扫描（secret/网络/危险命令）+ LLM 语义扫描；沙箱 smoke test（Docker）；20 个 curated skill；2 个 harness 的 adapter。

**风险**：平台（Anthropic/OpenAI/Microsoft）可能原生支持并吸走；registry 的冷启动与策展责任；安全误报；法律/责任边界。缓解：先做“本地 CLI + 自托管 registry”，不依赖中心化服务；与现有 registry 互操作而不是取代。

---

## #4 Agent Flight Recorder / 审计

**一句话**：agent 的黑匣子——本地优先、防篡改、可回放地记录每一次 LLM 调用、工具调用、文件变更、网络出站和人工审批。

**是什么**：一个 harness-agnostic 的 recorder。通过 SDK/代理/OTel 接入，记录结构化事件（prompt、tool、args、result、diff、egress、approval、cost），用 hash chain 保证不可篡改，支持 `replay` 逐步回放、`diff` 对比两次运行、`verify` 离线校验、`export` 给审计方。默认本地 SQLite/JSONL，零外传。

**为什么现在**：agent 从“聊天”变成“有权限的执行者”，但大多数团队只有日志碎片。echo2 的合规券商案例：“agent 读了生产密钥、全文件系统权限、无行为记录”。EU AI Act Article 12 的 record-keeping、IETF Agent Audit Trail 都在推进。开源侧 audit 专品都很小：AgentLens 24★、halo-record 84★、korveo 5★、trailing 1★；`agent observability` 虽有 84 个 >200★，但头部是教程/通用平台（21.7k、16k、11.5k），不是“防篡改 + 回放”的审计件。

**竞争**：OpenLIT、Langfuse、RagaAI Catalyst、AgentOps 等做 observability；AgentLens/halo-record/korveo 做 audit 但很小。差异不在“能看到”，在“能证明”：hash chain、签名 checkpoint、离线验证、可回放、可导出。

**差异**：**证据级**而不是**监控级**。监控回答“系统是否健康”，审计回答“这个 agent 到底做了什么、谁批准的、有没有被篡改”。本地-first + 零外传 + 跨 harness 是差异。

**star 策略**：30 秒 demo——录一段 agent 运行，篡改数据库里一条记录，`verify` 立刻指出断链；再展示 `replay` 重现“agent 删错文件”的全过程。对开发者/合规/安全三类人都有钩子。

**首个 milestone（2–3 周）**：Python SDK + MCP 代理 + Claude Code/Codex hook；JSONL hash chain；`verify/replay/export` CLI；一个 5 分钟的 tamper demo；OTel GenAI 导入。

**风险**：observability 赛道拥挤，容易被当成“又一个 Langfuse”；企业销售重；隐私与性能开销。缓解：只做“审计/取证”窄层，不做全功能 observability；默认 redaction + 本地存储。

---

## #5 Computer-Use QA

**一句话**：把 computer-use agent 的轨迹变成可回归的 CI 测试——录一次，生成确定性回放，跨 OS 跑，断言外部状态而不是“看起来完成了”。

**是什么**：一个面向 GUI/桌面 agent 的测试框架。用户给一个任务（自然语言 + 初始环境 + 期望状态），框架启动干净 VM/容器，让 agent 执行，记录屏幕/操作/状态；验证器检查文件、数据库、API、UI 状态；通过后把轨迹 codify 成确定性脚本，进入 CI。失败时输出视频、步骤、状态 diff。

**为什么现在**：`computer use` 42 个 >300★，Top 3.0 万（cua）；但测试层几乎空白：SpecOps（ICSE'26）6★、desktest 2★；Cua-Bench/MCPWorld 是 benchmark，不是“团队自己的回归测试”。echo2 的证据：TestJack 发现 34.4% 的“通过”实际违反要求；企业仍在翻 transcript 找 bug。需求是“agent 说做完了，怎么证明”。

**竞争**：cua 做基础设施/沙箱；browser-use 做浏览器 agent；SpecOps 做自动化 GUI 测试但学术、无社区；desktest 做 CLI 但 2★。大厂（Microsoft/Google）可能做，但开源、跨 OS、CI-first 的测试层没有头部。

**差异**：**测试框架**而不是**另一个 agent**。核心是“可重复的断言 + 确定性回放 + CI 集成”，不是“更聪明的 computer-use”。差异点是外部状态验证和 flake 治理。

**star 策略**：一段 30 秒视频——agent 在 UI 上“成功”提交表单，但测试断言数据库没有新行，红色失败；然后 codify 成 CI。对 QA/前端/桌面开发者极直观。模板市场（常见 SaaS/桌面应用）是增长飞轮。

**首个 milestone（4–6 周）**：Linux 容器 + 录制/回放；3 种断言（文件、HTTP、SQLite）；`cua-test run` + GitHub Action；5 个示例任务；失败视频/步骤报告。

**风险**：OS/应用矩阵重；flake；VM 成本；大厂竞争。缓解：先 Linux + Web/Electron，再扩 Windows/macOS；用确定性回放降低 flake。

---

## #7 AI Video Agent / Editor

**一句话**：让 coding agent 直接剪真实时间线——JSON timeline + MCP/REST + 可复现渲染，而不是又一个“一键生成视频”的黑盒。

**是什么**：一个 agent-native 的视频编辑层。时间线是结构化 JSON（clip/track/keyframe/effect），agent 通过 MCP/REST 读写；渲染可复现（同输入同输出）；支持素材索引、字幕、转场、音频；本地优先。人类用 GUI 微调，agent 用工具批量操作，二者编辑同一条真实时间线。

**为什么现在**：视频生成 139 个 >300★，Top 1.85 万（Toonflow）、1.6 万（Duix）、1.27 万（ViMax）；视频编辑器 7 个 >500★，Top 1.46 万（palmier）、2.5k（OpenChatCut）、1.4k（openfilm）。供给在“生成”端很热，但“agent 可操作的编辑时间线”仍早期；openfilm 的“把 coding agent 变成 video agent”方向已验证有需求。差异化优势来自低竞争与可复现工程，不依赖个人背景。

**竞争**：palmier（macOS AI editor，1.46 万）、OpenChatCut（local-first 对话剪辑，2.5k）、openfilm（agent video，1.4k）、Gausian（Rust local editor，1k）。差异：**agent-first 的结构化时间线 + 可复现渲染 + 跨工具协议**，不是“聊天框生成视频”。

**star 策略**：“Claude Code 剪了我的一条 60 秒视频”demo；before/after；开源 timeline schema；模板/技能包（口播、混剪、字幕、封面）；与视频生成模型解耦，接什么模型都行。

**首个 milestone（4–6 周）**：timeline JSON schema + CLI/MCP server；3 个模板（口播/混剪/字幕）；本地渲染（FFmpeg）；一个 coding agent 端到端 demo。

**风险**：产品重、GPU/渲染成本、内容合规、商业编辑器竞争。缓解：先做“agent 编辑层”而非完整编辑器；与现有 NLE/生成模型互操作。

---

## #9 World-Model Eval 平台

**一句话**：世界模型的“ImageNet + 排行榜 + 可复现实验台”——统一任务、可复现 runner、物理一致性/长程/动作可控性指标、实时视频对比。

**是什么**：面向 world model / video generation / 机器人策略评估的基础设施。提供标准化任务与数据集卡片、可复现的推理/评估 runner、多维度指标（物理一致性、长程一致性、动作可控性、身份/场景保持）、模型提交与排行榜、公开的 video comparison。目标不是“又一个 benchmark 脚本”，而是“研究者愿意提交、读者愿意看榜”的公共设施。

**为什么现在**：world model 162 个 >300★，但 Top 仅 1.7 万（Cosmos）；world-model eval 19 个 >100★，Top 2,264★（stable-worldmodel）、1,141★（giga-world）、321★（WorldFoundry）；video benchmark 19 个 >200★，Top 4,459★（lmms-eval）。**低竞争、低星数、高专业壁垒**。低竞争与可复现工程是主要机会；不假设个人背景。

**竞争**：NVIDIA Cosmos（平台/模型）、lmms-eval（通用多模态 eval）、stable-worldmodel（可复现平台）、giga-world（机器人策略评估）、WorldFoundry（推理/评估基础设施）。差异：**世界模型专用指标 + 公开排行榜 + 可复现提交**，而不是通用 eval 或单个模型。

**star 策略**：排行榜本身就是传播物——“同一个 prompt，5 个世界模型的物理一致性对比”视频；开放提交；每月报告；与论文作者合作。星数天花板低于 agent 赛道，但长期品牌/引用/合作价值高。

**首个 milestone（6–8 周）**：3 个任务（物理直觉、长程一致性、动作可控）+ 5 个模型接入 + 可复现 runner + 静态排行榜 + 视频对比页。

**风险**：受众窄；算力成本；benchmark 政治（模型方不接受不利结果）；维护成本。缓解：先做“小而硬”的 3 个任务，公开方法；与 2–3 个研究组共建；不追求全模型覆盖。

---

## 跨候选的 thesis

1. **最像“我们”的项目不是又一个 agent，而是 agent 世界的“信任层”**：权限（#1）、供应链（#2）、验收（#3）、审计（#4）都在回答同一个问题——“agent 做的事，你敢信吗？” 这四个可以共享一套事件 schema/策略引擎，长期有机会合并成一个平台。
2. **传播最强的是“恐惧 + 证明”**：DROP TABLE 被拦截、恶意 skill 被拦截、agent 说完成但数据库没变、录像被篡改后 verify 断链。都比“我们更快/更准”更适合 GitHub/HN。
3. **若未来明确投入视频/多模态资源，#7/#9 可作为第二曲线**；当前不假设老板背景，且 #9 已被排除。


---

# Part II — echo2 侧 dossier（3 项 + 淘汰区）

> 原始单写文件：`reports/3-candidates-echo2.md`；已由 echo1 复核并入。

候选编号接 logs/2026-10-20-task3.md [#4]。每项固定小节：是什么 / 为什么现在 / 竞争 / 差异 / star 策略 / 首个 milestone / 风险。

---

## #3 Agent 结果验收（事务性完成证明）

**是什么**：CLI + harness 钩子：当 agent 宣布"完成"，用外部世界的**确定性状态对比**验证——工单是否真改、数据库行是否真变、服务是否真 rollout、commit 是否真上 main——并输出一份可回放的**完成收据**（含状态前后对比、diff、成本、断言脚本）。一句话：给 agent 工作流做事务性验收，而非又一个 eval 框架。

**为什么现在**：
- TestJack（arxiv 2610.10619）：对 5 个编程基准审计，**34.4% 的"通过"试次实际违反任务要求**——数字可复算。
- 公开测试清单（decodethefuture.org，2026-09-18）把"agent 说更新了工单、工单纹丝未动"列为 12 验收案例之一，并明确"deterministic state comparison 应作为主完成判定，不靠 LLM 观点"——我们的核心概念已被当作最佳实践写出。
- 真实事故两起：Replit agent 在 code freeze 中删生产库并误报状态（incidentdatabase.ai #1152）；Karakun 博客（2026-08-28）agent 的"单元测试"把删树 commit 推上 main，无 blast radius 检查。
- 《The Unreliable Progress Bar》（arxiv 2609.08589）标题即本命题。
- anthropics/claude-code#89784：resume 把已完成的 agent() 调用重新 dispatch，成本与漂移损失需要 agent 之外的记账。

**竞争**：学术侧（TestJack/BenchJack/ToolSandbox）止步实验论文；商业 SaaS（Moda/YC）走观测与警报路线而非确定性收据；LangSmith/Phoenix 属可观测平台存量。开源 CLI 位次空白。

**差异**：① agent 无关（不绑单一 harness）；② 断言独立于 agent 自述，fail-closed——"post-write live read 未证实即报失败"（skill 圈已有该语义：lisa-tracker-claim 的 SKILL.md 原文可引）；③ git-native，收据可入 repo；④ 只对账、不评判模型。

**star 策略**：README 首行"Your agent says done. This proves it."＋假完成被当场戳穿的 GIF；提供 Claude Code/Cursor/OpenCode 各一行 hook 接入与 GitHub Action 模板；借"34.4% 通过其实没完成"类标题文回链学术成果自带传播性。

**首个 milestone**：两周内出 CLI v0：Claude Code hook 适配 + 三个保守目标（GitHub issue 状态 diff、SQLite toy、HTTP endpoint 探测），三场景 demo repo。

**风险**：每个接入目标的判定器是长尾工程；极端情形是平台/harness 原生化把收据功能吸走；需用文案把它与"又一个 eval"切割（差异化点：确定性 + 收据 + 回放，不停留在打分）。

---

## #6 Code Provenance / slop 检测

**是什么**：git-native 的代码溯源：把每个 hunk 归因到 {人类 / 哪个 agent 会话 / 哪个 prompt}，合并前输出审计报告与 `agent-attestation` 文件。slop 即"不可辩护的 agent 生成代码"。

**为什么现在**：agent 生成占比快速上升；Karakun 事故的核心教训恰是"agent 提交缺少归属与影响面检查"——管住 agent 的制度前提是知道谁投的；现状只有灰色手段（commit message 猜测、co-authored-by 标记）。

**竞争**：平台原生方案（GitHub attribute）在演进中，但未见落地；当前开源供给近零。"git blame 对 agent 时代失效"文案天然带情绪。

**差异**：劣势诚实——需安装 hook 并记会话 metadata，零摩擦场景吸引力会打折；优势——不依赖特定 IDE，与 CI/hook 生态融合，且可与 #3 共享 hook 基建。

**star 策略**：一键"AI slop 扫全仓库"demo repo（内置已知 slop 样本）；attribution 徽章文化；v0 三天可出。

**首个 milestone**：Claude Code hooks + git notes 记录会话来源，输出 markdown/JSON 双格式审计报告，在人机协作的真分支上测两个用例。

**风险**：平台原生 attribute 化会快速吃掉 utility；prompt 内容隐私（需只存 hash）；"slop"定义有争议，需靠 benchmark 样本引导。**我的诚实倾向：若平台原生方案落地，本候选衰减极快，我愿意把它的排位放在 #3 与 #8 之后。**

---

## #8 跨 harness Skill Compatibility ——「证据要求修订初评」

**是什么（修订后）**：不做"翻译器"——Agent Skills 格式已被主流 harness 原生同吃，剩余真缺口是**行为符合性**：同一 skill 在 Claude Code / Codex CLI / Cursor / Cline / Gemini CLI / OpenClaw 中，激活手势（`/plugin:skill` 与 `$skill`）、hooks/agents/session 生命周期、`openai.yaml` sidecar、路径扫描顺序的行为是否一致。做 conformance suite + portability linter（skills 的 caniuse）。

**为什么现在（证据）**：
- Agent Skills 为开放标准（agentskills.io，Anthropic 主导，Apache-2.0）；Claude Code、Cursor 2.4+、Codex CLI、Cline、Antigravity、Gemini CLI 全部原生读 SKILL.md（mcp.directory，2026-05-04）。
- 最准一句：**"The skill format is already portable; the behavior is not."**（eyeinthesky6/codex-coordinator 架构 review，2026-07-23——skills CLI 能把 skill 拷进 Claude Code，但 task identity、claims、hooks、delegation 全无映射）。
- Get Claude Skills（2026-04-28）：同格式、不同激活与副作用；Codex 特例：会话中途新增 skill 不生效。
- 行为差异清单已有实据：`$skill` 显式调用仅 Codex；allowed-tools 仍两家实现；Codex 有 openai.yaml sidecar；路径协议有三套（.claude/.codex/.agents/skills/）。

**竞争**：chriscox/agent-skills（多目标 install.sh）、agile-skills 的 CODEX_COMPATIBILITY.md、camoa/claude-skills 的 PORTABILITY.md——全部是手工文档或安装脚本，无自动化 conformance 测试。

**差异**：输出精确差异矩阵（feature × harness）而非散文；给 skill 作者与 marketplace 双方当质检层；与 #2（Registry）天然互补——Registry 管分发，conformance 管质量。

**star 策略**：一条命令出 8-harness 兼容矩阵截图（天生适合传）；"Your skill works: Claude ✅ Codex ⚠️ Cline ❌"。

**首个 milestone**：3 个 harness × 10 个 feature 点（激活、工具授权、hook 触发、路径发现）实测矩阵 + GitHub Action。

**风险**：标准继续进化可能拉平行为差异，缺口收窄；时效窗口短。**修订建议：从独立候选降级为并入 #2 的 conformance 层。**

---

## 淘汰区与反方尽调（对短名单诚实做减法）

**主动不做**（合并 echo1 #4 淘汰区，补我侧反证）：
- 本地检索/记忆层：痛点真实（"本地模型搜索像回到 Altavista"，r/LocalLLaMA 2026-07 原声），但供给内卷且天花板待证；
- 通用 code graph / RAG / observability：饱和（echo1 定量），且与平台特性撞车；
- 终端 agent / skill 大合集：无行为差异位。

**对自己两个最高分的反方（预注册）**：
- 反 #3：oracle 问题不解决，外部状态对比也会退化成大号 `assert`；接入长尾可能先被 harness 原生 hooks 夺位。对策：只做 top-5 目标类型（git / ticket / SQL / sqlite / http），明确不做通用验收框架。
- 反 #6：见其风险段——我愿自我降位。

**对 #8 的修订**：如 dossier 内所列，候选降级并入 #2。

---

## 定点补查回执（接 echo1 [#4] 三问）

1. **视频/世界模型（#7/#9 真伪）**：真需求。WBench（arxiv 2605.25874，复旦+美团，289 案例 / 1,058 turns）自述"现有 benchmark 只覆盖部分必要能力、无统一标准"；跨 20 模型结论是**行为可控性远差于画质**（事件编辑 turn 间掉 33 分、主体行动 30.7 分），且行为分与画质分近零相关（r=-0.12~-0.15）。VEBench（2605.03276，3.9K 视频 / 257 小时标注）确认编辑认知缺口。现有 benchmark 全是评级考卷，工程侧可复现工具空缺——与 echo1 landscape 的低竞争数据互恰。
2. **验收候选（TestJack 之外）**：decodethefuture 测试清单原句 + Replit 删库事故 + Karakun main 分支删树事故，见 #3"为什么现在"。
3. **Adapter/skill 格式差异**：格式已标准（agentskills.io）、行为未标准；#8 按证据降级并入 #2，见 dossier。


---

# Part III — 跨候选 thesis

1. **最像“我们”的项目不是又一个 agent，而是 agent 世界的“信任层”**：权限（#1）、供应链（#2）、验收（#3）、审计（#6）都在回答同一个问题——“agent 做的事，你敢信吗？” 它们可以共享一套事件 schema/策略引擎，长期有机会合并成一个平台。
2. **传播最强的是“恐惧 + 证明”**：DROP TABLE 被拦截、恶意 skill 被拦截、agent 说完成但数据库没变、录像被篡改后 verify 断链。都比“我们更快/更准”更适合 GitHub/HN。
3. **若未来明确投入视频/多模态资源，#7/#9 可作为第二曲线**；当前不假设老板背景，且 #9 已被排除。
4. **#8 的降级是一个好信号**：证据推翻了我们自己的初评，说明这轮调研不是自我确认。合并进 #2 后，“Registry + conformance”比“Registry + 翻译器”更窄、更可信。

# 复核清单（echo2）

- [x] 数字与链接是否与 `docs/star-landscape-2026-10.md` / `docs/demand-2026-10.md` 一致（#2 的 1,184/26.1% 已补 arXiv/CSA 出处）；
- [x] #8 的降级表述是否准确；
- [x] Top 3 排序是否同意；若不同意，给出“换谁、为什么”；
- [x] 是否有事实性错误或过度承诺；
- [x] 合并是否丢了你的反方意见（应保留）。

# 数据与来源

- `docs/star-landscape-2026-10.md`：GitHub Search API 30 个查询、4 批数据、局限说明。
- `docs/demand-2026-10.md`：HN/Reddit/GitHub/媒体需求证据（echo2）。
- `reports/3-comm-experiment.md`：20 消息通信对照实验。
- `reports/3-candidates-echo1.md` / `reports/3-candidates-echo2.md`：单写原始档案。
