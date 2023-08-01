# AIM Watermarker
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Code style: black](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)

**AIM Watermarker** è uno script Python che aggiunge il watermark di AIM ai PDF presenti in una cartella destinati al Portale Appunti.

## Requisiti

Python 3.6 o versioni successive

## Installazione

1. Clonare il repository o scaricare il codice sorgente
2. Installare le dipendenze con il comando `pip install -r requirements.txt`

## Utilizzo

Per utilizzare lo script, eseguire il file `watermarker.py` con i seguenti argomenti:

- `-p` o `--path`: indirizzo della cartella o del file da elaborare
- `-o` o `--overwrite`: sovrascrive il file originale (opzionale)

Esempio:

```bash
python watermarker.py -p /path/to/folder/with/pdfs -o
```

## Autori

- Teo Bucci ([@teobucci](https://github.com/teobucci))
- Jacopo Stringara ([@jstringara](https://github.com/jstringara))
