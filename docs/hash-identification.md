# Identificação de hash

## Por tamanho/forma (hashes "raw", sem prefixo)

| Tamanho | Hex chars | Algoritmo mais provável | Outras hipóteses (mesmo tamanho) |
|---|---|---|---|
| 128 bits | 32 | MD5 | NTLM, MD4, MD2, Double-MD5, LM, RIPEMD-128, Haval-128, Tiger-128, Skein(128), RAdmin v2.x, DCC |
| 160 bits | 40 | SHA-1 | RIPEMD-160, Haval-160, Tiger-160 |
| 224 bits | 56 | SHA-224 | — |
| 256 bits | 64 | SHA-256 | SHA3-256, RIPEMD-256, Haval-256, GOST, Keccak-256 |
| 384 bits | 96 | SHA-384 | SHA3-384 |
| 512 bits | 128 | SHA-512 | SHA3-512, Whirlpool, Skein-512 |

Regra prática: **tamanho não define o algoritmo** — só restringe as opções. Hashes
de mesmo tamanho são a pegadinha clássica (ex.: 32 hex pode ser MD5 **ou** NTLM
**ou** MD4). Sempre teste a hipótese mais provável primeiro, mas tenha um plano B.

## Por prefixo (hashes "com formato", crypt-style)

| Prefixo | Algoritmo | Hashcat mode | John format |
|---|---|---|---|
| `$1$` | md5crypt (Unix) | 500 | `md5crypt` |
| `$apr1$` | md5crypt (Apache) | 1600 | `md5crypt` (variant) |
| `$5$` | sha256crypt (Unix) | 7400 | `sha256crypt` |
| `$6$` | sha512crypt (Unix) | 1800 | `sha512crypt` |
| `$2a$`/`$2b$`/`$2y$` | bcrypt | 3200 | `bcrypt` |
| `$y$` | yescrypt (Unix moderno) | — (não suportado em todo hashcat) | — |
| `$pbkdf2-sha256$` | PBKDF2-HMAC-SHA256 (passlib) | 10900 | `pbkdf2-hmac-sha256` |
| `$pbkdf2$` | PBKDF2-HMAC-SHA1 (passlib) | 12000 | `pbkdf2-hmac-sha1` |
| `$dynamic_N$` | formato "dynamic" do John (expressão customizada) | depende de N | `dynamic_N` |

## Ferramentas de identificação

```bash
hashid -m "<hash>"            # lista candidatos por padrão
hashcat --identify arquivo    # hashcat tenta reconhecer (v6.2+)
```

Essas ferramentas **chutam por padrão/tamanho**, não garantem o algoritmo real.
Trate a saída delas como lista de hipóteses a testar, não como verdade.

## Checklist ao identificar um hash desconhecido

1. Tem `$algo$salt$hash`? -> é formato crypt-style, prefixo diz o algoritmo.
2. É só hex? -> conta os caracteres, usa a tabela de tamanho acima.
3. Tem `:` no meio? -> pode ser `hash:salt` ou `user:hash` (formato pwdump/LM/NTLM).
4. Tem caracteres fora de `[0-9a-f]` e não é `$...$`? -> pode já estar em
   Base64/Base32 (ex.: hashes de algumas APIs, JWT, etc.) — não confundir com
   o próprio hash.
