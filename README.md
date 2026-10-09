# CareerMentor V2 · ChatGPT + Codex

面向2027届软件工程校招的长期学习系统：南京就业，优先Python后端／AI应用，备选Java初级开发／软件测试。两个平台执行**同一核心教学标准**，都支持每日提问、动态技术追问、压力面试、知识盲区诊断、针对性复习、能力评价和长期记录。

ChatGPT优先理论与压力面试，Codex优先独立编程与代码实测。可以在任一平台完成当天训练；无需为了走流程每天来回切换。使用Markdown和Python标准库，不开发Web、不接付费API、不运行本地大模型。现有ChatGPT／Codex服务自身的账号权限和使用限额仍由平台决定。

## 先用起来

### Codex：本项目已放好Skill

1. 在Codex打开克隆或复制后的仓库文件夹。从GitHub新克隆时先在该文件夹执行 `python -X utf8 tools/init_workspace.py`，只初始化缺失的学习档案，不覆盖已有记录。
2. 输入：

   ```text
   $career-mentor 开始今日训练
   ```

3. 如果列表没有更新，重开项目会话或重启客户端。项目技能路径为 `.agents/skills/career-mentor/SKILL.md`；CLI／IDE支持的技能列表可用 `/skills` 检查。[官方技能规范](https://learn.chatgpt.com/docs/build-skills)

不必复制到全局目录、不必先装插件。初始化后，Skill会读五份本地学习档案，先恢复未完成题与复测；没有记录就说明尚未评估，提出一道小型诊断题。你先分析、自己编码，Codex审查和测试，默认保留你的原实现。

在其它电脑或项目使用时，复制整个本项目即可恢复本地历史；仅复制Skill或安装插件只带教学规则，不带个人档案。插件安装位置不能用作学习记录目录。

GitHub仓库只保存教学资源和工具，`data/`、私人训练报告、个人练习／项目代码均不上传。克隆仓库不会恢复个人历史；需要接续时请自行安全复制本地档案或导入保存的报告。仓库主页为 [mingw0788/career-mentor](https://github.com/mingw0788/career-mentor)，私有仓库需要有访问权限的GitHub账号。

### ChatGPT：项目指令是可靠入口

1. 在ChatGPT建立私人CareerMentor项目，把 [CHATGPT_INSTRUCTIONS.md](CHATGPT_INSTRUCTIONS.md) **全文粘贴到项目指令**。
2. 把 [CHATGPT_REFERENCE.md](handoff/CHATGPT_REFERENCE.md) 上传为项目参考资料，设置一次即可。它汇集同源的训练、面试、记录、复测和路线规范。
3. 在项目中输入“开始今日训练”或“模拟压力面试”。无需Codex已在线，也无需已有本地训练记录。
4. 从Codex切过来时额外提供最新 `handoff/latest-report.md`。项目没有可见历史时会如实说明，从一道诊断题开始。

没有项目功能时，在普通对话开头粘贴项目指令；以后新对话提供最新报告。指令自身含核心标准、常用模式和报告模板，参考资料提供更细的规则。文件工具不可用时用可复制Markdown报告，不影响理论训练或面试。项目指令和上传资料的作用见[官方项目说明](https://learn.chatgpt.com/docs/projects)。

ChatGPT可评估你给出的代码思路与片段；没有实际执行工具时标记静态观察／未运行，不谎称测试通过。编程实测建议带到Codex；可用的ChatGPT执行工具也可实测，明确来源环境。

## 日常只做这些操作

- 启动：“开始今日训练”。回答导师的**一道**题；需要时说“一级提示”“二级提示”“三级提示”。
- 收尾：“今天结束”或“我要切换到Codex／ChatGPT”。导师自动评价、保存可用记录，并准备**一份完整报告**，不必另下导出指令。
- 切换：把这一份报告作为文件上传或全文复制给另一个平台，说“导入学习报告，继续训练”。只有确实需要运行代码时再附代码文件。
- 下次仍用同平台时继续原项目；新会话若看不到最新历史，提供上次报告即可。无需每天手动编辑五份档案或逐题同步。

没有MCP或其它共享存储时，插件也不能让两个平台自动互读私人文件。报告传递是保留的必要手动步骤；完整历史建议定期私密备份。报告包含当前能力、证据摘要、全部有效薄弱点、原复测日期／实际结果、未完成题和提示等级，便于新会话接续。

“每天提问”指你启动当天训练后导师主动逐题提问。本交付没有创建后台提醒或定时任务；需要主动通知时可另用平台自带提醒能力，不是Skill本身的功能。

## 统一训练标准

- 每轮一道主要题目；先分析／作答／编码，再反馈和追问。不在同轮列一串独立子问。
- 默认不提前完整答案，按启发问题→关键思路→伪代码或局部示例提示；明确请求讲解可给完整答案，但同题不再算独立掌握。
- 记录独立／AI辅助／答案已揭示／未知，以及最高提示、外部AI自报、真实代码测试范围。
- 单次错误只形成具体待验证观察，判断引用证据与置信度；未测不记零分。
- 首次未掌握证据日为D（第0天）：下一次实际训练、D+3自然日、D+7变式复测。缺席形成逾期待办，不形成失败成绩；调整保留原计划和理由。
- 无提示独立解释、独立应用和延迟变式证据齐备才掌握；看过答案、提示后成功或一份外部报告均不够。
- 压力来自真实技术追问、反例和约束变化，允许中止；不虚构项目经验或南京招聘信息。

标准的唯一维护源在Skill的 `references/` 和 `assets/`。ChatGPT指令、可读规范、模板和插件均由同一个本地生成器制作，避免两套标准漂移。

## 指令

两平台均支持下列中文指令；Codex可加 `$career-mentor`，ChatGPT项目直接输入。

| 指令 | 用途 |
| --- | --- |
| 开始今日训练 | 昨日／到期复习→Python编程→计算机基础→压力追问→项目问答→评价→明日一项计划；可按时间调序／缩短，始终逐题 |
| 开始初始测评 | 通过实际回答与代码形成基线，未覆盖项保留未评估 |
| 模拟技术面试 | Python、Java、MySQL、算法、网络／操作系统、AI Agent、项目、综合校招；默认Python后端 |
| 模拟压力面试 | 根据回答技术深挖与约束变化，结束给有依据的评分 |
| 开始编程挑战 | 你先分析并实现，记录辅助情况 |
| 检查我的代码 | 保留原解答，检查正确性／边界／异常／质量，有工具才实测 |
| 找出我的不足 | 区分待验证观察、重复错误、未评估领域 |
| 针对性补弱 | 一项具体训练及有证据的复测 |
| 项目面试 | 基于真实贡献和材料追问；假设场景另标 |
| 每周能力总结 | 只统计可见最近7日记录，说明缺失及不可比部分 |
| 生成同步报告 | 显式导出；结束／切平台时也会自动准备 |
| 导入学习报告 | 保留来源、去重、冲突与待核验状态 |

兼容旧命令“生成ChatGPT同步报告”“生成Codex同步报告”“导入ChatGPT诊断报告”。可以说“暂停”“继续”或切换模式，保存原题与提示，不因切换重复记分。

## 实际文件与职责

| 文件／目录 | 职责 |
| --- | --- |
| [.agents/skills/career-mentor/SKILL.md](.agents/skills/career-mentor/SKILL.md) | 双平台可移植Skill入口，Codex发现与模式路由，按实际宿主适配持久化 |
| [CHATGPT_INSTRUCTIONS.md](CHATGPT_INSTRUCTIONS.md) | 可直接粘贴的ChatGPT项目指令；包含同源核心标准与报告模板 |
| [standards/core.md](standards/core.md) | 统一核心教学标准的生成副本 |
| [standards/training.md](standards/training.md)、[interviews.md](standards/interviews.md) | 每日训练／编程与八类模拟面试规范 |
| [standards/records.md](standards/records.md)、[roadmap.md](standards/roadmap.md)、[handoff.md](standards/handoff.md) | 证据、复测、动态五阶段路线与跨平台同步 |
| [templates/LEARNING_RECORD_TEMPLATE.md](templates/LEARNING_RECORD_TEMPLATE.md) | 统一当前题、尝试、薄弱点、面试及计划记录字段 |
| [templates/TRAINING_REPORT_TEMPLATE.md](templates/TRAINING_REPORT_TEMPLATE.md) | 两平台同用的 `career-mentor-report/v2` 报告 |
| [AGENTS.md](AGENTS.md) | Codex工作区读档、留历史及隐私规则 |
| `data/profile.md` | 已提供背景、偏好与待确认约束 |
| `data/progress.md` | 当前状态、原回答、提示／独立性、训练历史 |
| `data/weaknesses.md` | 具体薄弱点、证据、置信度和复测状态 |
| `data/interviews.md` | 面试追问、量表评分与证据 |
| `data/learning-plan.md` | 动态路线与调整历史 |
| [handoff/CHATGPT_REFERENCE.md](handoff/CHATGPT_REFERENCE.md) | 一次上传到ChatGPT的完整参考资料 |
| `handoff/latest-report.md` | 最新私人学习报告，仅本地维护；首次收尾／导出时生成，不随仓库分发 |
| `handoff/chatgpt-project-instructions.md` | 与根指令相同的兼容入口 |
| `exercises/`、`projects/` | 学生代码、真实项目及验收材料 |
| `plugins/career-mentor/` | 已生成的无MCP、无个人学习数据插件目录 |
| [.agents/plugins/marketplace.json](.agents/plugins/marketplace.json) | 本项目的可选本地插件目录清单 |
| [dist/career-mentor-skills-only.zip](dist/career-mentor-skills-only.zip) | 可分发插件ZIP；另有SHA256校验文件 |
| [verification/acceptance.md](verification/acceptance.md) | 实际验证结果与未验证边界 |
| `tools/build_distribution.py` | 标准库生成／打包与一致性检查，日常训练无需运行 |
| `tools/init_workspace.py` | 新克隆时只补缺失的五份本地档案；保留所有既有内容 |

报告导入时按需建立 `handoff/imports/`、`archive/`、`conflicts/`；不预填历史。测试副本只在 `.verification/`，不能当你的学习档案。

## Skills-only Plugin：可打包，安装需宿主支持

已生成同时含根 `plugin.json`（Agent Plugins格式）与 `.codex-plugin/plugin.json`（Codex兼容格式）的包；两者指向同一份教学资源。包内没有MCP服务器、Apps连接、hooks、API密钥、真实档案或学生代码。官方明确技能可不依赖MCP；新格式及兼容格式见[打包规范](https://developers.openai.com/plugins/build/plugins)和[技能规范](https://developers.openai.com/plugins/build/skills)。

### 支持本地插件目录的客户端

1. 保持本项目的 `plugins/career-mentor/` 与 `.agents/plugins/marketplace.json` 同时存在。
2. 重启支持该入口的桌面客户端，打开Plugins目录，选择 **CareerMentor本地插件** 来源，安装CareerMentor V2；支持的Codex CLI可在交互界面用 `/plugins`。
3. 新建聊天，再从插件／技能选择器选择CareerMentor并输入“开始今日训练”。ChatGPT支持的选择器可输入 `@`；普通项目指令方式不需要这些标记。
4. 安装到其它本地目录时，复制插件到 `plugins/career-mentor/`，在该项目的市场清单合并同一条目，路径相对项目根。不要覆盖已有清单。也可使用宿主提供的私有ZIP导入入口（如果实际提供）。

项目本身已发现同名Skill，**无需再装插件**；插件主要用于其它支持的环境。若同一客户端重复显示两个同名技能，选项目Skill即可，避免同时安装重复副本。

自定义本地来源、ZIP导入、组织发布和公有插件目录是不同入口；ZIP不是任意ChatGPT网页都能直接上传安装的保证。IDE扩展目前不支持插件，但可以使用项目Skill。[支持界面与安装说明](https://learn.chatgpt.com/docs/plugins)

本次没有读取到当前账号的ChatGPT插件导入权限，也没有在你的ChatGPT界面完成安装。不能据此断言账号支持或不支持。若没有自定义插件来源／导入入口、被组织策略限制或界面不兼容，直接使用上述项目指令方式，不需等待插件开放。没有发布到公有目录，也没有替你创建外部项目。

## 记录、隐私与维护

本机已有学习档案会保留；新克隆创建的空白档案初始状态为“尚未测评”。今后的回答和测试才形成证据。历史追加，当前摘要可更新但须关联历史；写前重读，多会话写入需要合并。同一份报告重复导入不重复计分，同ID异文保存冲突；新报告引用旧证据也不产生新成绩。

`data/`、私人报告、练习／项目代码、密钥和隔离测试已默认排除在Git之外；这不提供加密，也不能取消已追踪文件。不要自动公开档案、简历或项目秘密。插件构建采用固定文件白名单，拒绝包内额外残留文件；它不会把当前个人档案打入ZIP。

仅在修改教学源文件后重新生成：

```powershell
python -X utf8 tools/build_distribution.py
python -X utf8 tools/build_distribution.py --check
python -m unittest discover -s verification -v
```

间隔复测日期可用Skill内 `scripts/review_schedule.py` 计算；它不写学习记录或发送通知。日常使用不需要维护脚本、数据库或外部服务。

需要手动做的事：首次粘贴ChatGPT项目指令并上传一份参考资料；切平台时传一次报告；实际作答和写代码；保存私人备份。可选插件的安装／启用依账号和宿主界面完成。验证细节和明确未通过的环境检查见验收报告。
