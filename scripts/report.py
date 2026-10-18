"""Render evidence-bounded interview plans; no network or package installation."""
import argparse
import json
import shutil
import subprocess
from pathlib import Path
from pdf_layout import document

UNSCORED = '未评分：证据不足'
FIELDS = [('question', '具体问题'), ('observed_answer', '现场回答（整理版）'),
          ('strength', '具体优点'), ('mistake', '具体失误'),
          ('strategy', '修改策略'), ('optimized_script', '练习逐字稿')]
COUNTS = {'deductions': (5, 5), 'highlights': (5, 5), 'improvements': (4, None),
          'priorities': (4, None), 'future_questions': (8, 12), 'learning_resources': (5, 8)}


def question_view(question):
    score = question.get('score')
    if score is not None and (type(score) is not int or not 1 <= score <= 5):
        raise ValueError('评分只能为1—5整数或null')
    return {**question, 'score': UNSCORED if score is None else f'{score}/5'}


def validate(plan):
    errors = []
    allowed = {'title', 'mode', 'inputs', 'limitations', 'questions', *COUNTS,
               'focus_analysis', 'overall_review', 'transcript_markdown', 'source_registry', 'qa_transcript', 'metadata', 'conclusion'}
    if set(plan) - allowed:
        errors.append('存在数据契约之外的字段，请移除后重新生成')
    if not plan.get('transcript_markdown', '').strip():
        errors.append('缺少面试记录，不能复盘实际表现')
    if not plan.get('questions'):
        errors.append('缺少实质性问题')
    if not plan.get('limitations'):
        errors.append('必须明确分析范围和材料限制')
    if plan.get('mode') not in ('full', 'partial'):
        errors.append('mode必须是full或partial')
    supplied = plan.get('inputs', {})
    if plan.get('mode') == 'full' and not all(supplied.get(k) for k in ('resume', 'jd', 'interview')):
        errors.append('完整复盘需要简历、JD和面试记录')
    if not supplied.get('interview'):
        errors.append('必须提供面试证据')
    if 'blind_probability' in plan:
        errors.append('不接受通过概率字段')
    if not plan.get('qa_transcript'):
        errors.append('缺少按问答配对的原话逐字稿')
    for pair in plan.get('qa_transcript', []):
        if not pair.get('source_ref'):
            errors.append('逐字稿缺少来源定位')
        for key in ('question_verbatim', 'answer_verbatim'):
            text = pair.get(key)
            if not text or text not in plan.get('transcript_markdown', ''):
                errors.append('逐字稿原话必须可在原始转写中找到，缺失内容须保留原记录标记')
    for key, (minimum, maximum) in COUNTS.items():
        items = plan.get(key, [])
        if not isinstance(items, list) or len(items) < minimum or (maximum and len(items) > maximum):
            errors.append(f'{key}数量不符合约定')
        elif any(not isinstance(item, str) or not item.strip() for item in items):
            errors.append(f'{key}必须是非空文字列表')
    seen = set()
    for q in plan.get('questions', []):
        qid = q.get('id')
        if not qid or qid in seen:
            errors.append('问题ID缺失或重复')
        seen.add(qid)
        try:
            question_view(q)
        except ValueError as exc:
            errors.append(str(exc))
        if q.get('score') is not None and (not q.get('answer_verified') or not q.get('observed_answer', '').strip()):
            errors.append(f'{qid}无可靠回答证据，不得评分')
        for key, _ in FIELDS:
            if not q.get(key):
                errors.append(f'{qid}缺少{key}；证据不足时应明确标记')
        if not q.get('source_ref'):
            errors.append(f'{qid}缺少时间窗口或段落编号')
    return errors


