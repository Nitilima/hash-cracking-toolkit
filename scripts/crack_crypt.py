#!/usr/bin/env python3
"""Quebra md5crypt ($1$), sha256crypt ($5$) ou sha512crypt ($6$) via dicionario.

Usa a lib `crypt` da stdlib (glibc, mais rapido) quando disponivel, com
fallback para `passlib` (puro Python, funciona em qualquer SO/versao).
Nao depende de GPU - util quando hashcat falha por falta de memoria/driver.
"""
import argparse
import sys


def get_backend():
    try:
        import crypt
        return "stdlib", crypt
    except ImportError:
        pass
    try:
        from passlib.hash import md5_crypt, sha256_crypt, sha512_crypt
        return "passlib", {
            "1": md5_crypt,
            "5": sha256_crypt,
            "6": sha512_crypt,
        }
    except ImportError:
        return None, None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("hash_file", help="arquivo com o hash completo ($1$/$5$/$6$...)")
    ap.add_argument("wordlist", help="wordlist, uma palavra por linha")
    args = ap.parse_args()

    target = open(args.hash_file).read().strip()
    parts = target.split("$")
    if len(parts) < 4:
        print("Hash nao parece estar no formato $id$salt$hash")
        sys.exit(1)
    algo_id = parts[1]
    salt_full = "$".join(parts[:3]) + "$"

    backend, mod = get_backend()
    if backend is None:
        print("Nem 'crypt' (stdlib) nem 'passlib' disponiveis.")
        print("Instala com: pip install passlib")
        sys.exit(1)

    print(f"Backend: {backend} | algoritmo=${algo_id}$ | salt={salt_full}", file=sys.stderr)

    count = 0
    with open(args.wordlist, encoding="utf-8", errors="ignore") as f:
        for line in f:
            w = line.rstrip("\r\n")
            count += 1
            try:
                if backend == "stdlib":
                    ok = mod.crypt(w, salt_full) == target
                else:
                    hasher = mod.get(algo_id)
                    ok = hasher is not None and hasher.verify(w, target)
            except Exception:
                continue
            if ok:
                print(f"MATCH! palavra={w!r} (linha {count})")
                return
            if count % 200000 == 0:
                print(f"... {count} testadas", file=sys.stderr)

    print(f"Nenhuma bateu depois de {count} candidatos.")


if __name__ == "__main__":
    main()
