# 20 消息通信实验数据（task3 附录）

半合成语料：20 条消息（8 INFO / 5 ASK / 4 ACK / 3 ERROR），每条含唯一事实。用于比较“日志散文”与“邮箱 JSON”两种通道的字节/token 开销与盲还原率。

- `arm_a.md`：A 臂，日志散文（标题行 + 自然语言 body）。
- `arm_b/echo2/*.json`：B 臂，同一 body 的邮箱 JSON（v0.3 格式；含空 `reply_to`、缩进）。
- `quiz.md`：20 题盲测。
- `answers.md`：标准答案（读者不可见）。

方法/结果：`reports/3-comm-experiment.md`。
注意：语料为半合成，不含真实密钥/隐私；数字只用于同口径比较，不是真实 tokenizer。B 臂 v0.4 的紧凑化数据由同一语料重编码得到，报告中有实测值。
