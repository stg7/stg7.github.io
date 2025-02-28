#!/usr/bin/env /usr/local/Python/bin/python2.1
"""
  Decoder for bibliographic data, BibTeX
  Usage: python bibtex2xml.py bibfile.bib > bibfile.xml

  v.8
  (c)2002-06-23 Vidar Bronken Gundersen
  http://bibtexml.sf.net/
  Reuse approved as long as this notification is kept.
  Licence: GPL.

  Contributions/thanks to:
  Egon Willighagen, http://sf.net/projects/jreferences/
  Richard Mahoney (for providing a test case)

  Editted by Sara Sprenkle to be more robust and handle more bibtex features.  (c) 2003-01-15
  1.  Changed bibtex: tags to bibxml: tags.
  2.  Use xmlns:bibxml="http://bibtexml.sf.net/"
  3.  Allow spaces between @type and first {
  4.  "author" fields with multiple authors split by " and "
      are put in separate xml "bibxml:author" tags.
  5.  Option for Titles: words are capitalized
      only if first letter in title or capitalized inside braces
  6.  Removes braces from within field values
  7.  Ignores comments in bibtex file (including @comment{ or % )
  8.  Replaces some special latex tags, e.g., replaces ~ with '&#160;'
  9.  Handles bibtex @string abbreviations
        --> includes bibtex's default abbreviations for months
        --> does concatenation of abbr # " more " and " more " # abbr
  10. Handles @type( ... ) or @type{ ... }
  11. The keywords field is split on , or ; and put into separate xml
      "bibxml:keywords" tags
  12. Ignores @preamble

  Known Limitations
  1.  Does not transform Latex encoding like math mode and special latex symbols.
  2.  Does not parse author fields into first and last names.
      E.g., It does not do anything special to an author whose name is in the form LAST_NAME, FIRST_NAME
      In "author" tag, will show up as <bibxml:author>LAST_NAME, FIRST_NAME</bibxml:author>
  3.  Does not handle "crossref" fields other than to print <bibxml:crossref>...</bibxml:crossref>
  4.  Does not inform user of the input's format errors.  You just won't be able to
      transform the file later with XSL

  You will have to manually edit the XML output if you need to handle
  these (and unknown) limitations.

"""

import string, re

# set of valid name characters
valid_name_chars = r'[\w\-:]'

#
# define global regular expression variables
#
author_rex = re.compile(r'\s+and\s+')
rembraces_rex = re.compile(r'[{}]')
capitalize_rex = re.compile(r'({\w*})')

# used by bibtexkeywords(data)
keywords_rex = re.compile(r'[,;]')

# used by concat_line(line)
concatsplit_rex = re.compile(r'\s*#\s*')

# split on {, }, or " in verify_out_of_braces
delimiter_rex = re.compile(r'([{}"])',re.I)

field_rex = re.compile(r'\s*(\w*)\s*=\s*(.*)')
data_rex = re.compile(r'\s*(\w*)\s*=\s*([^,]*),?')


#
# return the string parameter without braces
#
def removebraces(str):
    return rembraces_rex.sub('',str)

# fix author so that it creates multiple authors,
# split by "and"
def bibtexauthor(data):
    bibtex = ''
    author_list = author_rex.split(data)
    for author in author_list:
        author = author.strip()
        bibtex = bibtex + '<bibxml:author>' + removebraces(author) + \
                 '</bibxml:author>' + '\n'
    return bibtex.strip()


# @return the bibtex for the title
# @param data --> title string
# braces are removed from title
def bibtextitle(data):
    title = removebraces(data)
    title = title.strip()
    bibtex = '<bibxml:title>' + title + \
             '</bibxml:title>'
    return bibtex


# @return the bibtex for the keyword
# keywords are assumed to be delimited by , or ;
def bibtexkeyword(data):
    bibtex = ''
    keyword_list = keywords_rex.split(data)
    for keyword in keyword_list:
        keyword = keyword.strip()
        bibtex = bibtex + '<bibxml:keywords>' + removebraces(keyword) + \
                 '</bibxml:keywords>' + '\n'
    return bibtex.strip()



# data = title string
# @return the capitalized title (first letter is capitalized), rest are capitalized
# only if capitalized inside braces
def capitalizetitle(data):
    title_list = capitalize_rex.split(data)
    title = ''
    count = 0
    for phrase in title_list:
        check = string.lstrip(phrase)

        # keep phrase's capitalization the same
        if check.find('{') == 0:
            title = title + removebraces(phrase)
        else:
        # first word --> capitalize first letter (after spaces)
            if count == 0:
                title = title + check.capitalize()
            else:
                title = title + phrase.lower()
        count = count + 1

    return title


