#!/usr/bin/env python3
"""Mide la diferencia real de tokens entre la version en espanol y la version
en ingles del MISMO documento de conocimiento.

Solo lectura: no toca AWS, no toca los repos, no sube nada. Lee dos archivos
locales y cuenta.

Dos formas de contar, en orden de preferencia:

  1. API de Anthropic (exacta para Claude, que es quien consume estos .md).
     Necesita ANTHROPIC_API_KEY exportada. Solo usa la stdlib.
  2. tiktoken (tokenizador de OpenAI). Es un PROXY: sirve para ver la
     direccion y el orden de magnitud, no es el tokenizador de Claude.
     Necesita: pip install tiktoken

Uso:
    python3 medir_tokens.py tokens_es.md tokens_en.md
"""

import json
import os
import sys
import urllib.error
import urllib.request

API_URL = "https://api.anthropic.com/v1/messages/count_tokens"
MODEL = "claude-opus-5"


def count_anthropic(text: str, api_key: str) -> int:
    payload = json.dumps(
        {"model": MODEL, "messages": [{"role": "user", "content": text}]}
    ).encode("utf-8")
    request = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
    )
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read())["input_tokens"]


def count_tiktoken(text: str) -> int:
    import tiktoken

    return len(tiktoken.get_encoding("o200k_base").encode(text))


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 1

    path_es, path_en = sys.argv[1], sys.argv[2]
    text_es = open(path_es, encoding="utf-8").read()
    text_en = open(path_en, encoding="utf-8").read()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    overhead = 0

    if api_key:
        try:
            # El wrapper de mensaje suma un costo fijo identico en ambos casos;
            # se mide con un contenido minimo y se descuenta, para que el ratio
            # no quede artificialmente comprimido.
            overhead = count_anthropic("x", api_key) - 1
            tokens_es = count_anthropic(text_es, api_key) - overhead
            tokens_en = count_anthropic(text_en, api_key) - overhead
            tokenizer = f"API de Anthropic ({MODEL}) — exacta"
        except urllib.error.HTTPError as exc:
            print(f"La API fallo ({exc.code}); probando con tiktoken.", file=sys.stderr)
            api_key = None

    if not api_key:
        try:
            tokens_es = count_tiktoken(text_es)
            tokens_en = count_tiktoken(text_en)
            tokenizer = "tiktoken o200k_base — PROXY, no es el tokenizador de Claude"
        except ImportError:
            print(
                "Sin ANTHROPIC_API_KEY y sin tiktoken instalado.\n"
                "  Opcion exacta:  export ANTHROPIC_API_KEY=...\n"
                "  Opcion proxy:   pip install tiktoken",
                file=sys.stderr,
            )
            return 1

    ahorro = (tokens_es - tokens_en) / tokens_es * 100
    sobrecosto = (tokens_es - tokens_en) / tokens_en * 100

    print(f"\nTokenizador: {tokenizer}")
    if overhead:
        print(f"(descontado el overhead fijo del wrapper: {overhead} tokens)")
    print()
    print(f"  Espanol : {tokens_es:>6} tokens   ({len(text_es):>6} caracteres)")
    print(f"  Ingles  : {tokens_en:>6} tokens   ({len(text_en):>6} caracteres)")
    print(f"  Delta   : {tokens_es - tokens_en:>6} tokens")
    print()
    print(f"  Escribir en ingles ahorra   {ahorro:.1f}% sobre el total en espanol")
    print(f"  Escribir en espanol cuesta  {sobrecosto:.1f}% mas que el ingles")
    print()
    print("Las dos cifras describen el mismo dato con denominador distinto.")
    print("La primera es la comparable con el '31%' que afirma el SKILL.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
