from match_utils import get_district, get_district_num, no_zeros
import ocdid


def dc_exceptions(estimated_ocdid, ed, role):
    
    if role == 'legislatorupperbody':
        return estimated_ocdid + '/ward:' + get_district_num(ed) 


def ma_exceptions(estimated_ocdid, ed, role):
    #finish this one day
    if 'councillor district' in ed:
        return None

def nh_exceptions(estimated_ocdid, ed, role):
    
    if role == 'executivecouncil':
        estimated_ocdid += '/executive_district:' + get_district_num(ed)
    elif role == 'legislatorlowerbody':
        estimated_ocdid += (u'/sldl:') +  get_district(ed)
    elif role == 'legislatorupperbody':
        estimated_ocdid += (u'/sldu:') +  get_district(ed)

    return estimated_ocdid


def va_exceptions(estimated_ocdid, ed, role):
    temp_ed = ed.replace('county', '').strip().replace(' ', '_')
    place = estimated_ocdid + '/place:{}'.format(temp_ed.replace('_city', ''))
    if 'county council district' in ed:
        temp_ed = ed.split('district')
        estimated_ocdid = place + '/council_district:{}'.format(temp_ed[-1])
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
