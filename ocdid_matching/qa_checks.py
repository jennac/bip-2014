from csv import DictWriter

#Some QA type reports

def no_ed_match(matched):

    needs_district = []
    
    for m in matched:
        if m['ocdid'] == '' or m['ts_id'] == '':
            needs_district.append({'State': m['State'],
                                'ED': m['Electoral District'],
                                'Office': m['Office Name'],
                                'ocdid': m['ocdid'],
                                'type': m['type'],
                                'name': m['name'],
                                'ts_id': m['ts_id'],
                                }
                                
    return needs_district

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


def write_report(qa_data, qa_report, fields, path):

    with open(path + qa_report, 'w') as report:
        writer = DictWriter(report, fieldnames=fields)
        writer.writeheader()
        for q in qa_data:
            writer.writerow(q)