#
# print the XML for the transformed "filecontents_source"
#
def bibtexdecoder(filecontents_source):
    filecontents = []
    endentry = ''

    # want @<alphanumeric chars><spaces>{<spaces><any chars>,
    pubtype_rex = re.compile(r'@(\w*)\s*{\s*(.*),')
    endtype_rex = re.compile(r'}\s*$')
    endtag_rex = re.compile(r'^\s*}\s*$')

    bracefield_rex = re.compile(r'\s*(\w*)\s*=\s*(.*)')
    bracedata_rex = re.compile(r'\s*(\w*)\s*=\s*{(.*)},?')

    quotefield_rex = re.compile(r'\s*(\w*)\s*=\s*(.*)')
    quotedata_rex = re.compile(r'\s*(\w*)\s*=\s*"(.*)",?')

    for line in filecontents_source:
        line = line[:-1]

        # encode character entities
        line = line.replace('&', '&amp;')
        line = line.replace('<', '&lt;')
        line = line.replace('>', '&gt;')

        # start item: publication type (store for later use)
        if pubtype_rex.match(line):
        # want @<alphanumeric chars><spaces>{<spaces><any chars>,
            arttype = pubtype_rex.sub(r'\g<1>',line)
            arttype = arttype.lower()
            artid   = pubtype_rex.sub(r'\g<2>', line)
            endentry = '</bibxml:' + arttype + '>' + '\n</bibxml:entry>\n'
            line = '<bibxml:entry id="' + artid + '">\n' + \
                   '<bibxml:' + arttype + '>'
        # end item

        # end entry if just a }
        if endtype_rex.match(line):
            line = endtag_rex.sub(endentry, line)

        field = ''
        data = ''
        # field, publication info
        # field = {data} entries
        if bracedata_rex.match(line):
            field = bracefield_rex.sub(r'\g<1>', line)
            field = field.lower()
            data =  bracedata_rex.sub(r'\g<2>', line)

        # field = "data" entries
        elif quotedata_rex.match(line):
            field = quotefield_rex.sub(r'\g<1>', line)
            field = field.lower()
            data =  quotedata_rex.sub(r'\g<2>', line)

        # field = data entries
        elif data_rex.match(line):
            field = field_rex.sub(r'\g<1>', line)
            field = field.lower()
            data =  data_rex.sub(r'\g<2>', line)

        if field == 'title':
            line = bibtextitle(data)
        elif field == 'author':
            line = bibtexauthor(data)
        elif field == 'keywords':
            line = bibtexkeyword(data)
        elif field != '':
            data = removebraces(data)
            data = data.strip()
            if data != '':
                line = '<bibxml:' + field + '>' + data.strip() + \
                       '</bibxml:' + field + '>'
            # get rid of the field={} type stuff
            else:
                line = ''

        if line != '':
                # latex-specific replacements
                # do this now after braces were removed
            line = line.replace('~', '&#160;')
            line = line.replace('\\\'a', '&#225;')
            line = line.replace('\\"a', '&#228;')
            line = line.replace('\\\'c', '&#263;')
            line = line.replace('\\"o', '&#246;')
            line = line.replace('\\"u', '&#252;')
            line = line.replace("\\'e", '&#233;')
            line = line.replace("\\'u", '&#250;')
            line = line.replace("\\cc", '&#231;')




            filecontents.append(line)

    return filecontents

#
# return 1 iff abbr is in line but not inside braces or quotes
# assumes that abbr appears only once on the line (out of braces and quotes)
#
def verify_out_of_braces(line, abbr):

    phrase_split = delimiter_rex.split(line)

    abbr_rex = re.compile( '\\b' + abbr + '\\b', re.I)

    open_brace = 0
    open_quote = 0

    for phrase in phrase_split:
        if phrase == "{":
            open_brace = open_brace + 1
        elif phrase == "}":
            open_brace = open_brace - 1
        elif phrase == '"':
            if open_quote == 1:
                open_quote = 0
            else:
                open_quote = 1
        elif abbr_rex.search(phrase):
            if open_brace == 0 and open_quote == 0:
                return 1

    return 0


