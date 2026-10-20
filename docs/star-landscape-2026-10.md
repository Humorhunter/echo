# star-landscape-2026-10：GitHub 高星赛道定量扫描（echo1 侧）

调研日期：2026-10-20（UTC）
方法：GitHub Search API，按 `stars` 降序取每个查询 Top 10；记录匹配仓库总数、Top 星数、Top 10 星数中位数、最大/中位 `stars/day`（按 `created_at` 折算）。原始 JSON 在 `tmp/research/github_landscape*.json`（未提交），查询语句在下表。
配对文档：`docs/demand-2026-10.md`（echo2 定性侧）。

## 0. 先给结论

1. **2026 年的主赛道是“agent harness / skills”，不是“又一个 LLM 应用”。** `created:>2026-01-01 stars:>1000` 有 **3,348** 个仓库；Top 10 星数中位数 **20.8 万**，头部 `morluto/rea` 34.0 万、`deepseek-ai/deepseek-harness` 25.5 万（3,804★/天）。这是极端拥挤、也极端容易起量的 Meta。
2. **“技能”是当前最强的内容形态，但纯技能包已内卷。** `agent skills` 自 2025 年以来 **655** 个仓库 >500★，Top 30.2 万，Top 10 中位数 13.0 万；头部是 `obra/superpowers` 30.2 万、`mattpocock/skills` 29.8 万、`anthropics/skills` 18.2 万。再做“又一个技能合集”很难差异化。
3. **安全/身份/供应链是热度与空位同时存在的少数区域。** `agent security` 217 个 >200★（Top 28.4 万，但 Top 10 中位数只有 1.68 万，说明头部是通用 harness，不是安全专品）；`agent firewall` 仅 14 个 >100★（Top 1,616★）；`sbom agent` 7 个 >50★；`prompt injection` 24 个 >200★。**需求已被 CVE 和事故验证，但开源“细粒度授权 + 审计 + 隔离”尚无头部。**
4. **代码知识图谱/记忆/上下文工程已被验证，但高度饱和。** `knowledge graph` 45 个 >500★，Top 12.9 万，中位数 1.05 万（Graphify 12.9 万、Understand-Anything 8.7 万、codegraph 7.4 万）；`agent memory` 415 个 >200★；`context engineering` 37 个 >300★。除非有强楔子，不建议正面进入。
5. **Computer-use 的“测试/QA”层是明显空位。** `computer use` 42 个 >300★，Top 3.0 万（`trycua/cua`）；但 `SpecOps`（ICSE'26 论文实现）6★、`desktest` 2★，测试框架层几乎没有星。**基础设施已有（cua/Cua-Bench/MCPWorld），缺“把 agent 轨迹变成可回归 CI 测试”的产品。**
6. **视频/世界模型是“低竞争、低当前星数、高专业壁垒”的长期选项。** `video generation` 139 个 >300★，Top 1.85 万；`video benchmark` 19 个 >200★，Top 4,459★；`world model evaluation` 19 个 >100★，Top 2,264★。星数天花板明显低于 agent 赛道，但低竞争与可复现工程适合做“研究者基础设施 + 排行榜”的长期品牌。
7. **local-first 搜索/记忆应淘汰。** `local_first` 285 个 >500★，Top 10.3 万、中位数 4.2 万；`agent memory` 415 个 >200★；`rag` 358 个 >500★。需求真，但供给更卷，双人文团队没有胜算。

## 1. 数据表（节选）

阈值不同，`匹配仓库数` 不能直接横比；它只表示“该查询下有多少仓库达到门槛”，用来判断赛道深度。

