# AIM Watermarker

**AIM Watermarker** è uno script Python che aggiunge il watermark di AIM ai PDF presenti in una cartella destinati al Portale Appunti.

## Requisiti

Python 3.10 o versioni successive.

## Installazione

1. Clonare il repository
2. Installare le dipendenze specificate in [`pyproject.toml`](pyproject.toml) usando [PDM](https://pdm-project.org/en/latest/):

```sh
pdm install
```

## Utilizzo

```
usage: cli.py [-h] [--path PATH] [--scale SCALE] [--position {topleft,topright,bottomleft,bottomright,center}] [--padding PADDING]

options:
  -h, --help            show this help message and exit
  --path PATH           Indirizzo della cartella o del file
  --scale SCALE         Scala del logo come percentuale della dimensione più corta
  --position {topleft,topright,bottomleft,bottomright,center}
                        Posizione del logo (allowed: topleft, topright, bottomleft, bottomright, center)
  --padding PADDING     Padding del logo come percentuale della dimensione più corta
```

Per utilizzare lo script, eseguire il file `cli.py`, è sufficiente specificare il percorso della cartella contenente i PDF da modificare, gli altri parametri possono essere lasciati di default.

Esempio:

```bash
python src/aim_watermark/cli.py --path /path/to/folder/with/pdfs
```

## Autori

- Teo Bucci ([@teobucci](https://github.com/teobucci))
- Jacopo Stringara ([@jstringara](https://github.com/jstringara))

## Licenza

Questo progetto è rilasciato sotto licenza MIT.
