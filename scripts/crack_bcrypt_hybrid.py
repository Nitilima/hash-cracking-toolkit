#!/usr/bin/env python3
"""Quebra bcrypt ($2a$/$2b$/$2y$) via dicionario, com ataque hibrido opcional
(palavra da wordlist + sufixo numerico de N digitos), em CPU pura.

bcrypt e' lento de proposito; sem filtrar a wordlist um ataque hibrido pode
ser inviavel (wordlist_size * 10**suffix_digits tentativas). Por padrao,
filtra a wordlist para palavras curtas e so-letras antes de testar os
sufixos - ajuste --filter-regex/--max-base-len se a wordlist for diferente.
"""
import argparse
import re
import sys

try:
    from passlib.hash import bcrypt
except ImportError:
    print("Precisa de passlib (e de preferencia da lib C 'bcrypt' pra ir rapido):")
    print("  pip install passlib bcrypt")
    sys.exit(1)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("hash_file", help="arquivo com o hash completo ($2b$...)")
    ap.add_argument("wordlist", help="wordlist, uma palavra por linha")
    ap.add_argument("--suffix-digits", type=int, default=0,
                     help="quantos digitos numericos tentar no final de cada palavra (0 = dicionario puro)")
    ap.add_argument("--filter-regex", default=r"[A-Za-z]+",
                     help="regex (fullmatch) pra filtrar a palavra-base antes de testar sufixos")
    ap.add_argument("--max-base-len", type=int, default=20,
                     help="tamanho maximo da palavra-base depois do filtro")
    args = ap.parse_args()

    target = open(args.hash_file).read().strip()
    pattern = re.compile(args.filter_regex)

    candidates = []
    with open(args.wordlist, encoding="utf-8", errors="ignore") as f:
        for line in f:
            w = line.rstrip("\r\n")
            if 0 < len(w) <= args.max_base_len and pattern.fullmatch(w):
                candidates.append(w)

    total_suffixes = 10 ** args.suffix_digits if args.suffix_digits else 1
    print(f"{len(candidates)} palavras-base filtradas, x{total_suffixes} sufixo(s) "
          f"= {len(candidates) * total_suffixes} tentativas", file=sys.stderr)

    for i, w in enumerate(candidates):
        suffixes = [f"{d:0{args.suffix_digits}d}" for d in range(total_suffixes)] if args.suffix_digits else [""]
        for suf in suffixes:
            cand = w + suf
            try:
                if bcrypt.verify(cand, target):
                    print(f"MATCH! {cand!r} (palavra-base #{i})")
                    return
            except Exception:
                continue
        if i % 2000 == 0:
            print(f"... {i}/{len(candidates)} palavras-base testadas", file=sys.stderr)

    print("Nenhum candidato filtrado bateu. Tente alargar --filter-regex/--max-base-len.")


if __name__ == "__main__":
    main()
