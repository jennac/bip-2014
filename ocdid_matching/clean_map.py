import re
from argparse import ArgumentParser
from csv import DictReader, DictWriter
from os import listdir

import ocdid
from ocdidmap_config import Dirs, Assign


def read_candidates(read_file):
    
    """
    Args:
    - candidate data flat file from Dropbox
    Returns:
    - dict with the read in data and the fieldnames
    """
    
    with open(Dirs.TEST_DIR + read_file, 'rU') as r_file:
        #    with open('/Users/jcolazzi/Dropbox/BIP Production/candidates/test_2014/' + read_file, 'rU') as r_file:
        reader = DictReader(r_file)
        fields = reader.fieldnames
        data = [row for row in reader]
        
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
                

def no_zeros(string):  
    
    """
    Removes preprended zeros.
    """ 
    
    while string[0] == '0':
        string = string[1:]
    return string

                
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
        
                
def get_district_num(ed):

    """
    Returns the district number for a given electoral district.
    Note: this might actually be letters or a letter/num combination
    If there is no match, it returns an empty string.
    """
    
    if re.match(r'\d+', ed.split()[-1]):
        return no_zeros(ed.split()[-1])
    elif re.match(r'[a-z]', ed.split()[-1]):
        return ed.split()[-1]
    else:
        return ''


#State exception functions for various state specific scenarios

def dc_exceptions(estimated_ocdid, ed, role):
    
    if role == 'legislatorupperbody':
        return estimated_ocdid + '/ward:' + get_district_num(ed) 

    
def vt_exceptions(estimated_ocdid, office, role):

    suffix = office.split(',')[-1].lower().strip().replace(' ', '-')

    if role == 'legislatorlowerbody':
        estimated_ocdid += (u'/sldl:')
        estimated_ocdid += suffix
    elif role == 'legislatorupperbody':
        estimated_ocdid += (u'/sldu:')
        estimated_ocdid += suffix
    if 'grand-isle' in estimated_ocdid:
        if 'chittenden' not in estimated_ocdid:
            estimated_ocdid = estimated_ocdid.replace('grand-isle', 'grand_isle-chittenden')
        else:
            estimated_ocdid = estimated_ocdid.replace('grand-isle', 'grand_isle')
 
    return estimated_ocdid

##

#Some QA type reports

def office_percentage_report(matched, match_count, unmatched_count, state):

    total = len(matched)
    statewide = 0
    congress = 0 
    stateleg = 0 
    lower_levels = 0
    
    for m in matched:
        ocdid = m['ocdid'].split('/')[-1].split(':')
        if ocdid[0] == 'state':
            statewide += 1
        elif ocdid[0] == 'sldl' or ocdid[0] == 'sldu':
            stateleg += 1
        elif ocdid[0] == 'cd':
            congress += 1
        elif not m['ocdid'] == '':
            lower_levels += 1
    
    if not total == 0:
        percent_statewide = float(statewide)/float(total) * 100
        percent_congress = float(congress)/float(total) * 100
        percent_stateleg = float(stateleg)/float(total) * 100
        percent_lower_levels = float(lower_levels)/float(total) * 100
        percent_matched = float(match_count)/float(total) * 100

    percentage_report =  {
        'state': state.upper(),
        'row_count': total,
        'match_count': match_count,
        'unmatched_count': unmatched_count,
        'statewide': percent_statewide,
        'congress': percent_congress, 
        'stateleg': percent_stateleg,
        'lower_levels': percent_lower_levels,
        'total_matched': percent_matched
        }

    return percentage_report


def write_report(qa_data, qa_report, fields):

    with open(Dirs.REPORTS_DIR + qa_report, 'w') as report:
        writer = DictWriter(report, fieldnames=fields)
        writer.writeheader()
        for q in qa_data:
            writer.writerow(q)
###

