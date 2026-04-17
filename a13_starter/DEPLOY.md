# A13 Starter 部署说明

本文件只关注部署和联调，不重复介绍产品功能。

除非特别说明，下面命令都在仓库根目录执行。

## 1. 本地部署

### 安装依赖

```bash
pip install -r a13_starter/requirements.txt
```

### 配置环境

推荐在仓库根目录写入 `.env.local`：

```bash
DASHSCOPE_API_KEY=你的key
LLM_PROVIDER=dashscope
DASHSCOPE_MODEL=qwen-plus
A13_API_HOST=127.0.0.1
A13_API_PORT=8000
```

### 启动服务

```bash
python -m a13_starter.api_server
```

### 检查服务

- 首页：`http://127.0.0.1:8000/`
- 健康检查：`http://127.0.0.1:8000/health`
- 环境自检：`http://127.0.0.1:8000/api/system-check`

## 2. Docker 部署

```bash
docker build -t a13-career-demo -f a13_starter/Dockerfile .
docker run --rm -p 8000:8000 \
  -e DASHSCOPE_API_KEY=你的key \
  -e LLM_PROVIDER=dashscope \
  -e DASHSCOPE_MODEL=qwen-plus \
  a13-career-demo
```

说明：

- Docker 运行时不会自动读取你本地的 `.env.local`
- 需要用 `-e` 明确传入环境变量

## 3. 推荐部署口径

### 演示环境

- 优先使用 `auto`
- 提前跑一遍样例，保证历史记录里已有数据
- 准备 `rule` 模式作为断网兜底

### 联调环境

- 启动后先检查 `/api/system-check`
- 再检查样例生成、文件上传、导出 PDF
- 再检查历史记录与复核提交

## 4. 常用联调命令

### 运行规则模式基准验证

```bash
python -m a13_starter.tools.run_benchmark --parser-mode rule
```

### 运行自动模式基准验证

```bash
python -m a13_starter.tools.run_benchmark --parser-mode auto
```

### 输出 benchmark 结果到文件

```bash
python -m a13_starter.tools.run_benchmark --parser-mode rule --output a13_starter/generated/benchmark_summary.json
```

## 5. 现场答辩建议

- 答辩前先确认 `health` 和 `system-check`
- 优先使用 `demo_resume_backend.txt` 做首个演示
- 第二个样例切到实施或前端，体现系统不是固定答案
- PDF 导出、历史记录、复核留痕建议至少现场演示一个

## 6. 风险与兜底

- 模型服务依赖外网和第三方接口
- 如果接口超时或 DNS 异常，`auto` 模式可能回退到规则解析
- 因此建议正式答辩前准备：
  - 1 套 `auto` 模式演示口径
  - 1 套 `rule` 模式兜底口径
