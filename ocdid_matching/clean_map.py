import re
from argparse import ArgumentParser
from csv import DictReader, DictWriter
from os import listdir

import ocdid
import state_exceptions as se

#get_district_num soon to be depricated
from match_ts import match_ts_ids, read_districts
from match_utils import get_district, get_district_num, no_zeros, get_level_and_role, merge_level_and_role
from ocdidmap_config import Dirs, Assign
from qa_checks import no_ed_match, office_percentage_report, write_report


def read_candidates(read_file):
    
    """
    Args:
    - candidate data flat file from Dropbox
    Returns:
    - dict with the read in data and the fieldnames
    """
    
    with open(Dirs.TEST_DIR + read_file, 'rU') as r_file:
        reader = DictReader(r_file)
        fields = reader.fieldnames
        data = [row for row in reader]

        if 'type' not in fields:
            fields.append('type')
        if 'name' not in fields:
            fields.append('name')
        if 'ts_id' not in fields:
            fields.append('ts_id')
        
    return {'cand_data': data, 'fields': fields}


def write_matches(matched, fields, write_file):
    
    with open(Dirs.STAGING_DIR + write_file, 'w') as w_file:
        writer = DictWriter(w_file, fieldnames=fields)
        writer.writeheader()
        for m in matched:
            try:
                writer.writerow(m)
            except UnicodeDecodeError:
                print row
                
                
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
    a1 = 0
    a2 = 0
    r = 0
    s = 0

    #print 'ED: {}\nOffice: {}'.format(ed, office)
    if level == 'administrativearea1':
        a1 += 1
        estimated_ocdid = ''
    elif level == 'administrativearea2':
        a2 += 1
        if 'county' in ed:
            if state == 'va' and 'city' in ed:
                estimated_ocdid = se.va_exceptions(estimated_ocdid, ed, role)
            elif 'county council district' in ed:
                temp_ed = ed.split()
                estimated_ocdid += '/county:{}/council_district:{}'.format(temp_ed[0], temp_ed[-1])
                if not ocdid.is_ocdid(estimated_ocdid):
                    estimated_ocdid = ''
            elif 'school' in ed:
                #print ed
                #temp_ed = ed.split('school board district')
                #ed = temp_ed[0].replace('county', '').strip().replace(' ', '_').replace('.', '')
                #estimated_ocdid += '/county:{}/school_district:{}'.format(ed, temp_ed[-1].strip())
                estimated_ocdid = ''
            elif 'subcircuit' in ed:
                estimated_ocdid = ''
            elif 'finance' in ed:
                estimated_ocdid = ''
            else:
                ed = ed.replace('county', '').strip().replace(' ', '_').replace('.', '')
                estimated_ocdid += '/county:{}'.format(ed)
        else: 
            #until muni support
            estimated_ocdid = ''
    elif level == 'regional':
        r += 1
        num = get_district_num(ed)
        if 'supreme' in ed:
            estimated_ocdid += 'supreme_court:{}'.format(num)
            if not ocdid.is_ocdid(estimated_ocdid):
                estimated_ocdid = ''
        elif 'circuit' in ed:
            pass
        estimated_ocdid = ''
    elif level == 'special':
        s += 1
        estimated_ocdid = ''
    else:
        estimated_ocdid = ''

    
    return (estimated_ocdid, (a1, a2, r, s))


