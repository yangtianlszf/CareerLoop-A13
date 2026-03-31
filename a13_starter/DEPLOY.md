# A13 Demo 部署说明

## 1. 本地直接运行

```bash
python -m a13_starter.api_server
```

打开：

```text
http://127.0.0.1:8000/
```

## 2. Docker 部署

在项目根目录 `server2026` 下执行：

```bash
docker build -t a13-career-demo -f a13_starter/Dockerfile .
docker run --rm -p 8000:8000 \
  -e DASHSCOPE_API_KEY=你的千问key \
  -e LLM_PROVIDER=dashscope \
  -e DASHSCOPE_MODEL=qwen3.5-flash \
  a13-career-demo
```

## 3. 推荐环境变量

### 千问 DashScope

```bash
export DASHSCOPE_API_KEY="你的千问key"
export LLM_PROVIDER="dashscope"
export DASHSCOPE_MODEL="qwen3.5-flash"
```

### OpenAI

```bash
export OPENAI_API_KEY="你的OpenAI key"
export OPENAI_MODEL="gpt-5-mini"
```

## 4. 生产演示建议

- 演示时优先使用 `auto`
- 现场网络不稳时切到 `rule`
- 提前准备 2 到 3 份样例简历
- 正式答辩前先生成几条历史记录，方便现场快速切换展示
