# 通信实验 A 臂：日志散文

## [2026-11-01T02:00Z][#1] echo1 (INFO)

Helios M1 里程碑从 2026-10-31 推迟到 2026-11-03，原因是集群 GPU 配额被临时收回 48 小时。负责人仍为 echo1，回滚点在 11-01 18:00Z。

## [2026-11-02T03:00Z][#2] echo1 (ASK)

请 echo2 在 2026-11-05 前复核 tokenizer 报告 v2，重点看中文标点切分和 8k 上下文截断；复核结论写入 reports/helios-tokenizer.md，并在日志 #21 回执。

## [2026-11-03T04:00Z][#3] echo2 (ACK)

已复核 task2 日志 #12 的指标定义，结论：通过。唯一修改是把 long-horizon 的窗口从 32 帧改成 48 帧；修改已写入 docs/metrics.md 第 4 节。

## [2026-11-04T05:00Z][#4] echo2 (ERROR)

2026-11-02T03:14Z 集群 A100 节点 7 掉线，影响 3 个训练 job；已自动重排队，预计延迟 2 小时 40 分。请 echo1 在 04:00Z 前确认 checkpoint 完整性。

## [2026-11-05T06:00Z][#5] echo1 (INFO)

新评估指标 long-horizon consistency 的权重定为 0.35；physical plausibility 权重 0.40；action controllability 权重 0.25。总权重必须为 1.0，缺项按 0 计。

## [2026-11-06T07:00Z][#6] echo1 (ASK)

请 echo2 在 11-06 前给出 5 个 world-model benchmark 候选，每个附论文链接、数据集规模、许可证；优先选 2025 年后发布且可本地复现的。结果放 docs/world-bench-shortlist.md。

## [2026-11-07T08:00Z][#7] echo2 (INFO)

Helios 的默认视频分辨率定为 768x1280，帧率 24fps，单段最长 12 秒；超过 12 秒必须切段并在 metadata 里写 segment_id。

## [2026-11-08T09:00Z][#8] echo1 (ACK)

已收到 echo2 的 benchmark 短名单，确认 3 个候选进入复现：WorldBench-Lite、Physion++、CausalVideo。复现预算上限 120 GPU 小时。

## [2026-11-09T01:00Z][#9] echo2 (INFO)

命名规范更新：所有实验目录用 helios-<日期>-<owner>-<序号>，例如 helios-20261103-echo1-01；不要再用实验名+随机后缀。旧目录保留只读。

## [2026-11-10T02:00Z][#10] echo2 (ASK)

请 echo1 在 11-07 前确认数据集许可证清单，特别是 CC-BY-NC 的 4 个数据集能否用于内部评测；不能用的标记为 blocked，不要删除原始记录。

## [2026-11-11T03:00Z][#11] echo1 (ERROR)

2026-11-04T09:22Z 发现 reports/3-candidates.md 的评分表有两行权重加总为 1.05；已回滚到 v0.9，等待 echo2 复核后再发布。

## [2026-11-12T04:00Z][#12] echo1 (INFO)

Helios 的 baseline 固定为 3 个：Cosmos-2B、StableVideo-XL、Oasis-1.5B；任何新模型必须先在 3 个 baseline 上跑同一套 48 帧评测。

## [2026-11-13T05:00Z][#13] echo2 (ACK)

已收到 11-03 的 M1 延期通知，确认回滚点 11-01 18:00Z；我会在 10-30 前冻结 feature branch，不再合入新功能。

## [2026-11-14T06:00Z][#14] echo2 (INFO)

对外 demo 只展示 3 个场景：物理碰撞、长程身份保持、动作可控；不展示失败案例，失败案例放内部 appendix。demo 时长控制在 90 秒。

## [2026-11-15T07:00Z][#15] echo1 (ASK)

请 echo2 在 11-08 前把 20 条通信 fixtures 转成邮箱格式，A 臂保留原散文，B 臂用同一 body；不要改事实、不要加解释。产出放 tmp/experiment/。

## [2026-11-16T08:00Z][#16] echo1 (INFO)

CI 规则更新：任何 PR 必须通过 3 项检查——unit test、tokenizer regression、license scan；缺一项直接 block，不允许 admin merge。

## [2026-11-17T09:00Z][#17] echo2 (ERROR)

2026-11-05T16:40Z 发现 benchmark 短名单里 Physion++ 的许可证字段为空；在补齐前不得用于对外报告，内部复现可以继续。

## [2026-11-18T01:00Z][#18] echo1 (ACK)

已确认 checkpoint 完整性：节点 7 上 3 个 job 的最后 checkpoint 均通过 SHA-256 校验；无需回滚，重排队继续。

## [2026-11-19T02:00Z][#19] echo2 (INFO)

周报格式改为 5 行以内：本周结论、关键数字、阻塞、下周计划、需要老板决策；详细内容放 appendix，不再复制日志。

## [2026-11-20T03:00Z][#20] echo2 (ASK)

请 echo1 在 11-09 前给出 Top 3 候选的 2 周 spike 计划，每个 spike 必须有可运行 demo、1 个真实用户试用、1 个停止条件；结果放 reports/3-spike.md。
