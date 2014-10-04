from csv import DictReader
import inflect
import re

from match_utils import get_district, no_spaces
import ocdid

# See separate readme for more details on these exceptions
# TODO: MAKE SAID README


# OCDID EXCEPTIONS
def co_exceptions(estimated_ocdid, ed, role):
    if 'school' in role:
        return estimated_ocdid + '/cd:{}'.format(get_district(ed))
    else:
        return ''


def dc_exceptions(estimated_ocdid, ed, role):

    if 'ward' in ed:
        return estimated_ocdid + '/ward:' + ed.strip()[-1]
    else:
        return ''


def il_exceptions(estimated_ocdid, ed):

    if 'appellate' in ed:
        return estimated_ocdid + '/court_of_appeals:{}'.format(get_district(ed))
    elif 'circuit' in ed and 'cook' not in ed:
        return estimated_ocdid + '/circuit_court:{}'.format(get_district(ed))
    else:
        return ''


def ky_exceptions(estimated_ocdid, ed):

    if 'supreme' in ed:
        return estimated_ocdid + '/court_of_appeals:{}'.format(get_district(ed))
    elif 'circuit' in ed:
        return estimated_ocdid + '/circuit_court:{}'.format(get_district(ed))
    elif 'judicial district' in ed:
        return estimated_ocdid + '/district_court:{}'.format(get_district(ed))
    else:
        return ''


def ma_exceptions(estimated_ocdid, ed, role):
    # finish this one day
    if 'councillor district' in ed:
        return None


def nh_exceptions(estimated_ocdid, ed, role):

    if role == 'executivecouncil':
        estimated_ocdid += '/executive_district:' + get_district(ed)
    elif role == 'legislatorlowerbody':
        estimated_ocdid += (u'/sldl:') + get_district(ed)
    elif role == 'legislatorupperbody':
        estimated_ocdid += (u'/sldu:') + get_district(ed)

    return estimated_ocdid


def va_exceptions(estimated_ocdid, ed):
    
    temp_ed = ed.replace('county', '').strip().replace(' ', '_')
    place = estimated_ocdid + '/place:{}'.format(temp_ed.replace('_city', ''))
    if 'county council district' in ed:
        temp_ed = ed.split('district')
        estimated_ocdid = place + '/council_district:{}'.format(temp_ed[-1])
    elif 'muni' in ed:
        temp_ed = ed.split('town')
        estimated_ocdid = estimated_ocdid + '/place:{}'.format(no_spaces(temp_ed[0]))
    else:
        estimated_ocdid = place
        
    if not ocdid.is_ocdid(estimated_ocdid):
        return ''
    else:
        return estimated_ocdid
    
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



#TARGET SMART VF EXCEPTIONS
def dc_ts_exceptions(ocdid, districts):

    suffix = ocdid.split('/')[-1]

    dc_name = ''
    
    if 'district:dc' in suffix:
        dc_type = 'state'
        dc_name = 'DC'
    elif 'ward' in suffix:
        dc_type = 'ward'
    else:
        dc_type = ''

    specific_suffix = suffix.split(':')[-1].strip()
    if dc_type == 'ward':
        possible_names = districts['vf_ward']
        if specific_suffix in possible_names:
            dc_name = possible_names[possible_names.index(specific_suffix)]
    
    return {'type': dc_type,
            'name': dc_name,
            'ts_id': '{}_{}'.format(dc_name, dc_type)
            }


def ma_ts_exceptions(specific_suffix, possible_names):

    p = inflect.engine()

    ed = specific_suffix.split()

    if re.match(r'\d+', ed[0]):
        ordinal_word = p.number_to_words(p.ordinal(int(ed[0][:-2]))).upper()
        ed[0] = ordinal_word
        specific_suffix = ' '.join(ed)

    for p in possible_names:
        if '&' in p:
            p = p.replace('&', 'AND')
        if ',' in p:
            p = p.replace(',', '')
        if specific_suffix in p:
            return p.split()[0]

    return ''


def md_ts_exceptions(specific_suffix, ocdid):
    if 'st_mary~s' in ocdid:
        specific_suffix = specific_suffix.replace('ST', 'SAINT')
    if specific_suffix == 'BALTIMORE':
        specific_suffix += ' COUNTY'

    return specific_suffix

def nh_ts_exceptions(specific_suffix, possible_names):
    nh_floats = {}
    with open('nh-floats.csv', 'rU') as nh_data:
        reader = DictReader(nh_data)
        for row in reader:
            nh_floats[row['float']] = row['regular']
            
        
    specific_suffix = specific_suffix.replace(' ', '')
   
    if specific_suffix in possible_names:
        return no_spaces(possible_names[possible_names.index(specific_suffix)])
    elif specific_suffix + 'F' in nh_floats:
       return specific_suffix + 'F-special-' + nh_floats[specific_suffix + 'F']
    else:
        print specific_suffix
        return ''


def va_ts_exceptions(specific_suffix, possible_names, vf_col):

    if not vf_col == 'vf_township':
        specific_suffix += ' CITY'

    if specific_suffix in possible_names:
        return no_spaces(possible_names[possible_names.index(specific_suffix)])
    else:
        return ''

    
def vt_ts_exceptions(vf_col, specific_suffix, possible_names):
    #print '------------------------------------------' 
    if vf_col == 'vf_sd':
        return 'CHITTENDEN-GRAND ISLE'
    else:
        sections = specific_suffix.split('-')
        nums = get_nums(specific_suffix)
        
        for p in possible_names:
            p_sections = p.split('-')
            if get_nums(p) == nums:
                #print specific_suffix
                if specific_suffix[:3] == p[:3]:
                    if len(sections) == len(p_sections):
                        if 'CALEDONIA' in specific_suffix and  'CALEDONIA' in p:
                            continue
                        else:
                            return p
                else:
                    pass
                    #print sections
                    #print p_sections

                   
#        for p in possible_names:
#            p_sections = p.split('-')
#            if len(sections) == len(p_sections):
#                if 'WINDHAM' == specific_suffix[:7] and p[:3] == 'WDH':
#                    return p
#                elif 'WINDSOR' == specific_suffix[:7] and p[:3] == 'WDR':
#                    return p
#                elif 'ESSEX' == specific_suffix[:5] and p[:3] == 'ESX':
#                    return p
#                if 'GRAND ISLE' == specific_suffix[:10] and p[:2] == 'GI':
#                    return p


    #print 'NOPE: {}'.format(specific_suffix)

    return ''
   
                
        
def get_nums(specific_suffix):
    sections = specific_suffix.split('-')
    nums = ''
    for s in sections:
        if re.match(r'\d', s):
            if len(nums) == 0:
                nums += s
            else:
                nums += '-' + s

    return nums


    
