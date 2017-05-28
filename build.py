#!/usr/bin/env python3
import sys
import os
import argparse

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
        html += """<h4 id="bib-year-{}">{}</h4>""".format(year, year)
        bib_per_year = ""
        for bib in reversed(bibtexs_per_year[year]):
            bib_per_year += bib + "\n"
        html += bib_to_html(bib_per_year)

    return html


def main(_):
    # argument parsing
    parser = argparse.ArgumentParser(description='build github static page',
                                     epilog="stg7 2017",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--publications',
                        type=str,
                        default="pub.bib",
                        help="puplications as bibtex file")
    parser.add_argument('--index_tpl',
                        type=str,
                        default="index.html.tpl",
                        help="index template")

    argsdict = vars(parser.parse_args())

    index = read_file(argsdict["index_tpl"])

    publications = read_bib_and_transform_to_html(argsdict["publications"])

    print(index.replace("{{pubs}}", publications))

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))