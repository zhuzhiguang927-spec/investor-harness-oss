# -*- coding: utf-8 -*-
"""
data_agent.py v5 - 股票数据拉取 (全自动化版)
- akshare雪球个股行情 + 同花顺盈利预测获取市场数据
- akshare同花顺财务摘要获取季报单季度数据（累计相减，精确无误差）
- 东方财富F10 BusinessAnalysis API获取产品/区域/毛利率（替代搜索引擎）
- 支持 --search-data 接收Agent搜索结果(JSON)（兼容旧流程）
- 直接输出最终MD文件

用法1(akshare+东方财富): python data_agent.py 600519.SH 贵州茅台 --out 600519_data.md
用法2(带搜索):                  python data_agent.py 600519.SH 贵州茅台 --out 600519_data.md --search-data search.json

数据源:
- 模块0(市场数据): akshare雪球个股行情 + 同花顺盈利预测
- 模块1(年报): akshare 东方财富年度利润表
- 模块2(季报): akshare 同花顺财务摘要 (累计相减 → 单季度)
- 模块3(产品拆分): 东方财富F10 BusinessAnalysis API (TYPE=1)
- 模块4(区域拆分): 东方财富F10 BusinessAnalysis API (TYPE=3)

--search-data JSON格式:
{
  "products": [
    {"name":"茅台酒","rev":1465.00,"pct":86.77,"margin":93.53,"rev_yoy":0.39,"year":2025},
    {"name":"系列酒","rev":222.75,"pct":13.19,"margin":76.11,"rev_yoy":-9.76,"year":2025},
    {"name":"茅台酒","rev":1459.28,"pct":83.80,"margin":94.06,"year":2024},
    {"name":"系列酒","rev":246.84,"pct":14.47,"margin":79.87,"year":2024}
  ],
  "regions": [
    {"name":"国内","rev":1639.88,"pct":97.12,"rev_yoy":-2.94,"year":2025},
    {"name":"国外","rev":48.50,"pct":2.87,"rev_yoy":-6.53,"year":2025},
    {"name":"国内","rev":1689.55,"pct":97.02,"year":2024},
    {"name":"国外","rev":51.89,"pct":2.98,"year":2024}
  ],
  "margins": [
    {"name":"茅台酒","margin":93.53,"year":2025},
    {"name":"系列酒","margin":76.11,"year":2025}
  ]
}
"""
import os, sys, json, re, subprocess, argparse, time, urllib.request, urllib.parse
import requests as _requests
import akshare as ak
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

QUERY_SCRIPT_CANDIDATES = [
    os.getenv("NEODATA_QUERY_SCRIPT", ""),
    os.path.expanduser("~/skills/neodata-financial-search/scripts/query.py"),
    os.path.expanduser("~/.codex/skills/NeoData金融搜索服务/scripts/query.py"),
]
QUERY_SCRIPT = next((p for p in QUERY_SCRIPT_CANDIDATES if p and os.path.exists(p)), "")
TOKEN_FILE = os.path.expanduser(r"~\.workbuddy\.neodata_token")
TOKEN_TTL_SECONDS = 12 * 3600
_NEODATA_FAILURE_SHOWN = False

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

# ============== 工具函数 ==============
def yi(v):
    try: return round(float(v)/1e8, 2)
    except: return None

def sg(d, *k, df=None):
    for x in k:
        if isinstance(d, dict): d = d.get(x, df)
        else: return df
    return d

def _warn_neodata_once(message):
    global _NEODATA_FAILURE_SHOWN
    if not _NEODATA_FAILURE_SHOWN:
        print(f"    [WARN] {message}")
        _NEODATA_FAILURE_SHOWN = True


def _token_cache_status(tp):
    if not os.path.exists(tp):
        return "missing"
    try:
        raw = open(tp, "r", encoding="utf-8").read().strip()
        if not raw:
            return "empty"
        if not raw.startswith("{"):
            return "legacy"
        data = json.loads(raw)
        token = data.get("tempToken") or data.get("token")
        saved_at = data.get("saved_at")
        if not token:
            return "invalid"
        if saved_at and time.time() - float(saved_at) > TOKEN_TTL_SECONDS:
            return "expired"
        return "valid"
    except Exception:
        return "invalid"


def tok():
    tp = os.path.expanduser(TOKEN_FILE)
    status = _token_cache_status(tp)
    if status in ("valid", "legacy"):
        return True
    if not QUERY_SCRIPT:
        _warn_neodata_once("NeoData 查询脚本不存在，无法读取或保存 token。")
        return False
    try:
        from connect_cloud_service import connect_cloud_service as cc
        r = cc(); t = r.get("token","") if isinstance(r, dict) else ""
    except Exception:
        status_text = {
            "missing": "不存在",
            "empty": "为空",
            "expired": "已过期",
            "invalid": "无效",
        }.get(status, "不可用")
        _warn_neodata_once(
            "NeoData token 缓存" + status_text +
            "，且当前 Python 环境没有 connect_cloud_service；请在暴露该工具的宿主刷新，或用 query.py --save-token 写入新 token。"
        )
        return False
    if not t:
        _warn_neodata_once("connect_cloud_service 未返回 NeoData token。")
        return False
    os.makedirs(os.path.dirname(tp), exist_ok=True)
    saved = subprocess.run([sys.executable, QUERY_SCRIPT, "--save-token", t],
        env={**os.environ, "PYTHONIOENCODING": "utf-8"}, capture_output=True)
    if saved.returncode != 0:
        _warn_neodata_once("NeoData token 保存失败。")
        return False
    return True

