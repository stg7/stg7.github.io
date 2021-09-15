#!/usr/bin/env python3
import sys
import os
import argparse
import re

import lxml.etree as ET

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

import thirdparty.bibtex2xml


def build_xml(bibtex):
    """ retuns a xml representation of a bibtex string using thirdparty tool """

    washeddata = thirdparty.bibtex2xml.bibtexwasher(bibtex.split("\n"))
    outdata = thirdparty.bibtex2xml.bibtexdecoder(washeddata)

    header = """<?xml version="1.0" ?>
<!DOCTYPE bibxml:file SYSTEM "{path}/bibtexml-strict.dtd" >
<bibxml:file xmlns:bibxml="http://bibtexml.sf.net/">""".format(path=os.path.dirname(os.path.realpath(__file__)) + "/thirdparty")

    footer = '</bibxml:file>'
    return header + "\n".join(outdata) + footer


def group_by_years(bibtextfilename):
    """ group bib entries by year, stable, that means origin ordering will be preserved"""
    with open(bibtextfilename, "r") as bfile:
        lines = bfile.readlines()

    # extract separate bib entries
    curr = ""
    bib_entries = []
    start_bibentry = False
    for line in lines:
        if re.match(".*@.*{.*,", line):
            start_bibentry = True
            bib_entries.append(curr)
            curr = ""
        if start_bibentry:
            curr += line
    bib_entries.append(curr)
    bib_entries = bib_entries[1:]

    def get_year(x):
        """ return year of one bib entry """
        for l in x.split("\n"):
            if re.match(".*year.*=.*", l):
                return l.split("=")[1].replace("{", "").replace("}", "").replace(",", "").replace("\"", "").strip()
        return "0000"

    # group all entries by year
    years = {}
    for bib in bib_entries:
        year = get_year(bib)
        years[year] = years.get(year, []) + [bib]
    return years


def bib_to_html(bib):
    """ convert bib entries as string to html """
    xml = build_xml(bib)
    dom = ET.fromstring(xml)
    xslt = ET.parse("{path}/bibtexml2html_year.xsl".format(path=os.path.dirname(os.path.realpath(__file__)) + "/thirdparty"))
    transform = ET.XSLT(xslt)
    newdom = transform(dom)
    html = str(ET.tostring(newdom, pretty_print=True), "utf-8")
    html = html.replace(r"$^\circ$", "&deg;")
    return html.replace('xmlns:bibxml="http://bibtexml.sf.net/"', "")


def generate_bib_file(bib, bibfolder="./bibs"):
    cleaned_bib = []
    for l in bib.split("\n"):
        if "@" in l:
            bibkey = l.split("{")[1].split(",")[0]
        if l.split("=")[0].strip() == "pdf":
            continue
        if l.split("=")[0].strip() == "slides":
            continue
        cleaned_bib.append(l)
    cleaned_bib = "\n".join(cleaned_bib)
    bibkey = bibkey.replace(":", "_")
    os.makedirs(bibfolder, exist_ok=True)
    bibfilename = bibfolder + "/" + bibkey + ".bib"
    with open(bibfilename, "w") as bibfile:
        bibfile.write(cleaned_bib)
    return bibfilename


def main(params):
    parser = argparse.ArgumentParser(description='generate html file based on bibtex file, sorted by year', epilog="stg7 2017", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-bibtexfile', type=str, default="bib/publications.bib", help='input bibtex file')
    parser.add_argument('-outputfile', type=str, default="output.html", help='output html filename')

    argsdict = vars(parser.parse_args())

    print("[start] building html file based on {}.".format(argsdict["bibtexfile"]))

    bibtexs_per_year = group_by_years(argsdict["bibtexfile"])

    outputfile = open(argsdict["outputfile"], "w")
    pr = lambda x: outputfile.write(x + "\n")
    for year in sorted(bibtexs_per_year.keys(), key=int, reverse=True):
        pr(""" <a href="#bib-year-{}" >{}</a> """.format(year, year))

    for year in sorted(bibtexs_per_year.keys(), key=int, reverse=True):
        pr("""<h1 id="bib-year-{}">{}</h1>""".format(year, year))
        bib_per_year = ""
        for bib in bibtexs_per_year[year]:
            bib_per_year += bib + "\n"

        pr(bib_to_html(bib_per_year))

    outputfile.close()

    print("[done ] html output written to {}.".format(argsdict["outputfile"]))


if __name__ == "__main__":
    main(sys.argv[1:])
