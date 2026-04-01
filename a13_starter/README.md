# A13 职业规划 Demo

这是我们给 2026 服务外包大赛 A13 题准备的本地演示版本。  
当前已经可以完成这条完整链路：

- 输入简历文本
- 上传本地简历文件
- 解析学生画像
- 和岗位模板做匹配评分
- 生成职业规划与行动建议
- 在网页中展示结果
- 自动保存历史记录
- 内置样例基准验证
- 导出 Markdown / HTML / Word 报告
- 通过打印页导出 PDF

## 一、队友怎么直接跑起来

### 1. 进入项目目录

```bash
cd a13_starter
```

如果你当前就在项目根目录 `server2026`，也可以不切目录，直接按下面命令运行。

### 2. 配置千问 API Key

我们现在默认推荐用千问 DashScope。

如果你的环境支持 `pip`，建议先执行：

```bash
pip install -r a13_starter/requirements.txt
```

这样可以补齐 `PDF` 解析依赖。
同时也会安装 `xlrd`，用于直接读取官方 `A13-JD采样数据.xls`。

如果你暂时不能装依赖也没关系，项目现在会优先使用已经生成好的岗位数据缓存，演示仍然能跑起来。

#### Windows PowerShell

```powershell
$env:DASHSCOPE_API_KEY="你的千问key"
$env:LLM_PROVIDER="dashscope"
$env:DASHSCOPE_MODEL="qwen3.5-flash"
$env:A13_API_PORT="8001"
```

#### Windows cmd

```cmd
set DASHSCOPE_API_KEY=你的千问key
set LLM_PROVIDER=dashscope
set DASHSCOPE_MODEL=qwen3.5-flash
set A13_API_PORT=8001
```

#### macOS / Linux / Git Bash

```bash
export DASHSCOPE_API_KEY="你的千问key"
export LLM_PROVIDER="dashscope"
export DASHSCOPE_MODEL="qwen3.5-flash"
export A13_API_PORT="8001"
```

### 3. 启动本地服务

```bash
python -m a13_starter.api_server
```

如果你的环境里 `python` 不行，就试：

```bash
python3 -m a13_starter.api_server
```

### 4. 打开浏览器

访问：

```text
http://127.0.0.1:8001/
```

如果你的机器上 `8000` 端口可用，也可以不设置 `A13_API_PORT`，默认就是 `8000`。

### 5. 页面里怎么操作

- 点击 `载入样例`，或者直接把自己的简历文本粘贴进左侧输入框
- 也可以点击 `解析本地简历文件`，直接上传 `txt / md / docx` 简历
- `解析模式` 选 `auto`
- 点击 `生成职业规划`
- 等几秒到十几秒，页面会显示学生画像、岗位匹配、职业路径、职业图谱和报告预览
- 生成后结果会自动进入“最近分析记录”
- 左侧会自动显示环境自检结果
- 页面支持检索官方原始 JD，并查看岗位模板对应的代表性样本
- 报告区可以直接下载 `Markdown / HTML / Word`，或通过打印页导出 `PDF`

## 二、推荐演示素材

推荐直接用这 3 份样例简历做展示：

- `a13_starter/samples/demo_resume_backend.txt`
- `a13_starter/samples/demo_resume_implementation.txt`
- `a13_starter/samples/demo_resume_frontend.txt`

建议演示顺序：

1. 先用 `demo_resume_backend.txt` 演示最稳
2. 再切换 `implementation` 或 `frontend` 展示不同类型学生会得到不同推荐

## 三、简历文件上传说明

现在页面已经支持直接上传本地简历文件。

目前支持：

- `txt`
- `md`
- `docx`
- `pdf`

说明：

- `pdf` 依赖当前环境里是否安装了解析库
- 如果环境里没有 PDF 解析依赖，系统会提示你优先上传 `txt / md / docx`
- 为了演示稳定，最推荐上传 `docx` 或直接粘贴文本
## 四、解析模式说明

页面里有 3 种解析模式：

- `auto`
  有 LLM key 时优先走大模型解析，没 key 时自动回退到规则解析
- `llm`
  强制走大模型解析
- `rule`
  强制走规则解析

平时开发和展示，推荐都用 `auto`。

## 五、如果不想开网页

可以直接在命令行运行：

```bash
python -m a13_starter.tools.match_resume_to_templates --parser-mode auto
```