def nq(q, dt="api"):
    if not QUERY_SCRIPT:
        _warn_neodata_once("NeoData 查询脚本不存在，跳过 NeoData 查询。")
        return []
    cmd = [sys.executable, QUERY_SCRIPT, "--query", q, "--data-type", dt]
    r = subprocess.run(cmd, capture_output=True, env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    if r.returncode != 0:
        err = r.stderr.decode("utf-8", errors="replace").strip().splitlines()
        detail = err[-1] if err else "查询脚本返回非零状态"
        _warn_neodata_once("NeoData 查询失败：" + detail)
        return []
    try: d = json.loads(r.stdout.decode("utf-8"))
    except: return []
    if d.get("code") != "200": return []
    return [{"type": i.get("type",""), "content": i.get("content","")}
            for i in sg(d, "data","apiData","apiRecall", df=[]) if i.get("content")]

def na(qq):
    r = []
    for q in qq: r.extend(nq(q))
    return r

def nq_retry(q, dt="api", retries=2):
    for attempt in range(retries + 1):
        try:
            result = nq(q, dt)
            if result: return result
        except: pass
        if attempt < retries: time.sleep(0.3)
    return []

# ============== 东方财富 BusinessAnalysis API ==============
# 数据源: 东方财富F10主营分析接口，返回结构化JSON（产品拆分+区域拆分+毛利率）
# TYPE=1: 按产品, TYPE=3: 按地区, 每年有半年报+年报两批数据

_EM_SESSION = _requests.Session()
_EM_SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': '*/*',
    'Referer': 'https://emweb.securities.eastmoney.com/',
})

_XQ_SESSION = _requests.Session()
_XQ_SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json,text/plain,*/*',
    'Referer': 'https://xueqiu.com/',
})

def _code_to_em(code):
    """股票代码转东方财富格式: 001339 -> SZ001339, 600519 -> SH600519, 600519.SH -> SH600519"""
    # 去掉已有的 .SH/.SZ 后缀
    code = code.replace('.SH', '').replace('.SZ', '')
    if code.startswith('6') or code.startswith('9'):
        return 'SH' + code
    return 'SZ' + code


def _float_or_none(v, digits=3):
    try:
        if v is None or pd.isna(v):
            return None
        text = str(v).strip().replace(",", "")
        if not text or text in ("-", "--"):
            return None
        return round(float(text), digits)
    except Exception:
        return None


def _forecast_yi(v):
    """把同花顺盈利预测的金额文本统一转成亿元。"""
    if v is None or pd.isna(v):
        return None
    text = str(v).strip().replace(",", "")
    m = re.search(r"(-?\d+(?:\.\d+)?)\s*(万亿|亿|万)?", text)
    if not m:
        return None
    amount = float(m.group(1))
    unit = m.group(2) or ""
    if unit == "万亿":
        amount *= 10000
    elif unit == "万":
        amount /= 10000
    elif unit != "亿":
        amount = yi(amount)
    return round(amount, 2)


def _fresh_xueqiu_token():
    try:
        r = _XQ_SESSION.get("https://xueqiu.com/", timeout=10)
        r.raise_for_status()
        return _XQ_SESSION.cookies.get("xq_a_token")
    except Exception:
        return None


def _fetch_xueqiu_spot_df(symbol):
    errors = []
    try:
        return ak.stock_individual_spot_xq(symbol=symbol, timeout=15), errors
    except Exception as e:
        errors.append(f"akshare内置token: {e}")

    token = _fresh_xueqiu_token()
    if token:
        try:
            return ak.stock_individual_spot_xq(symbol=symbol, token=token, timeout=15), errors
        except Exception as e:
            errors.append(f"akshare刷新token: {e}")
    else:
        errors.append("雪球token刷新失败")

    try:
        r = _XQ_SESSION.get(
            "https://stock.xueqiu.com/v5/stock/quote.json",
            params={"symbol": symbol, "extend": "detail"},
            headers={"Referer": f"https://xueqiu.com/S/{symbol}"},
            timeout=15,
        )
        data = r.json()
        quote = data.get("data", {}).get("quote")
        if not quote:
            raise ValueError(data.get("error_description") or data)
        field_map = {
            "current": "现价",
            "market_capital": "资产净值/总市值",
            "turnover_rate": "周转率",
            "pe_ttm": "市盈率(TTM)",
            "dividend_yield": "股息率(TTM)",
        }
        return pd.DataFrame(
            [{"item": label, "value": quote.get(key)} for key, label in field_map.items()]
        ), errors
    except Exception as e:
        errors.append(f"雪球直连接口: {e}")
        raise RuntimeError("; ".join(errors))


def fetch_market_akshare(code):
    """获取模板市场块字段: 实时行情来自雪球, 初始预测来自同花顺盈利预测。"""
    info = dict(price=None, tmcap=None, turnover=None, pe_ttm=None, dy=None,
                rev26=None, profit26=None, rev27=None, profit27=None,
                rev28=None, profit28=None,
                fwd_pe=None, fwd_ps=None)
    try:
        spot_df, spot_errors = _fetch_xueqiu_spot_df(_code_to_em(code))
        if spot_errors:
            print(f"    [INFO] 雪球行情已自动刷新token/兜底: {'; '.join(spot_errors)}")
        spot = dict(zip(spot_df["item"], spot_df["value"]))
        info["price"] = _float_or_none(spot.get("现价"), 2)
        info["tmcap"] = _yi_or_none(spot.get("资产净值/总市值"))
        info["turnover"] = _float_or_none(spot.get("周转率"), 2)
        info["pe_ttm"] = _float_or_none(spot.get("市盈率(TTM)"), 2)
        info["dy"] = _float_or_none(spot.get("股息率(TTM)"), 2)
    except Exception as e:
        print(f"    [WARN] akshare雪球个股行情失败: {e}")

    try:
        symbol = code.replace(".SH", "").replace(".SZ", "")
        fc_df = ak.stock_profit_forecast_ths(symbol=symbol, indicator="业绩预测详表-详细指标预测")
        if "预测指标" in fc_df.columns:
            rows = fc_df.set_index("预测指标")
            for year in (2026, 2027, 2028):
                forecast_col = next(
                    (c for c in fc_df.columns if f"预测{year}" in str(c) and "平均" in str(c)),
                    None,
                )
                if not forecast_col:
                    continue
                suffix = str(year)[-2:]
                if "营业收入(元)" in rows.index:
                    info[f"rev{suffix}"] = _forecast_yi(rows.at["营业收入(元)", forecast_col])
                if "净利润(元)" in rows.index:
                    info[f"profit{suffix}"] = _forecast_yi(rows.at["净利润(元)", forecast_col])
    except Exception as e:
        print(f"    [WARN] akshare同花顺盈利预测失败: {e}")

    if not info.get("rev26") or not info.get("profit26"):
        print("    [WARN] AkShare未返回完整2026E预测收入/利润；需联网补齐2026E后再计算Forward PE/PS。")
    if info.get("tmcap") and info.get("profit26") and info["profit26"] > 0:
        info["fwd_pe"] = round(info["tmcap"] / info["profit26"], 2)
    if info.get("tmcap") and info.get("rev26") and info["rev26"] > 0:
        info["fwd_ps"] = round(info["tmcap"] / info["rev26"], 2)
    return info