def assign_lower(state, ed, office, level, role, estimated_ocdid):
    a1 = 0
    a2 = 0
    r = 0
    s = 0

    #print 'ED: {}\nOffice: {}'.format(ed, office)
    if level == 'administrativearea1':
        a1 += 1
        estimated_ocdid = ''
        #print 'ADMIN1'
    elif level == 'administrativearea2':
        a2 += 1
        #print 'ADMIN2'
        if 'county' in ed:
            if 'council' in ed:
                if 'county council district' in ed:
                    temp_ed = ed.split()
                    estimated_ocdid += '/county:{}/council_district:{}'.format(temp_ed[0], temp_ed[-1])
                    if not ocdid.is_ocdid(estimated_ocdid):
                        estimated_ocdid = ''
            elif 'school' in ed:
                pass
            elif 'subcircuit' in ed:
                pass
            elif 'finance' in ed:
                estimated_ocdid = ''
            else:
                ed = ed.replace('county', '').strip().replace(' ', '_').replace('.', '')
                estimated_ocdid += '/county:{}'.format(ed)
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
        #print 'prolly some bullshit'
    else:
        estimated_ocdid = ''
        #print 'WHAT EVEN IS THIS'

    
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
        ed = d['Electoral District'].lower()
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
            elif state == 'vt':
                estimated_ocdid = vt_exceptions(estimated_ocdid, office, role)
            elif state == 'dc':
                estimated_ocdid = dc_exceptions(estimated_ocdid, ed, role)
            elif role == 'legislatorlowerbody':
                estimated_ocdid += (u'/sldl:') +  get_district_num(ed)
            elif role == 'legislatorupperbody':
                estimated_ocdid += (u'/sldu:') +  get_district_num(ed)
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
    office_percentages = office_percentage_report(matched, match_count, len(unmatched), state)
    print 'a1: {}\na2: {}\nr: {}\ns: {}\n'.format(a1, a2, r, s)

    print possible_errors
    return {'matched': matched, 
            'office_percentage_report': office_percentages,
            'invalid_id_report': possible_errors
            }


def get_level_and_role():
    landr_dict = {}

    with open(Dirs.STAGING_DIR + 'assigned.csv') as with_lr:
        reader = DictReader(with_lr)
        for row in reader: 
            landr_dict[row['UID']] = row

    return landr_dict


def merge_level_and_role(read_data, lower_levels):

    for row in read_data: 
        values = lower_levels.get(row['UID'], None)
        if values:
            row['level'] = values['level']
            row['role'] = values['role']

    return read_data
    

def main():
    usage = 'Assigns OCDIDs to BIP Candidate Files. Essentially, maps Electoral Districts.'
    parser = ArgumentParser(usage=usage)
    parser.add_argument('-s', action='store', dest='state', 
                        default=None, help='Abbreviation of state to assign')
    args = parser.parse_args()

    files = listdir(Dirs.TEST_DIR)
    #files = listdir('/Users/jcolazzi/Dropbox/BIP Production/candidates/test_2014/')
                    
    qa_percentages = []
    qa_invalid_ids = []

    for f in files: 
        if f.startswith('.') or f.startswith('_') or not f.endswith('.csv') or f.startswith('unverified'):
            continue
        elif args.state and not f.startswith(args.state.upper()):
            continue
        else:
            print '------------------------{}--------------------------------------'.format(f)
            read_data = read_candidates(f)
            lower_levels = get_level_and_role()
            read_data['cand_data'] = merge_level_and_role(read_data['cand_data'], lower_levels)
            id_data = assign_ids(read_data['cand_data'])
            matched = id_data['matched']
            
            qa_percentages.append(id_data['office_percentage_report'])

            qa_ids = id_data['invalid_id_report']
            if not len(qa_ids) == 0:
                qa_invalid_ids.extend(qa_ids)
            write_matches(matched, read_data['fields'], f)
            print '\n'

    #Generate QA Reports
    percentage_fields = ['state', 'row_count', 'match_count', 'unmatched_count', 
                         'statewide', 'congress', 'stateleg', 'lower_levels', 'total_matched']
    write_report(qa_percentages, 'Office_Percentages.csv', percentage_fields)

    invalid_id_fields = ['state', 'possible_error']
    write_report(qa_invalid_ids, 'Invalid_IDs.csv', invalid_id_fields)
   
    
            

if __name__=='__main__':
    main()



    #county == adminarea2
    
