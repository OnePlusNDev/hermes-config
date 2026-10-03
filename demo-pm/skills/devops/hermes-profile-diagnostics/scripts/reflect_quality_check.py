#!/usr/bin/env python3
"""Two-pass Hindsight reflect quality check for memory-cleanup runs.

Implements the documented protocol (see references/memory-maintenance.md):
  1. Run the conclusion-oriented PRIMARY reflect.
  2. Apply TWO independent gates, in this order:
     a. WORDING gate — does the answer AFFIRMATIVELY claim expired/archivable
        facts? A real analysis can be wrong here (the "creation-age false
        positive": it flags long-lived config as expired purely because its
        creation timestamp is old — see 2026-10-01 in the reference). A bare
        affirmation (「存在需要归档的过期事实」) is the classic degenerate echo.
        Either way, an affirmative verdict is never trusted on its own.
     b. TOKEN gate — `usage.input_tokens` against a MODEL-SPECIFIC baseline.
        glm-4-flash full-context ≈ 6.8-7.0K; a question echo ≈ 2.2K.
        deepseek-v4-flash reads the WHOLE bank: observed 112K-273K on the same
        bank, so pass --baseline 50000 (or higher) for deepseek. Sub-baseline =
        facts were never fed = the answer is meaningless regardless of wording.
  3. If EITHER gate is not satisfied, auto-run the DISAMBIGUATION reflect, which
     strips the age framing and forces the "content-invalidated vs merely old"
     distinction. That pass is authoritative.

Do NOT act on (and do not `[SILENT]`-prune from) a primary answer that fails
either gate — most often that is the recurring false positive, not a finding.

Run with the hermes venv python (hindsight_client is absent from system python):
  /Users/oneplusn/.hermes/hermes-agent/venv/bin/python3 reflect_quality_check.py \
      --url http://127.0.0.1:9178 --bank demo-pm-memory --baseline 50000

Exit code is always 0 unless the client raised; read stdout for the verdict.
"""
import argparse

PRIMARY = ('给出当前记忆健康度评估：是否存在需要归档的过期事实（30天以上）、'
           '重复信息或矛盾信息？请直接回答结论。')

# Forced distinction: "old creation time" != "content invalidated".
DISAMBIG = ('针对上一轮审计的过期判定做定向澄清。背景：以下事实均创建时间较早，'
            '但内容都是长期有效的活跃配置（飞书 AppID/端口/LLM key/处理规则/协作铁律），'
            '创建时间早并不等于内容已过期。请只回答一个判定：是否存在'
            '【因内容本身失效】而真正需要归档/删除的事实？'
            '若有，列出具体条目与理由；若没有，直接回答「无内容性过期事实」。')

# Negation markers that turn an "expired" mention into a CLEAN verdict.
_NEG = ('无', '不存在', '没有', '未发现', '零', '0 条')
# Phrases that assert expired/archivable content exists.
_KW = ('过期事实', '需归档', '需要归档', '已过期', '过期条目', '过期内容')


def claims_expired(text: str) -> bool:
    """True if the answer AFFIRMATIVELY asserts expired/archivable facts exist.

    Scans every occurrence of an "expired" keyword and checks a short window in
    front of it for a negation, so 「不存在需要归档的过期事实」 does NOT count as
    a claim while 「存在 30 天以上需归档的过期事实」 does.
    """
    t = text.replace('\n', ' ')
    for kw in _KW:
        i = t.find(kw)
        while i != -1:
            window = t[max(0, i - 12):i]
            if not any(n in window for n in _NEG):
                return True
            i = t.find(kw, i + 1)
    return False


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--url', default='http://127.0.0.1:9178',
                    help='profile daemon base URL (NOT :8888 unless it serves your bank)')
    ap.add_argument('--bank', default='demo-pm-memory')
    ap.add_argument('--budget', default='high', choices=['low', 'mid', 'high'],
                    help='reflect budget; prefer high (see 2026-09-15 correction)')
    ap.add_argument('--baseline', type=int, default=6000,
                    help='min plausible input_tokens for a full-context reflect. '
                         'glm-4-flash ~6000; deepseek-v4-flash pass 50000+')
    ap.add_argument('--always-disambig', action='store_true',
                    help='force the disambiguation reflect even if both gates pass')
    a = ap.parse_args()

    from hindsight_client import Hindsight  # import here so --help works without it
    c = Hindsight(base_url=a.url)

    r = c.reflect(bank_id=a.bank, query=PRIMARY, budget=a.budget, include_facts=True)
    it = r.usage.input_tokens
    affirm = claims_expired(r.text)
    print(f'[primary]  input_tokens={it} output_tokens={r.usage.output_tokens} budget={a.budget}')
    print(f'[primary]  text: {r.text.strip()}')

    token_ok = it >= a.baseline
    print(f'[gate]     wording: {"AFFIRMATIVE expired-claim" if affirm else "clean/negative"}')
    print(f'[gate]     tokens:  {it} {"≥" if token_ok else "<"} baseline {a.baseline}')

    if token_ok and not affirm and not a.always_disambig:
        print(f'[verdict]  both gates pass -> trust the primary ({it} tokens, no expired claim)')
        return 0

    if not token_ok:
        reason = f'primary BELOW baseline ({it} < {a.baseline}) -> facts likely not fed'
    elif affirm:
        reason = ('primary AFFIRMATIVELY claims expired facts -> may be the '
                  'creation-age false positive')
    else:
        reason = '--always-disambig requested'
    print(f'[verdict]  {reason}; running disambiguation reflect')

    r2 = c.reflect(bank_id=a.bank, query=DISAMBIG, budget=a.budget, include_facts=True)
    print(f'[disambig] input_tokens={r2.usage.input_tokens} '
          f'output_tokens={r2.usage.output_tokens}')
    print(f'[disambig] text: {r2.text.strip()}')
    if r2.usage.input_tokens < a.baseline:
        print('[verdict]  WARNING: disambiguation is ALSO sub-baseline — do not act on it; '
              'escalate to HTTP POST /reflect with budget=high')
    else:
        print('[verdict]  disambiguation is authoritative — use it, not the primary answer')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
