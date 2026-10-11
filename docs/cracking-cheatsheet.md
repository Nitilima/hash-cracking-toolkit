# Cheatsheet — John the Ripper & Hashcat

Convenções: `hash.txt` = arquivo com o hash (uma linha); `wordlist.txt` = dicionário.

## Preparar hash para o John

John aceita hash puro por linha na maioria dos formatos, mas prefixar com
`user:` evita ambiguidade:

```bash
printf "user:%s\n" "$(cat hash.txt)" > hash_john.txt
```

## Hashes "raw" (sem salt)

| Algoritmo | Hashcat | John |
|---|---|---|
| MD5 | `hashcat -m 0 hash.txt wordlist.txt` | `john --format=raw-md5 --wordlist=wordlist.txt hash_john.txt` |
| SHA-1 | `hashcat -m 100 ...` | `john --format=raw-sha1 ...` |
| SHA-256 | `hashcat -m 1400 ...` | `john --format=raw-sha256 ...` |
| SHA-512 | `hashcat -m 1700 ...` | `john --format=raw-sha512 ...` |
| MD4 | `hashcat -m 900 ...` | `john --format=raw-md4 ...` |
| NTLM | `hashcat -m 1000 ...` | `john --format=nt ...` |
| Double MD5 | `hashcat -m 2600 ...` | `john --format=dynamic_6 ...` (hash precisa do prefixo `$dynamic_6$`) |
| LM | `hashcat -m 3000 ...` | `john --format=lm ...` |
| RAdmin v2.x | `hashcat -m 9900 ...` | sem formato nativo — usar script próprio (md5(pass + zero-pad até 100 bytes)) |

Formatos `dynamic_N` do John exigem o hash **com o prefixo**, não só o hex puro:
```bash
echo '$dynamic_6$<hash_hex>' > hash_dyn.txt
john --format=dynamic_6 --wordlist=wordlist.txt hash_dyn.txt
```

## crypt(3) — md5crypt / sha256crypt / sha512crypt

```bash
hashcat -m 500  hash.txt wordlist.txt   # $1$ md5crypt
hashcat -m 7400 hash.txt wordlist.txt   # $5$ sha256crypt
hashcat -m 1800 hash.txt wordlist.txt   # $6$ sha512crypt

john --format=md5crypt    --wordlist=wordlist.txt hash_john.txt
john --format=sha256crypt --wordlist=wordlist.txt hash_john.txt
john --format=sha512crypt --wordlist=wordlist.txt hash_john.txt
```

## bcrypt

```bash
hashcat -m 3200 hash.txt wordlist.txt
john --format=bcrypt --wordlist=wordlist.txt hash_john.txt
```

Ataque híbrido (palavra + N dígitos no final) no Hashcat:
```bash
hashcat -a 6 -m 3200 hash.txt wordlist.txt ?d?d      # 2 dígitos
```
Gerando candidatos híbridos e repassando pro John via stdin:
```bash
hashcat --stdout -a 6 wordlist.txt ?d?d | john --format=bcrypt --stdin hash_john.txt
```

## PBKDF2-HMAC-SHA256 (passlib `$pbkdf2-sha256$rounds$salt$hash`)

```bash
hashcat -m 10900 hash.txt wordlist.txt
john --format=pbkdf2-hmac-sha256 --wordlist=wordlist.txt hash_john.txt
```

## Depois de crackear

```bash
hashcat -m <modo> hash.txt --show
john --format=<formato> --show hash_john.txt
```

## Hashcat sem GPU / em VM com pouca RAM

```bash
hashcat -O -w 1 --segment-size=1 -m <modo> hash.txt wordlist.txt
```
- `-O` = kernels otimizados (usam menos memória, limitam o tamanho máximo de senha)
- `-w 1` = perfil de workload mais leve
- `--segment-size=1` = lê a wordlist em blocos menores (menos RAM)

Se mesmo assim der `Not enough allocatable device memory`, geralmente é
limitação real do ambiente (RAM baixa na VM) — nesse caso, usar os scripts em
`scripts/` (CPU pura, sem OpenCL) como alternativa.

## Regra de ouro

Se um ataque passar de ~15 minutos sem decidir nada, para e revisa a hipótese
de formato/modo antes de insistir — raramente vale a pena deixar rodando "só
pra garantir".
