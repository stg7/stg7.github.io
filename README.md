# [stg7.github.io](https://stg7.github.io)

stg7.github.io page

## requirements
python3 and all other dependencies via `pip3 install -r requirements.txt`

## run

check the config file (`config.json`),
change settings,

```json
{
    "infos": {
        "author": "Steve Göring",
        "title": "stg7.github.io",
        "publications": "will be replaces by content of pub.bib"
    },
    "publications_file": "pub.bib",
    "template": "html.tpl",
    "start": "index.md"
}

```

run `./build.py`
