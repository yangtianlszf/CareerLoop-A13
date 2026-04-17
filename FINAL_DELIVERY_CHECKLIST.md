# 最终交付前检查清单

本清单用于赛前联调、提交包检查和答辩前自检。

## 1. 运行检查

- [ ] 依赖已安装：`pip install -r a13_starter/requirements.txt`
- [ ] 服务可启动：`python -m a13_starter.api_server`
- [ ] 首页可访问：`http://127.0.0.1:8000/`
- [ ] 健康检查正常：`/health`
- [ ] 环境自检正常：`/api/system-check`

## 2. 主流程检查

- [ ] 样例简历可正常生成职业规划
- [ ] 本地文件上传可用
- [ ] 主岗、备选岗和推荐解释展示正常
- [ ] 行动路径和岗位切换模拟正常
- [ ] 证据基线与原始样本切片可展示
- [ ] 历史记录能正常保存
- [ ] 复核提交与留痕正常

## 3. 导出检查

- [ ] Markdown 导出正常
- [ ] HTML 导出正常
- [ ] Word 导出正常
- [ ] PDF 导出正常

## 4. 数据与模板检查

- [ ] `A13_官方资料/A13-JD采样数据.xls` 存在
- [ ] `a13_starter/generated/job_profiles.jsonl` 存在
- [ ] `a13_starter/generated/role_profile_templates.json` 存在
- [ ] `a13_starter/generated/dataset_summary.json` 存在

## 5. Benchmark 检查

- [ ] 已运行 `python -m a13_starter.tools.run_benchmark --parser-mode rule`
- [ ] Top1 命中率结果已确认
- [ ] Top3 命中率结果已确认
- [ ] 至少准备一张 benchmark 结果截图用于答辩

## 6. 文档检查

- [ ] 根目录 `README.md` 已与实际项目状态一致
- [ ] `a13_starter/README.md` 运行说明正确
- [ ] `a13_starter/DEPLOY.md` 部署说明正确
- [ ] `答辩讲解提纲.md` 与 `答辩演示脚本.md` 已统一口径

## 7. 提交包检查

- [ ] 不提交 `.env.local`
- [ ] 不提交私有 API Key
- [ ] 不提交临时日志和无关缓存
- [ ] 不提交无关截图和个人开发文件
- [ ] 提交包内目录结构清晰

## 8. 赛题合规检查

- [ ] 演示材料中未出现院校名称
- [ ] 视频、PPT、报告和网页演示口径一致
- [ ] 所有“为什么推荐”的解释都能回到官方数据和岗位模板

## 9. 答辩当天建议

- [ ] 提前生成至少 2 条历史记录
- [ ] 准备 3 份最稳的样例简历
- [ ] 默认使用 `auto`
- [ ] 准备 `rule` 模式作为现场兜底
- [ ] 导出 PDF 或 Word 至少现场演示一次
