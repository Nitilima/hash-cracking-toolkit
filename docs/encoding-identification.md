# Como reconhecer um encoding (Base64, Hex, Base32...)

Antes de rodar qualquer coisa, vale treinar o olho pra reconhecer o tipo de
encoding só de olhar a string. Isso economiza um monte de tentativa-e-erro.

> Ver também: [`hash-identification.md`](hash-identification.md) para
> reconhecer **hashes** pelo tamanho/prefixo — este doc aqui é sobre
> **encoding** (reversível, sem chave), que é outra coisa (ver
> [`decoding-transformations.md`](decoding-transformations.md) pra entender
> a diferença entre hash/encoding/encryption).

## Base64

- **Alfabeto**: `A-Z`, `a-z`, `0-9`, `+`, `/` (variante URL-safe troca `+`/`/`
  por `-`/`_`).
- **Padding**: termina com `=` ou `==` quando o tamanho dos dados originais
  não é múltiplo de 3 bytes. Sem padding também é válido (depende de quem gerou).
- **Tamanho**: sempre múltiplo de 4 caracteres (contando o padding).
- **Como reconhecer**: mistura de maiúsculas e minúsculas e dígitos, às vezes
  `+`, `/`, `=`. É o mais "normal-looking" dos três.
- **Exemplo**: `c2hhZ2d5X0NPTkhFQ09PQ09OVElORU5UQUxfSVY=`
- **Decodificar**:
  ```bash
  echo -n "<string>" | base64 -d
  ```
  ```python
  import base64
  base64.b64decode(s + "=" * ((-len(s)) % 4))
  ```

## Hex (Base16)

- **Alfabeto**: só `0-9a-f` (ou `0-9A-F` maiúsculo).
- **Padding**: não tem — mas o tamanho é **sempre par** (cada byte vira
  exatamente 2 caracteres).
- **Como reconhecer**: só dígitos e letras de `a` a `f`, tamanho par. É fácil
  confundir com um hash cru (MD5/SHA*) à primeira vista — a diferença é que um
  hash tem tamanho fixo (32/40/64/128 chars) e **não decodifica pra nada**
  (é uma via só), enquanto um hex-encoding decodifica pra texto legível.
- **Exemplo**: `636c69636b65725f54454e5445494445495841524f5041535341444f5f49`
- **Decodificar**:
  ```bash
  echo -n "<string>" | xxd -r -p
  # ou
  python3 -c "print(bytes.fromhex('<string>').decode())"
  ```

## Base32

- **Alfabeto**: só `A-Z` maiúsculo e dígitos `2-7` (não usa `0`, `1`, `8`, `9`
  de propósito, pra evitar confundir `O`/`0` e `I`/`1`).
- **Padding**: termina com `=` até completar múltiplo de **8** caracteres.
- **Como reconhecer**: tudo maiúsculo, só letras e os dígitos 2-7, geralmente
  mais comprido que o Base64 equivalente (fica ~1.6x maior que o Base64 pros
  mesmos dados).
- **Exemplo**: `MFVWS4TBL5KVGT2UIVJE4T27JFEUS===`
- **Decodificar**:
  ```python
  import base64
  s = "<string>"
  base64.b32decode(s + "=" * ((-len(s)) % 8))
  ```

## Fluxograma rápido

```
A string só tem [0-9a-f] e tamanho par?
  -> provavelmente Hex (ou um hash cru, se não decodificar pra nada legível)

A string só tem [A-Z2-7] (+ talvez '=' no final) e tamanho múltiplo de 8?
  -> provavelmente Base32

A string tem letras maiúsculas E minúsculas misturadas (+ talvez
dígitos/+/// /= no final) e tamanho múltiplo de 4?
  -> provavelmente Base64
```

Se nenhuma bater (ou decodificar pra lixo), pode ser que precise de mais uma
camada por cima — ROT13/Caesar, reverter a string, XOR de 1 byte, etc. Ver
[`decoding-transformations.md`](decoding-transformations.md) e usar
`scripts/decode_helper.py` pra automatizar essa parte.

## E os hashes? (tamanho e prefixo)

Isso é outro assunto — hash não decodifica pra nada (é unidirecional). Pra
reconhecer QUE TIPO de hash você está vendo (pelo tamanho em hex ou pelo
prefixo tipo `$1$`/`$6$`/`$2b$`/`$pbkdf2-sha256$`), ver a tabela completa em
[`hash-identification.md`](hash-identification.md).

Resumo rapidíssimo:
- 32 hex -> família MD5/NTLM/MD4 (ambíguo, cuidado)
- 40 hex -> família SHA-1
- 64 hex -> família SHA-256
- 128 hex -> família SHA-512
- `$1$...` / `$5$...` / `$6$...` -> crypt Unix (md5crypt/sha256crypt/sha512crypt)
- `$2a$`/`$2b$`/`$2y$...` -> bcrypt (esse não tem ambiguidade, o prefixo já entrega)
- `$pbkdf2-sha256$rounds$salt$hash` -> PBKDF2-HMAC-SHA256 (formato passlib)
