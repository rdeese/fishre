import os
import csv
import json
from collections import defaultdict, OrderedDict
import regex

# ACRONYMS
lol_regex = regex.compile(r"(^|[^A-z])l+o+l+(l*o*l)*($|[^A-z])", regex.IGNORECASE)

# REPLACEMENT FORMS
def build_replacement_form_matcher(word, ignorecase=True,
                                   template=r"(^|[^A-z]){}($|[^A-z])"):
    expression = template.format(word)
    if ignorecase:
        re = regex.compile(expression, regex.IGNORECASE)
    else:
        re = regex.compile(expression)
    return lambda comment: [match[0] for match in re.finditer(comment)]

you_matcher = build_replacement_form_matcher("you")
u_matcher = build_replacement_form_matcher("u")
your_matcher = build_replacement_form_matcher("your")
ur_matcher = build_replacement_form_matcher("ur")
I_matcher = build_replacement_form_matcher("I", ignorecase=False)
i_matcher = build_replacement_form_matcher("i", ignorecase=False)
for_matcher = build_replacement_form_matcher("for")
number_4_matcher = build_replacement_form_matcher("4", template=r"(^|\s){}($|\s)")
before_matcher = build_replacement_form_matcher("before")
be4_matcher = build_replacement_form_matcher("be4")
b4_matcher = build_replacement_form_matcher("b4")
though_matcher = build_replacement_form_matcher("though")
tho_matcher = build_replacement_form_matcher("tho")
because_matcher = build_replacement_form_matcher("because")
becuz_matcher = build_replacement_form_matcher("becuz")
bcuz_matcher = build_replacement_form_matcher("bcuz")
cuz_matcher = build_replacement_form_matcher("cuz")
bc_matcher = build_replacement_form_matcher("bc")
bslashc_matcher = build_replacement_form_matcher("b/c")
what_matcher = build_replacement_form_matcher("what")
wat_matcher = build_replacement_form_matcher("wat")
whut_matcher = build_replacement_form_matcher("whut")
wut_matcher = build_replacement_form_matcher("wut")
people_matcher = build_replacement_form_matcher("people")
ppl_matcher = build_replacement_form_matcher("ppl")
be_matcher = build_replacement_form_matcher("be")
b_matcher = build_replacement_form_matcher("b")

# WORDS WITH A REPEATED CHARATER
repeated_char_regex = regex.compile(r"[^.\s]*(?P<char>[^.\s])\g<char>{2,}[^.\s]*", regex.IGNORECASE)

def lol_matcher(comment):
    return [match[0] for match in lol_regex.finditer(comment)]

def repeated_character_matcher(comment):
    return [match[0] for match in repeated_char_regex.finditer(comment)]


def count_all_in_csv(reader):
    """ count the things """
    token_counts = OrderedDict()
    token_counts['lol'] = { 'matcher': lol_matcher, 'count': 0, 'matches': [] }
    token_counts['you'] = { 'matcher': you_matcher, 'count': 0, 'matches': [] }
    token_counts['u'] = { 'matcher': u_matcher, 'count': 0, 'matches': [] }
    token_counts['your'] = { 'matcher': your_matcher , 'count': 0, 'matches': [] }
    token_counts['ur'] = { 'matcher': ur_matcher , 'count': 0, 'matches': [] }
    token_counts['I'] = { 'matcher': I_matcher , 'count': 0, 'matches': [] }
    token_counts['i'] = { 'matcher': i_matcher , 'count': 0, 'matches': [] }
    token_counts['for'] = { 'matcher': for_matcher , 'count': 0, 'matches': [] }
    token_counts['4'] = { 'matcher': number_4_matcher , 'count': 0, 'matches': [] }
    token_counts['before'] = { 'matcher': before_matcher , 'count': 0, 'matches': [] }
    token_counts['be4'] = { 'matcher': be4_matcher , 'count': 0, 'matches': [] }
    token_counts['b4'] = { 'matcher': b4_matcher , 'count': 0, 'matches': [] }
    token_counts['though'] = { 'matcher': though_matcher , 'count': 0, 'matches': [] }
    token_counts['tho'] = { 'matcher': tho_matcher , 'count': 0, 'matches': [] }
    token_counts['because'] = { 'matcher': because_matcher , 'count': 0, 'matches': [] }
    token_counts['becuz'] = { 'matcher': becuz_matcher , 'count': 0, 'matches': [] }
    token_counts['bcuz'] = { 'matcher': bcuz_matcher , 'count': 0, 'matches': [] }
    token_counts['cuz'] = { 'matcher': cuz_matcher , 'count': 0, 'matches': [] }
    token_counts['bc'] = { 'matcher': bc_matcher , 'count': 0, 'matches': [] }
    token_counts['b/c'] = { 'matcher': bslashc_matcher , 'count': 0, 'matches': [] }
    token_counts['what'] = { 'matcher': what_matcher , 'count': 0, 'matches': [] }
    token_counts['wat'] = { 'matcher': wat_matcher , 'count': 0, 'matches': [] }
    token_counts['whut'] = { 'matcher': whut_matcher , 'count': 0, 'matches': [] }
    token_counts['wut'] = { 'matcher': wut_matcher , 'count': 0, 'matches': [] }
    token_counts['people'] = { 'matcher': people_matcher , 'count': 0, 'matches': [] }
    token_counts['ppl'] = { 'matcher': ppl_matcher , 'count': 0, 'matches': [] }
    token_counts['be'] = { 'matcher': be_matcher , 'count': 0, 'matches': [] }
    token_counts['b'] = { 'matcher': b_matcher , 'count': 0, 'matches': [] }

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
