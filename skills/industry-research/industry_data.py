# -*- coding: utf-8 -*-
"""
industry_data.py - industry-research 行业研究 agent

输入: industry_input.txt (每行 code name_zh, # 开头的行为注释)
拉取: 7.1 表 1-14 列数据 (财务 + 估值 + 一致预期 + PEG)
输出: JSON 文件 (给 industry_build_table.py 用)

数据源 (复用 investor-harness/skills/company-analysis/data_agent.py + 腾讯 qt.gtimg.cn 行情):
  - 25A 财务:           data_agent.fetch_annuals_akshare  (akshare 东方财富年度利润表)
  - 26E-28E 一致预期:   data_agent.fetch_market_akshare   (akshare 同花顺盈利预测)
  - 卖方样本数:         akshare.stock_profit_forecast_ths (直接拉原始 df, len() 出数量)
  - 行情/总市值:        腾讯 qt.gtimg.cn (雪球 token 失效 + 东方财富 push2 被代理拦时唯一可用)

第 15 列 (主营业务/收入占比) 不在这里拉, 由 Agent 联网搜索 + 业务筛选后手工整理
(对齐 PCB golden template 7.1 章节格式: "PCB/FPC+AI PCB, 光模块新增 14.81 亿" 这种一句话描述)

用法:
  python industry_data.py --input industry_input.txt --out industry_data.json

依赖:
  - data_agent.py: ../company-analysis/data_agent.py
  - akshare, pandas, requests (走 urllib 内置)
"""
import os, sys, json, argparse, time, urllib.request
import warnings
warnings.filterwarnings("ignore")

DATA_AGENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "company-analysis"))
sys.path.insert(0, DATA_AGENT_DIR)

try:
    from data_agent import (
        fetch_market_akshare,
        fetch_annuals_akshare,
    )
except ImportError as e:
    print(f"[FATAL] 无法 import data_agent: {e}", file=sys.stderr)
    sys.exit(1)

import akshare as ak


# ============================================================
# 行情 (用腾讯 qt.gtimg.cn, 含总市值, 不被代理拦)
# ============================================================
def get_quote_tencent(code6):
    """腾讯 qt.gtimg.cn 拉单股行情
    沪市: sh600183  深市: sz002636
    返回: {price, prev_close, open, high, low, change_pct, pe_ttm,
           mcap_yi (亿元), float_mcap_yi (亿元), turnover_pct, name}
    """
    prefix = "sh" if code6.startswith("6") else "sz"
    url = f"http://qt.gtimg.cn/q={prefix}{code6}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        data = resp.read().decode("gbk")
        if chr(34) not in data:
            return None
        parts = data.split(chr(34))[1].split("~")
        if len(parts) < 50:
            return None
        return {
            "name": parts[1],
            "price": float(parts[3]) if parts[3] else None,
            "prev_close": float(parts[4]) if parts[4] else None,
            "open": float(parts[5]) if parts[5] else None,
            "high": float(parts[33]) if parts[33] else None,
            "low": float(parts[34]) if parts[34] else None,
            "change_pct": float(parts[32]) if parts[32] else None,
            "turnover_pct": float(parts[38]) if parts[38] else None,
            "pe_ttm": float(parts[39]) if parts[39] else None,
            "mcap_yi": float(parts[44]) if parts[44] else None,
            "float_mcap_yi": float(parts[45]) if parts[45] else None,
        }
    except Exception as e:
        print(f"[WARN] tencent quote fail {code6}: {e}", file=sys.stderr)
        return None


def get_quotes_batch(codes):
    """批量拉行情 (一次 HTTP 请求拉多只, 腾讯支持逗号分隔)"""
    codes_param = ",".join(
        ("sh" if c.startswith("6") else "sz") + c for c in codes
    )
    url = f"http://qt.gtimg.cn/q={codes_param}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=15)
        data = resp.read().decode("gbk")
        results = {}
        # 响应是多行, 每行一个股票
        for line in data.strip().split(";"):
            if chr(34) not in line:
                continue
            inner = line.split(chr(34))[1]
            parts = inner.split("~")
            if len(parts) < 50:
                continue
            code6 = parts[2]
            results[code6] = {
                "name": parts[1],
                "price": float(parts[3]) if parts[3] else None,
                "prev_close": float(parts[4]) if parts[4] else None,
                "open": float(parts[5]) if parts[5] else None,
                "high": float(parts[33]) if parts[33] else None,
                "low": float(parts[34]) if parts[34] else None,
                "change_pct": float(parts[32]) if parts[32] else None,
                "turnover_pct": float(parts[38]) if parts[38] else None,
                "pe_ttm": float(parts[39]) if parts[39] else None,
                "mcap_yi": float(parts[44]) if parts[44] else None,
                "float_mcap_yi": float(parts[45]) if parts[45] else None,
            }
        return results
    except Exception as e:
        print(f"[WARN] tencent batch quote fail: {e}", file=sys.stderr)
        return {}


