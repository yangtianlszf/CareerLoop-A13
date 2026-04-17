# Generated 目录说明

本目录保存的是项目运行、数据处理和联调过程中产生的结果文件，不是项目主文档目录。

## 主要文件类型

- `job_profiles.jsonl`：清洗后的岗位记录
- `role_profile_templates.json`：岗位模板库
- `dataset_summary.json`：数据统计摘要
- `analysis_history.db`：历史分析与复核数据库
- `career_plan_report.md`：最近一次示例报告输出
- `student_role_matches.md`：最近一次匹配结果输出

## 如何理解这里的 Markdown 文件

本目录下的 `*.md` 文件主要是运行产物，例如：

- 示例职业规划报告
- 示例岗位匹配结果
- 岗位模板文本化导出

它们用于展示输出样式或保留最近一次结果，不应替代根目录 `README.md`、`a13_starter/README.md`、`DEPLOY.md` 等正式文档。

## 提交版建议

- 必要时可以保留 `json/jsonl` 模板与数据文件
- `generated/*.md` 是否保留取决于你们是否需要附带示例输出
- 如果提交包需要更整洁，可以只保留最有代表性的一个示例报告
