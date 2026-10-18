# interview-review · 中文非技术岗面试复盘

给运营、电商、GTM、海外销售等非技术岗位求职者使用的 Codex skill。根据简历、JD和面试证据整理问题、评价回答、生成可练习的改进稿。材料不足时缩小评价范围；不预测录用概率。

**首版范围：macOS + Codex。** AI负责分析，Python脚本只负责报告生成和部分结构检查。不是独立运行的AI产品，也不用于替代招聘决策。

## 安装

在Codex中请求安装：https://github.com/jinaaron86-maker/interview-review 。也可将仓库下载为名为`interview-review`的文件夹，放入个人`~/.agents/skills/`目录；已有同名目录时先检查，避免覆盖。安装后若未出现，重启Codex。参见[OpenAI官方技能说明](https://learn.chatgpt.com/docs/build-skills)。

## 使用

在Codex中说：

> 使用 $interview-review 复盘这场非技术岗面试。请先检查我提供的材料和本次实际职责，明确能分析的范围，再生成报告。

提供当时简历、JD、面试录音或文字稿；可缺部分材料，但缺失会限制评价。没有任何面试记录时不能复盘实际表现。文字稿无时间戳时使用段落编号，回答证据不足时不评分。

## 示例与依赖

`examples/`中的材料和人物全部虚构。先在Codex中分析输入，再写review_plan.json；脚本不会自动从简历或录音生成分析。体验排版可以在仓库目录运行：

```sh
python3 scripts/report.py --plan examples/review_plan.json --out /tmp/interview-review-demo
```

输出目录必须为空；已存在时换一个新目录。Python要求3.9及以上，默认仅用标准库，不需要额外Python包。正式生成两份PDF，需要已安装的XeLaTeX、ctex、Fandol字体，以及tcolorbox、enumitem、fancyhdr排版包；本项目不自动安装软件或下载模型。缺少依赖或任一PDF生成失败会明确报错，并标注正式交付未完成，内部草稿保留。

本地转写使用用户已有工具，缺少工具时可直接提供文字稿；首版不提供内置转写器或云端接口。上传至用户已有云端服务前，必须明确服务商和上传范围并取得同意。本地转写不表示后续Codex分析完全离线。

## 输出和检查

正式交付只有两份PDF：

- `interview_review.pdf`：逐题评价、具体改进和练习逐字稿。
- `question_transcript.pdf`：面试官问题、追问与候选人现场回答原话，按顺序配对；不混入评分或优化答案，保留口头禅、重复和听辨不清标记。

时间戳缺失时用段落编号，缺失回答明确标注。内部生成材料保存在`_support/`，不作为额外交付。两份PDF都需要逐页视觉检查。

固定保留5条扣分点、5条亮点、至少4条改进方向和4条下一场优先级，后续问题8—12道、资料5—8条；不足时明确留作待验证项。现场回答整理版与练习稿分开，原始转写另存。

机械检查通过不代表事实、评分、来源或PDF视觉效果已通过人工审核。分享报告前自行核对并脱敏。勿将真实简历、JD、音视频或转写提交到仓库。

## 测试

```sh
python3 -m unittest discover -s tests
```

参见`VERIFICATION.md`了解实际验证范围与限制。MIT许可及来源说明见`LICENSE`、`NOTICE.md`。