def assign_ids(data):

    matched = []
    unmatched = []
    possible_errors = []

    match_count = 0

    a1 = 0
    a2 = 0
    r = 0
    s = 0

    for d in data:
        d['Office Name'] = d['Office Name'].strip()
        d['Candidate Name'] = d['Candidate Name'].strip()
        
        state = d['State'].lower()
        ed = d['Electoral District'].lower().replace('\'', '~')
        office = d['Office Name'].lower()
        level = d['level'].lower()
        role = d['role'].lower()
        
        estimated_ocdid = get_prefix(state)
         
        if level == 'country': 
            if role == 'legislatorlowerbody' and not ed == state:
                estimated_ocdid += '/cd:' + get_district_num(ed)
            elif not ed == state:
                estimated_ocdid = ''
            
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
                estimated_ocdid += (u'/sldl:') +  get_district(ed)
            elif role == 'legislatorupperbody':
                estimated_ocdid += (u'/sldu:') +  get_district(ed)
            else:
                unmatched.append(d)
        else:
            #estimated_ocdid = assign_lower(state, ed, office, level, role, estimated_ocdid)
            lower_data = assign_lower(state, ed, office, level, role, estimated_ocdid)
            if not lower_data[0] == '':
                matched.append(d)
            else:
                unmatched.append(d)
            estimated_ocdid = lower_data[0]
            a1 += lower_data[1][0]
            a2 += lower_data[1][1]
            r += lower_data[1][2]
            s += lower_data[1][2]

        
            
        if not ocdid.is_ocdid(estimated_ocdid) and not estimated_ocdid=='':
            invalid_id = {'state': state.upper(), 'possible_error': repr(estimated_ocdid)}
            possible_errors.append(invalid_id)
        if not estimated_ocdid=='':
            match_count += 1

        d['ocdid'] = estimated_ocdid
        d['ocdid_report'] = ''
        matched.append(d)

    
    print 'Rows in flat file: {}'.format(len(matched))
    print 'Matched rows: {}'.format(match_count)
    print 'Unmatched rows: {}\n'.format(len(unmatched))
    office_percentages = office_percentage_report(matched, len(data), len(unmatched), state)
    print 'a1: {}\na2: {}\nr: {}\ns: {}\n'.format(a1, a2, r, s)

    print 'POSSIBLE ERRORS:{}'.format(possible_errors)
    return {'matched': matched, 
            'office_percentage_report': office_percentages,
            'invalid_id_report': possible_errors
            }


def main():
    usage = 'Assigns OCDIDs to BIP Candidate Files. Essentially, maps Electoral Districts.'
    parser = ArgumentParser(usage=usage)
    parser.add_argument('-s', action='store', dest='state', 
                        default=None, help='Abbreviation of state to assign')
    args = parser.parse_args()

    files = listdir(Dirs.TEST_DIR)
                    
    qa_percentages = []
    qa_invalid_ids = []

    needs_district = []


    for f in files: 
        if f.startswith('.') or f.startswith('_') or not f.endswith('.csv') or f.startswith('unverified'):
            continue
        elif args.state and not f.startswith(args.state.upper()):
            continue
        else:
            print '------------------------{}--------------------------------------'.format(f)
            read_data = read_candidates(f)

            #assign level and role from bulk file
            lower_levels = get_level_and_role(Dirs.STAGING_DIR)
            read_data['cand_data'] = merge_level_and_role(read_data['cand_data'], lower_levels)

            #match to OCDID
            id_data = assign_ids(read_data['cand_data'])
            matched = id_data['matched']

            #match to TS data
            #districts = read_districts(f[:2].lower())
            #matched = match_ts_ids(matched, districts)

            #Gather QA Data/New Districts
            qa_percentages.append(id_data['office_percentage_report'])

            qa_ids = id_data['invalid_id_report']
            if not len(qa_ids) == 0:
                qa_invalid_ids.extend(qa_ids)
                
            no_ed_match = no_ed_match(matched) 
            if not len(no_ocdid) == 0:
                needs_district.extend(no_ocdid) 
                
            write_matches(matched, read_data['fields'], f)
            print '\n'


            
    #Generate QA Reports
    percentage_fields = ['state', 'row_count', 'match_count', 'unmatched_count', 
                         'statewide', 'congress', 'stateleg', 'lower_levels', 'total_matched']
    write_report(qa_percentages, 'Office_Percentages.csv', percentage_fields, Dirs.REPORTS_DIR)

    invalid_id_fields = ['state', 'possible_error']
    write_report(qa_invalid_ids, 'Invalid_IDs.csv', invalid_id_fields, Dirs.REPORTS_DIR)

    write_report(no_ocdid
    
            

if __name__=='__main__':
    main()