#
# a line in the form phrase1 # phrase2 # ... # phrasen
# is returned as phrase1 phrase2 ... phrasen
# with the correct punctuation
# Bug: Doesn't always work with multiple abbreviations plugged in
#
def concat_line(line):
    # only look at part after equals
    field = field_rex.sub(r'\g<1>',line)
    rest = field_rex.sub(r'\g<2>',line)

    concat_line = field + ' ='

    pound_split = concatsplit_rex.split(rest)

    phrase_count = 0
    length = len(pound_split)

    for phrase in pound_split:
        phrase = phrase.strip()
        if phrase_count != 0:
            if phrase.startswith('"') or phrase.startswith('{'):
                phrase = phrase[1:]
        elif phrase.startswith('"'):
            phrase = phrase.replace('"','{',1)

        if phrase_count != length-1:
            if phrase.endswith('"') or phrase.endswith('}'):
                phrase = phrase[:-1]
        else:
            if phrase.endswith('"'):
                phrase = phrase[:-1]
                phrase = phrase + "}"
            elif phrase.endswith('",'):
                phrase = phrase[:-2]
                phrase = phrase + "},"

        # if phrase did have \#, add the \# back
        if phrase.endswith('\\'):
            phrase = phrase + "#"
        concat_line = concat_line + ' ' + phrase

        phrase_count = phrase_count + 1

    return concat_line

# substitute abbreviations into filecontents
# @param filecontents_source - string of data from file
def bibtex_replace_abbreviations(filecontents_source):
    filecontents = filecontents_source.splitlines()

    #  These are defined in bibtex, so we'll define them too
    abbr_list = ['jan','feb','mar','apr','may','jun',
                 'jul','aug','sep','oct','nov','dec']
    value_list = ['January','February','March','April',
                  'May','June','July','August','September',
                  'October','November','December']

    abbr_rex = []
    total_abbr_count = 0

    front = '\\b'
    back = '(,?)\\b'

    for x in abbr_list:
        abbr_rex.append( re.compile( front + abbr_list[total_abbr_count] + back, re.I ) )
        total_abbr_count = total_abbr_count + 1


    abbrdef_rex = re.compile(r'\s*@string\s*{\s*('+ valid_name_chars + r'*)\s*=(.*)',
                             re.I)

    comment_rex = re.compile(r'@comment\s*{',re.I)
    preamble_rex = re.compile(r'@preamble\s*{',re.I)

    waiting_for_end_string = 0
    i = 0
    filecontents2 = ''

    for line in filecontents:
        if line == ' ' or line == '':
            continue

        if waiting_for_end_string:
            if re.search('}',line):
                waiting_for_end_string = 0
                continue

        if abbrdef_rex.search(line):
            abbr = abbrdef_rex.sub(r'\g<1>', line)

            if abbr_list.count(abbr) == 0:
                val = abbrdef_rex.sub(r'\g<2>', line)
                abbr_list.append(abbr)
                value_list.append(val.strip())
                abbr_rex.append( re.compile( front + abbr_list[total_abbr_count] + back, re.I ) )
                total_abbr_count = total_abbr_count + 1
            waiting_for_end_string = 1
            continue

        if comment_rex.search(line):
            waiting_for_end_string = 1
            continue

        if preamble_rex.search(line):
            waiting_for_end_string = 1
            continue


        # replace subsequent abbreviations with the value
        abbr_count = 0

        for x in abbr_list:

            if abbr_rex[abbr_count].search(line):
                if verify_out_of_braces(line,abbr_list[abbr_count]) == 1:
                    line = abbr_rex[abbr_count].sub( value_list[abbr_count] + r'\g<1>', line)
                # Check for # concatenations
                if concatsplit_rex.search(line):
                    line = concat_line(line)
            abbr_count = abbr_count + 1


        filecontents2 = filecontents2 + line + '\n'
        i = i+1


    # Do one final pass over file

    # make sure that didn't end up with {" or }" after the substitution
    filecontents2 = filecontents2.replace('{"','{{')
    filecontents2 = filecontents2.replace('"}','}}')

    afterquotevalue_rex = re.compile(r'"\s*,\s*')
    afterbrace_rex = re.compile(r'"\s*}')
    afterbracevalue_rex = re.compile(r'(=\s*{[^=]*)},\s*')

    # add new lines to data that changed because of abbreviation substitutions
    filecontents2 = afterquotevalue_rex.sub('",\n', filecontents2)
    filecontents2 = afterbrace_rex.sub('"\n}', filecontents2)
    filecontents2 = afterbracevalue_rex.sub(r'\g<1>},\n', filecontents2)

    return filecontents2

