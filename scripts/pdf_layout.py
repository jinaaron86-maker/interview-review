"""Native PDF layouts independently authored from the user's visual brief."""
import re


def escape(value):
    replacements = {'\\': r'\textbackslash{}', '{': r'\{', '}': r'\}', '%': r'\%',
                    '&': r'\&', '#': r'\#', '_': r'\_', '$': r'\$', '~': r'\textasciitilde{}', '^': r'\textasciicircum{}'}
    return ''.join(replacements.get(c, c) for c in str(value))


def emphasis(value):
    chunks = re.split(r'(\*\*.+?\*\*)', str(value))
    return ''.join(r'\textbf{' + escape(c[2:-2]) + '}' if c.startswith('**') and c.endswith('**') else escape(c) for c in chunks)


def panel(title, content, color):
    return (r'\begin{tcolorbox}[enhanced,breakable,sharp corners,boxrule=.6pt,'
            + f'colback={color}!5!white,colframe={color},colbacktitle={color},'
            + r'coltitle=white,fonttitle=\bfseries,title={' + escape(title)
            + r'},left=2mm,right=2mm,top=1.5mm,bottom=1.5mm]' + content + r'\end{tcolorbox}')


def bullets(values):
    return r'\begin{itemize}' + ''.join(r'\item ' + emphasis(v) for v in values) + r'\end{itemize}'


def document(plan, kind):
    meta = plan.get('metadata', {})
    title = plan.get('title', '面试复盘')
    transcript = kind == 'question_transcript'
    short = '问题逐字稿' if transcript else '面试复盘'
    preamble = r'''\documentclass[UTF8,fontset=fandol,10pt]{ctexart}
\usepackage[a4paper,margin=18mm,top=20mm,bottom=19mm]{geometry}
\usepackage[most]{tcolorbox}
\usepackage{enumitem,fancyhdr}
\definecolor{Navy}{HTML}{245781}
\definecolor{Risk}{HTML}{AC161C}
\definecolor{Good}{HTML}{167333}
\definecolor{Gold}{HTML}{9B8B39}
\definecolor{Slate}{HTML}{526273}
\pagestyle{fancy}\fancyhf{}
\setlength{\headheight}{15pt}
\fancyfoot[C]{\small\thepage}
\setlength{\parindent}{0pt}\setlength{\parskip}{4pt}
\setlist[itemize]{leftmargin=1.2em,itemsep=2pt,topsep=1pt}
\ctexset{section={format=\large\bfseries,beforeskip=12pt,afterskip=7pt},subsection={format=\normalsize\bfseries}}
\raggedbottom
'''
    preamble += r'\fancyhead[L]{\small ' + escape(title) + r'}\fancyhead[R]{\small ' + short + '}\n'
    body = r'\begin{document}\begin{center}'
    body += r'{\large ' + short + r'}\par\vspace{4mm}{\LARGE\bfseries ' + escape(title) + r'}\par'
    if transcript:
        body += r'\vspace{2mm}{\large\bfseries 问题与现场回答原话}\par'
    body += r'\vspace{3mm}{\small ' + escape(meta.get('info', '面试时长、轮次与日期：未提供')) + r'}\end{center}'
    if transcript:
        body += r'\textbf{版本与证据边界：}' + escape(meta.get('transcript_note', '校对状态未提供；不能据此确认已完成原录音人工听校。')) + r'\par '
        body += escape(plan['limitations']) + r'\par\textbf{阅读说明：}保留口头语、自我更正、追问及不确定标记；无时间戳时使用段落编号。\par'
        for index, pair in enumerate(plan['qa_transcript'], 1):
            body += r'\section*{' + escape(pair.get('topic', f'问答 {index}')) + '}'
            body += r'\textbf{[' + escape(pair['source_ref']) + r'] 面试官}\par ' + escape(pair['question_verbatim']) + r'\par '
            body += r'\textbf{候选人}\par ' + escape(pair['answer_verbatim']) + r'\par '
    else:
        body += panel('本场结论与证据边界', emphasis(plan.get('conclusion', plan['overall_review'])) + r'\par\small ' + escape(plan['limitations']), 'Navy')
        cards = [('Top 5 扣分点', 'deductions', 'Risk'), ('Top 5 可复用亮点', 'highlights', 'Good'),
                 ('需要改进的方向', 'improvements', 'Gold'), ('下一场优先级', 'priorities', 'Slate')]
        for index, (label, key, color) in enumerate(cards):
            body += r'\begin{minipage}[t]{.485\linewidth}\small ' + panel(label, bullets(plan[key]), color) + r'\end{minipage}'
            body += r'\hfill ' if index % 2 == 0 else r'\par\vspace{2mm}'
        body += r'\clearpage\section*{面试官问题与现场回答复盘}'
        fields = [('question', '具体问题'), ('observed_answer', '现场回答（整理版）'), ('strength', '具体优点'),
                  ('mistake', '具体失误'), ('strategy', '修改策略'), ('optimized_script', '练习逐字稿')]
        for q in plan['questions']:
            score = '未评分：证据不足' if q.get('score') is None else f"{q['score']}/5"
            content = r'\textbf{来源：}' + escape(q['source_ref']) + r'\quad\textbf{评分：}' + escape(score) + r'\par '
            content += ''.join(r'\textbf{' + label + r'：}' + emphasis(q[key]) + r'\par ' for key, label in fields)
            body += panel(q['id'] + ' · ' + q['question'], content, 'Navy')
        for key, label in [('focus_analysis', '动态重点追问'), ('overall_review', '整体复盘')]:
            body += r'\section*{' + label + '}' + emphasis(plan.get(key, '本场未充分验证。')) + r'\par '
        for key, label in [('future_questions', '后续面试问题'), ('learning_resources', '巩固资料')]:
            body += r'\section*{' + label + '}' + bullets(plan[key])
    return preamble + body + r'\end{document}'
