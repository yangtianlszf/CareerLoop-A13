# A13 Starter 运行说明

本目录是项目的主运行模块，包含本地服务、前端页面、核心逻辑、样例数据、工具脚本和生成结果。

除非特别说明，下面所有命令都默认在仓库根目录 `/home/qwp/workspace/CareerLoop-A13` 执行，不要先 `cd` 到 `a13_starter/` 再运行模块命令。

## 1. 这个子项目负责什么

`a13_starter/` 当前已经包含以下能力：

- 简历文本输入与本地文件上传
- 学生画像解析
- 岗位模板匹配与排序
- 主岗、备选岗和排序解释
- 行动路径、简历改写、面试题板
- 岗位切换模拟与能力差异对照
- 模板证据、原始样本切片和 JD 检索
- 历史记录、复核留痕、运营视图
- Markdown / HTML / Word / PDF 导出

## 2. 环境准备

### 安装依赖

```bash
pip install -r a13_starter/requirements.txt
```

当前依赖里主要包含：

- `xlrd`：读取官方 `A13-JD采样数据.xls`
- `pypdf`：解析 PDF 简历与验证 PDF 导出

### 准备环境变量

推荐在仓库根目录创建 `.env.local`：

```bash
DASHSCOPE_API_KEY=你的key
LLM_PROVIDER=dashscope
DASHSCOPE_MODEL=qwen-plus
A13_API_HOST=127.0.0.1
A13_API_PORT=8000
```

项目会自动读取仓库根目录下的 `.env` 与 `.env.local`。

如果没有模型 Key，也可以直接运行，系统会自动回退到规则解析。

## 3. 启动服务

```bash
python -m a13_starter.api_server
```

如果你的环境里使用的是 `python3`：

```bash
python3 -m a13_starter.api_server
```

启动后默认访问：

```text
http://127.0.0.1:8000/
```

## 4. 页面使用流程

推荐按下面顺序使用：

1. 在左侧输入简历文本，或点击 `选择本地文件`
2. 解析模式优先选择 `auto`
3. 点击 `生成职业规划`
4. 查看 `诊断总览`
5. 查看 `行动路径`
6. 查看 `证据基线`
7. 查看 `图谱与报告`
8. 需要时导出 `Markdown / HTML / Word / PDF`

## 5. 解析模式说明

- `auto`
  有模型配置时优先使用大模型解析，失败时自动回退到规则解析

- `llm`
  强制使用大模型解析

- `rule`
  完全使用本地规则解析，适合断网演示或基准验证

## 6. 内置样例

当前已内置 `7` 份样例，可直接用于答辩演示：

- `a13_starter/samples/demo_resume_backend.txt`
- `a13_starter/samples/demo_resume_implementation.txt`
- `a13_starter/samples/demo_resume_frontend.txt`
- `a13_starter/samples/demo_resume_data_analyst.txt`
- `a13_starter/samples/demo_resume_operations.txt`
- `a13_starter/samples/demo_resume_testdev.txt`
- `a13_starter/samples/student_resume.txt`

建议演示顺序：

1. 后端样例
2. 实施样例
3. 前端样例
4. 数据分析或测试开发样例

## 7. 常用命令

### 启动本地服务

```bash
python -m a13_starter.api_server
```

### 运行基准验证

```bash
python -m a13_starter.tools.run_benchmark --parser-mode rule
```

### 测试自动模式

```bash
python -m a13_starter.tools.run_benchmark --parser-mode auto
```

### 命令行匹配样例简历

```bash
python -m a13_starter.tools.match_resume_to_templates --parser-mode auto
```

## 8. 常见接口

- `GET /health`：服务健康检查
- `GET /api/system-check`：环境自检
- `GET /api/demo-resumes`：样例列表
- `POST /api/upload-resume-file`：上传简历文件
- `POST /api/career-plan`：生成职业规划
- `POST /api/export-report`：导出报告
- `GET /api/jd-search`：检索原始岗位样本

## 9. 生成结果在哪里

主要运行产物位于 `a13_starter/generated/`：

- `job_profiles.jsonl`：清洗后的岗位记录
- `role_profile_templates.json`：岗位模板库
- `dataset_summary.json`：数据集统计摘要
- `analysis_history.db`：历史分析与复核数据库
- `career_plan_report.md`：最近一次报告产物

其中 `generated/*.md` 属于运行输出，不是项目主文档。

## 10. 常见问题

### 页面打不开怎么办

- 先确认服务是否已经启动
- 再检查 `http://127.0.0.1:8000/health`
- 再检查 `http://127.0.0.1:8000/api/system-check`

### 没有模型 Key 能不能跑

可以。选择 `rule`，或者直接用 `auto` 让系统自动回退。

### PDF 简历解析失败怎么办

优先改用 `docx`、`txt` 或 `md`。`pdf` 依赖解析库与文件本身是否包含可抽取文本。

### 端口被占用怎么办

在 `.env.local` 中修改：

```bash
A13_API_PORT=8001
```

### 现场担心网络波动怎么办

- 展示时优先准备好样例
- 默认用 `auto`
- 如果网络不稳，立即切到 `rule`

## 11. 关联文档

- [../README.md](../README.md)
- [DEPLOY.md](DEPLOY.md)
- [答辩讲解提纲.md](答辩讲解提纲.md)
- [答辩演示脚本.md](答辩演示脚本.md)
- [提交版说明.md](提交版说明.md)
