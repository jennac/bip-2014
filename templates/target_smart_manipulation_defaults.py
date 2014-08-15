import table_defaults as td

class TargetSmartManipulationDataTemplate():
    def __init__(self,table_import_data,electoral_district_union=None,electoral_district_precinct_union=None):
        self.table_import_data=table_import_data
        self.tdt = table_import_data.tdt

        self.TABLES = {}

        for ed_def in table_import_data.ed_defs:
            self.TABLES[ed_def['district_import'].replace('IMPORT','ACTUAL')]=self.electoral_district_actual(ed_def['import_table'])
            #self.TABLES[ed_def['district_precinct_import'].replace('IMPORT','ACTUAL')]=self.electoral_district_precinct_actual(ed_def['precinct_join_import_table'])

        self.UNIONS = {
        
        }

    def electoral_district_actual(self,import_table):
        return dict(self.tdt.DEFAULT_ACTUAL_TABLE.items() + {
            'schema_table':'electoral_district',
            'import_table':import_table,
            'long_fields':({'long':'id_long','real':'id'},),
            'long_from':('id_long',),
            'distinct_on':('id_long',),
            }.items())