def render_markdown(plan):
    lines = ['# ' + plan.get('title', '面试复盘'), '', '## 基础信息', '',
             '模式：' + plan['mode'], '', '分析范围与限制：' + plan['limitations'], '']
    for key, heading in [('deductions', '5条扣分点'), ('highlights', '5条亮点'),
                         ('improvements', '改进方向'), ('priorities', '下一场优先级')]:
        lines += ['## ' + heading, ''] + [f'{i}. {v}' for i, v in enumerate(plan[key], 1)] + ['']
    lines += ['## 全部问答', '']
    for original in plan['questions']:
        q = question_view(original)
        lines += ['### ' + q['id'], '', '来源：' + q['source_ref'], '', '评分：' + q['score'], '']
        for key, label in FIELDS:
            lines += ['**' + label + '**', '', q[key], '']
    for key, heading in [('focus_analysis', '动态重点追问'), ('overall_review', '整体复盘')]:
        lines += ['## ' + heading, '', plan.get(key, '本场未充分验证，需补充材料。'), '']
    for key, heading in [('future_questions', '后续面试问题'), ('learning_resources', '巩固资料')]:
        lines += ['## ' + heading, ''] + [f'{i}. {v}' for i, v in enumerate(plan[key], 1)] + ['']
    return '\n'.join(lines)


def render_question_transcript(plan):
    lines = ['# 面试问题与现场回答逐字稿', '', '仅包含现场原话，不包含评分或优化答案。', '',
             '材料范围与限制：' + plan['limitations'], '']
    for index, pair in enumerate(plan['qa_transcript'], 1):
        lines += [f'## 问答{index}', '', '来源：' + pair['source_ref'], '',
                  '**面试官问题原话**', '', pair['question_verbatim'], '',
                  '**候选人回答原话**', '', pair['answer_verbatim'], '']
    return '\n'.join(lines)


def export_pdf(plan, out, stem='interview_review'):
    compiler = shutil.which('xelatex')
    if not compiler:
        return '未生成：缺少xelatex；内部草稿已保留，正式交付尚未完成'
    source = document(plan, stem)
    tex = out / (stem + '.tex')
    tex.write_text(source, encoding='utf-8')
    result = subprocess.run([compiler, '-no-shell-escape', '-interaction=nonstopmode', '-halt-on-error', tex.name], cwd=out, capture_output=True, text=True)
    log = (result.stdout + result.stderr).replace(str(Path.home()), '[HOME]').replace(str(out), '[OUTPUT]')
    (out / (stem + '_build_log.txt')).write_text(log, encoding='utf-8')
    for suffix in ('.aux', '.log', '.out'):
        tex.with_suffix(suffix).unlink(missing_ok=True)
    if result.returncode or not tex.with_suffix('.pdf').exists():
        return '生成失败：请检查对应构建日志；正式交付尚未完成'
    return '已生成，尚待逐页视觉检查'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    plan = json.loads(Path(args.plan).read_text(encoding='utf-8'))
    errors = validate(plan)
    if errors:
        print(json.dumps({'status': 'fail', 'errors': errors}, ensure_ascii=False))
        return 1
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    # A fresh output directory avoids stale PDFs being mistaken for current output.
    if any(out.iterdir()):
        raise SystemExit('输出目录必须为空，请为本次复盘选择新目录')
    delivery = out
    out = delivery / '_support'
    out.mkdir()
    markdown = render_markdown(plan)
    (out / 'interview_review.md').write_text(markdown, encoding='utf-8')
    (out / 'transcript_timestamped.md').write_text(plan['transcript_markdown'], encoding='utf-8')
    for filename, data in [('review_data.json', plan), ('source_registry.json', plan.get('source_registry', []))]:
        (out / filename).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    transcript = render_question_transcript(plan)
    (out / 'question_transcript.md').write_text(transcript, encoding='utf-8')
    pdf_status = export_pdf(plan, out)
    transcript_status = export_pdf(plan, out, 'question_transcript')
    generated = all(status.startswith('已生成') for status in (pdf_status, transcript_status))
    if generated:
        for stem in ('interview_review', 'question_transcript'):
            shutil.move(str(out / (stem + '.pdf')), str(delivery / (stem + '.pdf')))
    quality = {'status': 'mechanical_checks_passed', 'pdf': pdf_status, 'transcript_pdf': transcript_status,
               'delivery_status': 'generated_pending_review' if generated else 'incomplete', 'visual_qa': 'not_reviewed',
               'content_review': 'required', 'note': '机械校验不验证事实、链接有效性或评分合理性'}
    (out / 'quality_report.json').write_text(json.dumps(quality, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(quality, ensure_ascii=False))
    return 0 if generated else 1


if __name__ == '__main__':
    raise SystemExit(main())
