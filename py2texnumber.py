#!/usr/bin/env python
# (c) 2012 Vlad Gheorghiu, vsoftco@gmail.com
# All rights reserved

import re
import sys
import datetime


# Functions
def search_replace_line(keywords, pattern_in, pattern_out,
                        dictionary, line, line_idx):
    warnings = [] # undefined reference(s) warning(s) in (the current line)
    for keyword in keywords:
        for matches in re.finditer('\\\\'+keyword+
                                   '\{'+pattern_in+'.*?\}',line):
            # extract {pattern...} from \<keyword>{pattern...}
            match=re.search('\{.*?\}',matches.group()).group()
            # do the replacement whenever the {pattern...} is different
            # from the dictionary key
            if match not in dictionary:
                # undefined reference
                col_no=matches.start()+1 # the warning's column number
                warnings.append(['\\'+keyword+match, line_idx, col_no])
            if (match in dictionary and
                ('{'+pattern_out+str(dictionary[match])+'}')!=match):
                line=re.sub(keyword+match,
                            keyword+'_REPLACED_mark'
                            +'{'+pattern_out+
                            str(dictionary[match])+'}',line)
        line=re.sub(keyword+'_REPLACED_mark',keyword,line)
    return [line, warnings]


def create_label_dictionary(input_file, pattern_in):
    count=0 # number of distinct labels in the dictionary
    dictionary={} # this is the label dictionary
    warnings = [] # duplicate labels warning
    for line_no, current_line in enumerate(input_file, start=1):
        # search for \label{pattern...} in the current line
        for labels in re.finditer('\\\\label\{'
                                  +pattern_in+'.*?\}',current_line):
            # extract {pattern...} from \label{pattern...}
            label=re.search('\{.*?\}',labels.group()).group()
            # insert the UNIQUE label {pattern...} into the label dictionary
            if not label in dictionary:
                count+=1
                dictionary[label]=count
            else:
                col_no=labels.start()+1 # the warning's column number
                warnings.append(['\\label'+label, line_no, col_no])
    input_file.seek(0) # go back to the beginning of the file
    return [dictionary, warnings]


# Main program
if len(sys.argv) !=5:
    print 'Usage: python '+sys.argv[0]+\
          ' <in.tex> <out.tex> <pattern> <replacement>'
    print '(c) Vlad Gheorghiu 2012, vsoftco@gmail.com'
    sys.exit()

if sys.argv[1] == sys.argv[2]:
    print 'Cannot use the same output as the input!'
    sys.exit()

ifile = sys.argv[1] # input file
ofile = sys.argv[2] # output file
p_in  = sys.argv[3] # pattern to replace
p_out = sys.argv[4] # replacement

# standard LaTeX references... feel free to add more
keywords=['label','eqref','ref', 'pageref']

try:
    f_in  = open(ifile)
    try:
        f_out = open(ofile, 'w')
        # create the label dictionary
        [label_dictionary,label_warnings]=create_label_dictionary(f_in, p_in)
        # search and replace
        modified_lines=[] # list with the lines that are modified
        distinct_label_modifications = 0 # count modified \label{pattern...}
        reference_warnings = [] # reference warnings
        # line by line...
        for line_index, current_line in enumerate(f_in, start=1):
            [modified_line, warnings]=\
                search_replace_line(keywords, p_in, p_out, label_dictionary,
                                    current_line, line_index)
            if modified_line!=current_line: # the line was modified
                modified_lines+=[line_index]
            if warnings: # append reference warning(s) from the current line
                reference_warnings += warnings
            f_out.write(modified_line)
        # display the replacements
        print 'REPLACEMENTS:'
        for item in sorted(label_dictionary, key=label_dictionary.get):
            if item !='{'+p_out+str(label_dictionary[item])+'}':
                #modified
                distinct_label_modifications+=1
                print '\t'+item+' -> '+'{'+\
                      p_out+str(label_dictionary[item])+'}'
            else: # not modified
                print '\t'+item+' -> '+'{'+\
                      p_out+str(label_dictionary[item])+'}'+\
                      ' NOT MODIFIED'
        # display the warnings
        if label_warnings or reference_warnings:
            print 'WARNINGS:'
            if label_warnings:
                print 'Additional duplicate labels: '
                for item in label_warnings:
                    print '\t'+item[0]+ ' on line ' + item[1]+\
                          ' at position ' + item[2]
            if reference_warnings:
                print 'Undefined references: '
                for item in reference_warnings:
                    print '\t'+item[0]+ ' on line ' + item[1] +\
                          ' at position ' + item[2]
        else:
            print 'WARNINGS: None'
        # statistics
        print 'STATISTICS:'
        print '\tInput file: ' + ifile
        print '\tOutput file: ' + ofile
        print '\tInput pattern: \\label{'+p_in+'*}'
        print '\tOutput pattern: {'+p_out+'*}'
        print '\tTotal of '+str(len(label_dictionary))+' labels.'
        print '\tReplaced '+ str(distinct_label_modifications)+\
              ' distinct labels.'
        print '\tModified ' +str(len(modified_lines))+' lines: '+\
              str(modified_lines)
        now = datetime.datetime.now()
        print '\tCurrent Time and Date: '+now.strftime("%H:%M:%S %Y/%m/%d ")
    except IOError, iferr:
        print iferr
        if 'f_in' in locals():
            f_in.close()
except IOError, iferr:
    print iferr
    if 'f_out' in locals():
        f_out.close()
