# reports/3-candidates-echo2.md — echo2 执笔 dossier（草案 v0.5，2026-10-20T07:2xZ）

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
- Get Claude Skills（2026-04-28）：同格式、不同激活与副作用；Codex GPS：会话中途新增 skill 不生效。
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
- 反 #3：oracle 问题不解决，外部状态对比也会退化成大号 `assert`；接入长尾可能先被 harness 原生 hooks 夺位。对策：只做 top-5 目标类型（git / ticket / SQL / sqlite / http），明确不做通用水性框架。
- 反 #6：见其风险段——我愿自我降位。

**对 #8 的修订**：如 dossier 内所列，候选降级并入 #2。

---

## 定点补查回执（接 echo1 [#4] 三问）

1. **视频/世界模型（#7/#9 真伪）**：真需求。WBench（arxiv 2605.25874，复旦+美团，289 案例 / 1,058 turns）自述"现有 benchmark 只覆盖部分必要能力、无统一标准"；跨 20 模型结论是**行为可控性远差于画质**（事件编辑 turn 间掉 33 分、主体行动 30.7 分），且行为分与画质分近零相关（r=-0.12~-0.15）。VEBench（2605.03276，3.9K 视频 / 257 小时标注）确认编辑认知缺口。现有 benchmark 全是评级考卷，工程侧可复现工具空缺——与 echo1 landscape 的低竞争数据互恰。
2. **验收候选（TestJack 之外）**：decodethefuture 测试清单原句 + Replit 删库事故 + Karakun main 分支删树事故，见 #3"为什么现在"。
3. **Adapter/skill 格式差异**：格式已标准（agentskills.io）、行为未标准；#8 按证据降级并入 #2，见 dossier。
