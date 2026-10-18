# 报告数据格式

参照 examples/review_plan.json。它是明确标注的虚构示例，不是实际面试结论。

顶层字段：title；mode（full或partial）；inputs（resume、jd、interview三个布尔值）；limitations（范围与限制）；questions；deductions、highlights、improvements、priorities、future_questions、learning_resources（均为文字列表）；focus_analysis；overall_review；transcript_markdown；source_registry。

问题字段：id；source_ref（时间窗口或段落编号）；question；observed_answer；score（1—5整数或null）；answer_verified（是否有可靠回答证据）；strength；mistake；strategy；optimized_script。缺失内容须明确标记，不使用空字符串代替说明。

source_registry记录逻辑ID、材料种类、可追溯位置和核验范围，不记录个人绝对路径。公开资料在learning_resources中写标题、用途、来源链接及核验状态；无法确认的资料槽位写“待补充资料：待验证问题或练习方向”，不能伪造链接。

完整模式也可能有未评分题；完整代表三类材料齐全，不代表所有内容都已证实。机械检查只检查部分结构约束，分析者仍需核对材料真实性、缺JD的评价限制、来源支持程度、题目覆盖及优化稿是否虚构。

整体复盘应包含语言描述、经历阐述、业务思考三个维度，每个维度写证据、改进动作和未验证项。重点追问引用已有题号，不补造现场问题。

transcript_timestamped.md为兼容交付文件名；没有时间戳时，文件开头必须说明并使用段落编号。保存原始转写，不把优化稿混入其中。


## 正式交付与问答原话

正式交付固定为面试复盘PDF和问题逐字稿PDF；任何一份未生成都不算交付完成。内部资料位于_support。

新增必填qa_transcript列表，每项包含source_ref、question_verbatim和answer_verbatim。按现场顺序记录所有可辨认的问题、追问及回答；保留原语言、口头禅、重复和不确定标记，不复用observed_answer整理版。多段原话先按原文段落组织，保持可在transcript_markdown中逐段核对；回答缺失时使用原始转写中的缺失标记。原转写没有标记时先登记明确的缺失说明，不补造回答或时间。

可选metadata.info、metadata.transcript_note、conclusion及qa_transcript[].topic用于版式展示，见pdf-design.md；只填写已知信息。复盘文字可用双星号标记重点，原话不做这种编辑。
