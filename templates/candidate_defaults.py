import table_defaults as td
from reformat import contest_id,referendum_id,ed_concat,concat_us,nowtime

class CandidateTemplate():
    def __init__(self,election_key,state_key,candidate_file_location,referenda_file_location,source_prefix=None):
        self.tdt = td.TableDefaultTemplate(election_key,state_key,source_prefix,candidate_file_location=candidate_file_location,referenda_file_location=referenda_file_location)

        self.TABLES = {
            'CONTEST_IMPORT':dict(self.tdt.default_candidate_table().items()+{
                'udcs':dict(self.tdt.default_candidate_table()['udcs'].items() + {
                    'contest_type':'candidate',
                    }.items()),
                'table':'contest_import',
                'columns':{
                    'updated':{'function':nowtime,'columns':()},
                    'identifier':{'function':contest_id,'columns':(2,5,6)},
                    'id_long':{'function':contest_id,'columns':(2,5,6)},
                    'level':3,
                    'role': 4,
                    'state':2,
                    'office':6,
                    'level': 3,
                    'role':4,
                    'id_long': 22,
                    'ed_matched':23,
                    }
                }.items()
            ),

            'BALLOT_CONTEST_IMPORT':dict(self.tdt.default_referenda_table().items() + {
                'udcs':dict(self.tdt.default_candidate_table()['udcs'].items() + {
                    'contest_type':'referendum',
                    'electoral_district_type':'state',
                    'office':'statewide referendum',
                    'level':'administrativeArea1',
                    'role': 'ballotRole',
                    'ed_matched':'True'
                    }.items()),
                'filename':self.tdt.referenda_file_location,
                'table':'ballot_contest_import',
                'columns':{
                    'updated':{'function':nowtime,'columns':()},
                    'identifier':{'function':referendum_id,'columns':(2,3)},
                    'id_long':{'function':referendum_id,'columns':(2,3)},
                    'state':2,
                    'electoral_district_name':2,
                    'electoral_district_id_long':{'function':ed_concat,'columns':(2,),'defaults':{'type':'state'}},
                    }
                }.items()
            ),
            'CANDIDATE_IN_CONTEST_IMPORT':dict(self.tdt.default_candidate_table().items() + {
                'table':'candidate_in_contest_import',
                'columns':{
                    'candidate_id_long':1,
                    'contest_id_long':{'function':contest_id,'columns':(2,5,6)},
                    },
                }.items()
            ),

            'CANDIDATE_IMPORT':dict(self.tdt.default_candidate_table().items() + {
                'table':'candidate_import',
                'columns':{
                    'updated':{'function':nowtime,'columns':()},
                    'id_long':1,
                    'identifier':1,
                    #'office_level':3,
                    #'office_name':5,
                    'name':7,
                    'party':8,
                    'incumbent':10,
                    'phone':11,
                    'mailing_address':12,
                    'candidate_url':13,
                    'email':14,
                    'facebook_url':15,
                    'twitter_name':16,
                    'google_plus_url':17,
                    'wiki_word':18,
                    'youtube':19
                    },
                }.items()
            ),
        }

