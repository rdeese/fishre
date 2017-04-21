# fishre

fishre is a Python script for doing basic corpus analysis of YouTube video
comments, specifically in the CSV format output by 
[philbot9](https://github.com/philbot9)'s [YouTube Comment
Scraper](http://ytcomments.klostermann.ca/).

## Usage

fishre will perform analysis on all CSV files that it finds in the `csv`
directory.

```bash
git clone https://github.com/rdeese/fishre.git
cd fishre
cp -r /path/to/my/comment/csvs /csv
python count_tokens.py
open output
```

After fishre runs, the `output` directory will contain a CSV file of analysis
for each input CSV.

## Analysis

In addition to basic statistics about comment length, fishre records the
frequency and specific occurrences of common computer mediated communication
(CMC) forms:

* acronyms ("lol", "wtf", "omg", etc.)
* alternative orthographies and their standard counterparts ("u"/"you", 
"wat"/"what", etc.)
* laughter variants ("haha" & "hehe")
