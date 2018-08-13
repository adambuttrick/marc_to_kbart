#!/usr/bin/env python

import os
import sys
import re
from collections import defaultdict
from pymarc import MARCReader
import unicodecsv

kbart_header = [
    'publication_title',
    'print_identifier',
    'online_identifier',
    'date_first_issue_online',
    'num_first_vol_online',
    'num_first_issue_online',
    'date_last_issue_online',
    'num_last_vol_online',
    'num_last_issue_online',
    'title_url',
    'first_author',
    'title_id',
    'embargo_info',
    'coverage_depth',
    'coverage_notes',
    'publisher_name',
    'location',
    'title_notes',
    'staff_notes',
    'oclc_collection_name',
    'oclc_collection_id',
    'oclc_entry_id',
    'oclc_linkscheme',
    'oclc_number',
    'ACTION'
]


def clean_identifier(n):
    if re.match('[0-9{4}]|-', n):
        return n
    else:
	    n = re.sub('[^0-9]', '', n)
	    return n


def clean_text(s):
    subs = ["r' |/|", '.$', ',$']
    for sub in subs:
        s = re.sub(sub, '', s)

    s = re.sub('\s\:', ': ', s)

    return s


def fix_coverage(s):
    if '-' in s:
        s = s.split('-')
        start = s[0]
        end = s[1]

        return [start, end]

    else:
        return s


def create_file(mrc_file):
    filename = os.path.join(os.getcwd(), mrc_file)
    out_filename = os.path.splitext(filename)[0]+'_kbart.txt'
    with open(out_filename, 'w') as f_out:
        writer = unicodecsv.writer(f_out, dialect='excel-tab')
        writer.writerow(kbart_header)

    return out_filename


def convert(mrc_file, out_filename):
    mrc_filename = os.path.join(os.getcwd(), mrc_file)
    reader = MARCReader(file(mrc_filename))
    for record in reader:
        kbart_entry = defaultdict(lambda: '')
        kbart_marc_mapping = {
            '020': ['z', 'a'],
            '022': ['y', 'a'],
            '035': ['a'],
            '100': ['a'],
            '110': ['a'],
            '245': ['a', 'b'],
            '260': ['b'],
            '700': ['a'],
            '710': ['a'],
            '852': ['b', 'c', 'h', 'i'],
            '856': ['u'],
            '863': ['a'],
            '866': ['a']
        }
        overlap_fields = []
        for key, values in kbart_marc_mapping.items():
            for value in values:
                if record[key]is not None and record[key][value]:
                    field = key+value
                    overlap_fields.append(field)
			
        # print/online identifiers
        if '020a' in overlap_fields:
            kbart_entry['print_identifier'] = clean_identifier(
                record['020']['a'])
            kbart_entry['online_identifier'] = clean_identifier(
                record['020']['a'])
        elif '020z' in overlap_fields:
            kbart_entry['print_identifier'] = clean_identifier(
                record['020']['z'])
            kbart_entry['online_identifier'] = clean_identifier(
                record['020']['z'])
        elif '022a' in overlap_fields:
            kbart_entry['print_identifier'] = clean_identifier(
                record['022']['a'])
            kbart_entry['online_identifier'] = clean_identifier(
                record['022']['a'])
        elif '022y' in overlap_fields:
            kbart_entry['print_identifier'] = clean_identifier(
                record['022']['y'])
            kbart_entry['online_identifier'] = clean_identifier(
                record['022']['y'])

        # oclc_number
        if '035a' in overlap_fields:
            kbart_entry['oclc_number'] = clean_identifier(record['035']['a'])

        # first_author
        if '100a' in overlap_fields:
            kbart_entry['first_author'] = clean_text(record['100']['a'])
        elif '110a' in overlap_fields:
            kbart_entry['first_author'] = clean_text(record['110']['a'])
        elif '700a' in overlap_fields:
            kbart_entry['first_author'] = clean_text(record['700']['a'])
        elif '710a' in overlap_fields:
            kbart_entry['first_author'] = clean_text(record['710']['a'])

        # publication_title
        if '245a' in overlap_fields:
            if '245b' in overlap_fields:
                kbart_entry['publication_title'] = clean_text(record['245']['a'] +
                                                              record['245']['b'])
            else:
                kbart_entry['publication_title'] = clean_text(
                    record['245']['a'])

        # publisher_name
        if '260b' in overlap_fields:
            kbart_entry['publisher_name'] = clean_text(record['260']['b'])

        # location
        if '852i' in overlap_fields:
            kbart_entry['location'] = record['852']['b'] + ' ' + \
                record['852']['c'] + ' ' + \
                record['852']['h'] + ' ' + record['852']['i']
        elif '852h' in overlap_fields:
            kbart_entry['location'] = record['852']['b'] + ' ' + \
                record['852']['c'] + ' ' + record['852']['h']
        elif '852c' in overlap_fields:
            kbart_entry['location'] = record['852']['b'] + \
                ' ' + record['852']['c']
        elif '852b' in overlap_fields:
            kbart_entry['location'] = record['852']['b']

        # title_notes
        if '852z' in overlap_fields:
            kbart_entry['title_notes'] = record['852']['z']

        # title_url
        if '856u' in overlap_fields:
            kbart_entry['title_url'] = record['856']['u']
            kbart_entry['coverage_depth'] = 'fulltext'
        else:
            kbart_entry['coverage_depth'] = 'print'

        # num_first_volume_online
        if '863a' in overlap_fields:
            volume_coverage = fix_coverage(record['863']['a'])
            kbart_entry['num_first_vol_online'] = volume_coverage[0]
            kbart_entry['num_last_vol_online'] = volume_coverage[1]

        # num_first_volume_online
        if '866a' in overlap_fields:
            issue_coverage = fix_coverage(record['866']['a'])
            kbart_entry['date_first_issue_online'] = issue_coverage[0]
            kbart_entry['date_last_issue_online'] = issue_coverage[1]

        with open(out_filename, 'a') as f_out:
            writer = unicodecsv.writer(f_out, dialect='excel-tab')
            result = [kbart_entry[value] for value in kbart_header]
            writer.writerow(result)


if __name__ == '__main__':
    out = create_file(sys.argv[1])
    convert(sys.argv[1], out)
