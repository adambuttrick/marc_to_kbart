Basic script for converting MARC records into OCLC KBART format. Includes text and identifier cleaning, and some rudimentary coverage field parsing. Inconsistencies in the delineation of coverage in marc records make covering all the edge cases difficult, but formatted to be extended as needed.

Requires pymarc and  unicodecsv. Python 2.7 because some pymarc objects weren't playing nice with 3.6.

usage: convert.py foo.mrc