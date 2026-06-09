# -*- coding: utf-8 -*-
'''
validate_report.py v1 - ZZG 报告质量闸门
- 检查 11 维度报告的章节、表格、关键论点数量
- 与潍柴动力黄金模板 (golden-report-template-weichai-000338.md) 对照
- 不通过时退出码非零，阻断上传

Usage: python validate_report.py <report_path>
'''
import os
import re
import sys

# 11 维度必须章节
REQUIRED_SECTIONS = [
    '一、市场数据',
    '二、财务分析',
    '三、核心投资逻辑',
    '四、行业分析',
    '五、商业模式、客户结构与护城河分析',
    '六、竞争格局与公司地位',
    '七、成长路径',
    '八、管理层与公司治理',
    '九、地缘风险与政策风险',
    '十、共识与分歧',
    '十一、综合评价',
]

# 财务分析下必有的子章节
REQUIRED_FINANCIAL_SECTIONS = [
    '1、年报',
    '2、季报',
    '3、产品拆分',
    '4、区域拆分',
]

# 共识与分歧下必有子章节
REQUIRED_CONSENSUS_SECTIONS = [
    '1. 市场共识',
    '2. 看多论点',
    '3. 看空论点',
    '4. 关键跟踪变量',
]

# 黄金模板章节顺序与质量下限（潍柴动力）
GOLDEN_TEMPLATE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'templates', 'golden-report-template-weichai-000338.md'
)
GOLDEN_MIN_LENGTH = 10000  # 黄金模板约 12K，新报告不得短于此
GOLDEN_MIN_LINES = 350     # 黄金模板约 400 行


def fail(reason):
    print('[FAIL] ' + reason)
    return False


def ok(reason):
    print('[OK]   ' + reason)
    return True


def count_bullish_points(content):
    '''计算看多论点数量 (形如 "1. xxx" 的编号项)'''
    sec_start = content.find('### 2. 看多论点')
    sec_end = content.find('### 3. 看空论点')
    if sec_start < 0 or sec_end < 0:
        return 0
    section = content[sec_start:sec_end]
    # 匹配 "数字. " 开头的行
    return len(re.findall(r'^\d+\.\s+', section, re.MULTILINE))


def count_bearish_points(content):
    sec_start = content.find('### 3. 看空论点')
    sec_end = content.find('### 4. 关键跟踪变量')
    if sec_start < 0 or sec_end < 0:
        # 尝试找 4. 关键跟踪变量 不存在的情况
        sec_end = content.find('## 十一', sec_start)
    if sec_start < 0 or sec_end < 0:
        return 0
    section = content[sec_start:sec_end]
    return len(re.findall(r'^\d+\.\s+', section, re.MULTILINE))


def count_table_rows(content, header_pattern):
    '''统计以 header_pattern 开头的表格行数 (含表头)'''
    return len(re.findall(r'^\|' + header_pattern, content, re.MULTILINE))


