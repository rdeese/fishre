import os
import csv
import json
from collections import defaultdict, OrderedDict
from functools import reduce
import regex

# ACRONYMS
lol_regex = regex.compile(r"(^|[^A-z])l+(o+l+)+($|[^A-z])", regex.IGNORECASE)
def lol_matcher(comment):
    return [match[0] for match in lol_regex.finditer(comment)]

def build_acronym_matcher(acronym, template=None):
    if template:
        expression = template.format(acronym)
    else:
        acronym_with_repeats = "".join([letter + "+" for letter in acronym])
        expression = r"(^|[^A-z]){}($|[^A-z])".format(acronym_with_repeats)
    re = regex.compile(expression, regex.IGNORECASE)
    return lambda comment: [match[0] for match in re.finditer(comment)]

# REPLACEMENT FORMS
def build_replacement_form_matcher(word, ignorecase=True,
                                   template=r"(^|[^A-z]){}($|[^A-z])"):
    expression = template.format(word)
    if ignorecase:
        re = regex.compile(expression, regex.IGNORECASE)
    else:
        re = regex.compile(expression)
    return lambda comment: [match[0] for match in re.finditer(comment)]

# WORDS WITH A REPEATED CHARATER
REPEATED_CHAR_REGEX = regex.compile(r"[^.\s]*(?P<char>[^.\s])\g<char>{2,}[^.\s]*", regex.IGNORECASE)
def repeated_character_matcher(comment):
    return [match[0] for match in REPEATED_CHAR_REGEX.finditer(comment)]

# LAUGHTER
haha_regex = regex.compile(r"[^\s]*(h+a+h+a+)+[^\s]*", regex.IGNORECASE)
def haha_matcher(comment):
    return [match[0] for match in haha_regex.finditer(comment)]
hehe_regex = regex.compile(r"[^\s]*(h+e+h+e+)+[^\s]*", regex.IGNORECASE)
def hehe_matcher(comment):
    return [match[0] for match in hehe_regex.finditer(comment)]

def build_count_object(matcher):
    return {
        'count': 0,
        'matches': [],
        'matcher': matcher
    }

def build_acronym_counts_object():
    acronyms = [
        "omg", "omfg", "lmao", "lmfao", "btw","wtf",
        "nvm", "np", "smh", "ftw"
    ]

    acronym_counts = OrderedDict()
    acronym_counts['lol'] = build_count_object(lol_matcher)
    acronym_counts["k"] = build_count_object(build_acronym_matcher("k", template=r"(^|\s){}($|\s)"))
    acronym_counts["kk"] = build_count_object(build_acronym_matcher("(kk|kkkk+)", template=r"(^|\s){}($|\s)"))
    for acronym in acronyms:
        acronym_counts[acronym] = build_count_object(build_acronym_matcher(acronym))
    return acronym_counts

def build_form_counts_object():
    replacement_forms = [
        "for", "you", "u", "your", "ur", "before", "be4", "b4",
        "though", "tho", "because", "becuz", "bcuz", "cuz", "bc",
        "b/c", "what", "wat", "whut", "wut", "people", "ppl", "be", "b"
    ]

    form_counts = OrderedDict()
    form_counts["I"] = build_count_object(build_replacement_form_matcher("I", ignorecase=False))
    form_counts["i"] = build_count_object(build_replacement_form_matcher("i", ignorecase=False))
    form_counts["4"] = build_count_object(build_replacement_form_matcher("4", template=r"(^|\s){}($|\s)"))
    for form in replacement_forms:
        form_counts[form] = build_count_object(build_replacement_form_matcher(form))
    return form_counts

def build_laughter_counts_object():
    laughter_counts = OrderedDict()
    laughter_counts["haha"] = build_count_object(haha_matcher)
    laughter_counts["hehe"] = build_count_object(hehe_matcher)
    return laughter_counts

def format_token_count_table(token_counts, table_name):
    table_header = [[table_name, '', ''], ['token', 'count', 'matches']]
    return table_header + [[token, value['count'], value['matches']]
                           for token, value in token_counts.items()]

def format_repeats_table(repeats_dict):
    table_header = [["WORDS WITH REPEATED LETTERS", ""], ['word', 'count']]
    return table_header + sorted([list(pair) for pair in repeats_dict.items()], reverse=True, key=lambda x: x[1])

def format_output_table(tables):
    max_rows = max([len(table) for table in tables])
    for table in tables:
        num_padding_rows = max_rows - len(table)
        num_cols = len(table[0])
        table.extend(num_padding_rows*[num_cols*['']])
    combined_table = zip(*tables)
    return [reduce(lambda a,b: a+b, row) for row in combined_table]

def format_summary_table(total_length, total_words, num_comments):
    return [
        ["NUMBER OF COMMENTS"], [num_comments],
        ["TOTAL WORDS"], [total_words],
        ["AVERAGE COMMENT LENGTH (CHARACTERS)"], [total_length/num_comments],
        ["AVERAGE COMMENT LENGTH (WORDS)"], [total_words/num_comments],
    ]

def count_all_in_csv(reader):
    acronym_counts = build_acronym_counts_object()
    form_counts = build_form_counts_object()
    laughter_counts = build_laughter_counts_object()
    repeats_dict = defaultdict(lambda: 0)
    total_words = 0
    total_length = 0
    num_comments = 0
    
    reader.__next__() # pop off the header

    for entry in reader:
        comment = entry[3] or entry[10]

        if len(comment) != 0:
            num_comments += 1
        total_length += len(comment)
        total_words += len(comment.split())

        repeats = repeated_character_matcher(comment)
        for repeat in repeats:
            repeats_dict[repeat] += 1

        for token_counts in [acronym_counts, form_counts, laughter_counts]:
            for token in token_counts.keys():
                matches = token_counts[token]['matcher'](comment)
                token_counts[token]['count'] += len(matches)
                token_counts[token]['matches'].extend(matches)

    return (
        format_summary_table(total_length, total_words, num_comments),
        format_token_count_table(acronym_counts, "ACRONYMS"),
        format_token_count_table(form_counts, "REPLACEMENT FORMS"),
        format_token_count_table(laughter_counts, "LAUGHTER"),
        format_repeats_table(repeats_dict)
    )

def main():
    csv_dir = "csv"
    count_dir = "output"
    for filename in os.listdir(csv_dir):
        name, ext = os.path.splitext(filename)
        if ext != ".csv":
            continue;
        with open(os.path.join(csv_dir, filename), 'r') as csv_file:
            tables = count_all_in_csv(csv.reader(csv_file))
            output_table = format_output_table(tables)
        with open(os.path.join(count_dir, name + "-counts.csv"), 'w') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(output_table)


if __name__ == '__main__':
    main()
