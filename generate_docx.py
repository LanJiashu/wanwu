#!/usr/bin/env python3
import re
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml


def set_cell_shading(cell, color):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)


def set_cell_border(cell, **kwargs):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}></w:tcBorders>')
    for edge, val in kwargs.items():
        element = parse_xml(
            f'<w:{edge} {nsdecls("w")} w:val="{val.get("val", "single")}" '
            f'w:sz="{val.get("sz", "4")}" w:space="0" '
            f'w:color="{val.get("color", "000000")}"/>'
        )
        tcBorders.append(element)
    tcPr.append(tcBorders)


def add_formatted_run(paragraph, text, bold=False, italic=False, size=None, color=None, font_name=None):
    run = paragraph.add_run(text)
    run.bold = bold
    run.italic = italic
    if size:
        run.font.size = Pt(size)
    if color:
        run.font.color.rgb = RGBColor(*color)
    if font_name:
        run.font.name = font_name
        run._element.rPr.rFonts.set(qn('w:eastAsia'), font_name)
    else:
        run.font.name = '微软雅黑'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')
    return run


def parse_inline_text(paragraph, text, default_size=10.5, default_bold=False):
    parts = re.split(r'(\*\*.*?\*\*|\*.*?\*|`[^`]+`)', text)
    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            add_formatted_run(paragraph, part[2:-2], bold=True, size=default_size)
        elif part.startswith('*') and part.endswith('*') and not part.startswith('**'):
            add_formatted_run(paragraph, part[1:-1], italic=True, size=default_size)
        elif part.startswith('`') and part.endswith('`'):
            run = add_formatted_run(paragraph, part[1:-1], size=default_size)
            run.font.name = 'Consolas'
        else:
            add_formatted_run(paragraph, part, bold=default_bold, size=default_size)


def add_table(doc, headers, rows, col_widths=None):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = 'Table Grid'

    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ''
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_formatted_run(p, header, bold=True, size=10, color=(255, 255, 255))
        set_cell_shading(cell, "2E5090")

    for r_idx, row in enumerate(rows):
        for c_idx, cell_text in enumerate(row):
            cell = table.rows[r_idx + 1].cells[c_idx]
            cell.text = ''
            p = cell.paragraphs[0]
            parse_inline_text(p, str(cell_text), default_size=10)
            if r_idx % 2 == 1:
                set_cell_shading(cell, "E8EEF4")

    if col_widths:
        for i, width in enumerate(col_widths):
            for row in table.rows:
                row.cells[i].width = Cm(width)

    doc.add_paragraph()


def add_code_block(doc, code_text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(1)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)
    for line in code_text.split('\n'):
        run = add_formatted_run(p, line + '\n', size=9)
        run.font.name = 'Consolas'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Consolas')
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F5F5F5"/>')
    p._element.get_or_add_pPr().append(shading)


