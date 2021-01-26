#!/usr/bin/env python3

# pytexnumber.py
#
# Renumbers LaTeX references
#
# Type python3 pytexnumber.py --help for help

# Copyright (c) 2013 - 2021 Vlad Gheorghiu. All rights reserved.
#
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse
import re
import sys


# builds the labels dictionary
def build_labels(input_file, pattern_in, ignore_comments):
    count = 0  # number of distinct labels in the dictionary
    dictionary = {}  # this is the label dictionary
    warnings = []  # duplicate labels warning
    for line_no, cur_line in enumerate(input_file, start=1):
        if ignore_comments is True:
            cur_line = cur_line.split('%')[0]
        # search for \label{pattern...} in the current line
        for labels in re.finditer('\\\\label{'
                                  + pattern_in + '.*?}', cur_line):
            # extract {pattern...} from \label{pattern...}
            label = re.search('{.*?}', labels.group()).group()
            # insert the UNIQUE label {pattern...} into the label dictionary
            if label not in dictionary:
                count += 1
                dictionary[label] = count
            else:
                col_no = labels.start() + 1  # the warning's column number
                warnings.append(['\\label' + label, line_no, col_no])
    input_file.seek(0)  # go back to the beginning of the file
    return [dictionary, warnings]


# replaces all matching references in the current line (up to comments if comments are ignored)
def replace_refs_in_line(keywords, pattern_in, pattern_out,
                         dictionary, line, line_idx, ignore_comments):
    warnings = []  # undefined reference(s) warning(s) in (the current line)
    line_no_comments = line
    comment = ""
    if ignore_comments is True:
        line_split = line.split('%', 1)
        line_no_comments = line_split[0]
        if len(line_split) > 1:  # we have a comment
            comment = '%' + line_split[1]

    for keyword in keywords:
        for matches in re.finditer('\\\\' + keyword +
                                   '{' + pattern_in + '.*?}', line_no_comments):
            # extract {pattern...} from \<keyword>{pattern...}
            match = re.search('{.*?}', matches.group()).group()
            # do the replacement whenever the {pattern...} is different
            # from the dictionary key
            if match not in dictionary:
                # undefined reference
                col_no = matches.start() + 1  # the warning's column number
                warnings.append(['\\' + keyword + match, line_idx, col_no])
            if (match in dictionary and
                    ('{' + pattern_out + str(dictionary[match]) + '}') != match):
                line_no_comments = re.sub(keyword + match,
                                          keyword + '_REPLACED_mark'
                                          + '{' + pattern_out +
                                          str(dictionary[match]) + '}', line_no_comments)
        line_no_comments = re.sub(keyword + '_REPLACED_mark', keyword, line_no_comments)
    return [line_no_comments + comment, warnings]


# main program
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Renumbers LaTeX equations.'
                    'The program reads from the standard input and writes to the standard output.')
    parser.add_argument('pattern', nargs='?', help='input pattern, e.g., "eqn"')
    parser.add_argument('replacement', nargs='?', help='replacement pattern, e.g., "Eqn"')
    parser.add_argument('--ignore-comments', dest='comments', action='store_true',
                        help='ignore comments, true by default')
    parser.add_argument('--no-ignore-comments', dest='comments', action='store_false',
                        help='do not ignore comments, false by default')
    parser.set_defaults(comments=True)
    parser.add_argument('--log', help='log file')

    args = parser.parse_args()

    pattern = args.pattern  # pattern to replace
    replacement = args.replacement  # replacement
    ignore_comments = args.comments  # ignore LaTeX comments

    keywords = ['label', 'eqref', 'ref', 'pageref']  # modify as needed

    try:
        # process the stream
        with sys.stdin as f_in, sys.stdout as f_out:
            # create the label dictionary
            [label_dictionary, label_warnings] = build_labels(f_in, pattern, ignore_comments)
            # replace all matching references line by line
            modified_lines = []  # list with the lines that are modified
            distinct_label_modifications = 0  # count modified \label{pattern...}
            reference_warnings = []  # reference warnings
            for line_index, current_line in enumerate(f_in, start=1):
                [modified_line, warnings] = \
                    replace_refs_in_line(keywords, pattern, replacement, label_dictionary,
                                         current_line, line_index, ignore_comments)
                if modified_line != current_line:  # the line was modified
                    modified_lines += [line_index]
                if warnings:  # append reference warning(s) from the current line
                    reference_warnings += warnings
                f_out.write(modified_line)

        # display warnings
        original_stdout = sys.stdout
        sys.stdout = sys.stderr
        if label_warnings or reference_warnings:
            if reference_warnings:
                print('PARSING WARNING: Undefined references')
                for [item, row, col] in reference_warnings:
                    print(item + ', ' + str(row) + ':' + str(col))
            if label_warnings:
                print('PARSING WARNING: Duplicate labels')
                for [item, row, col] in label_warnings:
                    print(item + ', ' + str(row) + ':' + str(col))
        sys.stdout = original_stdout

        # write to log file (if any)
        if args.log is not None:
            try:
                with open(args.log, 'w') as logfile:
                    original_stdout = sys.stdout  # Save a reference to the original standard output
                    sys.stdout = logfile

                    # replacements
                    for item in sorted(label_dictionary, key=label_dictionary.get):
                        item_no_accolades = item
                        remove = ['{', '}']
                        for c in remove:
                            item_no_accolades = item_no_accolades.replace(c, '')
                        print(item_no_accolades + ' -> ' + replacement + str(label_dictionary[item]))
            except IOError as err:
                print(str(err))

    except IOError as err:
        print(str(err))