# ============================================================
# 卖方样本数 (akshare stock_profit_forecast_ths 原始 df)
# ============================================================
def get_consensus_with_count(code6):
    """调 akshare 同花顺盈利预测 (业绩预测详表-详细指标预测), 拿卖方样本数 (n_reports_26e)
    + 二次校准 26E/27E/28E 净利润中值

    返回: {np_26e_yi, np_27e_yi, np_28e_yi, n_reports_26e}
    """
    out = {"np_26e_yi": None, "np_27e_yi": None, "np_28e_yi": None, "n_reports_26e": 0}
    try:
        df = ak.stock_profit_forecast_ths(symbol=code6, indicator="业绩预测详表-详细指标预测")
        if df is None or df.empty:
            return out
        col26 = next((c for c in df.columns if "预测2026" in str(c) and "平均" in str(c)), None)
        if col26:
            out["n_reports_26e"] = int(df[col26].notna().sum())
        for year, k_dst in [(2026, "np_26e_yi"), (2027, "np_27e_yi"), (2028, "np_28e_yi")]:
            col = next((c for c in df.columns if f"预测{year}" in str(c) and "平均" in str(c)), None)
            if not col:
                continue
            sub = df[col].dropna()
            sub = sub[sub > 0]
            if len(sub) == 0:
                continue
            avg_yuan = sub.mean()
            out[k_dst] = round(float(avg_yuan) / 1e8, 2)
    except Exception as e:
        print(f"    [WARN] consensus_with_count fail {code6}: {e}", file=sys.stderr)
    return out


# ============================================================
# PEG 派生
# ============================================================
def calc_cagr(np_25a, np_26e, np_27e=None, np_28e=None):
    """按拉到的预测段数算几何平均 CAGR (用户原话: 有几年算几年)
    返回: (cagr_pct, years) 或 (None, 0)

    规则:
      - 26E 必须有 (一致预期必有), 25A 一般都有
      - 27E + 28E 都有 -> 3 年 CAGR: (28E/25A)^(1/3) - 1
      - 只有 27E, 没有 28E -> 2 年 CAGR: (27E/25A)^(1/2) - 1
      - 27E 也没有 -> 单年同比: 26E/25A - 1 (标 (单年同比))
      - 26E 或 25A 缺失 -> 不可算
    """
    if not np_25a or np_25a <= 0 or not np_26e or np_26e <= 0:
        return None, 0
    if np_27e and np_27e > 0 and np_28e and np_28e > 0:
        # 3 年
        cagr3 = (np_28e / np_25a) ** (1 / 3) - 1
        return cagr3 * 100, 3
    if np_27e and np_27e > 0:
        # 2 年 (有 27E, 没有 28E)
        cagr2 = (np_27e / np_25a) ** (1 / 2) - 1
        return cagr2 * 100, 2
    # 单年 (只有 26E)
    cagr1 = np_26e / np_25a - 1
    return cagr1 * 100, 1


def calc_peg(np_26e_yi, mcap_yi, np_25a_yi, np_27e_yi=None, np_28e_yi=None):
    """26E Forward PE + 按段数算的 CAGR + 26E PEG (传统 PEG = PE / G)

    返回: {fwd_pe_26e, cagr_pct, cagr_years, peg_26e}
      - cagr_years: 1 / 2 / 3 (实际算的年数, 0 = 不可算)
      - peg_26e: PE / CAGR, 不可算时 None
    """
    if not np_26e_yi or not mcap_yi or np_26e_yi <= 0:
        return {"fwd_pe_26e": None, "cagr_pct": None, "cagr_years": 0, "peg_26e": None}
    fwd_pe = mcap_yi / np_26e_yi
    cagr_pct, cagr_years = calc_cagr(np_25a_yi, np_26e_yi, np_27e_yi, np_28e_yi)
    peg = fwd_pe / cagr_pct if (cagr_pct is not None and cagr_pct > 0) else None
    return {
        "fwd_pe_26e": round(fwd_pe, 1),
        "cagr_pct": round(cagr_pct, 1) if cagr_pct is not None else None,
        "cagr_years": cagr_years,
        "peg_26e": round(peg, 2) if peg is not None else None,
    }


