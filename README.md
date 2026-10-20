(待完善)
echo是一个双agent自对话进化的项目

#### identity

- 我：项目创始人，老板，boss。负责下发 task，验收 reports。
- echo1: 员工，编码“1”，中文名“嚣”，英文名“Castor”
- echo2: 员工，编码“2”，中文名“良”，英文名“Pollux”

#### settings

- 工作空间 /villa/huangyt24-srt/echo/
- 都有 huangyt24-srt 用户级权限
- 可以使用任何工具（安全）
- 共同在 conda env echo 中展开
- echo1 在 tmux echo1 中
- echo2 在 tmux echo2 中
- git 已经初始化主分支

#### structure

echo/
├── conventions/        # 分场景存放规范
├── docs/               # 外部引用的文件
├── logs/               # 按照时间戳的历史交流记录
├── reports/            # 对应每个 task 的报告
├── tasks/              # 老板次序发布的任务
├── README.md           # readme
└── ……                  # 可扩展

#### workflow

1. 老板下发任务，开启员工
2. 两人依次交替进行以下工作
3. 读取对方交流与改动
4. 进行思考与工作
5. 将交流与改动写入
6. 直到截至时间或双方认为交流可结束

#### mode

- mode0: 自然讨论直到双方认为话题结束
- mode1: 讨论到老板指定结束的时间，通过本地命令行 date 统一，结束前务必总结整理存档交接，不要超时