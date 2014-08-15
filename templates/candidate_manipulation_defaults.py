
import table_defaults as td

class CandidateManipulationDataTemplate():
    def __init__(self,table_import_data):
        self.table_import_data=table_import_data
        self.tdt = table_import_data.tdt

        self.TABLES = {
            'CONTEST_ACTUAL':dict(self.tdt.DEFAULT_ACTUAL_TABLE.items() + {
                'schema_table':'contest',
                'import_table':self.table_import_data.TABLES['CONTEST_IMPORT']['table'],
                'long_fields':({'long':'id_long','real':'id'},{'long':'electoral_district_id_long','real':'electoral_district_id'}),
                'distinct_on':('id_long',),
                'long_from':('id_long',),
                'long_to':(
                    {
                        'to_table':'electoral_district_import',
                        'local_key':'electoral_district_id_long',
                        'to_key':'id_long',
                        'real_to_key':'id',
                        },
                    ),
                }.items()
            ),

            'BALLOT_CONTEST_ACTUAL':dict(self.tdt.DEFAULT_ACTUAL_TABLE.items() + {
                'schema_table':'contest',
                'import_table':self.table_import_data.TABLES['BALLOT_CONTEST_IMPORT']['table'],
                'long_fields':({'long':'id_long','real':'id'},{'long':'electoral_district_id_long','real':'electoral_district_id'}),
                'long_from':('id_long',),
                'long_to':(
                    {
                        'to_table':'electoral_district_import',
                        'local_key':'electoral_district_id_long',
                        'to_key':'id_long',
                        'real_to_key':'id',
                        },
                    ),
                }.items()
            ),
            'CANDIDATE_IN_CONTEST_ACTUAL':dict(self.tdt.DEFAULT_ACTUAL_TABLE.items() + {
                'schema_table':'candidate_in_contest',
                'import_table':self.table_import_data.TABLES['CANDIDATE_IN_CONTEST_IMPORT']['table'],
                'long_fields':({'long':'candidate_id_long','real':'candidate_id'},{'long':'contest_id_long','real':'contest_id'}),
                'long_to':(
                    {
                        'to_table':'candidate_import',
                        'local_key':'candidate_id_long',
                        'to_key':'id_long',
                        'real_to_key':'id'
                        },
                    {
                        'to_table':'contest_import',
                        'local_key':'contest_id_long',
                        'to_key':'id_long',
                        'real_to_key':'id'
                        }
                    )
                }.items()
            ),

            'CANDIDATE_ACTUAL':dict(self.tdt.DEFAULT_ACTUAL_TABLE.items() + {
                'schema_table':'candidate',
                'import_table':self.table_import_data.TABLES['CANDIDATE_IMPORT']['table'],
                'long_fields':({'long':'id_long','real':'id'},),
                'long_from':('id_long',),
                }.items()
            ),
        }
        self.UNIONS = {
            
        }