def fetch_eastmoney_business(code):
    """从东方财富F10获取产品拆分和区域拆分数据，返回 (products, regions, margins)"""
    em_code = _code_to_em(code)
    url = f"https://emweb.securities.eastmoney.com/PC_HSF10/BusinessAnalysis/PageAjax?code={em_code}"
    try:
        r = _EM_SESSION.get(url, timeout=15)
        data = r.json()
    except Exception as e:
        print(f"    [WARN] 东方财富API失败: {e}")
        return [], [], []

    records = data.get('zygcfx', [])
    if not records:
        return [], [], []

    # 按年份+类型分组
    # 过滤掉"其中:"前缀的子项（只保留合计项），只取年报数据（12-31）
    year_data = {}  # {year: {'products': [...], 'regions': [...]}}
    for rec in records:
        item_name = rec.get('ITEM_NAME', '')
        # 跳过"其中:"开头的子项
        if item_name.startswith('其中:'):
            continue
        # 只取年报数据（REPORT_DATE 含 12-31），跳过半年报（06-30）和中报（09-30）
        report_date = rec.get('REPORT_DATE', '')
        if '12-31' not in report_date:
            continue

        date_str = report_date[:4]
        try:
            year = int(date_str)
        except ValueError:
            continue
        op_type = rec['MAINOP_TYPE']
        bucket = year_data.setdefault(year, {'products': [], 'regions': []})

        rev_yi = rec['MAIN_BUSINESS_INCOME'] / 1e8
        pct = (rec['MBI_RATIO'] or 0) * 100
        margin = (rec['GROSS_RPOFIT_RATIO'] or 0) * 100

        if op_type == '1':
            bucket['products'].append({
                'name': item_name,
                'rev': round(rev_yi, 2),
                'pct': round(pct, 2),
                'margin': round(margin, 2),
                'year': year,
            })
        elif op_type == '3':
            bucket['regions'].append({
                'name': item_name,
                'rev': round(rev_yi, 2),
                'pct': round(pct, 2),
                'margin': round(margin, 2),
                'year': year,
            })

    # 汇总所有年份数据（已通过12-31过滤，无需再去重）
    products_all = []
    regions_all = []
    margins_all = []
    for year in sorted(year_data.keys()):
        prods = year_data[year]['products']
        regs = year_data[year]['regions']
        products_all.extend(prods)
        regions_all.extend(regs)
        for p in prods:
            margins_all.append({'name': p['name'], 'margin': p['margin'], 'year': year})

    return products_all, regions_all, margins_all

