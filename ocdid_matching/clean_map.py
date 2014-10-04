from argparse import ArgumentParser
from csv import DictReader, DictWriter
from os import listdir

import ocdid
import state_exceptions as se

from match_ts import match_ts_ids, read_districts
from match_utils import get_district, no_spaces
from ocdidmap_config import Dirs, Assign
from qa_checks import no_ed_match, numbers_report, write_report


def read_candidates(read_file):

    with open(Dirs.TEST_DIR + read_file, 'rU') as r_file:
        reader = DictReader(r_file)
        fields = reader.fieldnames
        data = [row for row in reader]

        if 'exlcude' not in fields:
            fields.append('exclude')

    return {'cand_data': data, 'fields': fields}


def write_matches(matched, fields, write_file):

    with open(Dirs.STAGING_DIR + write_file, 'w') as w_file:
        writer = DictWriter(w_file, fieldnames=fields)
        writer.writeheader()
        for m in matched:
            try:
                writer.writerow(m)
            except UnicodeDecodeError:
                print m


def get_prefix(state):

    """
    Generates statewide ocdid for a given state.
    (Except poor DC, they are a district)
    """

    prefix = Assign.OCD_PREFIX

    if state:
        if state == 'dc':
            prefix += 'district:dc'
        else:
            prefix += 'state:{}'.format(state)

    return prefix


def assign_lower(state, ed, office, level, role, estimated_ocdid):
    nothing = False

    if level == 'administrativearea1':
        nothing = True

    elif level == 'administrativearea2':

        if 'county' in ed:
            if state == 'va' and 'city' in ed:
                estimated_ocdid = se.va_exceptions(estimated_ocdid, ed)
            elif 'county council district' in ed:
                temp_ed = ed.split('county council district')
                estimated_ocdid += '/county:{}/council_district:{}'.format(
                    no_spaces(temp_ed[0]), no_spaces(temp_ed[-1].strip())
                )
            elif 'school' in ed:
                nothing = True
            elif 'subcircuit' in ed:
                nothing = True
            elif 'finance' in ed or 'dorchester county judicial' in ed:
                nothing = True
            else:
                ed = ed.replace('county', '').strip().replace(' ', '_').replace('.', '')
                estimated_ocdid += '/county:{}'.format(ed)
        else:
            nothing = True

    elif level == 'regional':

        if state == 'ky':
            estimated_ocdid = se.ky_exceptions(estimated_ocdid, ed)
        elif state == 'il':
            estimated_ocdid = se.il_exceptions(estimated_ocdid, ed)
        elif 'county' in ed and 'district' not in ed:
            ed = ed.replace('county', '').strip().replace(' ', '_').replace('.', '')
            estimated_ocdid += '/county:{}'.format(ed)
        elif 'supreme' in ed:
            estimated_ocdid += 'supreme_court:{}'.format(get_district(ed))
            if not ocdid.is_ocdid(estimated_ocdid):
                nothing = True
        elif 'circuit' in ed:
            nothing = True
        else:
            nothing = True

    elif level == 'locality':
        if state == 'va':
            estimated_ocdid = se.va_exceptions(estimated_ocdid, ed)
        else:
            nothing = True

    elif level == 'special':
        nothing = True

    else:
        nothing = True

    if state == 'co' and 'school' in role:
        estimated_ocdid = se.co_exceptions(estimated_ocdid, ed, role)
        nothing = False

    if nothing:
        estimated_ocdid = ''

    return estimated_ocdid


