#!/usr/bin/env python3
"""Two-pass Hindsight reflect quality check for memory-cleanup runs.

Implements the documented protocol (see references/memory-maintenance.md):
  1. Run the conclusion-oriented PRIMARY reflect.
  2. Judge it by `usage.input_tokens`, NOT by the wording. A full-context reflect
     on a ~48-fact bank costs ~6.8-7.0K input tokens. A degenerate "question echo"
     answer costs far less (~2.2K observed 2026-09-14) because the model answered
     without reading the bank.
  3. If the count is below the baseline, auto-run the DISAMBIGUATION reflect, which
     strips the age framing and asks only about superseded contradictions and exact
     duplicates. That pass is authoritative.

Do NOT act on a below-baseline primary answer, even if it claims "存在需要归档的
过期事实" — that is the recurring false positive, not a finding.

Run with the hermes venv python (hindsight_client is absent from system python):
  /Users/oneplusn/.hermes/hermes-agent/venv/bin/python3 reflect_quality_check.py \
      --url http://127.0.0.1:9178 --bank demo-pm-memory --baseline 6000

Exit code is always 0 unless the client raised; read stdout for the verdict.
"""
import argparse

PRIMARY = ('给出当前记忆健康度评估：是否存在需要归档的过期事实（30天以上）、'
           '重复信息或矛盾信息？请直接回答结论。')

DISAMBIG = ('以下事实是长期有效的运维配置规则（飞书 App ID、网关端口、Issue 处理流程、'
            'LLM 模型端点）。创建时间较早并不代表过期。请判断：其中是否存在'
            '(a)被后续信息取代的矛盾条目，(b)完全重复的冗余条目？'
            '只列出确实有问题的条目并说明理由；如果都没有，直接回答「无矛盾、无冗余」。')


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--url', default='http://127.0.0.1:9178',
                    help='profile daemon base URL (NOT :8888 unless it serves your bank)')
    ap.add_argument('--bank', default='demo-pm-memory')
    ap.add_argument('--baseline', type=int, default=6000,
                    help='min plausible input_tokens for a full-context reflect')
    a = ap.parse_args()

    from hindsight_client import Hindsight  # import here so --help works without it
    c = Hindsight(base_url=a.url)

    r = c.reflect(bank_id=a.bank, query=PRIMARY, budget='low', include_facts=True)
    it = r.usage.input_tokens
    print(f'[primary]  input_tokens={it} output_tokens={r.usage.output_tokens}')
    print(f'[primary]  text: {r.text.strip()}')

    if it >= a.baseline:
        print(f'[verdict]  primary read the bank ({it} >= {a.baseline}) -> trust it')
        return 0

    print(f'[verdict]  primary BELOW baseline ({it} < {a.baseline}) -> degenerate; '
          'running disambiguation reflect')
    r2 = c.reflect(bank_id=a.bank, query=DISAMBIG, budget='low', include_facts=True)
    print(f'[disambig] input_tokens={r2.usage.input_tokens} '
          f'output_tokens={r2.usage.output_tokens}')
    print(f'[disambig] text: {r2.text.strip()}')
    print('[verdict]  disambiguation is authoritative — use it, not the primary answer')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