def build_document():
    doc = Document()

    style = doc.styles['Normal']
    style.font.name = '微软雅黑'
    style._element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')
    style.font.size = Pt(10.5)
    style.paragraph_format.line_spacing = 1.35

    for level in range(1, 4):
        hs = doc.styles[f'Heading {level}']
        hs.font.name = '微软雅黑'
        hs._element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')
        hs.font.color.rgb = RGBColor(0x1A, 0x3C, 0x6E)

    sections = doc.sections
    for section in sections:
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)
        section.left_margin = Cm(3.17)
        section.right_margin = Cm(3.17)

    # ===== 封面 =====
    for _ in range(6):
        doc.add_paragraph()

    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_formatted_run(title_p, '锅炉制造企业AI化', bold=True, size=28, color=(0x1A, 0x3C, 0x6E))

    title_p2 = doc.add_paragraph()
    title_p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_formatted_run(title_p2, '可行性分析及实施方案', bold=True, size=28, color=(0x1A, 0x3C, 0x6E))

    doc.add_paragraph()

    sub_p = doc.add_paragraph()
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_formatted_run(sub_p, '智慧办公 + 智慧工厂', size=16, color=(0x4A, 0x6A, 0x9A))

    for _ in range(4):
        doc.add_paragraph()

    info_p = doc.add_paragraph()
    info_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_formatted_run(info_p, '2026年5月', size=14, color=(0x66, 0x66, 0x66))

    doc.add_page_break()

    # ===== 第一章 =====
    doc.add_heading('第一章 项目背景与目标', level=1)

    doc.add_heading('1.1 企业现状概述', level=2)
    p = doc.add_paragraph()
    parse_inline_text(p, '本企业为锅炉制造国有企业在多年的信息化建设中已部署以下核心业务系统：')

    items = [
        ('ERP系统', '覆盖财务、采购、库存、销售等核心业务流程'),
        ('MES系统', '管理生产执行、工单派发、生产报工、质检记录等制造过程'),
        ('WPS工作流系统', '支撑公文审批、流程签核等办公协同'),
        ('PLM系统', '管理产品生命周期、设计文档、工艺文件、BOM等'),
    ]
    for name, desc in items:
        p = doc.add_paragraph(style='List Bullet')
        add_formatted_run(p, name, bold=True, size=10.5)
        add_formatted_run(p, f'：{desc}', size=10.5)

    p = doc.add_paragraph()
    parse_inline_text(p, '上述系统各自运行形成了典型的"信息孤岛"格局数据链路未打通跨系统数据调用依赖人工操作效率低下。同时大量业务场景仍依赖人工经验判断缺乏智能化辅助手段。')

    p = doc.add_paragraph()
    add_formatted_run(p, '核心痛点：', bold=True, size=10.5)

    pain_points = [
        '数据孤岛：ERP/MES/PLM/WPS之间数据无法自动流转跨部门数据查询需人工操作',
        '知识碎片化：法规、标准、制度、工艺文件散落在不同系统和个人电脑中缺乏统一管理和智能检索',
        '人工审核效率低：体系文件、标准文件的人工纠错耗时耗力且易遗漏',
        '质检依赖经验：焊接质检高度依赖持证质检员的主观判断效率与一致性有待提升',
        '信息获取不便：操作人员在车间现场无法便捷获取工艺参数和操作规程',
    ]
    for pp in pain_points:
        p = doc.add_paragraph(style='List Bullet')
        parse_inline_text(p, pp, default_size=10.5)

    doc.add_heading('1.2 AI化改造总体目标', level=2)
    p = doc.add_paragraph()
    add_formatted_run(p, '智慧办公 + 智慧工厂', bold=True, size=10.5)
    add_formatted_run(p, '双轮驱动：', size=10.5)

    goals = [
        '智慧办公：通过AI助手实现公文辅助起草、制度智能问答、文本自动纠错、会议纪要生成等提升办公效率',
        '智慧工厂：通过AI视觉检测、设备参数智能推荐、工艺知识问答等提升制造质量和效率',
    ]
    for g in goals:
        p = doc.add_paragraph(style='List Bullet')
        parse_inline_text(p, g, default_size=10.5)

    doc.add_heading('1.3 项目范围界定', level=2)
    p = doc.add_paragraph()
    parse_inline_text(p, '本项目覆盖以下部门：')

    add_table(doc,
        ['部门', '核心业务', 'AI化需求方向'],
        [
            ['公司办', '公司管理', '公文起草、会议纪要、信息汇总'],
            ['人力资源', '人事管理', '制度问答、简历筛选、培训材料'],
            ['党群', '党建宣传', '宣传稿件撰写、活动策划'],
            ['财务', '财务管理', '单据OCR、报表摘要、合规审查'],
            ['采购', '采购管理', '合同比对、供应商资质审查'],
            ['安环', '安全环保', '隐患识别、合规检查清单'],
            ['质检', '锅炉制造质检', '焊缝AI检测、质检报告生成'],
            ['总师办', '体系/标准/信息化', '文本纠错、标准合规审查'],
            ['研究院', '技术研发', '文献检索、专利查新'],
            ['锅炉制造', '生产制造', '工艺问答、参数推荐'],
        ],
        col_widths=[3, 3.5, 6]
    )

    p = doc.add_paragraph()
    parse_inline_text(p, '各部门需求持续新增且存在跨部门协作需求（如质检与制造、采购与财务等）。')

    doc.add_heading('1.4 实施原则', level=2)
    principles = [
        '先易后难：优先落地技术成熟、价值明确的场景（文本纠错）再推进复杂场景（视觉质检、参数推荐）',
        '先办公后生产：办公场景风险可控、见效快；生产场景涉及安全责任需更审慎',
        '先试点后推广：每个场景先在1-2个部门试点验证后再全面推广',
        '安全第一：国企数据安全底线不可突破所有方案必须满足私有化部署要求',
        '人机协同：AI定位为辅助工具不替代人工决策尤其在涉及安全和质量的环节',
    ]
    for i, pr in enumerate(principles, 1):
        p = doc.add_paragraph()
        parse_inline_text(p, f'{i}. {pr}', default_size=10.5)

    doc.add_page_break()

    # ===== 第二章 =====
    doc.add_heading('第二章 AI能力边界与可行性分析', level=1)

    doc.add_heading('2.1 AI当前能做到什么（可行场景）', level=2)

    feasible_scenarios = [
        ('总师办：体系文件/标准文本纠错 ✅ 可行',
         '基于RAG（检索增强生成）技术将法规库、国标库、企业标准库构建为知识库AI可自动比对体系管理手册中的引用是否正确、标准编号是否有效、法规是否真实存在。文本纠错属于大模型擅长的语义理解与比对范畴结合知识库约束可实现较高准确率。预期效果：将人工纠错时间从数天缩短至数小时且能发现人工容易遗漏的引用错误。'),
        ('质检：焊接缺陷AI视觉检测 ✅ 可行（需明确预期）',
         '基于YOLOv8等目标检测模型对焊接质检图片进行自动缺陷识别（裂纹、气孔、夹渣、未焊透等）。\n关于"100%识别"的诚实回答：\n• 缺陷必检出（召回率）：无法保证100%。模型存在漏检概率尤其在缺陷微小或样本稀缺的情况下。但可通过调整置信度阈值将漏检率控制在极低水平（如<2%）代价是误检率会上升。\n• 检出必为缺陷（精确率）：无法保证100%。模型会将部分正常焊缝误判为缺陷。但误检比漏检更安全——误检可由人工复核排除漏检则可能放过真实缺陷。\n• 推荐策略：高召回率 + 人工复核。宁可多报不漏报将AI作为初筛工具最终由持证质检员确认。'),
        ('质检：质检报告自动生成 ✅ 可行',
         '基于质检数据（含AI检测结果）自动生成质检报告初稿。结构化数据到文本的生成是大模型的强项。'),
        ('采购：采购合同条款比对 ✅ 可行',
         '将待签合同与标准合同模板进行逐条比对标注差异条款和风险条款。文本比对与差异检测是大模型的基础能力。'),
        ('人力资源：简历筛选、公司制度问答、培训材料生成 ✅ 可行',
         '简历筛选：基于岗位需求自动提取简历关键信息并评分排序；制度问答：将公司制度文件导入知识库员工可自然语言提问获取准确答案；培训材料生成：基于制度文件和岗位要求自动生成培训大纲和考核题目。均为文本理解与生成类任务技术成熟。'),
        ('安环：安全隐患图片识别 ✅ 可行（需训练）',
         '基于视觉模型识别现场照片中的安全隐患（如未佩戴安全帽、违规堆放等）。目标检测模型可胜任但需要采集和标注现场图片进行模型训练。'),
        ('财务：报销单据OCR识别与初审、财务报表摘要生成 ✅ 可行',
         'OCR识别：自动识别发票、报销单据中的关键信息（金额、日期、供应商等）并与报销申请进行比对；报表摘要：自动生成财务报表的文字摘要和关键指标解读。OCR技术成熟大模型擅长数据解读和摘要生成。注意：财务数据涉及敏感信息必须严格权限控制。'),
        ('公司办/党群：公文起草辅助、会议纪要生成、宣传稿件撰写 ✅ 可行',
         '公文起草：基于模板和要点生成公文初稿人工修改定稿；会议纪要：基于会议录音转写文本自动整理为结构化纪要；宣传稿件：基于素材和主题生成宣传文章初稿。文本生成是大模型的核心能力但生成内容必须人工审核。'),
        ('锅炉制造：工艺文档问答 ✅ 可行',
         '将工艺文件、操作规程导入知识库操作人员可通过自然语言提问获取工艺参数和操作步骤。RAG问答技术成熟。'),
        ('研究院：技术文献检索与摘要 ✅ 可行',
         '对技术文献库进行语义检索自动生成文献摘要和对比分析。语义检索和摘要生成均为成熟技术。'),
    ]

    for title, content in feasible_scenarios:
        doc.add_heading(title, level=3)
        p = doc.add_paragraph()
        parse_inline_text(p, content, default_size=10.5)

    doc.add_heading('2.2 AI当前做不到什么（能力边界与限制）', level=2)

    not_feasible = [
        ('❌ 自动化画图（锅炉结构图/工程图）',
         '当前AI图像生成模型（如Stable Diffusion、DALL-E等）生成的是"看起来像"的图像而非精确的工程图纸。工程图需要严格的尺寸标注、公差配合、材料标注等精确信息AI无法保证这些工程精度。\n替代方案：AI可辅助生成设计说明文档、材料清单等文本类设计输出但工程图纸仍需CAD软件人工绘制。\n远期展望：AI辅助CAD（如自动标注、智能尺寸推荐）可能在3-5年内逐步成熟但完全自动画图在可预见的未来不可行。'),
        ('❌ 100%消除幻觉',
         '大语言模型的本质是基于概率的下一个词预测它不是"检索"知识而是"生成"回答。当知识库中没有相关信息时模型倾向于"编造"看似合理但实际错误的内容这就是幻觉（Hallucination）。\n我们能做的：通过RAG、引用溯源、置信度标注等手段大幅降低幻觉概率但无法完全消除。\n给领导的预期：AI输出必须经过人工审核尤其在涉及法规、标准、安全等关键领域。'),
        ('⚠️ 设备参数推荐（可行但必须加人工确认环节）',
         '基于知识库中的工艺规程、历史参数数据AI可以推荐设备参数。但关键限制：不能直接下发到设备。锅炉制造涉及高温高压安全红线参数错误可能导致严重安全事故。\n推荐方案：AI推荐参数 → 操作人员确认 → 班组长复核 → 方可执行。推荐结果通过APP/钉钉推送给操作人员但必须有人工确认环节。'),
        ('⚠️ AI辅助设计（可做方案初筛不可做最终设计）',
         'AI可基于历史方案和标准要求辅助生成设计方案初稿或对多个方案进行初步筛选。但锅炉设计涉及安全责任最终设计必须由持证设计人员审核签字AI不能替代。'),
        ('⚠️ 生产调度优化（可做建议不可自动执行）',
         'AI可基于订单、产能、物料等数据生成调度建议。但生产调度涉及多部门协调和突发情况处理AI无法处理所有边界情况建议仅供参考。'),
        ('❌ 替代人工做出最终质量判定',
         '锅炉属于特种设备质检判定涉及法定责任必须由持证质检员签字确认AI检测结果只能作为辅助参考。法规依据：《特种设备安全法》等法规要求质检人员持证上岗并承担法律责任。'),
        ('❌ 涉及法律责任的自主行为',
         '合同签署、安全审批、质量放行等涉及法律责任的环节AI不能自主执行必须由授权人员确认。'),
    ]

    for title, content in not_feasible:
        doc.add_heading(title, level=3)
        p = doc.add_paragraph()
        parse_inline_text(p, content, default_size=10.5)

    doc.add_heading('2.3 需要谨慎评估的"灰色地带"场景', level=2)

    add_table(doc,
        ['场景', '可行性', '关键约束', '建议'],
        [
            ['设备参数推荐', '⚠️ 可行', '必须人工确认不能直接下发', '推荐+确认流程'],
            ['AI辅助设计', '⚠️ 可行', '不可做最终设计', '方案初筛+人工审核'],
            ['生产调度优化', '⚠️ 可行', '不可自动执行', '建议参考+人工决策'],
            ['合同风险审查', '⚠️ 可行', '不可替代法务审核', '辅助标注+法务确认'],
            ['环保合规检查', '⚠️ 可行', '法规更新需及时', '知识库实时更新+人工复核'],
        ],
        col_widths=[3, 2.5, 4, 3.5]
    )

    doc.add_page_break()

    # ===== 第三章 =====
    doc.add_heading('第三章 关键问题讨论', level=1)

    # 3.1
    doc.add_heading('3.1 数据安全与权限问题', level=2)

    doc.add_heading('3.1.1 私有化部署与大模型API的选择', level=3)
    add_table(doc,
        ['方案', '优势', '劣势', '适用性'],
        [
            ['私有化部署', '数据不出内网安全性最高可定制化', '硬件成本高运维复杂', '✅ 推荐'],
            ['大模型API（公有云）', '无需硬件投入快速上线', '数据经过外部网络安全风险高', '❌ 不推荐'],
            ['混合方案', '非敏感数据用API敏感数据私有化', '架构复杂数据分类难度大', '⚠️ 备选'],
        ],
        col_widths=[3, 4, 3.5, 2.5]
    )
    p = doc.add_paragraph()
    add_formatted_run(p, '结论', bold=True, size=10.5)
    add_formatted_run(p, '：作为国企数据安全是底线必须选择', size=10.5)
    add_formatted_run(p, '私有化部署', bold=True, size=10.5)
    add_formatted_run(p, '方案。所有数据（包括对话记录、知识库、模型推理）均在企业内网完成不经过外部网络。', size=10.5)

    doc.add_heading('3.1.2 基于角色的知识库权限隔离方案（RBAC）', level=3)
    p = doc.add_paragraph()
    parse_inline_text(p, '采用**知识库级 + 文档级 + 段落级**三级权限控制：')

    add_code_block(doc, """知识库级权限：
├── 公共知识库（全员可访问）
│   ├── 公司制度库
│   ├── 通用法规库
│   └── 安全操作规程库
├── 部门知识库（部门内可访问）
│   ├── 财务知识库（仅财务部门）
│   ├── 人力资源库（仅HR部门）
│   └── 研究院技术库（仅研究院）
└── 专项知识库（指定人员可访问）
    ├── 质检标准库（质检+总师办）
    └── 采购合同库（采购+财务+法务）""")

    p = doc.add_paragraph()
    add_formatted_run(p, '权限控制机制：', bold=True, size=10.5)

    mechanisms = [
        '用户认证：与企业现有AD/LDAP对接统一身份认证',
        '角色定义：每个用户可属于多个角色每个角色对应不同知识库的访问权限',
        '检索过滤：RAG检索时根据用户角色动态过滤可访问的知识库确保用户只能检索到有权限的内容',
        '回答约束：即使用户通过其他渠道得知某文档存在若无权限AI也不会在回答中引用该文档内容',
        '审计日志：所有对话记录、知识库访问记录完整留痕可追溯',
    ]
    for m in mechanisms:
        p = doc.add_paragraph(style='List Bullet')
        parse_inline_text(p, m, default_size=10.5)

    doc.add_heading('3.1.3 敏感信息处理策略', level=3)
    add_table(doc,
        ['数据类型', '安全等级', '存储策略', '访问策略'],
        [
            ['财务数据（报表、成本、薪资）', '机密', '独立知识库加密存储', '仅财务部门授权人员'],
            ['人事数据（员工信息、考核）', '机密', '独立知识库加密存储', '仅HR部门授权人员'],
            ['合同数据（采购合同、商务条款）', '机密', '独立知识库加密存储', '仅采购+法务授权人员'],
            ['技术数据（工艺参数、设计文件）', '内部', '部门知识库', '部门内+授权人员'],
            ['制度法规（公开标准、公司制度）', '内部', '公共知识库', '全员可访问'],
        ],
        col_widths=[4, 2, 3.5, 3.5]
    )

    doc.add_heading('3.1.4 对话记录审计与追溯机制', level=3)
    audit_items = [
        '所有AI对话记录完整存储包括用户ID、时间戳、提问内容、AI回答、引用来源',
        '对话记录保留期不少于6个月满足审计合规要求',
        '支持按用户、时间、关键词等维度检索对话记录',
        '管理员可查看但不能修改对话记录确保审计完整性',
    ]
    for item in audit_items:
        p = doc.add_paragraph(style='List Bullet')
        parse_inline_text(p, item, default_size=10.5)

    # 3.2
    doc.add_heading('3.2 成本与硬件问题', level=2)

    doc.add_heading('3.2.1 私有化部署硬件选型', level=3)
    p = doc.add_paragraph()
    add_formatted_run(p, 'GPU服务器配置建议（全量部署方案）：', bold=True, size=10.5)
    p = doc.add_paragraph()
    parse_inline_text(p, '考虑到需要同时运行LLM推理和视觉模型训练/推理建议采用以下配置：')

    add_table(doc,
        ['配置项', '推荐方案', '说明'],
        [
            ['GPU', '4× NVIDIA A800 80GB 或 4× NVIDIA H20 96GB', 'A800为国内可采购的A100替代品H20为H100替代品'],
            ['CPU', '2× Intel Xeon 8468 (48核) 或等效', '支撑数据预处理和推理调度'],
            ['内存', '512GB DDR5', '模型加载和批处理需要大内存'],
            ['存储', '2× 1.92TB NVMe SSD（系统）+ 4× 3.84TB NVMe SSD（数据）', '知识库向量数据+模型文件'],
            ['网络', '2× 25GbE网卡', '多GPU通信和内网接入'],
            ['电源', '冗余电源 2× 2000W', '高可用'],
        ],
        col_widths=[2.5, 5.5, 5]
    )

    p = doc.add_paragraph()
    add_formatted_run(p, '为什么不能简单插卡到现有服务器：', bold=True, size=10.5)

    reasons = [
        '功耗问题：单张A800功耗约300W4张GPU功耗1200W现有服务器电源通常无法支撑',
        '散热问题：GPU高负载运行产热量远超普通服务器机柜散热设计4张GPU需要专用GPU服务器机箱',
        'PCIe通道：4张GPU需要4个PCIe 4.0 x16插槽现有服务器通常不具备',
        '内存带宽：GPU推理需要CPU快速供给数据普通服务器内存通道数不足',
    ]
    for r in reasons:
        p = doc.add_paragraph(style='List Bullet')
        parse_inline_text(p, r, default_size=10.5)

    p = doc.add_paragraph()
    add_formatted_run(p, '结论', bold=True, size=10.5)
    add_formatted_run(p, '：必须新采购专用GPU服务器不能在现有服务器上简单扩展。', size=10.5)

    doc.add_heading('3.2.2 30并发场景下的显存需求估算', level=3)
    p = doc.add_paragraph()
    add_formatted_run(p, 'LLM显存估算（以Qwen2.5-72B为例）：', bold=True, size=10.5)

    add_table(doc,
        ['项目', '显存占用'],
        [
            ['模型权重（FP16）', '~144GB'],
            ['KV Cache（30并发平均2048 token上下文）', '~60GB'],
            ['推理开销', '~10GB'],
            ['合计', '~214GB'],
        ],
        col_widths=[7, 4]
    )

    p = doc.add_paragraph()
    parse_inline_text(p, '4×A800 80GB = 320GB总显存可满足72B模型30并发需求。')

    p = doc.add_paragraph()
    add_formatted_run(p, '若选择14B模型（如Qwen2.5-14B）：', bold=True, size=10.5)

    add_table(doc,
        ['项目', '显存占用'],
        [
            ['模型权重（FP16）', '~28GB'],
            ['KV Cache（30并发）', '~30GB'],
            ['推理开销', '~5GB'],
            ['合计', '~63GB'],
        ],
        col_widths=[7, 4]
    )

    p = doc.add_paragraph()
    parse_inline_text(p, '1×A800 80GB即可满足但考虑到冗余和视觉模型训练建议仍采用4卡方案。')

    p = doc.add_paragraph()
    add_formatted_run(p, '推荐方案', bold=True, size=10.5)
    add_formatted_run(p, '：4×A800 80GB服务器。2卡用于LLM推理（72B模型）1卡用于视觉模型推理/训练1卡冗余/扩展。', size=10.5)

    doc.add_heading('3.2.3 总体拥有成本（TCO）分析', level=3)
    add_table(doc,
        ['成本项', '估算金额（万元）', '说明'],
        [
            ['GPU服务器采购', '80-120', '4×A800 80GB服务器'],
            ['存储扩容', '10-20', 'NAS/SAN扩容用于知识库和模型文件'],
            ['网络设备', '5-10', '交换机、防火墙等'],
            ['机房改造', '5-15', '电力扩容、空调升级'],
            ['软件开发/集成', '50-100', 'AI中台开发、系统集成、场景开发'],
            ['首年总投入', '150-265', ''],
            ['年电费', '8-12', 'GPU服务器7×24运行按0.8元/度估算'],
            ['年运维人力', '15-25', '1-2名AI运维工程师'],
            ['模型升级/知识库维护', '5-10', '年度模型更新、知识库扩容'],
            ['年度运维', '28-47', ''],
        ],
        col_widths=[3.5, 3, 6.5]
    )

    # 3.3
    doc.add_heading('3.3 模型选型问题', level=2)

    doc.add_heading('3.3.1 大语言模型选型对比', level=3)
    add_table(doc,
        ['模型', '参数量', '开源协议', '中文能力', '推理效率', '推荐度'],
        [
            ['Qwen2.5-72B', '72B', 'Apache 2.0', '⭐⭐⭐⭐⭐', '中等', '✅ 首选'],
            ['Qwen2.5-14B', '14B', 'Apache 2.0', '⭐⭐⭐⭐', '高', '✅ 备选'],
            ['DeepSeek-V3', '671B（MoE激活37B）', 'MIT', '⭐⭐⭐⭐⭐', '中等', '⚠️ MoE架构显存需求大'],
            ['DeepSeek-R1', '671B（MoE）', 'MIT', '⭐⭐⭐⭐⭐', '低', '❌ 推理模型不适合RAG场景'],
            ['ChatGLM4-9B', '9B', 'Apache 2.0', '⭐⭐⭐⭐', '高', '⚠️ 参数量偏小'],
            ['Llama3.1-70B', '70B', 'Llama License', '⭐⭐⭐', '中等', '❌ 中文能力弱'],
        ],
        col_widths=[2.5, 2.5, 2, 2, 1.5, 3.5]
    )

    p = doc.add_paragraph()
    add_formatted_run(p, '推荐方案：Qwen2.5-72B', bold=True, size=10.5)

    reasons_qwen = [
        '中文能力在开源模型中处于第一梯队尤其擅长中文文本理解和生成',
        'Apache 2.0协议允许商业使用无法律风险',
        '72B参数量在4×A800上可流畅运行30并发',
        '阿里云持续更新迭代社区活跃长期维护有保障',
        '对RAG场景优化较好支持长上下文（128K）',
    ]
    for r in reasons_qwen:
        p = doc.add_paragraph(style='List Bullet')
        parse_inline_text(p, r, default_size=10.5)

    doc.add_heading('3.3.2 视觉模型选型', level=3)
    add_table(doc,
        ['模型', '用途', '推荐度'],
        [
            ['YOLOv8', '焊接缺陷检测、安全隐患识别', '✅ 首选'],
            ['YOLOv11', '同上精度略高', '✅ 备选'],
            ['PaddleDetection', '同上国产框架', '⚠️ 备选'],
        ],
        col_widths=[3, 5, 3.5]
    )

    p = doc.add_paragraph()
    add_formatted_run(p, '推荐方案：YOLOv8', bold=True, size=10.5)
    p = doc.add_paragraph()
    parse_inline_text(p, '工业缺陷检测领域验证最多社区资源最丰富支持目标检测、实例分割等多种任务训练流程成熟推理速度快。')

    doc.add_heading('3.3.3 模型规模选择', level=3)
    p = doc.add_paragraph()
    add_formatted_run(p, '全量部署方案', bold=True, size=10.5)
    add_formatted_run(p, '：LLM选择72B参数量全量部署不做量化压缩。文本纠错场景对模型理解能力要求高量化可能影响纠错准确率。4×A800显存充足无需量化即可运行72B模型。全量部署保证最佳效果避免量化引入的精度损失。', size=10.5)

    # 3.4
    doc.add_heading('3.4 扩展维护与升级问题', level=2)

    doc.add_heading('3.4.1 硬件升级路径', level=3)
    add_table(doc,
        ['升级方向', '方案', '时机'],
        [
            ['GPU扩容', '增加GPU服务器节点组成推理集群', '并发需求超过单机承载能力时'],
            ['集群化', '引入Kubernetes + GPU调度实现多节点负载均衡', '3-5台GPU服务器时'],
            ['存储扩容', '增加NAS容量或引入分布式存储', '知识库数据量超过10TB时'],
            ['网络升级', '升级至100GbE InfiniBand', '多节点GPU集群通信瓶颈时'],
        ],
        col_widths=[3, 5, 5]
    )

    doc.add_heading('3.4.2 模型升级策略', level=3)
    strategies = [
        '版本管理：每个模型版本独立存储保留历史版本可回滚',
        '灰度发布：新模型先在测试环境验证再对5%用户开放逐步扩大',
        'A/B测试：新旧模型并行运行对比效果指标确认新模型无退化后全量切换',
        '热替换：通过vLLM等推理框架支持模型热加载无需停机即可切换模型版本',
    ]
    for s in strategies:
        p = doc.add_paragraph(style='List Bullet')
        parse_inline_text(p, s, default_size=10.5)

    doc.add_heading('3.4.3 知识库更新机制', level=3)
    updates = [
        '定期更新：法规库、国标库每季度检查更新及时同步最新版本',
        '事件驱动更新：新法规发布、标准修订时即时更新知识库',
        '版本管理：知识库文档支持版本控制可追溯每次修改',
        '过期标记：已废止的法规和标准标记为"已废止"避免AI引用过期信息',
        '更新通知：知识库更新后自动通知相关用户',
    ]
    for u in updates:
        p = doc.add_paragraph(style='List Bullet')
        parse_inline_text(p, u, default_size=10.5)

    doc.add_heading('3.4.4 运维监控体系', level=3)
    add_table(doc,
        ['监控项', '工具', '告警阈值'],
        [
            ['GPU利用率', 'Prometheus + Grafana', '>90%持续5分钟'],
            ['显存占用', 'Prometheus + Grafana', '>95%'],
            ['推理延迟', 'Prometheus + Grafana', 'P99 > 10秒'],
            ['系统可用性', 'Prometheus + Grafana', '<99.5%'],
            ['知识库检索延迟', 'Prometheus + Grafana', '>3秒'],
            ['对话异常率', '自定义', '>5%'],
        ],
        col_widths=[3.5, 4, 4]
    )

    # 3.5
    doc.add_heading('3.5 与现有信息化系统对接', level=2)

    doc.add_heading('3.5.1 对接方案对比', level=3)
    add_table(doc,
        ['方案', '优势', '劣势', '推荐度'],
        [
            ['API集成', '松耦合安全性好不影响现有系统', '依赖系统是否开放API', '✅ 首选'],
            ['数据库直连', '数据获取直接实时性好', '强耦合安全风险高影响现有系统性能', '❌ 不推荐'],
            ['中间件/数据总线', '统一管理可复用', '架构复杂初期投入大', '⚠️ 中期引入'],
        ],
        col_widths=[3, 4, 3.5, 2.5]
    )

    p = doc.add_paragraph()
    add_formatted_run(p, '推荐策略：API优先中间件渐进', bold=True, size=10.5)
    steps = [
        '一期：通过API与各系统对接快速实现数据互通',
        '二期：引入企业服务总线（ESB）或数据中台统一管理数据流',
        '三期：建设统一数据湖实现跨系统数据分析和AI训练',
    ]
    for s in steps:
        p = doc.add_paragraph(style='List Bullet')
        parse_inline_text(p, s, default_size=10.5)

    doc.add_heading('3.5.2 各系统对接技术路径', level=3)
    add_table(doc,
        ['系统', '对接方式', '数据流向', '实施步骤'],
        [
            ['ERP', 'API或定时数据导出', 'ERP → AI中台', '确认API→开发同步接口→权限映射'],
            ['MES', 'API或数据库视图（只读）', 'MES ↔ AI中台', '确认接口→质检回写→参数查询接口'],
            ['PLM', 'API或文件同步', 'PLM → AI中台', '文档导出接口→自动同步→版本对齐'],
            ['WPS工作流', 'API', 'WPS ↔ AI中台', '审批接口→文档自动处理→结果回写'],
        ],
        col_widths=[2.5, 3.5, 3, 4.5]
    )

    doc.add_heading('3.5.3 单点登录与统一身份认证', level=3)
    sso_items = [
        '与企业现有AD/LDAP/统一认证平台对接实现一次登录全系统通行',
        'AI中台用户权限与企业组织架构同步无需单独维护用户体系',
        '支持OAuth2.0/SAML等标准协议对接',
    ]
    for item in sso_items:
        p = doc.add_paragraph(style='List Bullet')
        parse_inline_text(p, item, default_size=10.5)

    # 3.6
    doc.add_heading('3.6 开源项目"万物"（Wanwu）二次开发可行性评估', level=2)

    doc.add_heading('3.6.1 Wanwu项目能力分析', level=3)
    p = doc.add_paragraph()
    parse_inline_text(p, 'Wanwu（万物）是一个开源的AI应用开发平台提供对话、知识库、工作流等基础能力。其核心功能包括：大模型对话管理、知识库构建与RAG、工作流编排、多模型支持、API服务。')

    doc.add_heading('3.6.2 与本企业需求的匹配度', level=3)
    add_table(doc,
        ['需求', 'Wanwu支持度', '差距'],
        [
            ['私有化部署', '✅ 支持', '无'],
            ['知识库RAG', '✅ 支持', '需增强权限控制'],
            ['多部门权限隔离', '⚠️ 基础支持', '需二次开发实现细粒度RBAC'],
            ['工作流编排', '✅ 支持', '需定制业务工作流'],
            ['视觉模型服务', '❌ 不支持', '需独立部署视觉模型服务'],
            ['ERP/MES对接', '❌ 不支持', '需二次开发数据对接'],
            ['钉钉/微信集成', '⚠️ 基础支持', '需二次开发'],
            ['审计日志', '⚠️ 基础支持', '需增强满足合规要求'],
        ],
        col_widths=[3.5, 3, 6]
    )

    doc.add_heading('3.6.3 二次开发的风险与收益', level=3)
    p = doc.add_paragraph()
    add_formatted_run(p, '收益：', bold=True, size=10.5)
    benefits = [
        '降低从零开发的成本和周期',
        '社区持续更新可跟进AI技术发展',
        '基础功能（对话、知识库）开箱即用',
    ]
    for b in benefits:
        p = doc.add_paragraph(style='List Bullet')
        parse_inline_text(p, b, default_size=10.5)

    p = doc.add_paragraph()
    add_formatted_run(p, '风险：', bold=True, size=10.5)
    risks = [
        '深度定制可能与上游更新产生冲突升级时需谨慎合并',
        '权限体系需要大幅改造工作量大',
        '视觉模型服务需要独立开发Wanwu不覆盖',
        '社区版功能可能不如商业版完整',
    ]
    for r in risks:
        p = doc.add_paragraph(style='List Bullet')
        parse_inline_text(p, r, default_size=10.5)

    p = doc.add_paragraph()
    add_formatted_run(p, '结论', bold=True, size=10.5)
    add_formatted_run(p, '：可行但需谨慎评估。建议以Wanwu为基础平台进行二次开发但需明确以下边界：', size=10.5)

    boundaries = [
        'Wanwu负责对话管理、知识库RAG、工作流编排等基础能力',
        '权限体系需要深度改造这是最大的二次开发工作量',
        '视觉模型服务独立部署通过API与Wanwu集成',
        'ERP/MES/PLM对接需要独立开发数据管道',
        '保留替换能力：若Wanwu无法满足需求可切换到其他平台（如Dify、FastGPT等）',
    ]
    for b in boundaries:
        p = doc.add_paragraph(style='List Bullet')
        parse_inline_text(p, b, default_size=10.5)

    # 3.7
    doc.add_heading('3.7 AI幻觉问题与准确性保障', level=2)

    doc.add_heading('3.7.1 为什么豆包等AI会"东拉西扯"', level=3)
    p = doc.add_paragraph()
    add_formatted_run(p, '大模型生成原理：', bold=True, size=10.5)
    parse_inline_text(p, '大语言模型（LLM）的工作方式是"预测下一个最可能的词"而非"检索事实"。它通过在海量文本上训练学习到了词语之间的统计关联但并不真正"理解"事实的真伪。')

    p = doc.add_paragraph()
    add_formatted_run(p, '幻觉产生的原因：', bold=True, size=10.5)

    hallucination_causes = [
        '训练数据局限：模型的知识截止于训练数据的时间点之后的新信息它不知道',
        '概率生成而非检索：当被问到训练数据中不常见的领域时模型会基于概率"编造"看似合理但实际错误的回答',
        '缺乏事实校验：模型内部没有"事实核查"机制它不知道自己不知道什么',
        '上下文干扰：长对话中模型可能被之前的错误信息"带偏"继续编造',
        '过度自信：模型不会说"我不知道"而是倾向于给出一个看起来合理的答案',
    ]
    for c in hallucination_causes:
        p = doc.add_paragraph(style='List Bullet')
        parse_inline_text(p, c, default_size=10.5)

    p = doc.add_paragraph()
    add_formatted_run(p, '为什么豆包等公开AI幻觉更严重：', bold=True, size=10.5)
    public_reasons = [
        '公开AI面向通用场景知识面广但深度不足',
        '没有企业专属知识库约束容易"自由发挥"',
        '优化了"有用性"而非"准确性"倾向于给出回答而非承认不知道',
    ]
    for r in public_reasons:
        p = doc.add_paragraph(style='List Bullet')
        parse_inline_text(p, r, default_size=10.5)

    doc.add_heading('3.7.2 我们方案中的多重防护策略', level=3)
    p = doc.add_paragraph()
    parse_inline_text(p, '我们采用**"知识库约束 + 引用溯源 + 人工审核"**三层防护：')

    p = doc.add_paragraph()
    add_formatted_run(p, '第一层：知识库约束（RAG）', bold=True, size=10.5)
    rag_items = [
        'AI回答必须基于知识库中的文档不允许"自由发挥"',
        '检索相关文档片段作为上下文喂给模型约束其回答范围',
        '当知识库中没有相关文档时AI应回答"未找到相关信息"而非编造',
    ]
    for item in rag_items:
        p = doc.add_paragraph(style='List Bullet')
        parse_inline_text(p, item, default_size=10.5)

    p = doc.add_paragraph()
    add_formatted_run(p, '第二层：引用溯源', bold=True, size=10.5)
    source_items = [
        'AI的每一条回答必须标注来源文档和具体段落',
        '用户可点击来源链接查看原文验证AI回答的准确性',
        '无来源的回答标记为"AI推断仅供参考"',
    ]
    for item in source_items:
        p = doc.add_paragraph(style='List Bullet')
        parse_inline_text(p, item, default_size=10.5)

    p = doc.add_paragraph()
    add_formatted_run(p, '第三层：人工审核', bold=True, size=10.5)
    review_items = [
        '关键场景（法规引用、标准判定等）AI输出必须经人工审核',
        '建立审核流程：AI初检 → 人工复核 → 确认/修正',
        '审核结果反馈到系统持续优化',
    ]
    for item in review_items:
        p = doc.add_paragraph(style='List Bullet')
        parse_inline_text(p, item, default_size=10.5)

    doc.add_heading('3.7.3 诚实回答：能否保证100%准确性？', level=3)
    p = doc.add_paragraph()
    add_formatted_run(p, '不能。', bold=True, size=12, color=(0xCC, 0x00, 0x00))

    p = doc.add_paragraph()
    parse_inline_text(p, '任何声称100%准确的AI方案都是不诚实的。原因如下：')

    accuracy_reasons = [
        'RAG检索可能不完整：知识库可能未覆盖所有相关文档导致检索遗漏',
        '模型理解可能偏差：即使检索到正确文档模型可能误解文档含义',
        '知识库可能过时：法规和标准更新后若知识库未及时同步将产生错误引用',
        '边界情况：模糊表述、多义条款等边界情况模型可能判断错误',
    ]
    for r in accuracy_reasons:
        p = doc.add_paragraph(style='List Bullet')
        parse_inline_text(p, r, default_size=10.5)

    p = doc.add_paragraph()
    add_formatted_run(p, '我们能承诺的：', bold=True, size=10.5)

    promises = [
        '通过RAG + 引用溯源将幻觉率从公开AI的10-30%降低至2-5%',
        '通过人工审核将最终输出错误率控制在1%以下',
        '通过持续迭代（知识库更新、模型升级、反馈修正）逐步提升准确性',
        '永远保留人工审核环节尤其在涉及法规、标准、安全的场景',
    ]
    for pr in promises:
        p = doc.add_paragraph(style='List Bullet')
        parse_inline_text(p, pr, default_size=10.5)

    # 3.8
    doc.add_heading('3.8 持续学习能力', level=2)

    doc.add_heading('3.8.1 LLM + 知识库方案的持续学习', level=3)
    p = doc.add_paragraph()
    add_formatted_run(p, '知识库增量更新（主要手段）：', bold=True, size=10.5)
    parse_inline_text(p, '这是最核心的持续学习方式。知识库可以随时添加新文档无需重新训练模型。')

    add_table(doc,
        ['更新类型', '频率', '方式'],
        [
            ['法规更新', '不定期', '法规发布后即时导入'],
            ['国标更新', '季度', '定期检查更新批量导入'],
            ['企业制度更新', '不定期', '制度发布后即时导入'],
            ['工艺文件更新', '不定期', 'PLM同步后自动导入'],
            ['纠错反馈积累', '持续', '人工审核反馈自动入库'],
        ],
        col_widths=[3.5, 2.5, 6]
    )

    p = doc.add_paragraph()
    add_formatted_run(p, '模型微调（辅助手段）：', bold=True, size=10.5)
    parse_inline_text(p, '当知识库更新无法满足需求时（如模型对特定领域理解不足）可进行模型微调。')

    add_table(doc,
        ['微调类型', '场景', '频率', '数据需求'],
        [
            ['SFT（监督微调）', '模型输出格式不规范', '半年一次', '1000+高质量问答对'],
            ['LoRA微调', '特定领域术语理解不足', '按需', '500+领域语料'],
            ['DPO/RLHF', '模型回答偏好对齐', '年度', '人工偏好标注数据'],
        ],
        col_widths=[3, 3.5, 2, 3.5]
    )

    p = doc.add_paragraph()
    add_formatted_run(p, '推荐策略', bold=True, size=10.5)
    add_formatted_run(p, '：知识库更新为主模型微调为辅。90%的持续学习需求通过知识库更新解决仅当模型基础能力不足时才进行微调。', size=10.5)

    doc.add_heading('3.8.2 Hermes持续学习能力评估与引入可行性', level=3)
    p = doc.add_paragraph()
    parse_inline_text(p, 'Hermes是一个支持持续学习的AI框架其核心能力是在不重新训练模型的情况下通过记忆机制和知识注入实现"学习"新知识。')

    add_table(doc,
        ['评估维度', '结论', '说明'],
        [
            ['技术可行性', '⚠️ 需评估', 'Hermes的持续学习机制与RAG方案有重叠需评估整合方式'],
            ['与Wanwu兼容性', '⚠️ 需验证', '需确认Hermes能否与Wanwu平台集成'],
            ['实际需求', '✅ 有需求', '持续学习是长期运营的核心能力'],
            ['引入时机', '二期', '一期先跑通基础流程二期再引入持续学习能力'],
        ],
        col_widths=[3, 2.5, 7]
    )

    p = doc.add_paragraph()
    add_formatted_run(p, '建议', bold=True, size=10.5)
    add_formatted_run(p, '：一期不引入Hermes先用RAG + 知识库增量更新实现基础持续学习。二期评估Hermes或其他持续学习框架的引入。', size=10.5)

    doc.add_heading('3.8.3 Skill（技能插件）与工作流（Workflow）在业务中的作用与价值', level=3)

    p = doc.add_paragraph()
    add_formatted_run(p, 'Skill（技能插件）：', bold=True, size=10.5)
    parse_inline_text(p, 'Skill是预定义的AI能力模块每个Skill封装了一个具体的业务能力：')

    add_table(doc,
        ['Skill示例', '所属部门', '功能'],
        [
            ['文本纠错', '总师办', '对体系文件进行引用错误、语法错误等纠错'],
            ['合同比对', '采购', '将待签合同与标准模板逐条比对'],
            ['报表摘要', '财务', '自动生成财务报表摘要'],
            ['制度问答', '全员', '基于知识库回答公司制度相关问题'],
            ['参数推荐', '锅炉制造', '基于工艺规程推荐设备参数'],
        ],
        col_widths=[3, 3, 6.5]
    )

    p = doc.add_paragraph()
    add_formatted_run(p, 'Skill的价值：', bold=True, size=10.5)
    skill_values = [
        '将通用LLM能力封装为具体业务动作降低用户使用门槛',
        '每个Skill可独立配置提示词、知识库、权限实现精细化管理',
        '新需求可通过开发新Skill快速响应无需修改底层架构',
    ]
    for v in skill_values:
        p = doc.add_paragraph(style='List Bullet')
        parse_inline_text(p, v, default_size=10.5)

    p = doc.add_paragraph()
    add_formatted_run(p, 'Workflow（工作流）：', bold=True, size=10.5)
    parse_inline_text(p, 'Workflow是多步骤的业务流程编排将多个Skill和人工审核环节串联：')

    add_code_block(doc, """文本纠错工作流示例：
文档上传 → 文档解析分段 → 知识库检索比对 → LLM纠错分析
→ 引用溯源校验 → 输出纠错报告 → 人工审核确认 → 归档

焊接质检工作流示例：
质检图片上传 → YOLOv8缺陷检测 → 检测结果结构化
→ LLM生成质检描述 → 质检报告生成 → 质检员确认 → 回写MES""")

    p = doc.add_paragraph()
    add_formatted_run(p, 'Workflow的价值：', bold=True, size=10.5)
    wf_values = [
        '将复杂业务流程标准化、自动化减少人工操作环节',
        '在关键节点插入人工审核确保安全合规',
        '跨系统协同：一个工作流可同时调用AI中台、ERP、MES等多个系统',
    ]
    for v in wf_values:
        p = doc.add_paragraph(style='List Bullet')
        parse_inline_text(p, v, default_size=10.5)

    # 3.9
    doc.add_heading('3.9 架构选型：训练专属大模型 vs LLM + 知识库', level=2)

    doc.add_heading('3.9.1 为什么多需求+权限场景不适合训练一个大模型', level=3)
    p = doc.add_paragraph()
    parse_inline_text(p, '训练专属大模型的方案：收集企业所有业务数据训练一个专属大模型使其"记住"所有知识。')

    p = doc.add_paragraph()
    add_formatted_run(p, '问题：', bold=True, size=10.5)

    problems = [
        '数据量不足：训练一个可用的大模型需要数百万条高质量数据企业内部数据远不够',
        '权限无法隔离：模型一旦"记住"了财务数据任何提问都可能泄露无法按角色隔离',
        '更新成本极高：每次法规更新都需要重新训练模型训练一次耗时数天到数周',
        '灾难性遗忘：新数据训练可能导致模型"忘记"之前学过的知识',
        '无法溯源：模型生成的回答无法追溯到具体文档来源',
        '维护困难：模型训练需要专业AI工程师企业难以长期维护',
    ]
    for pr in problems:
        p = doc.add_paragraph(style='List Bullet')
        parse_inline_text(p, pr, default_size=10.5)

    p = doc.add_paragraph()
    add_formatted_run(p, '结论', bold=True, size=10.5)
    add_formatted_run(p, '：多需求+权限场景下训练专属大模型不可行。', size=10.5)

    doc.add_heading('3.9.2 LLM + 知识库 + Skill + 工作流 = 最佳适配方案', level=3)
    add_table(doc,
        ['维度', '训练专属模型', 'LLM + 知识库 + Skill + 工作流'],
        [
            ['权限隔离', '❌ 无法实现', '✅ 知识库级权限控制'],
            ['知识更新', '❌ 需重训练', '✅ 知识库增量更新即时生效'],
            ['引用溯源', '❌ 无法溯源', '✅ 每条回答可追溯到原文'],
            ['新需求响应', '❌ 需重新训练', '✅ 新建Skill/工作流即可'],
            ['维护成本', '❌ 极高', '✅ 较低'],
            ['准确性', '⚠️ 不稳定', '✅ 知识库约束+人工审核'],
            ['数据安全', '❌ 权限泄露风险', '✅ 按角色隔离'],
        ],
        col_widths=[3, 4, 5.5]
    )

    p = doc.add_paragraph()
    add_formatted_run(p, '推荐架构', bold=True, size=10.5)
    add_formatted_run(p, '：通用大模型（Qwen2.5-72B） + 部门知识库（按权限隔离） + 业务Skill（按场景封装） + 工作流（按流程编排） = 企业AI能力平台', size=10.5)

    # 3.10
    doc.add_heading('3.10 平台统一性', level=2)

    doc.add_heading('3.10.1 是否可以通过一个平台承载所有AI能力', level=3)
    p = doc.add_paragraph()
    add_formatted_run(p, '可以。', bold=True, size=10.5)
    parse_inline_text(p, '推荐统一AI中台架构将所有AI能力整合到一个平台。')

    p = doc.add_paragraph()
    add_formatted_run(p, '统一平台的功能模块规划：', bold=True, size=10.5)

    add_code_block(doc, """AI中台
├── 对话服务（通用对话/部门专属对话/Skill对话）
├── 知识库服务（文档管理/权限管理/版本管理/更新管理）
├── 技能引擎（Skill管理/提示词管理/Skill市场）
├── 工作流引擎（工作流设计器/工作流执行/人工审核节点）
├── 视觉模型服务（焊接质检模型/安全隐患识别模型/模型训练管理）
├── 系统集成（ERP/MES/PLM/WPS对接）
├── 安全与权限（统一认证SSO/角色权限RBAC/审计日志/数据脱敏）
└── 运维监控（模型监控/服务监控/告警管理）""")

    doc.add_heading('3.10.2 需要独立部署的组件', level=3)
    add_table(doc,
        ['组件', '部署方式', '原因'],
        [
            ['LLM推理服务', 'GPU服务器主节点', '显存需求大'],
            ['视觉模型服务', 'GPU服务器独立节点', '可与LLM共享GPU但建议独立部署避免资源争抢'],
            ['知识库服务', '普通服务器', '向量数据库CPU密集型无需GPU'],
            ['工作流引擎', '普通服务器', '无GPU需求'],
            ['前端Web服务', '普通服务器', '无GPU需求'],
        ],
        col_widths=[3, 4, 5.5]
    )

    p = doc.add_paragraph()
    add_formatted_run(p, '推荐部署架构', bold=True, size=10.5)
    add_formatted_run(p, '：1台GPU服务器（运行LLM推理 + 视觉模型推理/训练）+ 1-2台普通服务器（运行知识库、工作流、前端、API网关等）+ 现有服务器（ERP/MES/PLM/WPS保持不变通过API对接）。', size=10.5)

    doc.add_page_break()

    # ===== 第四章 =====
    doc.add_heading('第四章 总体技术架构方案', level=1)

    doc.add_heading('4.1 整体架构', level=2)

    add_code_block(doc, """┌─────────────────────────────────────────────────────────────┐
│                        应用层                                │
│  文本纠错助手 | 焊接质检系统 | 合同比对助手 | 制度问答助手   │
│  参数推荐助手 | 钉钉/微信小程序 | ...                        │
├─────────────────────────────────────────────────────────────┤
│                      AI中台层                                │
│  LLM推理服务(Qwen2.5) | 知识库服务(向量DB+RAG管线)          │
│  技能引擎(Skill管理) | 工作流引擎(Workflow编排执行)          │
│  视觉模型服务(YOLOv8) | 统一API网关                          │
│  安全与权限(SSO/RBAC/审计/脱敏)                              │
├─────────────────────────────────────────────────────────────┤
│                      数据接入层                              │
│  ERP接口 | MES接口 | PLM接口 | WPS接口 | 文件/数据库同步管道 │
├─────────────────────────────────────────────────────────────┤
│                      基础设施层                              │
│  GPU服务器(4×A800 80GB) | 应用/数据服务器 | 网络/安全设备    │
└─────────────────────────────────────────────────────────────┘""")

    doc.add_heading('4.2 技术栈推荐', level=2)
    add_table(doc,
        ['层级', '组件', '推荐技术', '说明'],
        [
            ['LLM推理', '推理框架', 'vLLM', '高性能推理支持连续批处理PagedAttention优化显存'],
            ['LLM推理', '模型', 'Qwen2.5-72B', '中文能力最强开源模型之一'],
            ['知识库', '向量数据库', 'Milvus', '国产开源高性能向量数据库支持亿级向量检索'],
            ['知识库', '文档解析', 'Unstructured + 自研解析器', '支持PDF/Word/Excel/WPS等格式'],
            ['知识库', 'Embedding模型', 'BGE-M3', '中文语义向量模型效果好'],
            ['知识库', 'RAG框架', 'LlamaIndex / LangChain', '成熟的RAG管线框架'],
            ['视觉模型', '目标检测', 'YOLOv8', '工业缺陷检测首选'],
            ['视觉模型', '推理服务', 'Triton Inference Server', 'NVIDIA推理服务框架支持多模型'],
            ['应用平台', '基础平台', 'Wanwu（二次开发）', '提供对话、知识库、工作流基础能力'],
            ['前端', 'Web前端', 'React/Vue', '现代Web框架'],
            ['前端', '移动端', '钉钉小程序 / 微信小程序', '车间操作人员移动访问'],
            ['集成', 'API网关', 'Kong / Nginx', '统一API入口认证鉴权'],
            ['集成', '消息队列', 'RabbitMQ / Kafka', '异步数据同步'],
            ['运维', '容器化', 'Docker + Kubernetes', '服务编排与管理'],
            ['运维', '监控', 'Prometheus + Grafana', '系统监控与告警'],
            ['安全', '认证', 'Keycloak', '统一身份认证SSO'],
        ],
        col_widths=[2, 2.5, 4, 4]
    )

    doc.add_heading('4.3 部署架构', level=2)

    doc.add_heading('4.3.1 网络拓扑（内网隔离方案）', level=3)

    add_code_block(doc, """企业内网
├── GPU服务器 (AI专网段) ←→ 应用服务器 (业务网段)
│   LLM+视觉模型              知识库+工作流
│                                  │
│                           API网关 (DMZ区)
│                                  │
│              ┌───────────────────┼───────────────────┐
│              │                   │                   │
│        ERP服务器            MES服务器           PLM/WPS服务器
│        (业务网段)           (业务网段)           (业务网段)
│
├── 用户终端 (办公网段)
│
❌ 无直连外部网络 —— AI系统不暴露到外部网络""")

    p = doc.add_paragraph()
    add_formatted_run(p, '网络隔离要点：', bold=True, size=10.5)
    network_points = [
        'GPU服务器位于AI专网段仅应用服务器可访问不直接暴露给用户终端',
        'API网关位于DMZ区负责认证鉴权和请求转发',
        '业务系统（ERP/MES/PLM）位于业务网段通过API网关与AI中台通信',
        'AI系统不暴露到外部网络所有访问均在内网完成',
        '钉钉/微信小程序通过企业内网VPN或专用通道访问',
    ]
    for np in network_points:
        p = doc.add_paragraph(style='List Bullet')
        parse_inline_text(p, np, default_size=10.5)

    doc.add_heading('4.3.2 GPU服务器配置建议', level=3)
    add_table(doc,
        ['组件', '配置', '用途'],
        [
            ['GPU', '4× NVIDIA A800 80GB', 'LLM推理(2卡) + 视觉模型(1卡) + 冗余(1卡)'],
            ['CPU', '2× Intel Xeon 8468', '数据预处理、推理调度'],
            ['内存', '512GB DDR5', '模型加载、批处理缓存'],
            ['系统盘', '2× 1.92TB NVMe SSD (RAID1)', '操作系统、推理框架'],
            ['数据盘', '4× 3.84TB NVMe SSD (RAID5)', '模型文件、向量数据'],
            ['网络', '2× 25GbE', 'GPU间通信、内网接入'],
        ],
        col_widths=[2.5, 5, 5]
    )

    doc.add_heading('4.3.3 并发与负载均衡方案', level=3)
    add_code_block(doc, """用户请求
    ↓
API网关（认证鉴权）
    ↓
负载均衡器（Nginx/HAProxy）
    ↓
vLLM推理服务
├── GPU 0-1: LLM推理 (72B模型, Tensor Parallelism)
├── GPU 2: 视觉推理 (YOLOv8)
└── GPU 3: 冗余/训练

并发策略：
- vLLM支持连续批处理（Continuous Batching）可高效处理30并发
- LLM推理使用2卡通过Tensor Parallelism将72B模型分布在2张GPU上
- 视觉模型推理使用1卡YOLOv8推理速度快单卡可支撑较高并发
- 第4卡作为冗余当LLM并发高峰时可临时加入推理集群""")

    doc.add_page_break()

    # ===== 第五章 =====
    doc.add_heading('第五章 优先落地场景详细方案', level=1)

    doc.add_heading('5.1 场景一：文本纠错（优先级最高）', level=2)

    doc.add_heading('5.1.1 业务痛点', level=3)
    p = doc.add_paragraph()
    parse_inline_text(p, '体系管理手册（包括质量手册、程序文件、作业指导书等）基于体系管理文件（法规、国家标准、行业标准等）人工编写。由于编写人员对法规标准的掌握程度不一手册中可能存在以下错误：')

    error_types = [
        '引用错误：引用了不存在的法规或标准编号',
        '引用到错误的标准：标准编号正确但引用的内容与标准原文不符',
        '法规捏造：编造了不存在的法规名称或条款',
        '引用到错误的数据：引用的数值、参数与标准原文不一致',
        '语法错误：语句不通顺、表述不规范',
        '逻辑错误：前后矛盾、逻辑不自洽',
    ]
    for e in error_types:
        p = doc.add_paragraph(style='List Bullet')
        parse_inline_text(p, e, default_size=10.5)

    p = doc.add_paragraph()
    parse_inline_text(p, '目前这些错误完全依赖人工逐条核对效率低下且容易遗漏。')

    doc.add_heading('5.1.2 纠错类型详细定义', level=3)
    add_table(doc,
        ['纠错类型', '定义', '示例', '检测难度'],
        [
            ['引用错误', '引用的法规/标准编号不存在或已废止', '引用"GB/T 12345-2018"但该标准实际为"GB/T 12345-2019"', '低（知识库直接比对）'],
            ['标准引用错误', '标准编号正确但引用内容与原文不符', '标准要求"≥10MPa"手册写成">10MPa"', '中（需语义比对）'],
            ['法规捏造', '引用了完全不存在的法规', '引用"《锅炉安全管理条例》"但该法规不存在', '低（知识库查证）'],
            ['数据错误', '引用的数值、参数与原文不一致', '标准规定"壁厚不小于12mm"手册写成"壁厚不小于10mm"', '中（需数值比对）'],
            ['语法错误', '语句不通顺、表述不规范', '"锅炉的应该进行水压试验"（缺少主语）', '低（LLM擅长）'],
            ['逻辑错误', '前后矛盾、逻辑不自洽', '前文说"采用一级探伤"后文要求"按二级探伤标准执行"', '高（需上下文理解）'],
        ],
        col_widths=[2.5, 3.5, 3.5, 3]
    )

    doc.add_heading('5.1.3 技术实现方案', level=3)

    p = doc.add_paragraph()
    add_formatted_run(p, '知识库构建：', bold=True, size=10.5)

    add_code_block(doc, """知识库架构：
├── 法规库
│   ├── 《特种设备安全法》
│   ├── 《锅炉安全技术规程》(TSG 11-2020)
│   ├── 《固定式压力容器安全技术监察规程》
│   └── ... (持续扩充)
├── 国标库
│   ├── GB/T 16507-2013 水管锅炉
│   ├── GB/T 16508-2013 锅壳锅炉
│   ├── NB/T 47014-2011 承压设备焊接工艺评定
│   └── ... (持续扩充)
├── 行业标准库
│   ├── JB/T 相关标准
│   └── ... (持续扩充)
└── 企业标准库
    ├── 质量管理手册
    ├── 程序文件
    ├── 作业指导书
    └── ... (持续扩充)""")

    p = doc.add_paragraph()
    add_formatted_run(p, '文档导入与结构化流程：', bold=True, size=10.5)

    import_steps = [
        '文档上传：支持PDF、Word、WPS等格式批量上传',
        '文档解析：自动识别文档类型（法规、国标、企业标准等）；提取文档元数据（编号、版本、发布日期、实施日期等）；识别文档结构（章节、条款、附录等）',
        '文档分段：按条款/段落进行语义分段每段保留完整的语义上下文',
        '向量化索引：使用BGE-M3模型将每段文本转换为向量存入Milvus',
        '元数据索引：同时建立标准编号、法规名称等结构化索引支持精确检索',
    ]
    for i, step in enumerate(import_steps, 1):
        p = doc.add_paragraph()
        parse_inline_text(p, f'{i}. {step}', default_size=10.5)

    p = doc.add_paragraph()
    add_formatted_run(p, 'RAG纠错流程：', bold=True, size=10.5)

    add_code_block(doc, """待纠错文档上传
    ↓
文档解析与分段
    ↓
逐段处理：
    ├── 提取该段中的引用信息（标准编号、法规名称、数值参数等）
    ├── 结构化检索：根据标准编号/法规名称精确检索知识库
    ├── 语义检索：根据段落内容语义检索相关标准条款
    ├── LLM比对分析：
    │   ├── 引用是否存在？
    │   ├── 引用内容是否与原文一致？
    │   ├── 数值参数是否正确？
    │   ├── 语法是否规范？
    │   └── 逻辑是否自洽？
    └── 输出纠错建议（附引用来源）
    ↓
纠错报告汇总
    ↓
人工审核确认""")

    p = doc.add_paragraph()
    add_formatted_run(p, '引用溯源机制：', bold=True, size=10.5)
    parse_inline_text(p, '每条纠错建议包含以下信息：')

    add_table(doc,
        ['字段', '说明'],
        [
            ['错误类型', '引用错误/标准引用错误/法规捏造/数据错误/语法错误/逻辑错误'],
            ['原文位置', '第X章第X节第X条'],
            ['原文内容', '手册中的原始表述'],
            ['纠错建议', '修正后的表述'],
            ['引用来源', '知识库中的原文出处（文档名+条款号）'],
            ['置信度', '高/中/低'],
        ],
        col_widths=[3, 9]
    )

    p = doc.add_paragraph()
    add_formatted_run(p, '知识库更新机制：', bold=True, size=10.5)

    kb_updates = [
        '法规/国标更新监控：定期（每月）检查国家标准化管理委员会、市场监管总局等官方渠道的标准更新。新标准发布后及时导入知识库。已废止标准标记为"已废止"并在纠错时提示"该标准已废止请引用最新版本"',
        '企业标准更新：企业标准修订发布后即时更新知识库。保留历史版本支持版本对比',
        '更新通知：知识库更新后自动通知总师办相关人员。对已纠错文档中引用了已更新标准的条款标记"需重新审核"',
    ]
    for u in kb_updates:
        p = doc.add_paragraph(style='List Bullet')
        parse_inline_text(p, u, default_size=10.5)

    doc.add_heading('5.1.4 预期效果与验收标准', level=3)
    add_table(doc,
        ['指标', '目标值', '说明'],
        [
            ['引用错误检出率', '≥95%', '对不存在的标准编号、已废止标准的检出'],
            ['法规捏造检出率', '≥98%', '对编造法规名称的检出'],
            ['数据错误检出率', '≥85%', '对数值参数与原文不一致的检出'],
            ['语法错误检出率', '≥90%', '对语句不通顺的检出'],
            ['逻辑错误检出率', '≥70%', '对前后矛盾的检出（难度最高）'],
            ['误报率', '≤15%', 'AI报告的错误中实际不是错误的比例'],
            ['处理速度', '≤5分钟/万字', '单份文档的纠错处理时间'],
            ['人工审核效率提升', '≥60%', '相比纯人工纠错节省的时间'],
        ],
        col_widths=[3.5, 2.5, 6.5]
    )

    p = doc.add_paragraph()
    add_formatted_run(p, '验收方式：', bold=True, size=10.5)
    p = doc.add_paragraph()
    parse_inline_text(p, '1. 准备50份已标注错误的测试文档（含各类型错误）\n2. AI系统对测试文档进行纠错\n3. 统计各类型错误的检出率、误报率\n4. 人工审核AI输出记录审核时间与纯人工纠错时间对比')

    # 5.2
    doc.add_heading('5.2 场景二：焊接质检（深度学习/CV）', level=2)

    doc.add_heading('5.2.1 业务痛点', level=3)
    welding_pains = [
        '焊接质检依赖持证质检员目视或借助放大镜检查效率有限',
        '不同质检员判断标准可能不一致存在主观性',
        '大批量生产时质检员工作负荷大可能遗漏缺陷',
        '质检记录需手动填写和录入MES系统工作量大',
    ]
    for wp in welding_pains:
        p = doc.add_paragraph(style='List Bullet')
        parse_inline_text(p, wp, default_size=10.5)

    doc.add_heading('5.2.2 技术实现方案', level=3)

    p = doc.add_paragraph()
    add_formatted_run(p, '数据采集与标注流程：', bold=True, size=10.5)

    add_code_block(doc, """1. 数据采集
   ├── 从现有质检记录中收集历史质检图片（含合格和不合格样本）
   ├── 在生产线上安装工业相机实时采集焊缝图片
   └── 收集X射线探伤底片（如已有数字化）

2. 数据标注
   ├── 由资深质检员对图片进行标注
   │   ├── 标注缺陷类型（裂纹、气孔、夹渣、未焊透、咬边等）
   │   ├── 标注缺陷位置（边界框）
   │   └── 标注严重程度（轻微/中等/严重）
   ├── 标注工具：LabelImg / CVAT / Roboflow
   └── 标注格式：YOLO格式（.txt）

3. 数据增强
   ├── 旋转、翻转、缩放
   ├── 亮度、对比度调整
   ├── 添加噪声（模拟不同拍摄条件）
   └── 目标：每类缺陷至少500张标注图片""")

    p = doc.add_paragraph()
    add_formatted_run(p, 'YOLOv8模型训练与迭代：', bold=True, size=10.5)

    add_code_block(doc, """1. 基础训练
   ├── 使用YOLOv8l（大模型）作为基础模型
   ├── 划分训练集/验证集/测试集（7:2:1）
   ├── 训练参数：epochs=300, batch=16, imgsz=640
   └── 输出：mAP@0.5、mAP@0.5:0.95等指标

2. 模型优化
   ├── 根据验证集结果调整超参数
   ├── 针对漏检率高的缺陷类型增加样本
   ├── 调整置信度阈值：降低阈值提高召回率（宁可误报不漏报）
   └── 反复迭代直到满足验收标准

3. 模型量化（可选）
   ├── 导出为ONNX格式
   ├── 使用TensorRT优化推理速度
   └── 在GPU上推理延迟<50ms/张""")

    p = doc.add_paragraph()
    add_formatted_run(p, '推理服务部署：', bold=True, size=10.5)

    add_code_block(doc, """工业相机拍摄焊缝图片
    ↓
图片上传至AI中台（通过MES接口或直接上传）
    ↓
YOLOv8推理服务检测缺陷
    ↓
输出检测结果：
├── 缺陷类型
├── 缺陷位置（边界框坐标）
├── 置信度
└── 整体判定建议（合格/待人工复核）
    ↓
结果回写MES系统
    ↓
若"待人工复核"→ 通知质检员现场确认""")

    p = doc.add_paragraph()
    add_formatted_run(p, '与MES质检流程集成：', bold=True, size=10.5)

    mes_steps = [
        'AI检测结果作为"初筛"结果写入MES质检记录',
        'AI判定"合格"的焊缝仍需质检员抽检确认（抽检比例可设定如10%）',
        'AI判定"待人工复核"的焊缝必须由质检员逐个确认',
        '质检员确认结果反馈到AI系统用于模型持续优化',
        '最终质检结论仍由持证质检员签字确认',
    ]
    for i, step in enumerate(mes_steps, 1):
        p = doc.add_paragraph()
        parse_inline_text(p, f'{i}. {step}', default_size=10.5)

    doc.add_heading('5.2.3 预期效果与验收标准', level=3)
    add_table(doc,
        ['指标', '目标值', '说明'],
        [
            ['缺陷召回率', '≥95%', '真实缺陷中被AI检出的比例（宁可误报不漏报）'],
            ['缺陷精确率', '≥80%', 'AI报告的缺陷中真实缺陷的比例'],
            ['推理速度', '≤100ms/张', '单张图片检测时间'],
            ['质检效率提升', '≥50%', '相比纯人工目视检测节省的时间'],
            ['质检一致性', '提升', '减少不同质检员之间的判断差异'],
        ],
        col_widths=[3.5, 2.5, 6.5]
    )

    p = doc.add_paragraph()
    add_formatted_run(p, '关于"100%检出"的诚实说明：', bold=True, size=10.5)

    honesty_items = [
        '任何视觉检测模型都无法保证100%的缺陷检出率',
        '微小缺陷（如微裂纹）在图像中可能不明显模型可能漏检',
        '罕见缺陷类型由于训练样本不足检出率可能较低',
        '推荐策略：将AI作为初筛工具配合人工抽检将漏检风险降至最低',
        '随着数据积累和模型迭代检出率会持续提升',
    ]
    for item in honesty_items:
        p = doc.add_paragraph(style='List Bullet')
        parse_inline_text(p, item, default_size=10.5)

    doc.add_page_break()

    # ===== 第六章 =====
    doc.add_heading('第六章 实施路线图', level=1)

    doc.add_heading('6.1 分期实施计划', level=2)

    doc.add_heading('一期（1-3月）：AI中台搭建 + 文本纠错场景落地', level=3)
    add_table(doc,
        ['阶段', '时间', '工作内容', '交付物'],
        [
            ['基础设施', '第1月', 'GPU服务器采购部署网络配置', '可用的GPU服务器环境'],
            ['平台搭建', '第1-2月', 'Wanwu二次开发部署vLLM推理服务知识库服务搭建', '可用的AI中台基础平台'],
            ['知识库构建', '第2月', '法规库、国标库、企业标准库导入', '文本纠错知识库'],
            ['文本纠错开发', '第2-3月', 'RAG纠错流程开发引用溯源机制纠错报告生成', '文本纠错Skill'],
            ['测试验收', '第3月', '测试文档纠错验收指标验证', '验收报告'],
        ],
        col_widths=[2.5, 2, 4.5, 3.5]
    )

    doc.add_heading('二期（4-6月）：焊接质检 + 更多部门知识库接入', level=3)
    add_table(doc,
        ['阶段', '时间', '工作内容', '交付物'],
        [
            ['数据准备', '第4月', '焊接质检图片采集与标注', '标注数据集'],
            ['模型训练', '第4-5月', 'YOLOv8模型训练与优化', '焊接质检模型'],
            ['质检系统集成', '第5月', '推理服务部署与MES对接', '焊接质检AI服务'],
            ['部门知识库', '第5-6月', '人力资源、采购、安环等部门知识库接入', '多部门AI助手'],
            ['测试验收', '第6月', '焊接质检验收各部门AI助手试用', '验收报告'],
        ],
        col_widths=[2.5, 2, 4.5, 3.5]
    )

    doc.add_heading('三期（7-12月）：设备参数推荐 + 跨部门工作流 + 移动端集成', level=3)
    add_table(doc,
        ['阶段', '时间', '工作内容', '交付物'],
        [
            ['参数推荐', '第7-8月', '工艺参数知识库构建参数推荐Skill开发', '参数推荐AI助手'],
            ['跨部门工作流', '第8-9月', '质检-制造、采购-财务等跨部门工作流', '跨部门自动化流程'],
            ['移动端集成', '第9-10月', '钉钉/微信小程序开发', '移动端AI助手'],
            ['系统深度对接', '第10-11月', 'ERP/MES/PLM深度数据对接', '数据互通'],
            ['持续优化', '第11-12月', '模型升级知识库扩充反馈迭代', '优化报告'],
        ],
        col_widths=[2.5, 2, 4.5, 3.5]
    )

    doc.add_heading('6.2 里程碑与交付物', level=2)
    add_table(doc,
        ['里程碑', '时间', '交付物', '验收标准'],
        [
            ['M1 基础设施就绪', '第1月', 'GPU服务器环境', '模型可加载推理'],
            ['M2 中台上线', '第2月', 'AI中台基础平台', '对话、知识库功能可用'],
            ['M3 文本纠错验收', '第3月', '文本纠错Skill', '各类型错误检出率达标'],
            ['M5 焊接质检验收', '第5月', '焊接质检模型', '缺陷召回率≥95%'],
            ['M6 多部门上线', '第6月', '多部门AI助手', '3个以上部门知识库可用'],
            ['M8 参数推荐上线', '第8月', '参数推荐助手', '推荐准确率≥85%'],
            ['M10 移动端上线', '第10月', '钉钉/微信小程序', '移动端可正常使用'],
            ['M12 全系统验收', '第12月', '完整AI化平台', '全部验收指标达标'],
        ],
        col_widths=[3, 2, 3.5, 4]
    )

    doc.add_heading('6.3 风险与应对措施', level=2)
    add_table(doc,
        ['风险', '概率', '影响', '应对措施'],
        [
            ['GPU服务器采购周期长', '高', '延误1-2月', '提前启动采购流程预留备选供应商'],
            ['焊接质检标注数据不足', '高', '模型精度不达标', '一期即开始数据采集引入半自动标注工具'],
            ['Wanwu二次开发工作量超预期', '中', '延期', '评估Dify/FastGPT等替代方案保留切换能力'],
            ['各系统API不开放', '中', '数据无法对接', '与供应商协商必要时采用数据库视图（只读）方案'],
            ['用户接受度低', '中', '推广困难', '加强培训设置AI使用激励机制'],
            ['模型幻觉导致严重错误', '低', '信任危机', '所有关键输出必须人工审核建立审核流程'],
            ['知识库更新不及时', '中', '纠错引用过期标准', '建立定期更新机制设置过期预警'],
        ],
        col_widths=[3.5, 1.5, 2.5, 5.5]
    )

    doc.add_page_break()

    # ===== 第七章 =====
    doc.add_heading('第七章 投资估算', level=1)

    doc.add_heading('7.1 硬件采购估算', level=2)
    add_table(doc,
        ['项目', '规格', '数量', '单价（万元）', '小计（万元）'],
        [
            ['GPU服务器', '4×A800 80GB 512GB内存', '1台', '80-100', '80-100'],
            ['应用服务器', '双路Xeon 256GB内存', '2台', '3-5', '6-10'],
            ['存储扩容', 'NAS/SAN 20TB可用', '1套', '5-10', '5-10'],
            ['网络设备', '25GbE交换机+防火墙', '1套', '3-5', '3-5'],
            ['机房改造', '电力扩容+空调', '-', '5-15', '5-15'],
            ['硬件小计', '', '', '', '99-140'],
        ],
        col_widths=[2.5, 3.5, 1.5, 2.5, 2.5]
    )

    doc.add_heading('7.2 软件开发/集成估算', level=2)
    add_table(doc,
        ['项目', '工作量（人月）', '单价（万元/人月）', '小计（万元）'],
        [
            ['AI中台搭建与Wanwu二次开发', '6-8', '3-4', '18-32'],
            ['文本纠错场景开发', '3-4', '3-4', '9-16'],
            ['焊接质检场景开发', '4-6', '3-4', '12-24'],
            ['系统集成（ERP/MES/PLM/WPS）', '4-6', '3-4', '12-24'],
            ['移动端开发', '2-3', '3-4', '6-12'],
            ['测试与部署', '3-4', '2-3', '6-12'],
            ['项目管理', '3-4', '2-3', '6-12'],
            ['软件小计', '', '', '69-132'],
        ],
        col_widths=[4, 2.5, 3, 3]
    )

    doc.add_heading('7.3 年度运维估算', level=2)
    add_table(doc,
        ['项目', '年费用（万元）', '说明'],
        [
            ['电费', '8-12', 'GPU服务器7×24运行'],
            ['运维人力', '15-25', '1-2名AI运维工程师'],
            ['模型升级', '3-5', '年度模型版本更新'],
            ['知识库维护', '2-5', '法规标准更新、数据标注'],
            ['硬件维保', '3-5', 'GPU服务器维保'],
            ['年度运维小计', '31-52', ''],
        ],
        col_widths=[3.5, 3, 6.5]
    )

    doc.add_heading('7.4 总投资汇总', level=2)
    add_table(doc,
        ['类别', '金额（万元）'],
        [
            ['硬件采购（一次性）', '99-140'],
            ['软件开发（一次性）', '69-132'],
            ['首年总投入', '168-272'],
            ['年度运维（每年）', '31-52'],
        ],
        col_widths=[5, 4]
    )

    p = doc.add_paragraph()
    parse_inline_text(p, '以上为粗略估算实际金额需根据招标结果和详细需求分析确定。建议预留15-20%的应急预算。')

    doc.add_page_break()

    # ===== 第八章 =====
    doc.add_heading('第八章 总结与建议', level=1)

    doc.add_heading('8.1 核心结论', level=2)
    conclusions = [
        'AI化改造可行：当前AI技术（LLM + 知识库 + 视觉模型）已具备在锅炉制造企业落地的成熟度但需明确能力边界合理设定期望',
        'LLM + 知识库是最佳架构：多部门、多需求、需权限隔离的场景下训练专属大模型不可行LLM + 知识库 + Skill + 工作流是最佳适配方案',
        '私有化部署是必选项：国企数据安全底线不可突破必须私有化部署需新采购GPU服务器',
        'AI是辅助不是替代：尤其在涉及安全、质量、法规的场景AI输出必须经人工审核不能替代人工决策',
        '幻觉无法100%消除：但可通过RAG + 引用溯源 + 人工审核将错误率控制在可接受范围',
        '文本纠错应优先落地：技术成熟、价值明确、风险可控是最佳的切入点',
        '焊接质检可行但需数据积累：模型精度依赖标注数据量建议一期即开始数据采集',
    ]
    for i, c in enumerate(conclusions, 1):
        p = doc.add_paragraph()
        parse_inline_text(p, f'{i}. {c}', default_size=10.5)

    doc.add_heading('8.2 给领导的建议', level=2)
    suggestions = [
        '合理设定期望：AI不是万能的需要给团队和用户正确的预期。AI是"智能助手"而非"智能替代"',
        '重视数据基础：AI的效果很大程度上取决于数据质量。建议同步推进数据治理和标准化工作',
        '分步投入降低风险：采用分期实施策略一期投入验证效果后再决定后续投入规模',
        '培养AI人才：建议培养1-2名企业内部AI运维工程师确保系统长期可持续运行',
        '建立审核机制：在制度层面明确AI输出的审核流程和责任归属避免AI输出直接用于关键决策',
        '持续迭代：AI系统不是一次性建设项目需要持续的知识库更新、模型优化和场景扩展建议纳入年度信息化预算',
    ]
    for i, s in enumerate(suggestions, 1):
        p = doc.add_paragraph()
        parse_inline_text(p, f'{i}. {s}', default_size=10.5)

    doc.add_heading('8.3 下一步行动', level=2)
    add_table(doc,
        ['序号', '行动项', '责任方', '时间'],
        [
            ['1', '成立AI化项目组明确项目组织架构', '公司办/总师办', '立即'],
            ['2', '启动GPU服务器采购流程', '信息化部门', '立即'],
            ['3', '评估Wanwu/Dify/FastGPT等平台选择基础平台', '信息化部门', '第1月'],
            ['4', '收集法规、国标、企业标准等文档启动知识库建设', '总师办', '第1月'],
            ['5', '同步启动焊接质检图片采集与标注', '质检部门', '第1月'],
            ['6', '制定AI使用规范和审核流程', '总师办/安环', '第2月'],
            ['7', '一期开发与验收', '项目组', '第1-3月'],
        ],
        col_widths=[1.5, 5, 3, 2.5]
    )

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    parse_inline_text(p, '本方案基于当前AI技术发展水平编写随着技术进步部分能力边界可能发生变化建议每年评估更新。', default_size=9)

    output_path = '/workspace/锅炉制造企业AI化可行性分析及实施方案.docx'
    doc.save(output_path)
    print(f'Document saved to: {output_path}')


if __name__ == '__main__':
    build_document()
