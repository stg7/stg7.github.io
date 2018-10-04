#!/usr/bin/env python3
import sys
import os
import argparse
import json
import glob

import mistletoe

from libs.generate_html import group_by_years
from libs.generate_html import bib_to_html



def read_file(filename):
    with open(filename) as file:
        content = "".join(file.readlines())
    return content


def read_bib_and_transform_to_html(bibfile):
    bibtexs_per_year = group_by_years(bibfile)
    html = ""

    #for year in sorted(bibtexs_per_year.keys(), key=int, reverse=True):
    #    html += """ <a href="#bib-year-{}" >{}</a> """.format(year, year)

    for year in sorted(bibtexs_per_year.keys(), key=int, reverse=True):
        html += """<h2 id="bib-year-{}">{}</h2>""".format(year, year)
        bib_per_year = ""
        for bib in reversed(bibtexs_per_year[year]):
            bib_per_year += bib + "\n"
        html += bib_to_html(bib_per_year)

    return html


def read_config(configfilename):
    try:
        with open(configfilename) as cfg_fp:
            config = json.load(cfg_fp)
    except Exception as e:
        print(f"{configfilename} is not valid, please check")
        print(e)
        sys.exit(1)
    return config


def linkname(x, page, config):
    current_page = x == page
    if x == config["start"]:
        x = "start"
    x = os.path.splitext(x)[0]
    x = x.title()
    if current_page:
        x = "*" + x + "*"
    return x



def postprocess(content, infos, pages):
    for k in infos:
        pattern = r"{{"+ k + r"}}"
        content = content.replace(pattern, infos[k])

    for md_page in pages:
        html_page = os.path.splitext(md_page)[0] + ".html"
        content = content.replace(md_page, html_page)
    return content


def read_photos(photos_dir):
    res = []
    small = list(glob.glob(photos_dir + "/small/*"))

    for sm in small:
        large = sm.replace("/small/", "/large/")
        res.append(f"""
            <a href="{large}" target="_blank"><img src="{sm}" /></a>
            """.strip())
    return "\n".join(res)


def main(_):
    # argument parsing
    parser = argparse.ArgumentParser(description='build github static page',
                                     epilog="stg7 2017,2018",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--config',
                        type=str,
                        default="config.json",
                        help="config file")

    argsdict = vars(parser.parse_args())

    # read config
    config = read_config(argsdict["config"])

    #print(config)

    template = read_file(config["template"])

    publications = read_bib_and_transform_to_html(config["publications_file"])
    config["infos"]["publications"] = publications
    config["infos"]["photos"] = read_photos(config["photos_dir"])
    #print(publications)

    pages = list(glob.glob("**/*.md", recursive=True))
    pages = list(filter(lambda x: not x.startswith("libs/") and x != "README.md", pages))

    if config["start"] in pages:
        # first page is always index.md
        pages = [config["start"]] + [y for y in pages if y != "index.md"]

    # parse each page to a html version
    for page in pages:
        html = os.path.splitext(page)[0] + ".html"

        toc = mistletoe.markdown(" | ".join(["[{y}]({x})".format(x=x,y=linkname(x, page, config)) for x in pages]))
        config["infos"]["toc"] = toc
        page_md = read_file(page)

        content = mistletoe.markdown(page_md)
        content = postprocess(content, config["infos"], pages)
        config["infos"]["content"] = content
        rendered_html = postprocess(template, config["infos"], pages)
        print(f"{page} rendered to {html}")
        with open(html, "w") as html_fp:
            html_fp.write(rendered_html)

    return
    index = read_file()

    publications = read_bib_and_transform_to_html(argsdict["publications"])

    print(index.replace("{{pubs}}", publications))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
