# CareerMentor V2 双平台验收

验证日期：2026-10-08，Asia/Shanghai。交付使用Markdown、Python标准库和现有ChatGPT／Codex服务；没有实现Web、付费API调用、本地模型或MCP服务。

## 验证范围与档案保护

自动化测试和合成学生对话都在 `.verification/` 隔离副本中进行。合成回答、错误、分数和复测计划不是用户的真实能力记录，不能合并到根目录 `data/`。改版保留五份原学习档案和原初始化报告；验证结束核对其SHA256。

| 检查 | 实际结果与边界 |
| --- | --- |
| 项目Skill规范 | `skill-creator/scripts/quick_validate.py` 实际执行，输出 `Skill is valid!` |
| 插件内Skill规范 | 对 `plugins/career-mentor/skills/career-mentor` 实际执行同一验证器，输出 `Skill is valid!` |
| 两平台同源标准 | 指令内核心与canonical核心逐字一致，记录／报告模板逐字一致；由分发测试实际检查 |
| 生成件一致性 | `tools/build_distribution.py --check` 实际退出0；30个生成件、16个插件文件无漂移；ChatGPT指令6668字符 |
| 复测日期 | 标准库unittest 7/7通过；D+3／D+7、到期／逾期、下一次训练事件、缺席、单槽完成、闰年跨年与无效输入 |
| 分发行为 | 标准库unittest 7/7通过；ZIP资源闭包、无个人档案／MCP／Apps／hooks、可复现字节及SHA256、只读check、重建、保留已有marketplace、同名路径冲突与额外私密文件拒绝 |
| 全部自动化 | `python -X utf8 -m unittest discover -s verification -v` 实际执行：14项通过，退出0 |
| 新Codex进程发现 | 新启动ephemeral Codex进程实际退出0；启动技能清单包含新版career-mentor，路径指向隔离副本；未调用文件工具来伪造发现 |
| ChatGPT指令前向试用 | 独立测试代理仅载入项目指令／参考资料，之后按无本地文件与执行工具的ChatGPT条件教学；初始训练一道题，错误后一级提示且无完整解答；暂停后保留原题与提示，进入压力面试并按实际回答追问 |
| ChatGPT自动收尾报告 | 用户仅说“今天结束”，即输出完整v2报告；引用两次实际回答，未观察项保持未评估，全部有效复测／暂停题保留，时间不可知写unknown，未假装写本地或已同步 |
| ChatGPT新上下文接续 | 独立新代理仅读项目指令＋上一报告，使用隔离模拟日期10月11日；正确识别next_session待办及D+3今日到期，D+7保留10月15日，旧题暂停状态保留，只出一道无提示新变式，无虚构复测成绩 |
| Codex真实代码检查 | 对故意含顺序错误的合成提交实际运行9例：6通过、3失败，准确复现输入顺序错误；原代码SHA256及快照一致。它是成功发现错误的验证，不是学生代码全部通过 |
| Codex证据记录 | 实际写入隔离progress／weaknesses，最高提示3、AI辅助，不能计独立完成；单题多用例失败仅支持一个待验证知识点，next_session／10月11日／10月15日均未进行 |
| Codex自动收尾与旧报告保留 | 仅收到“今天结束”即保存未完成题、追加日终及下一项专项计划，生成 `R-2026-10-08-Codex-001`；旧初始化报告实际存入archive，代码未改，无新增作答或虚假完成 |
| Codex新上下文读档接续 | 独立新代理无原对话记忆，实际读取隔离磁盘档案；保留旧代码和暂停题，next_session选择一道原输入顺序的新变式，新题提示0，D+3／D+7原计划保留；未答题不产生复测成绩 |
| ChatGPT报告导入Codex | 实际归档完整原文及SHA256、保留两项外部待核验观察／原复测计划／两道暂停追问；接受明确unknown时间，不补造本地作答、测试或分数 |
| 同份报告重复导入 | 实际再次导入同ID＋同SHA256，五份隔离data文件哈希均不变；没有重复证据、评分或复测任务 |
| 同ID异文冲突 | 导入保留同ID但附加注释的异文，实际保存独立conflict文件并追加冲突索引；原导入SHA256不变，除索引所在progress外的四份隔离档案均不变，未新增学习成绩或复测任务 |
| 真实档案与文件链接 | 核对五份真实学习档案＋初始化报告，6个文件SHA256均未变化；32份交付Markdown的相对链接检查缺失0，嵌入核心逐字一致 |

新Codex发现日志：`.verification/v2/codex-discovery.md`、`discovery-events.jsonl`。上述“ChatGPT试用”是隔离代理的行为测试，不是登录用户真实ChatGPT网页完成的界面测试。