def with_suffix(code6):
    return code6 + ".SH" if code6.startswith("6") else code6 + ".SZ"


# ============================================================
# 处理单只
# ============================================================
def process_one(code6, name_zh, quote_dict):
    result = {"code": code6, "name_zh": name_zh, "code_with_suffix": with_suffix(code6)}

    # 1. 行情 (腾讯)
    q = quote_dict.get(code6, {})
    if q:
        for k, v in q.items():
            if v is not None:
                result[k] = v

    # 2. 25A 财务 (data_agent)
    try:
        annuals = fetch_annuals_akshare(with_suffix(code6), 2025, 2025)
        if annuals:
            a = annuals[-1]
            result["rev_25a_yi"] = a.get("rev")
            result["rev_25a_yoy_pct"] = a.get("rg")
            result["np_25a_yi"] = a.get("profit")
            result["np_25a_yoy_pct"] = a.get("pg")
            result["gm_25a_pct"] = a.get("gm")
            result["nm_25a_pct"] = a.get("nm")
            result["rd_rate_25a_pct"] = a.get("rdr")
            result["mgmt_rate_25a_pct"] = a.get("mar")
            result["sale_rate_25a_pct"] = a.get("ser")
    except Exception as e:
        print(f"[WARN] 25A fin fail {code6}: {e}", file=sys.stderr)

    # 3. 一致预期 (data_agent 主数据 + akshare 拿卖方样本数)
    try:
        market = fetch_market_akshare(with_suffix(code6))
        for k_src, k_dst in [("profit26", "np_26e_yi"), ("profit27", "np_27e_yi"), ("profit28", "np_28e_yi")]:
            if market.get(k_src):
                result[k_dst] = market[k_src]
        if market.get("fwd_pe") and not result.get("fwd_pe_26e"):
            result["fwd_pe_26e"] = market["fwd_pe"]
    except Exception as e:
        print(f"[WARN] consensus fail {code6}: {e}", file=sys.stderr)

    consensus_count = get_consensus_with_count(code6)
    result["n_reports_26e"] = consensus_count["n_reports_26e"]
    for k in ["np_26e_yi", "np_27e_yi", "np_28e_yi"]:
        if consensus_count.get(k) is not None:
            result[k] = consensus_count[k]

    # 4. PEG (传统 PEG = Forward PE / CAGR, CAGR 按段数算)
    peg = calc_peg(
        np_26e_yi=result.get("np_26e_yi"),
        mcap_yi=result.get("mcap_yi"),
        np_25a_yi=result.get("np_25a_yi"),
        np_27e_yi=result.get("np_27e_yi"),
        np_28e_yi=result.get("np_28e_yi"),
    )
    result.update(peg)

    return result


# ============================================================
# 主入口
# ============================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="industry_input.txt 路径")
    ap.add_argument("--out", required=True, help="输出 JSON 路径")
    args = ap.parse_args()

    codes = []
    with open(args.input, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(maxsplit=1)
            codes.append((parts[0], parts[1] if len(parts) > 1 else parts[0]))
    print(f"[info] {len(codes)} companies to process")

    # 一次性批量拉行情 (腾讯一次 HTTP 请求)
    print("[info] 批量拉行情 (腾讯 qt.gtimg.cn) ...", file=sys.stderr)
    quote_dict = get_quotes_batch([c for c, _ in codes])
    print(f"[info] 行情拉到 {len(quote_dict)} 只", file=sys.stderr)

    results = []
    for code6, name in codes:
        print(f"[info] processing {code6} {name} ...", file=sys.stderr)
        try:
            r = process_one(code6, name, quote_dict)
            results.append(r)
        except Exception as e:
            print(f"[error] {code6}: {e}", file=sys.stderr)
            results.append({"code": code6, "name_zh": name, "error": str(e)})
        time.sleep(0.3)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"[done] {len(results)} -> {args.out}")


if __name__ == "__main__":
    main()
