import os
from utils.process_schema import rip_schema

script_settings = {
        'exception_state_configs':os.path.join(os.environ['BMS_HOME'],'exception_state_configs'),
        'exception_ed_maps':os.path.join(os.environ['BMS_HOME'],'exception_ed_maps'),
        'templates':os.path.join(os.environ['BMS_HOME'],'templates'),
        'candidates':os.path.join(os.environ['DROPBOX_HOME'],'BIP Production','candidates'),
        'voterfiles':os.path.join(os.environ['BMS_HOME'],'voterfiles'),
        'voterfile_pattern':r'TS_Google.*\.txt$',
        'compressed_voterfile_pattern':r'TS_Google.*\.zip$',
        'process_units':os.path.join(os.environ['BMS_HOME'],'process_units'),
        }

#precinct_name = ('vf_county_code','vf_precinct_id','vf_precinct_name')
#locality_name = 'vf_county_name'
HIERARCHY = ['election','state']
timestamp_suffix = 'timestamped'
json_location = os.path.join(os.environ['BMS_HOME'],'json')
reduced_voterfile_name = 'vf_reduced'
candidate_file_name = 'candidates'
voterfile_zip_name = 'voterfile.zip'
voterfile_delimiter = '\t'

DATABASE_CONF = {
        'user':os.environ['PGUSER'],
        'db':os.environ['BBIP_PGDB'],
        'pw':os.environ['PGPASSWORD']
        }

SCHEMA_FILE = os.path.join(os.environ['BMS_HOME'],'config','bip_schema.sql')
SCHEMA_TABLES,SCHEMA_ENUMS,SCHEMA_FKS,SCHEMA_SEQS = rip_schema(SCHEMA_FILE)
SCHEMA_TABLE_DICT = dict((t.name,t) for t in SCHEMA_TABLES)
