"""Generate the signal review from the workbook, using only the Python standard library."""
from pathlib import Path
import html
import re
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'docs' / '情绪各模态信号整理.xlsx'
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def read_sheet(archive, name, strings):
    rows = {}
    for row in ET.fromstring(archive.read(name)).findall('.//m:sheetData/m:row', NS):
        cells = {}
        for cell in row:
            value, inline = cell.find('m:v', NS), cell.find('m:is', NS)
            if value is not None:
                text = strings[int(value.text)] if cell.get('t') == 's' else value.text
            elif inline is not None:
                text = ''.join(inline.itertext())
            else:
                continue
            cells[re.sub(r'\d', '', cell.get('r'))] = text
        rows[int(row.get('r'))] = cells
    return rows


def esc(value):
    return html.escape(str(value), quote=True)


def main():
    with zipfile.ZipFile(SOURCE) as archive:
        strings = [''.join(node.itertext()) for node in ET.fromstring(archive.read('xl/sharedStrings.xml')).findall('m:si', NS)] if 'xl/sharedStrings.xml' in archive.namelist() else []
        matrix = read_sheet(archive, 'xl/worksheets/sheet1.xml', strings)
        references = read_sheet(archive, 'xl/worksheets/sheet2.xml', strings)
    modalities = [matrix[5][col] for col in 'BCDEFG']
    records = [matrix[row] for row in range(6, 45)]
    refs = [references[row] for row in range(3, 58)]
    assert len(records) == 39 and len(refs) == 55
    counts = [sum(row.get(col, '').startswith('✓') for row in records) for col in 'BCDEFG']
    caveats = [sum(bool(row.get(col)) and not row[col].startswith('✓') for row in records) for col in 'BCDEFG']
    matrix_rows = []
    for number, row in enumerate(records, 6):
        emotion = row['A']
        cells = [f'<th scope="row">{esc(emotion)}<small>原表第 {number} 行</small></th>']
        supported = []
        for index, col in enumerate('BCDEFG'):
            value = row.get(col, '')
            if not value:
                cells.append('<td class="missing"><span>未收录</span></td>')
                continue
            positive = value.startswith('✓')
            supported.append(str(index))
            linked = [ref for ref in refs if f'{emotion}-{modalities[index]}' in ref.get('D', '').split('；')]
            links = ' '.join(f'<a href="#ref-{esc(ref["A"])}" aria-label="参考条目 {esc(ref["A"])}">[{esc(ref["A"])}]</a>' for ref in linked)
            body = value[1:].strip() if positive else value
            cells.append(f'<td><details><summary class="{"yes" if positive else "qualified"}">{"有证据" if positive else "结论受限"}</summary><p>{esc(body).replace(chr(10), "<br>")}</p><div class="citations">{links}</div></details></td>')
        matrix_rows.append(f'<tr data-modalities="{",".join(supported)}" data-emotion="{esc(emotion)}">'+''.join(cells)+'</tr>')
    ref_html = []
    for ref in refs:
        url = ref.get('E', '')
        assert not url or url.startswith(('https://doi.org/', 'https://'))
        link = f'<a href="{esc(url)}">DOI / 原文入口</a>' if url else '<span>原表未提供公开链接</span>'
        ref_html.append(f'<li id="ref-{esc(ref["A"])}"><p>{esc(html.unescape(ref["B"]))}</p><div class="ref-meta"><span>{esc(ref["C"])}</span>{link}</div><details><summary>对应情绪与模态</summary><p>{esc(ref.get("D", ""))}</p></details></li>')
    coverage = ''.join(f'<tr><th scope="row">{esc(modality)}</th><td>{count} / 39</td><td>{caveat}</td></tr>' for modality, count, caveat in zip(modalities, counts, caveats))
    options = ''.join(f'<option value="{i}">{esc(name)}</option>' for i, name in enumerate(modalities))
    notes = ''.join(f'<li>{esc(matrix[row]["B"])}</li>' for row in range(46, 50))
    page = '''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>情绪各模态信号综述 · 表达、识别与生理测量证据</title>
<meta name="description" content="依据情绪各模态信号整理工作簿，梳理39类情绪及相关状态在面部、语音、心率、心率变异性、皮肤电和呼吸中的证据。">
<link rel="stylesheet" href="../assets/site.css"><link rel="stylesheet" href="../assets/signals.css"><script src="../assets/signals.js" defer></script></head>
<body><a class="skip" href="#overview">跳到综述内容</a>
<header class="top"><div class="wrap bar"><a class="brand" href="../index.html">ZJU-ECLab <span>研究资料</span></a><a href="../index.html">返回主页</a></div></header>
<section class="hero"><div class="wrap"><p class="eyebrow">EMOTION &amp; MULTIMODAL SIGNALS</p><h1>情绪各模态信号综述</h1><p class="intro">表达、识别与生理测量证据的分类梳理。</p><div class="hero-links"><a class="button" href="#matrix">查看证据矩阵</a><a class="text-link" href="情绪各模态信号整理.xlsx" download>下载原始 Excel</a></div><dl class="metrics"><div><dt>情绪及相关状态</dt><dd>39</dd></div><div><dt>模态指标</dt><dd>6</dd></div><div><dt>参考条目（含未发表）</dt><dd>55</dd></div></dl></div></section>
<nav class="review-nav" aria-label="本页目录"><div class="wrap"><a href="#overview">核心解读</a><a href="#modalities">模态梳理</a><a href="#matrix">证据矩阵</a><a href="#boundaries">适用边界</a><a href="#references">参考文献</a></div></nav>
<main class="wrap review">
<section id="overview"><h2>如何理解这份证据</h2><p class="lead">本页依据工作簿“证据矩阵”和“参考文献”两张表整理，呈现原表收录的文献线索及限定条件，不把证据有无转换为识别准确率或证据强度排名。</p>
<div class="reading-grid"><article><h3>行为表达与生理测量分开看</h3><p>面部和语音条目包括表达、人类判断及自动识别研究。心率、心率变异性、皮肤电和呼吸分列，避免将不同生理指标混为一类。</p></article><article><h3>同一标记，可能对应不同证据</h3><p>“有证据”沿用原表的 ✓，可能指表达、识别或测量。具体任务、样本和输入组合需要展开单元格查看，不能由此认定单指标能够可靠识别情绪。</p></article><article><h3>空白保留为“未收录”</h3><p>羞耻、内疚、失望、懊悔、欲求在原矩阵中未列出六类指标证据。这反映原表的收录范围，不表示这些情绪没有相关研究。</p></article></div>
<div class="coverage"><div><h3>原表覆盖概览</h3><p>统计对象为情绪与模态的单元格，不是论文数量、效应大小或可识别性。“结论受限”对应原表非空但未标 ✓ 的单元格。</p></div><div class="table-scroll"><table><caption class="sr-only">六类模态的原表收录情况</caption><thead><tr><th scope="col">模态指标</th><th scope="col">标 ✓ 的情绪数</th><th scope="col">结论受限的情绪数</th></tr></thead><tbody>__COVERAGE__</tbody></table></div></div></section>
<section id="modalities"><h2>六类模态，分别回答什么问题</h2><div class="modality-grid">
<article><h3>面部表情</h3><p>原表涉及基本情绪、积极情绪和认知相关状态。笑容、扬眉、皱眉等属于表达线索；挫败、困惑、投入的自动识别条目采用面部 AU、头姿与身体运动联合输入，不能归为面部单模态性能。</p><a href="#ref-36">联合输入研究线索 [36]</a></article>
<article><h3>语音</h3><p>覆盖语音韵律与非言语发声，二者应区分。自豪、兴趣的条目涉及音高、强度、语速等声学表达；声学差异并不直接等于可靠识别结论。</p><a href="#ref-35">积极情绪发声综述 [35]</a></article>
<article><h3>心率（HR）</h3><p>原表收录基本情绪、焦虑、无聊、同情等条目。烦躁条目虽然测量了心率，但主要组间差异是血压与去甲肾上腺素，故单独标为“结论受限”。</p><a href="#ref-17">烦躁条目的限定 [17]</a></article>
<article><h3>心率变异性（HRV / RSA）</h3><p>与心率分开统计。原表包含情绪诱发、同情、儿童害羞及放松相关研究；害羞证据来自儿童演讲任务，不能直接外推到所有人群和情境。</p><a href="#ref-12">儿童害羞研究 [12]</a></article>
<article><h3>皮肤电（EDA / SCL / SCR）</h3><p>原表在多种情绪下列入皮肤电证据。同情条目标注“已测量，未见条件差异”，不能作为该任务下已有区分效果的证据。</p><a href="#ref-15">同情与生理测量 [15]</a></article>
<article><h3>呼吸</h3><p>条目涉及情绪相关呼吸模式和主动慢呼吸。原表将慢呼吸列为放松相关证据；它与自发情绪表达或情绪自动识别属于不同研究范式。</p><a href="#ref-46">慢呼吸系统综述 [46]</a></article>
</div></section>
<section id="matrix"><h2>情绪 × 模态证据矩阵</h2><p>展开单元格查看原表记录及参考条目。筛选会保留该模态下所有非空条目，包括“结论受限”；单元格“未收录”对应原表空白。</p>
<div class="filter-panel" hidden><label>搜索情绪<input id="emotion-search" type="search" placeholder="例如：开心、焦虑、平静"></label><label>按模态筛选<select id="modality-filter" aria-label="按模态筛选"><option value="all">全部模态</option>__OPTIONS__</select></label><button id="reset" type="button">重置筛选</button><button id="expand" type="button" aria-pressed="false">展开当前证据</button></div><p id="result-count" role="status" aria-live="polite">显示全部 39 类情绪及相关状态</p>
<div class="table-scroll matrix-scroll" tabindex="0" role="region" aria-label="可横向滚动的情绪模态证据矩阵"><table class="matrix-table"><caption>39 类情绪及相关状态的原表证据记录</caption><thead><tr><th scope="col">情绪 / 状态</th>__HEADERS__</tr></thead><tbody>__ROWS__</tbody></table></div><p id="empty-state" hidden>没有匹配的情绪，请调整筛选条件。</p>
</section>
<section id="boundaries"><h2>研究使用时的边界</h2><div class="notice"><p>以下内容是对原表的整理，不是对 55 项参考条目的逐篇重新核验。原表的文献类型和定位信息予以保留；计划用于实验或论文论证时，应回到原文核对任务、样本、统计结果及适用范围。</p></div><ul class="notes">__NOTES__<li>“委屈”的面部条目同时包含已列文献和未发表研究标注；未发表条目没有作者、年份或公开链接，不作为已公开验证的独立结论。</li><li>矩阵数字来自工作簿收录情况，不能用于比较模态优劣，也不能代替对单项证据质量的评估。</li></ul><p>来源：<a href="情绪各模态信号整理.xlsx" download>情绪各模态信号整理.xlsx</a>，“证据矩阵”A5:G44 及注释 A46:B50、“参考文献”A2:E57。</p></section>
<section id="references"><h2>参考文献与研究条目</h2><p>以下 55 项沿用原表顺序；DOI 链接来自原工作簿。第 55 项为未发表研究标注。</p><ol class="references">__REFERENCES__</ol></section>
</main><footer class="wrap"><p>ZJU-ECLab · 多模态情绪识别</p><a href="../index.html">返回研究资料主页</a></footer></body></html>'''
    replacements = {'__COVERAGE__': coverage, '__OPTIONS__': options, '__HEADERS__': ''.join(f'<th scope="col">{esc(m)}</th>' for m in modalities), '__ROWS__': ''.join(matrix_rows), '__NOTES__': notes, '__REFERENCES__': ''.join(ref_html)}
    for key, value in replacements.items():
        page = page.replace(key, value)
    (ROOT / 'docs' / '情绪各模态信号综述.html').write_text(page, encoding='utf-8')
    print('Generated: 39 emotions, 6 modalities, 55 references')
    print('Coverage:', dict(zip(modalities, counts)), 'Qualified:', dict(zip(modalities, caveats)))


if __name__ == '__main__':
    main()
