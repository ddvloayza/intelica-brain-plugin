# Token benchmark: español vs inglés

Existe para que la decisión de en qué idioma se escriben los `.md`
generados tenga un número reproducible detrás, y no una afirmación.

## Por qué está esto acá

Hasta la versión 0.7.0, tres archivos del repo (`SKILL.md`,
`ARCHITECTURE.md`, `CHANGELOG.md`) afirmaban que escribir en inglés
ahorraba "~31% de tokens, medido". No había ninguna medición: ni script,
ni datos, ni registro. Al medirlo de verdad el ahorro resultó ser
**9.6%** — casi 3 veces menos.

## Cómo reproducirlo

```bash
pip install tiktoken   # solo si no tenés ANTHROPIC_API_KEY
python3 medir_tokens.py tokens_es.md tokens_en.md
```

Los dos `.md` son el mismo documento real del repo de conocimiento
(`inbox/Portal-Prod/2026-07-25-analisis-metricas-denver-prd-90-dias.md`),
uno en cada idioma, con los identificadores intactos en ambos.

Con `ANTHROPIC_API_KEY` exportada usa el tokenizador exacto de Claude. Sin
ella cae a `tiktoken o200k_base`, que es de OpenAI: sirve para la
dirección y el orden de magnitud, no para publicar el número como exacto.

## Resultado (tiktoken o200k_base, 2026-08-08)

| | Tokens | Caracteres |
|---|---|---|
| Español | 1829 | 6739 |
| Inglés | 1653 | 6478 |

El inglés ahorra **9.6%** sobre el total en español.

## Por qué es tan poco

El español es solo **3.9% más largo en caracteres**, pero cuesta **10.6%
más en tokens** — o sea que ~4 puntos vienen de que dice lo mismo con más
letras, y ~6 de que el tokenizador lo fragmenta peor.

Lo que aplasta el total es que estos documentos son densos en
identificadores: `itl-0003-portal-prd-ec2-denver-02`,
`dbo.vw_active_session_history`, `period=3600`, nombres de namespace,
rutas. Todo eso tokeniza idéntico en los dos idiomas y no se traduce
nunca. Solo cambia la prosa alrededor, que es la minoría del archivo.

Una comparación de prosa genérica sí daría algo cercano al 30%. Sobre
**estos** documentos, no — y esa es la comparación que importa.

## Si cambia el tipo de documento

Si en algún momento los `.md` pasan a ser mucho más narrativos y menos
densos en identificadores, el ahorro del inglés sube y esta decisión vale
la pena revisarla. Volvé a correr el script con un documento
representativo del nuevo formato en vez de asumir que el 9.6% sigue
valiendo.
