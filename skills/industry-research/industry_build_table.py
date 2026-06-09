# -*- coding: utf-8 -*-
"""
industry_build_table.py - industry-research 7.1 财务对比表生成器

输入:
  --input  industry_data.py 输出的 JSON (含 1-14 列数据)
  --business 业务描述 JSON: {code6: "一句话业务描述", ...} (用于第 15 列, 可选)
输出: 7.1 表 markdown (15 列固定, 对齐 industry-research/SKILL.md 7.1 表定义)

用法:
  # 1. 跑 industry_data.py 拉 1-14 列
  python industry_data.py --input industry_input.txt --out industry_data.json

  # 2. Agent 联网整理第 15 列业务描述, 存为 ccl_business.json
  #    格式: {"600183": "覆铜板和粘结片 (CCL 高速料) + 印制线路板", ...}

  # 3. 跑 build_table 生成 7.1 表
  python industry_build_table.py --input industry_data.json --business ccl_business.json --out ccl_7_1.md

数据列 (15 列固定, 对齐 PCB golden template 7.1 章节):
  1  公司
  2  2025 收入(亿)
  3  25A 同比
  4  25A 归母净(亿)
  5  25A 同比
  6  毛利率
  7  净利率
  8  研发费用率
  9  管理费用率
  10 销售费用率
  11 当前总市值(亿)
  12 26E 前向 PE
  13 净利 CAGR (3Y/2Y/1Y, 按拉到几年预测算几何平均)
  14 26E PEG
  15 主营业务/收入占比   (Agent 联网整理, 一句话业务描述)
"""
import argparse
import json
import os


def fmt(v, suffix=''):
    """数值格式化: 数字按 suffix 加单位, None 显示「不可算」"""
    if v is None:
        return '不可算'
    if isinstance(v, str):
        return v
    if isinstance(v, (int, float)):
        if suffix == '%':
            return f"{v:.2f}%"
        if suffix == 'x':
            return f"{v:.1f}x"
        return f"{v:.2f}"
    return str(v)


def fmt_cagr(cagr_pct, cagr_years):
    """CAGR 格式化: 带年数标注
      - 3 年 CAGR: 47.30%
      - 2 年 CAGR: 35.20% (2Y)
      - 1 年同比: 55.50% (单年同比)
      - 不可算:   不可算
    """
    if cagr_pct is None or cagr_years == 0:
        return '不可算'
    base = f"{cagr_pct:.2f}%"
    if cagr_years == 1:
        return f"{base} (单年同比)"
    if cagr_years == 2:
        return f"{base} (2Y)"
    if cagr_years == 3:
        return base
    return base  # fallback


def get_peg(r):
    """PEG 升序, None 排最后"""
    p = r.get('peg_26e')
    if p is None:
        return 9999
    return p


def load_business(path):
    """加载业务描述 dict {code6: str}, 文件不存在或解析失败返回空 dict"""
    if not path or not os.path.exists(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARN] business JSON 解析失败: {e}", flush=True)
        return {}


def render_md(data, business):
    lines = []
    lines.append('| 公司 | 2025 收入(亿) | 25A 同比 | 25A 归母净(亿) | 25A 同比 | 毛利率 | 净利率 | 研发费用率 | 管理费用率 | 销售费用率 | 当前总市值(亿) | 26E 前向 PE | 净利 CAGR | 26E PEG | 主营业务/收入占比 |')
    lines.append('|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|')

    for r in data:
        # 公司名: 优先用 r["name"] (腾讯拉到的), 兜底 r["name_zh"]
        name = r.get('name') or r.get('name_zh') or r.get('code')
        code = r.get('code')
        biz = business.get(code, '待补')
        row = '| ' + ' | '.join([
            name,
            fmt(r.get('rev_25a_yi')),
            fmt(r.get('rev_25a_yoy_pct'), '%'),
            fmt(r.get('np_25a_yi')),
            fmt(r.get('np_25a_yoy_pct'), '%'),
            fmt(r.get('gm_25a_pct'), '%'),
            fmt(r.get('nm_25a_pct'), '%'),
            fmt(r.get('rd_rate_25a_pct'), '%'),
            fmt(r.get('mgmt_rate_25a_pct'), '%'),
            fmt(r.get('sale_rate_25a_pct'), '%'),
            fmt(r.get('mcap_yi')),
            fmt(r.get('fwd_pe_26e'), 'x'),
            fmt_cagr(r.get('cagr_pct'), r.get('cagr_years')),
            fmt(r.get('peg_26e')),
            biz,
        ]) + ' |'
        lines.append(row)
    return '\n'.join(lines) + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True, help='industry_data.py 输出 JSON 路径')
    ap.add_argument('--business', help='第 15 列业务描述 JSON 路径, 可选', default=None)
    ap.add_argument('--out', required=True, help='输出 markdown 路径')
    args = ap.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)

    business = load_business(args.business)

    # 按 PEG 升序排, None 排最后
    data_sorted = sorted(data, key=get_peg)

    md = render_md(data_sorted, business)

    with open(args.out, 'w', encoding='utf-8') as f:
        f.write(md)

    # 同时 stdout 输出, 方便 agent 立刻看到
    print(md)
    print(f'[done] wrote {args.out}, {len(data)} 家公司, 第 15 列 {len(business)} 条业务描述')


if __name__ == '__main__':
    main()
