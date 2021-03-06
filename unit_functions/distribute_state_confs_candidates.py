from config import script_settings,candidate_file_name,voterfile_zip_name
from mac_oshelper import list_helper, join_helper 
import re, os,shutil
import argparse

def write_state_init(election,state):
    shutil.copyfile(os.path.join(script_settings['templates'],'unit_init_candidate.py'),os.path.join(script_settings['process_units'],election,state,'__init__.py'))

def copy_state_conf(state, election, overwrite_init):
    state=state.lower()
    cand_file = [f for f  in os.listdir(os.path.join(script_settings['candidates'],election)) if re.match(r'{state}.*Candidates.*.csv'.format(state=state),f,flags=re.IGNORECASE)]
    voter_file = [f for f in os.listdir(os.path.join(script_settings['voterfiles'],state)) if re.match(script_settings['compressed_voterfile_pattern'],f)]
    if len(cand_file) > 0 and len(voter_file) > 0:
        cand_file = os.path.join(script_settings['candidates'],election,cand_file[0])
        voter_file = os.path.join(script_settings['voterfiles'],state,voter_file[0])
        conf_file = os.path.join(script_settings['exception_state_configs'],election,'state_conf_data_{state}.py'.format(state=state))
        ed_map_file = os.path.join(script_settings['exception_ed_maps'],election,'ed_map_template_{state}.py'.format(state=state))

        if not os.path.exists(os.path.join(script_settings['process_units'],str(election),state)):
            os.makedirs(os.path.join(script_settings['process_units'],str(election),state))
        if os.path.exists(os.path.join(script_settings['process_units'],str(election),state,'ed_map.py')):
            os.remove(os.path.join(script_settings['process_units'],str(election),state,'ed_map.py'))
        if os.path.exists(ed_map_file):
            os.link(ed_map_file,os.path.join(script_settings['process_units'],str(election),state,'ed_map.py'))
        if os.path.exists(os.path.join(script_settings['process_units'],str(election),state,'state_conf_data.py')):
            os.remove(os.path.join(script_settings['process_units'],str(election),state,'state_conf_data.py'))
        if os.path.exists(conf_file):
            os.link(conf_file,os.path.join(script_settings['process_units'],str(election),state,'state_conf_data.py'))
        if os.path.exists(os.path.join(script_settings['process_units'],str(election),state,voterfile_zip_name)):
            os.remove(os.path.join(script_settings['process_units'],str(election),state,voterfile_zip_name))
        os.link(voter_file,os.path.join(script_settings['process_units'],str(election),state,voterfile_zip_name))
        if os.path.exists(os.path.join(script_settings['process_units'],str(election),state,candidate_file_name)):
            os.remove(os.path.join(script_settings['process_units'],str(election),state,candidate_file_name))
        os.symlink(cand_file,os.path.join(script_settings['process_units'],str(election),state,candidate_file_name))
        if overwrite_init or not os.path.exists(os.path.join(script_settings['process_units'],election,state,'__init__.py')):
            write_state_init(election,state)
        """
        with open(conf_file,'r') as f, open(os.path.join(script_settings['process_units'],state,'state_conf.py'),'w') as g, open(ed_map_file,'r') as h, open(os.path.join(script_settings['process_units'],state,'ed_map.py'),'w') as j:
            if overwrite_init:
                write_init(state)
            for n in h:
                j.write(n)
            for n in f:
                if 'state_specific.STATE' in n:
                    g.write(n.replace('NJ',state.upper()))
                elif 'state_specific.UNCOMPRESSED_VOTER_FILE_LOCATION' in n:
                    g.write(n.replace('example',os.path.join(script_settings['voterfiles'],state,voter_file.replace('.zip','.txt'))))
                else:
                    g.write(n)
        """

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='''
    distribute ed_map and state_conf. Create process units if they
    do not already exist
    distributes to all states by default, but can be limited by include
    and exclude parameters
    ''')
    parser.add_argument('-i', '--include', help="states to include",nargs='*',default=[])
    parser.add_argument('-x', '--exclude', help="states to exclude",nargs='*',default=[])
    parser.add_argument('-e', '--election', help="election to process",type=int,default=-1)
    parser.add_argument('-o', '--overwrite', help="overwrite present __init__ files with default values",action='store_true')
    args = parser.parse_args()
    if args.election > 0:
        elections = [str(args.election)]
    else:
        elections = list_helper(os.listdir(script_settings['candidates']))
    for election in elections:
        if not os.path.exists(os.path.join(script_settings['process_units'],str(election))):
            os.makedirs(os.path.join(script_settings['process_units'],str(election)))
        with open(os.path.join(script_settings['process_units'],election,'__init__.py'),'w') as election_init:
            states = [re.match(r'(?P<state>\w\w)\s.*Candidates.csv',f,flags=re.IGNORECASE).groupdict()['state'] for f  in list_helper(os.listdir(os.path.join(script_settings['candidates'],election))) if re.match(r'(?P<state>\w\w)\s.*Candidates.csv',f,flags=re.IGNORECASE)]
            for state in states:
                if (len(args.include) == 0 or state.lower() in [i.lower() for i in args.include]) and (len(args.exclude) == 0 or state.lower() in [x.lower() for x in args.exclude]):
                    copy_state_conf(state,election,args.overwrite)