也可以直接跑内置样例验证：

```bash
python -m a13_starter.tools.run_benchmark --parser-mode rule
```

这会输出 4 个典型学生样例的命中率、解释覆盖、报告就绪度和闭环能力评分。

运行后会生成这些结果文件：

- `a13_starter/generated/student_role_matches.json`
- `a13_starter/generated/student_role_matches.md`
- `a13_starter/generated/career_plan.json`
- `a13_starter/generated/career_plan_report.md`

## 六、生成结果会写到哪里

主要输出目录：

- `a13_starter/generated/`

你们演示时最常用的是：

- `career_plan_report.md`
- `student_role_matches.json`
- `career_plan.json`

## 七、项目里现在已经有什么

目前已经做好的能力包括：

- 官方 JD 数据导入
- 岗位库与岗位模板生成
- 学生简历解析
- 岗位匹配评分
- 职业规划生成
- Markdown 报告生成
- 本地网页演示
- 简历文件上传解析
- 千问 LLM 解析接入
- `auto / llm / rule` 三种模式切换
- 分析结果持久化存档
- 职业图谱可视化
- 官方原始 JD 检索与模板证据回看
- RAG 式证据链：分块检索、重排与片段引用
- 环境自检
- 内置样例验证中心
- HTML / Word / PDF 导出
- Docker 部署文件

## 八、常见问题

### 1. PowerShell 提示 `export` 不是命令

因为 `export` 是 bash 写法。  
在 PowerShell 里要写：

```powershell
$env:DASHSCOPE_API_KEY="你的千问key"
```

### 2. 点击生成后要等多久

正常情况：

- 3 到 10 秒：正常
- 10 到 20 秒：也正常
- 超过 30 秒：需要怀疑网络、key、模型拥堵或接口异常

### 3. 没有千问 key 能不能跑

可以。  
把页面里的 `解析模式` 设成 `rule`，或者直接用 `auto`，系统会回退到规则解析。

### 4. 上传 PDF 失败怎么办

优先换成 `docx / txt / md`。  
因为 PDF 是否能解析，取决于当前机器里有没有安装 PDF 解析依赖。

### 5. 页面打不开怎么办

先看终端里有没有报错。  
再确认你是不是已经运行了：

```bash
python -m a13_starter.api_server
```

然后确认浏览器打开的是：

```text
http://127.0.0.1:8000/
```

### 6. 启动时报端口占用

说明 `8000` 端口已经被别的程序用了。  
先把旧的 Python 服务关掉，再重新启动。

### 7. PDF 怎么导出最稳

推荐用页面里的 `导出 PDF` 按钮。  
它会打开打印页，然后你在浏览器里选择“另存为 PDF”，这样中文显示最稳定。

## 九、如果想用 OpenAI 而不是千问

也支持 OpenAI。

### PowerShell

```powershell
$env:OPENAI_API_KEY="你的OpenAI key"
$env:OPENAI_MODEL="gpt-5-mini"
python -m a13_starter.api_server
```

### Bash

```bash
export OPENAI_API_KEY="你的OpenAI key"
export OPENAI_MODEL="gpt-5-mini"
python3 -m a13_starter.api_server
```

## 十、项目结构速览

- `a13_starter/api_server.py`
  本地 API 服务入口
- `a13_starter/web/`
  网页演示界面
- `a13_starter/src/`
  核心逻辑，包括画像抽取、匹配、职业规划、LLM 解析、文件解析
- `a13_starter/tools/`
  数据导入和批处理脚本
- `a13_starter/samples/`
  样例简历
- `a13_starter/generated/`
  生成结果
- `a13_starter/DEPLOY.md`
  Docker 和部署说明
- `a13_starter/答辩讲解提纲.md`
  答辩讲解建议

## 十一、当前最建议的用法

如果你只是想快速演示：

1. 配好千问 key
2. 运行 `python -m a13_starter.api_server`
3. 打开 `http://127.0.0.1:8000/`
4. 点击 `载入样例` 或上传一份 `docx` 简历
5. `解析模式` 选 `auto`
6. 点击 `生成职业规划`

## 十二、提醒

- API key 不要提交到 Git 仓库
- 如果 key 发到群里或聊天里了，建议尽快重置
- 正式答辩前，建议提前生成一遍演示结果，避免现场网络波动影响展示
