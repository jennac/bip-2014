import re
from csv import DictReader

    
def no_zeros(string):  
    
    """
    Removes preprended zeros.
    """ 
    
    while string[0] == '0':
        string = string[1:]
    return string

def add_zeros(string):
    
    while len(string) < 3:
        string = '0' + string
    return string

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

def get_district(ed):
    
    dist = ed.split('district')[-1].strip()
    dist = dist.replace(' ', '_')

    return dist

#Used to merge level and role data together after a bulk edit;
# probably don't need to use again    
def get_level_and_role(path):
    landr_dict = {}

    with open(path + 'assigned.csv') as with_lr:
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
    
    
