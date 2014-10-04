import json
import re

from fuzzywuzzy import fuzz

import state_exceptions as se
from match_utils import add_zeros, no_spaces
from ocdidmap_config import Dirs


def read_districts(state):

    path = Dirs.DISTRICT_DIR + state + '/'
    filename = '{}_all_districts.json'.format(state)

    with open(path + filename) as data_file:
        districts = json.load(data_file)

    return districts


def which_level(type):

    high = ['vf_cd', 'vf_hd', 'vf_sd', 'vf_source_state',
            'vf_county_name', 'vf_township']
    if type in high:
        return 'high'
    else:
        return 'low'


def get_type(ocdid, ed):

    if ocdid == '':
        return None

    suffix = ocdid.split('/')[-1]

    if 'sldl:' in suffix:
        return {'state_rep_district': 'vf_hd'}

    elif 'sldu:' in suffix:
        return {'state_senate_district': 'vf_sd'}

    elif 'cd:' in suffix:
        return {'congressional_district': 'vf_cd'}

    elif 'state:' in suffix:
        return {'state': 'vf_source_state'}

    elif 'state:va' in ocdid and 'place' in suffix:
        if 'muni' not in ed.lower():
            return {'county': 'vf_county_name'}

    elif 'place' in ocdid and 'muni' in ed.lower():
        return {'township': 'vf_township'}

    elif 'council_district:' in suffix:
        return {'county_council': 'vf_county_council'}

    elif 'county:' in suffix:
        return {'county': 'vf_county_name'}

    elif 'court' in suffix:
        return {'judicial district': 'vf_judicial_district'}

    else:
        return None


def get_high_level(vf_col, ocdid, districts):

    # Reads in all possible districts as ripped from the VF
    possible_names = districts[vf_col]

    # Pull most specific section of the ocdid & clean up
    suffix = ocdid.split('/')[-1]
    specific_suffix = suffix.split(':')[-1].upper().replace('_', ' ').replace('~', '')

    if re.match(r'[0-9]+', specific_suffix):
        specific_suffix = add_zeros(specific_suffix)
    if 'state:md' in ocdid:
        specific_suffix = se.md_ts_exceptions(specific_suffix, ocdid)

    # Check for state exception cases
    if 'state:nh' in ocdid:
        if vf_col == 'vf_hd':
            return se.nh_ts_exceptions(specific_suffix, possible_names)
    elif 'state:ma' in ocdid:
        if vf_col == 'vf_hd' or vf_col == 'vf_sd':
            return se.ma_ts_exceptions(specific_suffix, possible_names)
    elif 'state:vt' in ocdid:
        if vf_col == 'vf_hd' or 'GRAND ISLE' in specific_suffix:
            return se.vt_ts_exceptions(vf_col, specific_suffix, possible_names)
    elif 'state:va' in ocdid and 'place:' in ocdid:
        return se.va_ts_exceptions(specific_suffix, possible_names, vf_col)

    # Match to possible districts if there are no exceptions
    if specific_suffix in possible_names:
        return no_spaces(possible_names[possible_names.index(specific_suffix)])
    else:
        for p in possible_names:
            if fuzz.ratio(specific_suffix, p) >= 90:
                return no_spaces(possible_names[possible_names.index(p)])
            elif fuzz.partial_ratio(specific_suffix, p) >= 90:
                return no_spaces(possible_names[possible_names.index(p)])
            else:
                return ''


def get_name(vf_col, ocdid, districts, state):

    full_name = ''
    small = ['IN', 'NJ', 'NM', 'OK']

    ocdid_split = ocdid.split('/')
    suffix = ocdid_split[-1]
    specific_suffix = suffix.split(':')[-1].upper()

    if re.match(r'[0-9]+', specific_suffix):
            specific_suffix = add_zeros(specific_suffix)

    possible_names = districts[vf_col]

    if which_level(vf_col) == 'high':
        full_name = get_high_level(vf_col, ocdid, districts)

    else:
        if vf_col == 'vf_county_council':

            if state in small and re.match(r'[0-9]+', specific_suffix):
                specific_suffix = specific_suffix[1:]

            county_ocdid = ocdid.split('/council_district')[0]
            county = get_high_level('vf_county_name', county_ocdid, districts)

            for p in possible_names:
                if specific_suffix == p:
                    index = possible_names.index(specific_suffix)
                    full_name = '{}_{}'.format(county, possible_names[index])
                elif county in p and len(county) > 2:
                    if ocdid.split(':')[-1] in p:
                        full_name = '{}_{}'.format(county, specific_suffix)
        elif vf_col == 'vf_judicial_district':
            # print ocdid
            # print possible_names
            pass

    # print 'FULL NAME: {}'.format(full_name)

    return full_name


def match_ts_ids(matched, districts):

    for m in matched:
        ocdid = m['ocdid']

        if m['State'].upper() == 'DC':
            dc_data = se.dc_ts_exceptions(ocdid, districts)
            m['type'] = dc_data['type']
            m['name'] = dc_data['name']
            m['ts_id'] = dc_data['ts_id']
            continue

        ts_type = get_type(ocdid, m['Electoral District'])

        if ts_type is not None:
            m['type'] = ts_type.keys()[0]
            m['name'] = get_name(ts_type[m['type']], ocdid,
                                 districts, m['State'])
            if not m['name'] == '':
                m['ts_id'] = '{}_{}'.format(m['name'], m['type'])
            else:
                m['ts_id'] = ''

        else:
            m['type'] = ''
            m['name'] = ''
            m['ts_id'] = ''

    return matched


# [u'vf_county_name', u'vf_judicial_district', u'vf_township',
#  u'vf_county_council', u'vf_school_district', u'vf_cd', u'vf_hd',
#  u'vf_municipal_district', u'vf_source_state', u'vf_ward',
#  u'vf_city_council', u'vf_sd']