def assign_ids(data):

    matched = []
    unmatched = []
    possible_errors = []

    match_count = 0

    for d in data:
        nothing = False

        d['Office Name'] = d['Office Name'].strip()
        d['Candidate Name'] = d['Candidate Name'].strip()

        state = d['State'].lower()
        ed = d['Electoral District'].lower().replace('\'', '~').replace('.', '')
        office = d['Office Name'].lower()
        level = d['level'].lower()
        role = d['role'].lower()

        estimated_ocdid = get_prefix(state)

        if level == 'country':
            if role == 'legislatorlowerbody' and not ed == state:
                estimated_ocdid += '/cd:' + get_district(ed)
            elif not ed == state:
                nothing = True

        elif level == 'administrativearea1':
            if ed == state:
                estimated_ocdid = estimated_ocdid
            elif state == 'dc':
                estimated_ocdid = se.dc_exceptions(estimated_ocdid, ed, role)
            elif state == 'ma' and 'councillor district' in ed:
                estimated_ocdid = ''
            elif state == 'nh':
                estimated_ocdid = se.nh_exceptions(estimated_ocdid, ed, role)
            elif state == 'vt':
                estimated_ocdid = se.vt_exceptions(estimated_ocdid, office, role)
            elif role == 'legislatorlowerbody':
                estimated_ocdid += (u'/sldl:') + get_district(ed)
            elif role == 'legislatorupperbody':
                estimated_ocdid += (u'/sldu:') + get_district(ed)
            else:
                nothing = True
        else:
            nothing = True

        if nothing:
            estimated_ocdid = assign_lower(state, ed, office,
                                           level, role, estimated_ocdid)
            if not estimated_ocdid == '':
                nothing = False

        if nothing:
            estimated_ocdid = ''

        if not ocdid.is_ocdid(estimated_ocdid) and not estimated_ocdid == '':
            invalid_id = {'state': state.upper(),
                          'possible_error': repr(estimated_ocdid)}
            possible_errors.append(invalid_id)
            estimated_ocdid = ''
        if not estimated_ocdid == '':
            match_count += 1

        # Exclude stuff for 141003 QA
        excludes = ['IN', 'KY', 'MD']
        if d['State'] in excludes:
            if d['level'].lower() == 'adminisitrativearea2':
                d['exclude'] = 'x'

        d['ocdid'] = estimated_ocdid
        d['ocdid_report'] = ''
        if not any(m['UID'] == d['UID'] for m in matched):
            matched.append(d)

    print 'Rows in flat file: {}'.format(len(matched))
    print 'Matched rows: {}'.format(match_count)
    print 'Unmatched rows: {}\n'.format(len(unmatched))
    print 'POSSIBLE ERRORS:{}'.format(len(possible_errors))

    return {'matched': matched,
            'invalid_id_report': possible_errors
            }


def main():
    usage = 'Assigns OCDIDs to BIP Candidate Files. Essentially, maps Electoral Districts.'
    parser = ArgumentParser(usage=usage)
    parser.add_argument('-s', action='store', dest='state',
                        default=None, help='Abbreviation of state to assign')
    args = parser.parse_args()

    files = listdir(Dirs.TEST_DIR)

    qa_invalid_ids = []
    qa_by_the_numbers = []

    no_ed_matched = []

    all_the_data = []
    all_fields = []

    for f in files:
        if f.startswith('.') or f.startswith('_') or not f.endswith('.csv') or f.startswith('unverified'):
            continue
        elif args.state and not f.startswith(args.state.upper()):
            continue
        else:
            print '------------------------{}--------------------------------------'.format(f)
            read_data = read_candidates(f)

            # match to OCDID
            id_data = assign_ids(read_data['cand_data'])
            matched = id_data['matched']
            all_the_data.extend(matched)

            # match to TS data
            districts = read_districts(f[:2].lower())
            matched = match_ts_ids(matched, districts)

            # Gather QA Data/New Districts
            qa_by_the_numbers.append(numbers_report(matched, f[:2]))

            qa_ids = id_data['invalid_id_report']
            if not len(qa_ids) == 0:
                qa_invalid_ids.extend(qa_ids)

            needs_district = no_ed_match(matched)
            if not len(needs_district) == 0:
                no_ed_matched.extend(needs_district)

            write_matches(matched, read_data['fields'], f)
            all_fields = read_data['fields']


    # Generate QA Reports
    write_report(all_the_data, 'all_states.csv',
                 all_fields, Dirs.REPORTS_DIR)

    numbers_fields = ['state_name', 'total_rows', 'ocdid_matched',
                      'all_matched', 'statewide', 'congress', 'state_leg',
                      'lower_level', 'all_percent', 'ocdid_percent']
    write_report(qa_by_the_numbers, 'Numbers.csv',
                 numbers_fields, Dirs.REPORTS_DIR)

    invalid_id_fields = ['state', 'possible_error']
    write_report(qa_invalid_ids, 'Invalid_IDs.csv',
                 invalid_id_fields, Dirs.REPORTS_DIR)

    no_ed_fields = ['state', 'level', 'role', 'ed',
                    'ocdid', 'type', 'name', 'ts_id']
    write_report(no_ed_matched, 'no_ed_match.csv',
                 no_ed_fields, Dirs.REPORTS_DIR)

if __name__ == '__main__':
    main()