#
# convert @type( ... ) to @type{ ... }
#
def no_outer_parens(filecontents):

    # do checking for open parens
    # will convert to braces
    paren_split = re.split('([(){}])',filecontents)

    open_paren_count = 0
    open_type = 0
    look_next = 0

    # rebuild filecontents
    filecontents = ''

    at_rex = re.compile(r'@\w*')

    for phrase in paren_split:
        if look_next == 1:
            if phrase == '(':
                phrase = '{'
                open_paren_count = open_paren_count + 1
            else:
                open_type = 0
            look_next = 0

        if phrase == '(':
            open_paren_count = open_paren_count + 1

        elif phrase == ')':
            open_paren_count = open_paren_count - 1
            if open_type == 1 and open_paren_count == 0:
                phrase = '}'
                open_type = 0

        elif at_rex.search( phrase ):
            open_type = 1
            look_next = 1

        filecontents = filecontents + phrase

    return filecontents


# make all whitespace into just one space
# format the bibtex file into a usable form.
def bibtexwasher(filecontents_source):

    space_rex = re.compile(r'\s+')
    comment_rex = re.compile(r'\s*%')

    filecontents = []

    # remove trailing and excessive whitespace
    # ignore comments
    for line in filecontents_source:
        line = line.strip()
        line = space_rex.sub(' ', line)
        # ignore comments
        if not comment_rex.match(line):
            filecontents.append(' '+ line)

    filecontents = ''.join(filecontents)

    # the file is in one long string

    filecontents = no_outer_parens(filecontents)

    #
    # split lines according to preferred syntax scheme
    #
    filecontents = re.sub(r'(=\s*{[^=]*)},', r'\g<1>},\n', filecontents)

    # add new lines after commas that are after values
    filecontents = re.sub(r'"\s*,', '",\n', filecontents)
    filecontents = re.sub(r'=\s*([\w\d]+)\s*,', r'= \g<1>,\n', filecontents)
    filecontents = re.sub(r'(@\w*)\s*({(\s*)[^,\s]*)\s*,',
                          r'\n\n\g<1>\g<2>,\n', filecontents)

    # add new lines after }
    filecontents = re.sub(r'"\s*}','"\n}\n', filecontents)
    filecontents = re.sub(r'}\s*,','},\n', filecontents)


    filecontents = re.sub(r'@(\w*)', r'\n@\g<1>', filecontents)

    # character encoding, reserved latex characters
    filecontents = re.sub(r'{\\\&}', '&', filecontents)
    filecontents = re.sub(r'\\\&', '&', filecontents)

    # do checking for open braces to get format correct
    open_brace_count = 0
    brace_split = re.split('([{}])',filecontents)

    # rebuild filecontents
    filecontents = ''

    for phrase in brace_split:
        if phrase == '{':
            open_brace_count = open_brace_count + 1
        elif phrase == '}':
            open_brace_count = open_brace_count - 1
            if open_brace_count == 0:
                filecontents = filecontents + '\n'

        filecontents = filecontents + phrase

    filecontents2 = bibtex_replace_abbreviations(filecontents)

    # gather
    filecontents = filecontents2.splitlines()
    i=0
    j=0         # count the number of blank lines
    for line in filecontents:
        # ignore blank lines
        if line == '' or line == ' ':
            j = j+1
            continue
        filecontents[i] = line + '\n'
        i = i+1

    # get rid of the extra stuff at the end of the array
    # (The extra stuff are duplicates that are in the array because
    # blank lines were removed.)
    length = len( filecontents)
    filecontents[length-j:length] = []

    return filecontents


def filehandler(filepath):
    try:
        fd = open(filepath, 'r')
        filecontents_source = fd.readlines()
        fd.close()
    except:
        print('Could not open file:', filepath)
    washeddata = bibtexwasher(filecontents_source)
    outdata = bibtexdecoder(washeddata)
    print('<?xml version="1.0" encoding="iso-8859-1"?>')
    print('<!DOCTYPE bibxml:file SYSTEM "bibtexml-strict.dtd" >')
    print('<bibxml:file xmlns:bibxml="http://bibtexml.sf.net/">')
    print()
    for line in outdata:
        print(line)
    print('  <!-- manual cleanup may be required... -->')
    print('</bibxml:file>')


# main program

def main():
    import sys
    if sys.argv[1:]:
        filepath = sys.argv[1]
    else:
        print("No input file")
        sys.exit()
    filehandler(filepath)

if __name__ == "__main__": main()


# end python script