def validate(report_path):
    if not os.path.exists(report_path):
        return fail('报告文件不存在: ' + report_path)

    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()

    all_ok = True
    length = len(content)
    lines = content.count(chr(10))

    print()
    print('=' * 60)
    print('ZZG 报告质量闸门')
    print('=' * 60)
    print('  Path:', report_path)
    print('  Size:', length, 'chars /', lines, 'lines')
    print()

    # 1. 标题格式检查
    first_line = content.splitlines()[0] if content.splitlines() else ''
    if not re.match(r'^#\s+\S+（\S+）完整分析报告\s*$', first_line):
        all_ok &= fail(
            '首行 H1 标题格式错误: ' + first_line[:80] + chr(10) +
            '  期望: # {公司名}（{代码}）完整分析报告'
        )
    else:
        all_ok &= ok('首行 H1 标题格式正确')

    # 2. 11 维度章节
    for sec in REQUIRED_SECTIONS:
        if '## ' + sec not in content:
            all_ok &= fail('缺少章节: ' + sec)
    if all(s in content for s in REQUIRED_SECTIONS):
        all_ok &= ok('11 维度章节完整')

    # 3. 财务分析子章节
    for sub in REQUIRED_FINANCIAL_SECTIONS:
        if sub not in content:
            all_ok &= fail('财务分析缺少子章节: ' + sub)
    if all(s in content for s in REQUIRED_FINANCIAL_SECTIONS):
        all_ok &= ok('财务分析 4 个子章节完整 (年报/季报/产品/区域)')

    # 4. 共识与分歧子章节
    for sub in REQUIRED_CONSENSUS_SECTIONS:
        if sub not in content:
            all_ok &= fail('共识与分歧缺少子章节: ' + sub)
    if all(s in content for s in REQUIRED_CONSENSUS_SECTIONS):
        all_ok &= ok('共识与分歧 4 个子章节完整 (共识/看多/看空/跟踪变量)')

    # 5. 看多 / 看空 论点数量
    bull = count_bullish_points(content)
    bear = count_bearish_points(content)
    if bull < 5:
        all_ok &= fail('看多论点数不足: ' + str(bull) + ' < 5')
    else:
        all_ok &= ok('看多论点数: ' + str(bull))
    if bear < 5:
        all_ok &= fail('看空论点数不足: ' + str(bear) + ' < 5')
    else:
        all_ok &= ok('看空论点数: ' + str(bear))

    # 6. 数据来源说明
    if '数据来源与说明' not in content and '数据来源' not in content:
        all_ok &= fail('缺少 数据来源与说明 章节')
    else:
        all_ok &= ok('数据来源与说明 存在')

    # 7. 关键表格存在性
    annual_rows = count_table_rows(content, r'年份\|营收')
    quarter_rows = count_table_rows(content, r'季度\|营收')
    product_rows = count_table_rows(content, r'年份\|产品')
    region_rows = count_table_rows(content, r'年份\|地区')
    if annual_rows == 0:
        all_ok &= fail('缺少年报数据表 (含「年份|营收」表头)')
    else:
        all_ok &= ok('年报数据表存在 (行数: ' + str(annual_rows) + ')')
    if quarter_rows == 0:
        all_ok &= fail('缺少季报数据表')
    else:
        all_ok &= ok('季报数据表存在 (行数: ' + str(quarter_rows) + ')')
    if product_rows == 0:
        all_ok &= fail('缺少产品拆分表')
    else:
        all_ok &= ok('产品拆分表存在 (行数: ' + str(product_rows) + ')')
    if region_rows == 0:
        all_ok &= fail('缺少区域拆分表')
    else:
        all_ok &= ok('区域拆分表存在 (行数: ' + str(region_rows) + ')')

    # 8. 与黄金模板的长度对照
    if length < GOLDEN_MIN_LENGTH:
        all_ok &= fail(
            '报告总长度 ' + str(length) + ' 字符 < 黄金模板下限 ' + str(GOLDEN_MIN_LENGTH) + chr(10) +
            '  报告明显短于潍柴模板，需补充章节或论证'
        )
    else:
        all_ok &= ok('报告长度 ' + str(length) + ' >= 黄金模板下限 ' + str(GOLDEN_MIN_LENGTH))

    if lines < GOLDEN_MIN_LINES:
        all_ok &= fail('报告行数 ' + str(lines) + ' < 黄金模板下限 ' + str(GOLDEN_MIN_LINES))
    else:
        all_ok &= ok('报告行数 ' + str(lines) + ' >= 黄金模板下限 ' + str(GOLDEN_MIN_LINES))

    # 9. 黄金模板存在性检查
    if os.path.exists(GOLDEN_TEMPLATE_PATH):
        with open(GOLDEN_TEMPLATE_PATH, 'r', encoding='utf-8') as f:
            golden = f.read()
        ok('黄金模板存在: ' + os.path.basename(GOLDEN_TEMPLATE_PATH) +
           ' (' + str(len(golden)) + ' chars)')
    else:
        all_ok &= fail('黄金模板不存在: ' + GOLDEN_TEMPLATE_PATH)

    print()
    if all_ok:
        print('=' * 60)
        print('PASS - 报告通过质量闸门，可以上传 IMA')
        print('=' * 60)
        return True
    else:
        print('=' * 60)
        print('FAIL - 报告未通过质量闸门，禁止上传，请回 Step 4 重写')
        print('=' * 60)
        return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python validate_report.py <report_path>')
        sys.exit(2)
    ok = validate(sys.argv[1])
    sys.exit(0 if ok else 1)