# 保留旧搜索函数作为 fallback（但不再主动使用）
def _clean_html(html):
    """清理HTML"""
    text = re.sub(r'<em[^>]*>(.*?)</em>', r'\1', html)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'&[a-zA-Z]+;', ' ', text)
    text = re.sub(r'&#\d+;', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def sogou_search(query, timeout=15):
    url = f"https://www.sogou.com/web?query={urllib.parse.quote(query)}"
    try:
        r = _SEARCH_SESSION.get(url, timeout=timeout)
        text = _clean_html(r.text)
        if len(text) < 500 or '验证' in text[:2000]: return ""
        return text[:20000]
    except: return ""

def web_search(query, timeout=15):
    text = sogou_search(query, timeout)
    if len(text.strip()) > 500: return text
    return ""

# ============== NeoData 解析函数 ==============
def fn(text, key):
    i = text.find(key)
    if i < 0:
        alt = key.replace("：", ":")
        i = text.find(alt)
    if i < 0: return None
    seg = text[i+len(key):]
    ns = 0
    while ns < len(seg):
        if seg[ns].isdigit() or seg[ns] in [".", "-", ","]: break
        ns += 1
    num = []
    for ch in seg[ns:ns+80]:
        if ch.isdigit() or ch in ".,-": num.append(ch)
        elif ch in "万亿元": break
        else: break
    if not num: return None
    s = "".join(num).replace(",", "")
    try: val = float(s)
    except: return None
    rest = seg[ns+len(num):ns+len(num)+10]
    if "亿" in rest: val *= 1e8
    elif "万" in rest: val *= 1e4
    return val

def fp(text, key):
    i = text.find(key)
    if i < 0:
        alt = key.replace("：", ":")
        i = text.find(alt)
    if i < 0: return None
    seg = text[i+len(key):]
    num = []
    for ch in seg[:80]:
        if ch.isdigit() or ch in ".-": num.append(ch)
        elif ch == "%": break
        elif num: break
    if not num: return None
    try: return float("".join(num))
    except: return None

# ============== 数据解析 ==============
def parse_market(contents):
    info = dict(price=None, tmcap=None, turnover=None, pe_ttm=None, dy=None,
                rev26=None, profit26=None, rev27=None, profit27=None,
                fwd_pe=None, fwd_ps=None)
    for c in contents:
        t, tx = c["type"], c["content"]
        if "实时行情" in t:
            info["price"] = fn(tx, "最新价格")
            info["tmcap"] = fn(tx, "总市值")
            info["turnover"] = fp(tx, "换手率")
            info["pe_ttm"] = fp(tx, "市盈率")
            info["dy"] = fp(tx, "股息率")
        elif "市场观点" in t:
            m = re.search(r"2026年.*?预测净利润[为\s]*([\d,\.]+)", tx)
            if m: info["profit26"] = yi(m.group(1).replace(",",""))
            m = re.search(r"2026年.*?预测营业收入[为\s]*([\d,\.]+)", tx)
            if m: info["rev26"] = yi(m.group(1).replace(",",""))
            m = re.search(r"2027年.*?预测净利润[为\s]*([\d,\.]+)", tx)
            if m: info["profit27"] = yi(m.group(1).replace(",",""))
            m = re.search(r"2027年.*?预测营业收入[为\s]*([\d,\.]+)", tx)
            if m: info["rev27"] = yi(m.group(1).replace(",",""))
    if info.get("tmcap") and info.get("profit26") and info["profit26"] > 0:
        info["fwd_pe"] = round(info["tmcap"] / info["profit26"], 2)
    if info.get("tmcap") and info.get("rev26") and info["rev26"] > 0:
        info["fwd_ps"] = round(info["tmcap"] / info["rev26"], 2)
    return info

def parse_annual(text, target_year=None):
    m = re.search(r"统计截止日期[^\d]*(\d{4})", text)
    yr = None
    if m:
        yr = int(m.group(1))
        rv = fn(text, "营业总收入") or fn(text, "营业收入")
        if rv is None: return None
        pr = fn(text, "归母净利润") or fn(text, "净利润")
        gm = fp(text, "销售毛利率")
        if gm is None:
            mao = fn(text, "销售毛利") or fn(text, "毛利")
            if mao and rv: gm = round(mao/rv*100, 2)
        nm = fp(text, "销售净利率")
        # 交叉校验：NeoData的"销售净利率"口径可能与"归母净利润"不一致
        # 当差异>1个百分点时，优先使用归母净利润/营收计算值
        if pr and rv:
            calc_nm = round(pr/rv*100, 2)
            if nm is None:
                nm = calc_nm
            elif abs(nm - calc_nm) > 1.0:
                nm = calc_nm
        se = fn(text, "销售费用"); ma = fn(text, "管理费用"); rd = fn(text, "研发费用") or 0
        ser = round(se/rv*100,2) if se and rv else None
        mar = round(ma/rv*100,2) if ma and rv else None
        rdr = round(rd/rv*100,2) if rd and rv else None
        rg = fp(text, "营业收入同比增长")
        pg = fp(text, "归母净利润同比增长")
        return dict(year=yr, rev=yi(rv), profit=yi(pr), rg=rg, pg=pg,
                    gm=gm, nm=nm, ser=ser, mar=mar, rdr=rdr)
    else:
        if target_year:
            pattern = rf"{target_year}年[，,\s]+营业总收入[^\d]*?([\d.,]+)\s*亿元"
            m = re.search(pattern, text)
            if m:
                rv = float(m.group(1).replace(",","")) * 1e8
                pattern2 = rf"{target_year}年[^\d]*?归母净利润[^\d]*?([\d.,]+)\s*亿元"
                m2 = re.search(pattern2, text)
                pr = float(m2.group(1).replace(",","")) * 1e8 if m2 else None
                return dict(year=target_year, rev=yi(rv), profit=yi(pr),
                           rg=None, pg=None, gm=None, nm=None, ser=None, mar=None, rdr=None)
    return None

def parse_quarter(text):
    """解析NeoData返回的季报数据（财务主要复合指标）— [已弃用, 保留作fallback]"""
    m = re.search(r"统计截止日期[^\d]*(\d{6})", text)
    if not m: return None
    yr, mo = int(m.group(1)[:4]), int(m.group(1)[4:])
    q = (mo-1)//3 + 1
    rv = None
    rv_m = re.search(r"营业(?:总)?收入(\d[\d,.]*)[万亿]?元", text)
    if rv_m:
        val = float(rv_m.group(1).replace(",", ""))
        rest = text[rv_m.start()+len(rv_m.group(0)):rv_m.start()+len(rv_m.group(0))+5]
        if "亿" in rv_m.group(0): val *= 1e8
        elif "万" in rv_m.group(0): val *= 1e4
        rv = val
    pr = None
    pr_m = re.search(r"归母净利润(\d[\d,.]*)[万亿]?元", text)
    if pr_m:
        val = float(pr_m.group(1).replace(",", ""))
        if "亿" in pr_m.group(0): val *= 1e8
        elif "万" in pr_m.group(0): val *= 1e4
        pr = val
    else:
        pr_m = re.search(r"扣非净利润(\d[\d,.]*)[万亿]?元", text)
        if pr_m:
            val = float(pr_m.group(1).replace(",", ""))
            if "亿" in pr_m.group(0): val *= 1e8
            elif "万" in pr_m.group(0): val *= 1e4
            pr = val
    if rv is None:
        nm = fp(text, "销售净利率")
        kui_fei_m = re.search(r"扣非净利润(\d[\d,.]*)[万亿]?元", text)
        kui_fei = float(kui_fei_m.group(1).replace(",", "")) if kui_fei_m else None
        if kui_fei and nm and nm > 0:
            if pr is None: pr = kui_fei
            rv = kui_fei / (nm / 100)
        else:
            mao_candidates = re.findall(r"(?:销售)?毛利(\d[\d,.]*)", text)
            mao_candidates = [float(v.replace(",", "")) for v in mao_candidates if float(v.replace(",", "")) > 0]
            mao = mao_candidates[0] if mao_candidates else None
            gm = fp(text, "销售毛利率")
            if mao and gm and gm > 0:
                rv = mao / (gm / 100)
    gm = fp(text, "销售毛利率")
    if gm is None:
        mao_candidates = re.findall(r"(?:销售)?毛利(\d[\d,.]*)", text)
        mao_candidates = [float(v.replace(",", "")) for v in mao_candidates if float(v.replace(",", "")) > 0]
        if mao_candidates and rv: gm = round(mao_candidates[0]/rv*100, 2)
    nm = fp(text, "销售净利率")
    if nm is None and pr and rv: nm = round(pr/rv*100, 2)
    return dict(label=f"{yr}Q{q}", year=yr, month=mo,
                rev=yi(rv), profit=yi(pr), gm=gm, nm=nm)

# ============== akshare 年报/季报 ==============
def _parse_ths_val(v):
    """将同花顺的 '12.34亿' 转为 12.34, '5678.90万' 转为 0.5679, '56.78%' 转为 56.78
    所有金额统一转为亿为单位。"""
    if pd.isna(v) or v is False or v == 'False':
        return None
    s = str(v).strip()
    if '亿' in s:
        try: return float(s.replace('亿', ''))
        except: return None
    if '万' in s:
        try: return round(float(s.replace('万', '')) / 10000, 4)
        except: return None
    if '%' in s:
        try: return float(s.replace('%', ''))
        except: return None
    try: return float(s)
    except: return None


def _rate_of(amount, base):
    if amount is None or base is None or pd.isna(amount) or pd.isna(base) or float(base) == 0:
        return None
    return round(float(amount) / float(base) * 100, 2)


def _yi_or_none(v):
    if v is None or pd.isna(v):
        return None
    return yi(v)


def fetch_annuals_akshare(code, start_year=2015, end_year=None):
    """
    通过 akshare 东方财富年度利润表获取年报数据。
    输出字段与原 NeoData 年报记录一致，供现有 Markdown 模板直接复用。
    """
    em_code = _code_to_em(code)
    try:
        df = ak.stock_profit_sheet_by_yearly_em(symbol=em_code)
    except Exception as e:
        print(f"    [WARN] akshare年度利润表失败: {e}")
        return []

    if df is None or df.empty:
        print("    [WARN] akshare年度利润表返回空数据")
        return []

    df = df.copy()
    df["_report_date"] = pd.to_datetime(df["REPORT_DATE"], errors="coerce")
    df["_year"] = df["_report_date"].dt.year
    if end_year is None:
        end_year = datetime.now().year
    df = df[(df["_year"] >= start_year) & (df["_year"] <= end_year)]
    df = df.dropna(subset=["_year", "TOTAL_OPERATE_INCOME"])
    df = df.sort_values("_year")

    results = []
    for _, row in df.iterrows():
        rev = row.get("TOTAL_OPERATE_INCOME")
        profit = row.get("PARENT_NETPROFIT")
        cost = row.get("OPERATE_COST")
        if pd.isna(rev):
            continue
        gm = None if pd.isna(cost) else round((float(rev) - float(cost)) / float(rev) * 100, 2)
        results.append(dict(
            year=int(row["_year"]),
            rev=_yi_or_none(rev),
            profit=_yi_or_none(profit),
            rg=None if pd.isna(row.get("TOTAL_OPERATE_INCOME_YOY")) else round(float(row.get("TOTAL_OPERATE_INCOME_YOY")), 2),
            pg=None if pd.isna(row.get("PARENT_NETPROFIT_YOY")) else round(float(row.get("PARENT_NETPROFIT_YOY")), 2),
            gm=gm,
            nm=_rate_of(profit, rev),
            ser=_rate_of(row.get("SALE_EXPENSE"), rev),
            mar=_rate_of(row.get("MANAGE_EXPENSE"), rev),
            rdr=_rate_of(row.get("RESEARCH_EXPENSE"), rev),
        ))
    return results[-11:]


def fetch_quarters_akshare(code):
    """
    通过 akshare 同花顺财务摘要获取季报数据。
    一次请求返回所有报告期（累计），然后计算单季度数据。
    关键: 同花顺累计值在每年Q1重置，所以跨年时Q1不减去上一年Q4。
    返回: list[dict]，按时间倒序（最新在前），每条含 label/year/month/rev/profit/gm/nm
    """
    # 去掉 .SH/.SZ 后缀，只保留纯数字代码
    pure_code = code.replace('.SH', '').replace('.SZ', '')
    try:
        df = ak.stock_financial_abstract_ths(symbol=pure_code, indicator='按报告期')
    except Exception as e:
        print(f"    [WARN] akshare同花顺财务摘要失败: {e}")
        return []

    if df is None or df.empty:
        print(f"    [WARN] akshare同花顺返回空数据")
        return []

    # 解析关键字段
    df['_rev'] = df['营业总收入'].apply(_parse_ths_val)
    df['_profit'] = df['净利润'].apply(_parse_ths_val)
    df['_gm'] = df['销售毛利率'].apply(_parse_ths_val)
    df['_nm'] = df['销售净利率'].apply(_parse_ths_val)

    # 只保留有营收数据的行
    df = df.dropna(subset=['_rev'])

    # 按报告期排序
    df = df.sort_values('报告期').reset_index(drop=True)

    # 累计相减得到单季度数据
    results = []
    prev_rev = 0
    prev_profit = 0
    prev_year = 0
    q_map = {'03-31': (1, 3), '06-30': (2, 6), '09-30': (3, 9), '12-31': (4, 12)}

    for _, row in df.iterrows():
        date_str = str(row['报告期'])  # e.g. '2024-09-30'
        mmdd = date_str[5:] if len(date_str) >= 10 else ''
        if mmdd not in q_map:
            continue
        q, month = q_map[mmdd]
        year = int(date_str[:4])

        # 跨年重置: Q1 是新年度的第一个报告期，累计值就是单季度值
        if year != prev_year:
            prev_rev = 0
            prev_profit = 0

        single_rev = round(row['_rev'] - prev_rev, 2)
        single_profit = round(row['_profit'] - prev_profit, 2) if row['_profit'] is not None else None
        gm = row['_gm']
        nm = round(single_profit / single_rev * 100, 2) if single_rev and single_profit and single_rev > 0 else row['_nm']

        results.append(dict(
            label=f"{year}Q{q}",
            year=year,
            month=month,
            rev=single_rev,
            profit=single_profit,
            gm=gm,
            nm=nm,
        ))

        prev_rev = row['_rev']
        prev_profit = row['_profit'] if row['_profit'] is not None else 0
        prev_year = year

    # 按时间倒序（最新在前），取最近12季
    results = sorted(results, key=lambda x: (x['year'], x['month']), reverse=True)[:12]
    return results

# ============== 产品/区域/毛利率提取（从东方财富API数据中筛选） ==============
def filter_by_years(items, years):
    """从items中筛选指定年份的数据"""
    return [i for i in items if i.get('year') in years]

def search_product_breakdown(name, year):
    """此函数保留兼容性，实际由 fetch_eastmoney_business 替代"""
    return []

def search_region_breakdown(name, year):
    """此函数保留兼容性，实际由 fetch_eastmoney_business 替代"""
    return []

def search_product_margins(name, year):
    """此函数保留兼容性，实际由 fetch_eastmoney_business 替代"""
    return []

# ============== 计算辅助 ==============
def calc_yoy(recs, key):
    for i in range(1, len(recs)):
        c, p = recs[i].get(key), recs[i-1].get(key)
        if c is not None and p and p != 0:
            recs[i][key+"_yoy"] = round((c-p)/p*100, 2)
    if recs: recs[0][key+"_yoy"] = None

def calc_qoq(recs):
    import math
    by = {}
    for r in recs: by.setdefault(r["year"],[]).append(r)
    for yr in sorted(by):
        if yr-1 not in by: continue
        cq = sorted(by[yr], key=lambda x: x["month"])
        pq = sorted(by[yr-1], key=lambda x: x["month"])
        cm = {q["month"]: q for q in cq}
        pm = {q["month"]: q for q in pq}
        for q in cq:
            m = q["month"]
            cur_rev = q.get("rev")
            prev_rev = pm[m].get("rev") if m in pm else None
            # 营收增速: 当期和同期都必须是有效数值
            if prev_rev and cur_rev and not math.isnan(cur_rev) and not math.isnan(prev_rev) and prev_rev != 0:
                q["rev_yoy"] = round((cur_rev - prev_rev) / prev_rev * 100, 2)
            # 净利润增速: 同理
            cur_p = q.get("profit")
            prev_p = pm[m].get("profit") if m in pm else None
            if prev_p and cur_p and not math.isnan(cur_p) and not math.isnan(prev_p) and prev_p != 0:
                q["profit_yoy"] = round((cur_p - prev_p) / prev_p * 100, 2)

# ============== NeoData 年报旧取数逻辑（保留解析兼容） ==============
def fetch_annual_year(name, yr):
    cs1 = nq_retry(f"{name} {yr}年报 营收 净利润 毛利率 净利率")
    cs2 = nq_retry(f"{name} {yr}年报 销售费用 管理费用 研发费用")
    best_r = None
    for c in cs1:
        r = parse_annual(c["content"], target_year=yr)
        if r and r.get("gm") is not None:
            best_r = r; break
        elif best_r is None and r:
            best_r = r
    if best_r is None:
        for c in cs2:
            r = parse_annual(c["content"], target_year=yr)
            if r: best_r = r; break
    fee_data = {}
    for c in cs2:
        text = c["content"]
        se = fn(text, "销售费用"); ma = fn(text, "管理费用"); rd = fn(text, "研发费用")
        if best_r and best_r.get("rev"):
            rv = best_r["rev"] * 1e8
            if se: fee_data["ser"] = round(se/rv*100, 2)
            if ma: fee_data["mar"] = round(ma/rv*100, 2)
            if rd: fee_data["rdr"] = round(rd/rv*100, 2)
    if best_r and fee_data:
        best_r.update(fee_data)
    return yr, best_r, cs1 + cs2  # 返回原始NeoData内容

def fetch_quarter_q(name, yr, q):
    """获取单季度数据 — [已弃用, 保留作fallback]"""
    q_name = {1: "一季度", 2: "二季度", 3: "三季度", 4: "四季度"}[q]
    queries = [
        f"{name} {yr}年{q_name}财报 营业总收入 净利润",
        f"{name} {yr}年{q_name}财报 营业收入 利润 毛利率",
        f"{name} {yr}年{q_name} 营收 净利润 毛利率 净利率",
    ]
    for query in queries:
        cs = nq_retry(query)
        for c in cs:
            r = parse_quarter(c["content"])
            if r and r.get("rev") and r["rev"] < 1000:
                return r
    return None

# ============== MD 输出 ==============
def fmt_num(v, suffix=""):
    if v is None: return "-"
    if isinstance(v, float):
        import math
        if math.isnan(v) or math.isinf(v): return "-"
        if abs(v) >= 100:
            return f"{v:,.0f}{suffix}"
        elif abs(v) >= 1:
            return f"{v:,.1f}{suffix}"
        else:
            return f"{v:.2f}{suffix}"
    return f"{v}{suffix}"

def build_md(code, name, mkt, ann, qrecs, prod_list, reg_list, margins):
    """
    生成最终MD报告，格式对齐 600519_data_v2.md 模板。
    只输出摘要表格，不输出原始接口内容。
    模板结构: 0市场数据 → 1年报(11年) → 2季报(12季) → 3产品拆分 → 4区域拆分 → [DATA_END]
    """
    lines = []
    lines.append(f"# {name}（{code}）- Data Agent")
    lines.append("[DATA_START]")

    # ===== 模块0: 市场数据 =====
    lines.append("## 0、市场数据")
    lines.append("|指标|值|")
    lines.append("|:---|---:|")
    mkt_map = [
        ("现价", "price", "元"),
        ("总市值", "tmcap", "亿元"),
        ("换手率", "turnover", "%"),
        ("市盈率TTM", "pe_ttm", ""),
        ("股息率", "dy", "%"),
        ("2026E预测收入", "rev26", "亿元"),
        ("2026E预测利润", "profit26", "亿元"),
        ("2027E预测收入", "rev27", "亿元"),
        ("2027E预测利润", "profit27", "亿元"),
        ("2028E预测收入", "rev28", "亿元"),
        ("2028E预测利润", "profit28", "亿元"),
        ("Forward PE", "fwd_pe", ""),
        ("Forward PS", "fwd_ps", ""),
    ]
    for label, key, unit in mkt_map:
        v = mkt.get(key)
        if key in {"rev27", "profit27", "rev28", "profit28"} and v is None:
            continue
        display = fmt_num(v)
        lines.append(f"|{label}|{display}{unit if display != '-' else ''}|")
    lines.append("")

    # ===== 模块1: 年报(近11年) =====
    lines.append("## 1、年报（近11年）")
    cols = ["年份","营收(亿)","增速","净利润(亿)","增速","净利率","毛利率","研发费用率","销售费用率","管理费用率"]
    lines.append("|" + "|".join(cols) + "|")
    lines.append("|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in ann[-11:]:
        row = [
            str(r["year"]),
            fmt_num(r.get("rev")),
            fmt_num(r.get("rev_yoy"), "%"),
            fmt_num(r.get("profit")),
            fmt_num(r.get("profit_yoy"), "%"),
            fmt_num(r.get("nm"), "%"),
            fmt_num(r.get("gm"), "%"),
            fmt_num(r.get("rdr"), "%"),
            fmt_num(r.get("ser"), "%"),
            fmt_num(r.get("mar"), "%"),
        ]
        lines.append("|" + "|".join(row) + "|")
    lines.append("")

    # ===== 模块2: 季报(12季) =====
    # 12季全输出营收/净利润/净利率/毛利率，增速只填最近8季
    lines.append("## 2、季报（近12季，单季度）")
    qcols = ["季度","营收(亿)","增速","净利润(亿)","增速","净利率","毛利率"]
    lines.append("|" + "|".join(qcols) + "|")
    lines.append("|:---|---:|---:|---:|---:|---:|---:|")
    for idx, r in enumerate(qrecs[:12]):
        # 前面8个季度有增速，后面4个季度增速为"-"
        if idx < 8:
            rev_yoy = fmt_num(r.get("rev_yoy"), "%")
            profit_yoy = fmt_num(r.get("profit_yoy"), "%")
        else:
            rev_yoy = "-"
            profit_yoy = "-"
        row = [
            r["label"],
            fmt_num(r.get("rev")),
            rev_yoy,
            fmt_num(r.get("profit")),
            profit_yoy,
            fmt_num(r.get("nm"), "%"),
            fmt_num(r.get("gm"), "%"),
        ]
        lines.append("|" + "|".join(row) + "|")
    lines.append("")

    # ===== 模块3: 产品拆分(近3年对照，含毛利率+同比) =====
    # 构建margin查找表: {(name, year): margin}
    margin_map = {}
    for m in margins:
        margin_map[(m.get("name"), m.get("year"))] = m.get("margin")

    # 合并product数据和margin数据到产品条目
    # 计算同比增速：仅当相邻两年分类科目名称完全一致时才计算
    all_years = sorted(set(p["year"] for p in prod_list), reverse=True)[:3]
    # 按年份排序的prod列表
    prod_by_year = {}
    for p in prod_list:
        prod_by_year.setdefault(p["year"], []).append(p)
    # 计算同比（仅在相邻两年科目名称集合完全一致时才计算）
    for yr in all_years:
        prev_yr = yr - 1
        if prev_yr in prod_by_year:
            cur_names = set(p["name"] for p in prod_by_year[yr])
            prev_names = set(p["name"] for p in prod_by_year[prev_yr])
            if cur_names == prev_names:
                # 科目完全一致，计算同比
                cur_items = {p["name"]: p for p in prod_by_year[yr]}
                prev_items = {p["name"]: p for p in prod_by_year[prev_yr]}
                for pname, cur in cur_items.items():
                    if prev_items[pname].get("rev") and cur.get("rev"):
                        cur["rev_yoy"] = round((cur["rev"] - prev_items[pname]["rev"]) / prev_items[pname]["rev"] * 100, 2)
            # 科目不一致时不计算增速，仅列数据

    if prod_list:
        lines.append("## 3、产品拆分（年报）")
        lines.append("|年份|产品|营收(亿)|占比|毛利率|同比增速|")
        lines.append("|:---|:---|---:|---:|---:|---:|")
        # 按年份倒序，每年内按营收倒序
        for yr in sorted(all_years, reverse=True):
            items = sorted(prod_by_year.get(yr, []), key=lambda x: x.get("rev", 0), reverse=True)
            for p in items:
                margin = p.get("margin") or margin_map.get((p["name"], yr))
                lines.append(f"|{yr}|{p['name']}|{fmt_num(p.get('rev'))}|{fmt_num(p.get('pct'), '%')}|{fmt_num(margin, '%')}|{fmt_num(p.get('rev_yoy'), '%')}|")
        lines.append("")
    else:
        lines.append("## 3、产品拆分（年报）")
        lines.append("|年份|产品|营收(亿)|占比|毛利率|同比增速|")
        lines.append("|:---|:---|---:|---:|---:|---:|")
        lines.append("|-|未获取到数据|-|-|-|-|")
        lines.append("")

    # ===== 模块4: 区域拆分(近3年对照，含同比) =====
    # 计算区域同比增速：仅当相邻两年分类科目名称完全一致时才计算
    reg_by_year = {}
    for r in reg_list:
        reg_by_year.setdefault(r["year"], []).append(r)
    all_reg_years = sorted(set(r["year"] for r in reg_list), reverse=True)[:3]
    for yr in all_reg_years:
        prev_yr = yr - 1
        if prev_yr in reg_by_year:
            cur_names = set(r["name"] for r in reg_by_year[yr])
            prev_names = set(r["name"] for r in reg_by_year[prev_yr])
            if cur_names == prev_names:
                # 科目完全一致，计算同比
                cur_items = {r["name"]: r for r in reg_by_year[yr]}
                prev_items = {r["name"]: r for r in reg_by_year[prev_yr]}
                for rname, cur in cur_items.items():
                    if prev_items[rname].get("rev") and cur.get("rev"):
                        cur["rev_yoy"] = round((cur["rev"] - prev_items[rname]["rev"]) / prev_items[rname]["rev"] * 100, 2)
            # 科目不一致时不计算增速，仅列数据

    if reg_list:
        lines.append("## 4、区域拆分（年报）")
        lines.append("|年份|地区|营收(亿)|占比|同比增速|")
        lines.append("|:---|:---|---:|---:|---:|")
        for yr in sorted(all_reg_years, reverse=True):
            items = sorted(reg_by_year.get(yr, []), key=lambda x: x.get("rev", 0), reverse=True)
            for r in items:
                lines.append(f"|{yr}|{r['name']}|{fmt_num(r.get('rev'))}|{fmt_num(r.get('pct'), '%')}|{fmt_num(r.get('rev_yoy'), '%')}|")
        lines.append("")
    else:
        lines.append("## 4、区域拆分（年报）")
        lines.append("|年份|地区|营收(亿)|占比|同比增速|")
        lines.append("|:---|:---|---:|---:|---:|")
        lines.append("|-|未获取到数据|-|-|-|")
        lines.append("")

    lines.append("[DATA_END]")
    return "\n".join(lines)

# ============== 季报同比增速表（独立模板输出） ==============
def build_quarter_yoy_table(qrecs, target_year=None):
    """
    生成指定年度的季报同比增速表（Q1~Q4），单季度口径。
    数据来源: fetch_quarters_akshare 返回的 qrecs（需已通过 calc_qoq 计算YoY）。
    
    输出格式:
    |季度|营收(亿)|营收增速|净利润(亿)|净利润增速|净利率|毛利率|
    |:---|---:|---:|---:|---:|---:|---:|
    |2025Q1|514.43|+10.66%|268.47|+11.56%|52.19%|92.11%|
    |...|...|...|...|...|...|...|
    
    参数:
        qrecs: list[dict], fetch_quarters_akshare + calc_qoq 后的结果
        target_year: int, 要输出的年份（默认取 qrecs 中最新年份）
    
    返回:
        str, Markdown 表格字符串（不含标题行，调用方自行添加 ## 标题）
    
    示例（2025年贵州茅台）:
        >>> # qrecs 来自 fetch_quarters_akshare("600519.SH")
        >>> # calc_qoq(qrecs)  # 计算YoY
        >>> print(build_quarter_yoy_table(qrecs, 2025))
        |季度|营收(亿)|营收增速|净利润(亿)|净利润增速|净利率|毛利率|
        |:---|---:|---:|---:|---:|---:|---:|
        |2025Q1|514.4|+10.66%|268.5|+11.56%|52.19%|92.11%|
        |2025Q2|396.5|+7.26%|185.6|+5.25%|46.80%|90.63%|
        |2025Q3|398.1|+0.35%|192.2|+0.48%|48.29%|91.44%|
        |2025Q4|411.5|-19.35%|176.9|-30.34%|43.00%|90.99%|
    """
    if not qrecs:
        return "> 暂无季报数据\n"
    
    # 确定目标年份
    if target_year is None:
        target_year = max(r.get("year", 0) for r in qrecs)
    
    # 筛选目标年份的季度数据，按 Q1~Q4 正序
    year_q = [r for r in qrecs if r.get("year") == target_year]
    year_q = sorted(year_q, key=lambda x: x.get("month", 0))
    
    if not year_q:
        return f"> {target_year}年暂无季报数据\n"
    
    # 构建表头
    lines = []
    lines.append("|季度|营收(亿)|营收增速|净利润(亿)|净利润增速|净利率|毛利率|")
    lines.append("|:---|---:|---:|---:|---:|---:|---:|")
    
    # 填充每行数据
    for r in year_q:
        rev_yoy = r.get("rev_yoy")
        profit_yoy = r.get("profit_yoy")
        
        # 增速格式: 正数带+号，负数带-号
        def fmt_yoy(v):
            if v is None: return "-"
            return f"{v:+.2f}%" if v >= 0 else f"{v:.2f}%"
        
        row = [
            r["label"],
            fmt_num(r.get("rev")),
            fmt_yoy(rev_yoy),
            fmt_num(r.get("profit")),
            fmt_yoy(profit_yoy),
            fmt_num(r.get("nm"), "%"),
            fmt_num(r.get("gm"), "%"),
        ]
        lines.append("|" + "|".join(row) + "|")
    
    return "\n".join(lines)


# ============== 主流程 ==============
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("code"); ap.add_argument("name")
    ap.add_argument("--out", default=None, help="输出最终MD文件路径")
    ap.add_argument("--json", default=None, help="输出中间JSON文件路径")
    ap.add_argument("--search-data", default=None, help="Agent搜索结果JSON文件(产品/区域/毛利率)")
    ap.add_argument("--quiet", action="store_true", help="减少控制台输出，适合Agent调用")
    args = ap.parse_args()
    code, name = args.code, args.name

    if args.quiet:
        import builtins
        builtins.print = lambda *a, **k: None

    t0 = time.time()
    print(f"\n{'='*20} Data Agent v5: {name} ({code}) {'='*20}")
    # ====== 并行拉取：市场、年报、季报、东方财富业务拆分 ======
    print("\n[阶段1] akshare/东方财富并行拉取...")
    with ThreadPoolExecutor(max_workers=4) as pool:
        mkt_future = pool.submit(fetch_market_akshare, code)
        annual_future = pool.submit(fetch_annuals_akshare, code)
        quarter_future = pool.submit(fetch_quarters_akshare, code)
        business_future = None
        if not (args.search_data and os.path.exists(args.search_data)):
            business_future = pool.submit(fetch_eastmoney_business, code)

        mkt = mkt_future.result()
        print(f"  市场数据: price={mkt.get('price')}, fwd_pe={mkt.get('fwd_pe')}")

        ann = annual_future.result()
        ann_dict = {r["year"]: r for r in ann if r.get("year")}
        ann = sorted(ann_dict.values(), key=lambda x: x["year"])
        calc_yoy(ann, "rev"); calc_yoy(ann, "profit")
        print(f"  年报(akshare): {len(ann)} 年")

        qrecs = quarter_future.result()
        if qrecs:
            calc_qoq(qrecs)
        print(f"  季报(akshare): {len(qrecs)} 季")

        em_prods, em_regs, em_margins = [], [], []
        if business_future is not None:
            em_prods, em_regs, em_margins = business_future.result()

    t1 = time.time()
    print(f"\n[阶段1] 完成 ({t1-t0:.1f}s)")

    # ====== 产品/区域/毛利率数据（东方财富API为主，--search-data为兼容） ======
    prod_all, reg_all, margins = [], [], []

    if args.search_data and os.path.exists(args.search_data):
        # 从Agent传入的JSON文件读取搜索结果（兼容旧流程）
        print(f"\n[阶段2] 从 {args.search_data} 读取搜索结果...")
        with open(args.search_data, "r", encoding="utf-8") as f:
            sd = json.load(f)
        prod_all = sd.get("products", [])
        reg_all = sd.get("regions", [])
        margins = sd.get("margins", [])
        print(f"  产品拆分: {len(prod_all)} 条, 区域拆分: {len(reg_all)} 条, 毛利率: {len(margins)} 条")
    else:
        # 只取最近3年数据（年报）
        this_year = datetime.now().year
        target_years = [this_year - 1, this_year - 2, this_year - 3]  # 2024, 2023, 2022
        prod_all = filter_by_years(em_prods, target_years)
        reg_all = filter_by_years(em_regs, target_years)
        margins = filter_by_years(em_margins, target_years)

        print(f"  东方财富API: 产品: {len(prod_all)}条, 区域: {len(reg_all)}条, 毛利率: {len(margins)}条")

        # 如果东方财富没拿到数据，尝试 NeoData 搜索补充（通常不需要）
        if not prod_all and not reg_all:
            print("  [WARN] 东方财富API无数据，跳过搜索（旧搜索已被弃用）")

    t2 = time.time()
    print(f"\n[阶段2] 完成 ({t2-t1:.1f}s)")

    # ====== 阶段3: 输出 ======
    md_content = build_md(code, name, mkt, ann, qrecs, prod_all, reg_all, margins)

    out_path = args.out
    if out_path:
        out_dir = os.path.dirname(os.path.abspath(out_path))
        if out_dir: os.makedirs(out_dir, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"\n[OK] 最终MD: {out_path}")
    else:
        print("\n--- 最终MD ---")
        print(md_content)

    # 同时输出JSON中间文件
    json_path = args.json
    if not json_path and args.out:
        json_path = args.out.rsplit(".", 1)[0] + "_intermediate.json"
    if json_path:
        intermediate = {
            "code": code, "name": name,
            "market": mkt, "annual": ann, "quarter": qrecs,
            "product_search": prod_all, "region_search": reg_all, "margins": margins,
        }
        json_dir = os.path.dirname(os.path.abspath(json_path))
        if json_dir: os.makedirs(json_dir, exist_ok=True)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(intermediate, f, ensure_ascii=False, indent=2)
        print(f"[OK] 中间JSON: {json_path}")

    print(f"\n{'='*20} 总耗时: {time.time()-t0:.1f}s {'='*20}")

if __name__ == "__main__":
    main()
