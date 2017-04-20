import os
import csv
import json
from collections import defaultdict, OrderedDict
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

def build_token_counts_object():
    acronyms = [
        "omg", "omfg", "lmao", "lmfao", "btw","wtf",
        "nvm", "np", "smh", "ftw"
    ]
    replacement_forms = [
        "for", "you", "u", "your", "ur", "before", "be4", "b4",
        "though", "tho", "because", "becuz", "bcuz", "cuz", "bc",
        "b/c", "what", "wat", "whut", "wut", "people", "ppl", "be", "b"
    ]

    token_counts = OrderedDict()

    token_counts['lol'] = build_count_object(lol_matcher)
    token_counts["k"] = build_count_object(build_acronym_matcher("k", template=r"(^|\s){}($|\s)"))
    token_counts["kk"] = build_count_object(build_acronym_matcher("(kk|kkkk+)", template=r"(^|\s){}($|\s)"))
    for acronym in acronyms:
        token_counts[acronym] = build_count_object(build_acronym_matcher(acronym))

    token_counts["I"] = build_count_object(build_replacement_form_matcher("I", ignorecase=False))
    token_counts["i"] = build_count_object(build_replacement_form_matcher("i", ignorecase=False))
    token_counts["4"] = build_count_object(build_replacement_form_matcher("4", template=r"(^|\s){}($|\s)"))
    for form in replacement_forms:
        token_counts[form] = build_count_object(build_replacement_form_matcher(form))

    token_counts["haha"] = build_count_object(haha_matcher)
    token_counts["hehe"] = build_count_object(hehe_matcher)

    return token_counts


def count_all_in_csv(reader):
    token_counts = build_token_counts_object()
    repeats_dict = defaultdict(lambda: 0)
    
    reader.__next__() # pop off the header

    for entry in reader:
        comment = entry[3] or entry[10]
        repeats = repeated_character_matcher(comment)
        for repeat in repeats:
            repeats_dict[repeat] += 1

        for token in token_counts.keys():
            matches = token_counts[token]['matcher'](comment)
            token_counts[token]['count'] += len(matches)
            token_counts[token]['matches'].extend(matches)

    return ([[token, value['count'], value['matches']]
             for token, value in token_counts.items()],
            sorted(repeats_dict.items(), reverse=True, key=lambda x: x[1]))

def main():
    csv_dir = "csv"
    count_dir = "output"
    for filename in os.listdir(csv_dir):
        name, ext = os.path.splitext(filename)
        if ext != ".csv":
            continue;
        with open(os.path.join(csv_dir, filename), 'r') as csv_file:
            token_counts, repeat_counts = count_all_in_csv(csv.reader(csv_file))
        with open(os.path.join(count_dir, name + "-tokens.csv"), 'w') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(['token', 'count', 'matches'])
            writer.writerows(token_counts)
        with open(os.path.join(count_dir, name + "-repeats.csv"), 'w') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(['word', 'count'])
            writer.writerows(repeat_counts)


if __name__ == '__main__':
    main()
