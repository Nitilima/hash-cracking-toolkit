# Quando a senha crackeada não é a senha final

Hash quebrado != informação final. É comum (em CTFs e as vezes em exfiltração
real) que o "texto em claro" recuperado seja só mais uma camada embrulhada em
uma transformação **reversível e sem chave secreta** — não é criptografia,
é encoding. Hashing, encoding e encryption são coisas diferentes:

- **Hash**: uma via, não reversível (MD5, SHA*, bcrypt...). É o que você
  acabou de quebrar.
- **Encoding**: reversível, sem chave (Base64, Hex, Base32, URL-encode...).
  Serve só pra representar bytes como texto — qualquer um pode desfazer.
- **Encryption**: reversível, mas precisa de chave/senha (AES, RSA...). Se o
  enunciado diz "nenhuma etapa exige chave criptográfica secreta", **não é
  isso** — procure encoding ou cifra de substituição simples.

## Coisas pra testar, nessa ordem

1. **Base64** — alfabeto `A-Za-z0-9+/=`, comprimento múltiplo de 4.
   ```bash
   echo -n "<string>" | base64 -d
   ```
2. **Hex** — só `0-9a-f`, comprimento par.
   ```python
   bytes.fromhex("<string>").decode()
   ```
3. **Base32** — alfabeto `A-Z2-7=`, comprimento múltiplo de 8 (completa com `=`).
   ```python
   import base64
   base64.b32decode(s + "=" * ((-len(s)) % 8))
   ```
4. **ROT13 / Caesar** — se depois de decodificar a string ainda parecer
   "embaralhada" mas só com letras, tenta todos os 25 shifts:
   ```python
   for shift in range(26):
       print(shift, "".join(
           chr((ord(c)-65+shift)%26+65) if c.isupper() else
           chr((ord(c)-97+shift)%26+97) if c.islower() else c
           for c in s
       ))
   ```
5. **Atbash** (`a<->z, b<->y, ...`) — raro, mas simples de testar.
6. **Reverter a string** (`s[::-1]` / `rev`) — parece bobo, mas aparece.
6. **XOR com chave de 1 byte** — se sobrar caracteres não-imprimíveis depois
   do hex/base64, testa XOR com todas as 256 chaves procurando só
   letras/dígitos/`_` no resultado:
   ```python
   for k in range(256):
       out = bytes(c ^ k for c in data)
       if all(chr(b).isalnum() or chr(b) == '_' for b in out):
           print(k, out)
   ```
7. **Combinações** — às vezes é mais de uma camada (ex.: Base64 -> Caesar,
   Base32 -> reverter string, Hex -> XOR). Vai desfazendo camada por camada,
   sempre checando se o resultado parcial já parece "quase legível" (letras
   e `_` aparecendo, mesmo que embaralhado) antes de desistir da camada atual.

## Ferramenta visual

CyberChef (recipe "Magic" ou montar manualmente From Base64 / From Hex /
From Base32 / ROT13 Brute Force / XOR Brute Force) resolve a maior parte
disso sem escrever código. Use `scripts/decode_helper.py` pra automatizar
no terminal.

## Sinais de que a transformação está certa

- Sobra um separador óbvio (`_`, `-`, `:`) dividindo a string em partes.
- Aparece uma palavra reconhecível em um idioma natural.
- O comprimento final "bate" com algo que faz sentido (ex.: múltiplo de uma
  palavra + separador + número).
