#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
zzg1_make_input.py - ZZG1 行业研究 zzg1_input.txt 自动生成器

用法：
  python zzg1_make_input.py --industry "印制电路板" --codes "002384,300476,..." --out zzg1_input.txt

数据源：Agent 用 cn-web-search / 浏览器搜索「<行业> A 股 头部 上市公司」等关键词后整理的 A 股代码列表
输出：zzg1_input.txt（每行 code name_zh）

公司池筛选规则（Agent 在调用本脚本前必须完成）：
  1. 只含 A 股上市（沪深主板/创业板/科创板/北交所），剔除港股/美股/未上市
  2. 只含行业本体公司，剔除上下游/材料/设备/概念股/代工配套
  3. 按总市值降序；有多少拿多少，上限 10 家（不要为凑数拉边缘公司）
"""
import argparse
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--industry', required=True, help='行业名，如 印制电路板 / 半导体设备 / 光模块')
    ap.add_argument('--keywords', default='', help='行业关键词，逗号分隔，用于在 input 头部注释')
    ap.add_argument('--top', type=int, default=10, help='取前 N 家（默认 10），实际按 --codes 传入的数量截断')
    ap.add_argument('--out', required=True, help='输出 zzg1_input.txt 路径')
    ap.add_argument('--codes', help='逗号分隔 A 股代码列表（Agent 联网搜索 + 业务筛选后整理）')
    ap.add_argument('--names', help='逗号分隔公司名（与 codes 对应，拼音或中文均可）')
    args = ap.parse_args()

    if not args.codes:
        print('ERROR: 必须通过 --codes 传入 A 股代码列表。', file=sys.stderr)
        print('代码列表由 Agent 联网搜索后整理，必须满足：', file=sys.stderr)
        print('  1. 只含 A 股上市（剔除港股/美股/未上市）', file=sys.stderr)
        print('  2. 只含行业本体（剔除上下游/材料/设备/概念股/代工配套）', file=sys.stderr)
        print('  3. 按总市值降序；有多少拿多少，上限 10 家', file=sys.stderr)
        sys.exit(1)

    codes = [c.strip() for c in args.codes.split(',') if c.strip()]
    if args.names:
        names = [n.strip() for n in args.names.split(',')]
    else:
        names = [''] * len(codes)
    if len(names) < len(codes):
        names += [''] * (len(codes) - len(names))

    # 有多少拿多少，超过 --top 才截断
    if len(codes) > args.top:
        print(f'[warn] 输入 {len(codes)} 家公司，超过 --top={args.top}，只取前 {args.top} 家', file=sys.stderr)
        codes = codes[:args.top]
        names = names[:args.top]

    with open(args.out, 'w', encoding='utf-8') as f:
        f.write(f'# ZZG1 行业研究 7.1 input\n')
        f.write(f'# 行业: {args.industry}\n')
        if args.keywords:
            f.write(f'# 关键词: {args.keywords}\n')
        f.write(f'# 共 {len(codes)} 家 A 股行业本体公司（已剔除港股/美股/上下游/材料/设备/概念股）\n')
        f.write(f'# 每行格式: code name_zh\n')
        for c, n in zip(codes, names):
            if n:
                f.write(f'{c} {n}\n')
            else:
                f.write(f'{c}\n')

    print(f'[done] {len(codes)} companies -> {args.out}', file=sys.stderr)


if __name__ == '__main__':
    main()
