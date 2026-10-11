#!/usr/bin/env python3
"""Tenta destrinchar uma string recuperada que nao parece texto final.

Testa, em sequencia: Base64, Hex, Base32, reverter string, ROT13/Caesar
(todos os 25 shifts) e XOR de 1 byte (todas as 256 chaves) - e reaplica
nos resultados intermediarios (ate --max-depth camadas), procurando algo
so com letras/digitos/pontuacao comum.

Uso: python3 decode_helper.py "<string>"
"""
import argparse
import base64
import string
import sys

PRINTABLE = set(string.ascii_letters + string.digits + "_-. :/")


def looks_readable(s: str) -> bool:
    if not s:
        return False
    printable_ratio = sum(c in PRINTABLE for c in s) / len(s)
    if printable_ratio <= 0.9:
        return False
    # so-letras (ex.: saida de ROT/Caesar errado) ainda pode ser lixo; usa
    # proporcao de vogais pra distinguir texto real de ruido embaralhado
    letters = [c for c in s if c.isalpha()]
    if len(letters) >= 6:
        vowel_ratio = sum(c.lower() in "aeiou" for c in letters) / len(letters)
        if vowel_ratio < 0.28:
            return False
    return True


def try_base64(s: str):
    try:
        pad = (-len(s)) % 4
        raw = base64.b64decode(s + "=" * pad)
        return raw.decode("utf-8")
    except Exception:
        return None


def try_hex(s: str):
    try:
        clean = s.strip()
        if len(clean) % 2 != 0:
            return None
        return bytes.fromhex(clean).decode("utf-8")
    except Exception:
        return None


def try_base32(s: str):
    try:
        pad = (-len(s)) % 8
        raw = base64.b32decode(s.upper() + "=" * pad)
        return raw.decode("utf-8")
    except Exception:
        return None


def try_reverse(s: str):
    return s[::-1]


def try_rot_all(s: str):
    results = []
    for shift in range(1, 26):
        out = []
        for c in s:
            if c.isupper():
                out.append(chr((ord(c) - 65 + shift) % 26 + 65))
            elif c.islower():
                out.append(chr((ord(c) - 97 + shift) % 26 + 97))
            else:
                out.append(c)
        results.append((f"rot{shift}", "".join(out)))
    return results


def try_xor_all(s: str):
    try:
        data = s.encode("latin-1")
    except Exception:
        return []
    results = []
    for key in range(256):
        out = bytes(b ^ key for b in data)
        try:
            text = out.decode("utf-8")
        except UnicodeDecodeError:
            continue
        if looks_readable(text):
            results.append((f"xor_0x{key:02x}", text))
    return results


def explore(s: str, depth: int, max_depth: int, seen, trail):
    if s in seen or depth > max_depth:
        return
    seen.add(s)

    if looks_readable(s) and depth > 0:
        print(f"[{' -> '.join(trail)}] {s!r}")
        # nao da' pra parar aqui: reverter string preserva a proporcao de
        # vogais, entao um "quase certo" (faltando so inverter) passa igual
        # a resposta final - melhor sempre continuar e deixar o usuario
        # escolher a leitura que fizer mais sentido.

    candidates = []
    b64 = try_base64(s)
    if b64:
        candidates.append(("base64", b64))
    hexd = try_hex(s)
    if hexd:
        candidates.append(("hex", hexd))
    b32 = try_base32(s)
    if b32:
        candidates.append(("base32", b32))
    candidates.append(("reverse", try_reverse(s)))
    candidates.extend(try_rot_all(s))
    candidates.extend(try_xor_all(s))

    for name, val in candidates:
        explore(val, depth + 1, max_depth, seen, trail + [name])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("string", help="a string recuperada pra destrinchar")
    ap.add_argument("--max-depth", type=int, default=2,
                     help="quantas camadas tentar empilhar (mais profundidade = mais ruido de falsos positivos em XOR/ROT)")
    args = ap.parse_args()

    print(f"Entrada: {args.string!r}\n")
    explore(args.string, 0, args.max_depth, set(), [])


if __name__ == "__main__":
    main()