代码实测产物：`.verification/v2/codex/exercises/review-Q-2026-10-08-001/test-results.json` 与 `submission.original.py`；原提交SHA256为 `dbb6c864c9bfade6f6f8d8a3b5bc96d01513ebd4aa031f4741da79d6cd793a62`。结构与档案保护结果在 `.verification/v2/structure-results.json`。最终ZIP的SHA256见 `dist/career-mentor-skills-only.sha256`；ZIP本身不含这些测试材料。

ChatGPT合成对话与报告：`.verification/v2/chatgpt/transcript.md`、`report.md`；新上下文回复：`.verification/v2/resume/response.md`。报告SHA256为 `93ed5dd62731e589bea49cdf02d1a31b311a4405e86f3b1701bd87e30b406d29`。这些记录只供验证，不是用户学习历史。

导入产物：`.verification/v2/import/handoff/imports/R-20261008-CGPT-001.md`；去重前档案哈希在 `before-duplicate.json`。新Codex上下文是使用真实文件工具的隔离代理测试，窄范围经自动审核读取成功；不能代替下述默认sandbox路径的产品端到端验证。

交接最终文件核验在 `.verification/v2/handoff-results.json`：原导入未变、异文原始字节已保存、没有意外学习档案变更、Codex旧初始化报告逐字节归档均通过。

## 实际修复

- 两平台共用 `references/core.md`，ChatGPT指令／可读规范／模板／插件由同一生成器产生，不再把ChatGPT仅当Codex的外围辅助。
- Skill不再按安装路径的固定层级找学习档案，支持插件缓存安装；档案绑定实际工作区，缓存不存学生记录。
- 统一独立性、0–4量表、首次证据日D及延迟复测判据；澄清“无提示且未见答案”的判断，未知不计独立。
- 没有时钟工具时报告时间允许明确 `unknown`，不为生成报告每天额外索取时间；结束或切平台自动准备报告。
- 修正portable manifest的 `extensions.com.openai.interface` 嵌套与默认提示数组；保留已有marketplace名称和其它条目。
- 合并ChatGPT参考资料时移除失效本地超链接，插件资源链接均在包内可解析。
- 读档接续中发现隔离档案的暂停区仍有初始化“无”，历史题干引用也曾只指向可变当前状态；已补充明确规则：当前摘要与明细保持一致，题干引用固定ID历史／文件。生成件重新构建并复查。这项规则修订未再次做长期多次换题实验，不声称完全杜绝摘要漂移。

## 明确未完成的产品验证

当前工具不能读取用户ChatGPT账号的自定义插件导入权限。已生成插件目录、ZIP和本地marketplace，但没有在用户真实ChatGPT界面安装、发布插件或创建项目；不据此断言账号支持或不支持。可靠入口是复制 `CHATGPT_INSTRUCTIONS.md` 到项目指令，上传一份参考资料。

本机普通sandbox文件工具多次报 `helper_unknown_error: setup refresh had errors`。窄范围、经自动审核的文件操作可执行，本次构建及自动化测试因此得以完成。此前独立CLI的“读取档案并接续”检查在默认sandbox下被此错误阻断；**该默认权限路径没有通过端到端恢复验证**，与新版Skill启动发现成功是两回事。没有通过关闭沙箱或更改全局配置绕过问题。

没有逐一实测全部八类面试、全部每日七环节、长期真实学习或2027实际投递。规则和模板已覆盖这些模式，不能把有限行为测试解释为未来所有对话必然符合规范。没有创建自动提醒；日常需用户启动训练、实际作答，切平台传一份报告。

## 可重复检查

```powershell
python -X utf8 tools/build_distribution.py --check
python -X utf8 -m unittest discover -s verification -v
```

Skill创建器验证依赖PyYAML，仅验证环境使用忽略目录 `.verification/deps/`，没有变成Skill运行时依赖。日期工具、分发生成器和本项目自动化测试均为标准库。

## GitHub分发准备验证

为私有仓库分发补充 `tools/init_workspace.py`：新克隆只创建缺失的五份空白档案，既有字节及修改时间保留，不生成私人报告或训练成绩。新增3项隔离测试通过，连同原测试共17项通过。默认路线与核心五阶段一致；所有默认目标明确标为可更正的仓库默认值，不冒充新用户自述。

仓库采用LF文本换行与二进制ZIP属性，实际重建后 `build_distribution.py --check` 通过，避免Windows克隆导致源文本与打包字节不一致。Git发布范围仅教学资源、公共指令、模板、插件和标准库工具；排除data、私人报告、练习／项目代码、隔离验证和密钥。提交身份使用GitHub隐私邮箱。