| 类别 | 查询 | 匹配仓库数 | Top★ | Top10 中位★ | 最大★/天 | 代表项目 |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 2026 破圈 | `created:>2026-01-01 stars:>1000` | 3,348 | 340,103 | 208,099 | 3,804 | morluto/rea |
| agent 新库 | `agent created:>2025-01-01 stars:>1000` | 1,740 | 340,071 | 236,739 | 1,799 | morluto/rea |
| MCP | `mcp created:>2024-06-01 stars:>500` | 1,311 | 340,072 | 111,738 | 1,799 | morluto/rea |
| coding agent | `coding agent created:>2024-06-01 stars:>500` | 919 | 302,261 | 160,575 | 1,295 | obra/superpowers |
| agent skills | `agent skills created:>2025-01-01 stars:>500` | 655 | 302,263 | 130,135 | 1,154 | obra/superpowers |
| agent memory | `agent memory created:>2024-06-01 stars:>200` | 415 | 284,309 | 44,793 | 1,034 | affaan-m/ECC |
| RAG | `rag created:>2024-06-01 stars:>500` | 358 | 129,365 | 65,712 | 650 | Graphify-Labs/graphify |
| local-first | `local-first created:>2024-01-01 stars:>500` | 285 | 102,620 | 41,637 | 586 | nexu-io/open-design |
| agent security | `agent security created:>2024-06-01 stars:>200` | 217 | 284,309 | 16,797 | 1,034 | affaan-m/ECC |
| world model | `world model created:>2024-01-01 stars:>300` | 162 | 17,474 | 6,195 | 116 | NVIDIA/cosmos |
| video generation | `video generation created:>2024-06-01 stars:>300` | 139 | 18,538 | 7,450 | 81 | HBAI-Ltd/Toonflow-app |
| terminal agent | `terminal agent created:>2024-06-01 stars:>500` | 139 | 152,793 | 60,294 | 455 | anthropics/claude-code |
| agent sandbox | `agent sandbox created:>2024-06-01 stars:>200` | 134 | 84,178 | 13,772 | 159 | bytedance/deer-flow |
| agent observability | `agent observability created:>2024-06-01 stars:>200` | 84 | 21,731 | 8,969 | 61 | NirDiamant/agents-towards-production |
| LLM eval | `llm evaluation created:>2024-06-01 stars:>500` | 56 | 34,781 | 7,906 | 77 | Tencent/WeKnora |
| knowledge graph | `knowledge graph created:>2025-01-01 stars:>500` | 45 | 129,366 | 10,461 | 650 | Graphify-Labs/graphify |
| computer use | `computer use agent created:>2024-06-01 stars:>300` | 42 | 30,279 | 2,973 | 139 | trycua/cua |
| MCP gateway | `mcp gateway created:>2024-06-01 stars:>200` | 39 | 78,637 | 4,698 | 317 | diegosouzapw/OmniRoute |
| context engineering | `context engineering created:>2024-06-01 stars:>300` | 37 | 64,267 | 6,654 | 208 | gsd-build/get-shit-done |
| skill marketplace | `skill marketplace created:>2025-01-01 stars:>200` | 29 | 27,542 | 2,628 | 117 | OthmanAdi/planning-with-files |
| prompt injection | `prompt injection created:>2024-06-01 stars:>200` | 24 | 20,638 | 849 | 97 | NVIDIA/SkillSpector |
| agent provenance | `agent provenance created:>2024-06-01 stars:>100` | 21 | 6,061 | 481 | 29 | wiltodelta/remove-ai-watermarks |
| video benchmark | `video benchmark created:>2024-01-01 stars:>200` | 19 | 4,459 | 405 | 14 | EvolvingLMMs-Lab/lmms-eval |
| world-model eval | `world model evaluation created:>2024-01-01 stars:>100` | 19 | 2,264 | 414 | 10 | galilai-group/stable-worldmodel |
| agent tracing | `agent tracing created:>2024-06-01 stars:>200` | 17 | 16,176 | 1,157 | 138 | raga-ai-hub/RagaAI-Catalyst |
| AI education | `ai education created:>2024-06-01 stars:>500` | 15 | 40,612 | 2,260 | 84 | Crosstalk-Solutions/project-nomad |
| skill registry | `skill registry created:>2024-06-01 stars:>100` | 14 | 53,231 | 2,616 | 199 | VoltAgent/awesome-openclaw-skills |
| agent firewall | `agent firewall created:>2024-06-01 stars:>100` | 14 | 1,616 | 297 | 20 | hardenrun/aif |
| reproducible research | `reproducible research created:>2024-01-01 stars:>200` | 12 | 5,297 | 445 | 49 | aipoch/open-science |
| agent package manager | `agent package manager created:>2024-06-01 stars:>100` | 8 | 4,067 | 535 | 10 | microsoft/apm |
| SBOM agent | `SBOM agent created:>2024-06-01 stars:>50` | 7 | 947 | 163 | 24 | ZeroDayEvil/ai-security-tool |
| AI video editor | `video editor ai created:>2024-06-01 stars:>500` | 7 | 14,607 | 1,015 | 94 | palmier-io/palmier-pro |

## 2. 头部样本说明了什么

### 2.1 起量靠“一句话钩子”，不是架构图

2026 破圈 Top 10 里，多数是**可一句话说清、30 秒可演示**的东西：

- `morluto/rea`：Reverse engineer anything with agents（34.0 万）
- `mattpocock/skills`：Skills for Real Engineers（29.8 万）
- `affaan-m/ECC`：agent harness optimization：skills/instincts/memory/security（28.4 万）
- `DietrichGebert/ponytail`：让 agent 像“最懒的资深工程师”一样思考（16.8 万）
- `JuliusBrussee/caveman`：用更少 token 说话（11.4 万）

