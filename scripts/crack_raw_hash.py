#!/usr/bin/env python3
"""Testa varias receitas de hash 'raw' (sem salt) contra uma wordlist, em CPU pura.

Util quando hashcat/John nao estao disponiveis ou falham por falta de
GPU/memoria. Cobre as pegadinhas mais comuns de hashes de mesmo tamanho
(MD5 vs NTLM vs MD4 vs Double-MD5 vs RAdmin v2.x).
"""
import argparse
import hashlib
import sys


def md4_hex(b: bytes):
    """MD4 via hashlib (OpenSSL) com fallback pra pycryptodome.

    Em sistemas com OpenSSL 3.x "legacy provider" desabilitado (comum em
    Ubuntu/Debian recentes), hashlib.new('md4') falha com "unsupported hash
    type". Kali e distros de pentest costumam ter o legacy habilitado, mas
    nao da pra contar com isso - por isso o fallback.
    """
    try:
        return hashlib.new("md4", b).hexdigest()
    except Exception:
        pass
    try:
        from Crypto.Hash import MD4
        return MD4.new(b).hexdigest()
    except Exception:
        return None


def md5(b: bytes) -> str:
    return hashlib.md5(b).hexdigest()


def build_recipes(word: str):
    b = word.encode("utf-8", errors="ignore")
    recipes = {
        "md5": md5(b),
        "md5_upper": md5(word.upper().encode()),
        "md5_lower": md5(word.lower().encode()),
        "md5_reversed": md5(word[::-1].encode()),
        "sha1": hashlib.sha1(b).hexdigest(),
        "sha256": hashlib.sha256(b).hexdigest(),
        "sha512": hashlib.sha512(b).hexdigest(),
        "double_md5_hex": hashlib.md5(hashlib.md5(b).hexdigest().encode()).hexdigest(),
        "double_md5_raw": hashlib.md5(hashlib.md5(b).digest()).hexdigest(),
    }
    if len(b) <= 100:
        recipes["radmin_100pad"] = md5(b + b"\x00" * (100 - len(b)))
    ntlm = md4_hex(word.encode("utf-16le"))
    if ntlm:
        recipes["ntlm_md4"] = ntlm
    md4 = md4_hex(b)
    if md4:
        recipes["md4"] = md4
    return recipes


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("hash_file", help="arquivo com o hash (uma linha)")
    ap.add_argument("wordlist", help="wordlist, uma palavra por linha")
    args = ap.parse_args()

    target = open(args.hash_file).read().strip().lower()

    with open(args.wordlist, encoding="utf-8", errors="ignore") as f:
        for i, line in enumerate(f, 1):
            w = line.rstrip("\r\n")
            for name, h in build_recipes(w).items():
                if h and h.lower() == target:
                    print(f"MATCH! receita={name} palavra={w!r} (linha {i})")
                    return
            if i % 500000 == 0:
                print(f"... {i} candidatos testados", file=sys.stderr)

    print("Nenhuma receita bateu.")


if __name__ == "__main__":
    main()
