import os
import csv
import json
from collections import defaultdict
import regex

lol_regex = regex.compile(r"(^|[^A-z]+)l+o+l+(l*o*l)*($|[^A-z]+)", regex.IGNORECASE)
repeated_char_regex = regex.compile(r"[^.\s]*(?P<char>[^.\s])\g<char>{2,}[^.\s]*", regex.IGNORECASE)

def lol_matcher(comment):
    return [match[0] for match in lol_regex.finditer(comment)]

def repeated_character_matcher(comment):
    return [match[0] for match in repeated_char_regex.finditer(comment)]


def count_all_in_csv(reader):
    """ count the things """
    token_counts = {
        'lol': { 'matcher': lol_matcher, 'count': 0, 'matches': [] }
    }

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
            sorted(repeats_dict.items(), key=lambda x: x[1]))

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
