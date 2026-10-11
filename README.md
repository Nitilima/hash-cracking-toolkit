# p4ssw0rd_crack1ng

Kit de referência pessoal para quebra e identificação de hashes — comandos,
scripts e cheatsheets que uso no dia a dia em pentest/CTF/estudo de segurança.

> Uso autorizado apenas: pentest com permissão, CTF, laboratório próprio ou
> estudo. Não use isso contra sistemas/credenciais sem autorização.

## Estrutura

```
docs/
  hash-identification.md       -> como reconhecer o formato de um hash
  cracking-cheatsheet.md       -> comandos prontos de John/Hashcat por formato
  decoding-transformations.md  -> quando a "senha" crackeada não é a senha final
scripts/
  crack_raw_hash.py            -> testa várias receitas de hash "raw" (MD5/SHA*/NTLM/MD4/Double-MD5/RAdmin) sem precisar de GPU
  crack_crypt.py               -> md5crypt/sha256crypt/sha512crypt ($1$/$5$/$6$) via passlib, sem GPU
  crack_pbkdf2.py              -> PBKDF2-HMAC-SHA256 (formato passlib $pbkdf2-sha256$...), sem GPU
  crack_bcrypt_hybrid.py       -> bcrypt ($2b$) com ataque híbrido wordlist+sufixo, sem GPU
  decode_helper.py             -> tenta destrinchar uma string "estranha" (Base64/Hex/Base32/ROT/XOR/reverse)
```

## Quando usar os scripts Python em vez de John/Hashcat

Hashcat precisa de um backend OpenCL/CUDA; em VM sem GPU (ou com pouca RAM) ele
pode falhar com "not enough allocatable device memory" mesmo em modos leves.
Os scripts em `scripts/` fazem a mesma conta via `hashlib`/`passlib`/`bcrypt`
em CPU pura — mais lento que GPU, mas não depende de driver/memória de vídeo.
São um complemento ao John/Hashcat, não um substituto: sempre tente as
ferramentas padrão primeiro, use os scripts quando o ambiente não permitir.

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r scripts/requirements.txt
```

## Uso rápido

```bash
# hash "raw" (MD5/SHA1/SHA256/SHA512/NTLM/MD4/Double-MD5/RAdmin...)
python3 scripts/crack_raw_hash.py hash.txt wordlist.txt

# crypt(3): md5crypt ($1$), sha256crypt ($5$), sha512crypt ($6$)
python3 scripts/crack_crypt.py hash.txt wordlist.txt

# PBKDF2-HMAC-SHA256 (formato passlib $pbkdf2-sha256$rounds$salt$hash)
python3 scripts/crack_pbkdf2.py hash.txt wordlist.txt

# bcrypt com ataque híbrido (palavra + sufixo numérico de N dígitos)
python3 scripts/crack_bcrypt_hybrid.py hash.txt wordlist.txt --suffix-digits 2

# destrinchar uma string recuperada que não parece texto final
python3 scripts/decode_helper.py "c2hhZ2d5X0NPTkhFQ09PQ09OVElORU5UQUxfSVY="
```

Veja `docs/` para os comandos equivalentes em John the Ripper e Hashcat.
