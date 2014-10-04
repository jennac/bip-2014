from csv import DictWriter

# Some QA type reports


def no_ed_match(matched):

    needs_district = []

    for m in matched:
        exclude = m.get('exclude', '')
        if not exclude == 'x':
            if m['ocdid'] == '' or m['ts_id'] == '':
                needs_district.append({'state': m['State'],
                                       'level': m['level'],
                                       'role': m['role'],
                                       'ed': m['Electoral District'],
                                       'ocdid': m['ocdid'],
                                       'type': m['type'],
                                       'name': m['name'],
                                       'ts_id': m['ts_id'],
                                       })

    return needs_district


def numbers_report(matched, state_name):

    ocdid_matched = 0
    all_matched = 0
    statewide = 0
    congress = 0
    state_leg = 0
    lower_level = 0

    for m in matched:
        if not m['ocdid'] == '':
            if not m['ts_id'] == '':
                all_matched += 1
            else:
                ocdid_matched += 1

            ocdid = m['ocdid'].split('/')[-1]

            if 'state' in ocdid:
                statewide += 1
            elif 'cd' in ocdid:
                congress += 1
            elif 'sldl' in ocdid or 'sldu' in ocdid:
                state_leg += 1
            else:
                lower_level += 1


    return {'state_name': state_name,
            'total_rows': len(matched),
            'ocdid_matched': ocdid_matched,
            'all_matched': all_matched,
            'statewide': statewide,
            'congress': congress,
            'state_leg': state_leg,
            'lower_level': lower_level,
            'all_percent': 100 * float(all_matched)/float(len(matched)),
            'ocdid_percent': 100 * float(ocdid_matched)/float(len(matched))
            }


def write_report(qa_data, qa_report, fields, path):

    with open(path + qa_report, 'w') as report:
        writer = DictWriter(report, fieldnames=fields)
        writer.writeheader()
        for q in qa_data:
            writer.writerow(q)
