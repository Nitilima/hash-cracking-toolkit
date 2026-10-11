#!/usr/bin/env python3
"""Quebra PBKDF2-HMAC-SHA256 no formato passlib ($pbkdf2-sha256$rounds$salt$hash)
via dicionario, em CPU pura (sem GPU).
"""
import argparse
import sys

try:
    from passlib.hash import pbkdf2_sha256
except ImportError:
    print("Precisa de passlib: pip install passlib")
    sys.exit(1)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("hash_file", help="arquivo com o hash completo ($pbkdf2-sha256$...)")
    ap.add_argument("wordlist", help="wordlist, uma palavra por linha")
    args = ap.parse_args()

    target = open(args.hash_file).read().strip()

    count = 0
    with open(args.wordlist, encoding="utf-8", errors="ignore") as f:
        for line in f:
            w = line.rstrip("\r\n")
            count += 1
            try:
                if pbkdf2_sha256.verify(w, target):
                    print(f"MATCH! palavra={w!r} (linha {count})")
                    return
            except Exception:
                continue
            if count % 200000 == 0:
                print(f"... {count} testadas", file=sys.stderr)

    print(f"Nenhuma bateu depois de {count} candidatos.")


if __name__ == "__main__":
    main()