**含义**：候选项目必须有一个“不解释就懂”的钩子；但纯钩子生命周期短，需要第二层基础设施做护城河。

### 2.2 真正的“层”比“包”更持久

高星里能长期站住的，往往是**层**：harness、registry、runtime、gateway、knowledge graph。单文件 skill / prompt 可以爆，但容易被复制。
**含义**：我们要做的不是“又一个 skill”，而是“skill/MCP/agent 世界的某个缺失层”，并用一个极轻的 hook 把人带进来。

### 2.3 安全类“需求强、头部弱”

- `agent security` 查询 Top 10 中位数仅 1.68 万，且第一名是通用 harness `affaan-m/ECC`，不是安全专品。
- 安全专品里，`Anthropic-Cybersecurity-Skills` 3.47 万、`cloudflare/security-audit-skill` 3.28 万、`NVIDIA/SkillSpector` 2.06 万，都是**扫描/技能**，不是**运行时授权 + 审计 + 隔离的一体件**。
- `agent firewall` Top 1,616★、`agent package manager` Top 4,067★、`SBOM agent` Top 947★：**有产品，但都还很小**。

**含义**：这是“高需求 + 低饱和”的少数象限；缺点是安全产品信任门槛高，需要可验证的 demo 和开放标准。

### 2.4 代码图谱/记忆：需求真，但别正面硬刚

`Graphify-Labs/graphify` 12.9 万、`Understand-Anything` 8.7 万、`codegraph` 7.4 万、`codebase-memory-mcp` 4.7 万；`agent memory` 还有 `claude-mem` 10.2 万、`hindsight` 5.2 万、`memU` 1.5 万。
**含义**：这类项目适合做“差异化楔子”（例如只做多 repo/增量/可验证 provenance），不适合做“又一个 code graph / memory”。

### 2.5 视频/世界模型：星数低，但竞争也低

视频生成 Top 1.85 万、视频 benchmark Top 4,459、world-model eval Top 2,264。对比 agent skills 的 30 万，天花板差一个数量级。
**含义**：如果目标是“纯 star 最大化”，视频不是最优；如果目标是“长期研究品牌 + 可多轮打磨”，它是可考虑的第二曲线，但不依赖个人背景。

## 3. 需求 × 供给矩阵（与 echo2 合并用）

|  | 供给已饱和 | 供给未饱和 |
| --- | --- | --- |
| **需求已强验证** | agent skills、agent memory、code graph、local-first、RAG、terminal agent | **agent 权限/身份层、skill/MCP 供应链安全、agent 结果验收、computer-use QA** |
| **需求待验证** | 通用 agent observability（Langfuse/OpenLIT 已占） | **code provenance/slop、world-model eval、AI video agent** |

## 4. 对候选项目的硬约束（从数据反推）

1. **必须有 30 秒钩子**：一句命令/一张图/一个“之前不可能”的对比。
2. **必须是一个“层”**：registry / runtime / verifier / leaderboard，而不是一次性脚本。
3. **必须能跨 harness**：Claude Code、Codex、OpenCode、OpenClaw 至少覆盖 2–3 个；单平台插件会被平台吸走。
4. **必须能公开验证**：安全类要有可复现攻击 demo；评测类要有可复现实验；视频类要有可对比输出。
5. **避免正面进入**：code graph、agent memory、通用 RAG、local-first 搜索、通用 observability、通用 eval 框架。

## 5. 数据局限

- GitHub star 受营销、榜单、刷星影响；本表只做赛道相对比较，不做质量判断。
- `created_at` 折算 `stars/day` 会高估新库、低估老库；仅用于“爆发力”排序。
- 查询阈值不同，`匹配仓库数` 不可直接横比；同一项目可能命中多个查询（如 `affaan-m/ECC` 同时出现在 agent/security/memory）。
- 未抓取 star 时间序列；`stars/day` 是平均值，不是当前斜率。若要做“瞬间火完 vs 长尾”，需要 star 历史（task2 已建议，未执行）。
- 2026 年数据含大量 AI 生成/营销项目，头部星数可能包含非真实采用。

## 6. 下一步

- 与 `docs/demand-2026-10.md` 合并，按评分表打分，产出 8–10 个候选与 Top 3。
- 对 Top 3 各做一次“反方尽调”：找 3 个最强竞品、3 个失败先例、1 个平台吸走风险。
- 20 消息通信实验放在短名单之后，不抢主任务。
