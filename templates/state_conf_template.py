import os, imp
import target_smart_defaults as tsd
import target_smart_manipulation_defaults as tsmd
import candidate_defaults as cd
import candidate_manipulation_defaults as cmd
from config import reduced_voterfile_name,candidate_file_name,voterfile_zip_name



class StateConfTemplate():
    def __init__(self,unit,ed_defs=(),EXTRA_DISTRICTS=None,COUNTY_SCHOOL_DISTRICT=False,COUNTY_JUDICIAL_DISTRICT=False,ed_map_wrapper=None,VOTER_FILE_DISTRICTS=None):
        #self.COUNTY_SCHOOL_DISTRICT = COUNTY_SCHOOL_DISTRICT
        #self.COUNTY_JUDICIAL_DISTRICT = COUNTY_JUDICIAL_DISTRICT
        #self.UNCOMPRESSED_VOTER_FILE_ZIP_LOCATION = os.path.join(unit.__path__[0],voterfile_zip_name)
        #self.EXTRA_DISTRICTS = EXTRA_DISTRICTS
        #self.tst = tsd.TargetSmartTemplate(unit.election_key,unit.state_key,os.path.join(unit.__path__[0],reduced_voterfile_name),'_'.join(unit.partition_suffixes),ed_defs)
        #self.VOTER_FILE_DISTRICTS = VOTER_FILE_DISTRICTS or self.tst.VOTER_FILE_DISTRICTS
        #self.REDUCED_VOTER_FILE_LOCATION = self.tst.VOTER_FILE_LOCATION
        #self.ed_defs = self.tst.ed_defs
        #self.ed_map_wrapper = ed_map_wrapper
        pass

    def post_district_trigger(self,unit):
        #self.ed_map_template = unit.ed_map.EdMapTemplate(unit.districts,self.COUNTY_SCHOOL_DISTRICT, self.COUNTY_JUDICIAL_DISTRICT)
        #if self.ed_map_wrapper:
        #    self.ed_map=self.ed_map_wrapper(self.ed_map_template.ed_map)
        #else:
        #    self.ed_map=self.ed_map_template.ed_map
        self.ct = cd.CandidateTemplate(unit.election_key,unit.state_key,os.path.join(unit.__path__[0],candidate_file_name),os.path.join(unit.__path__[0],'referenda'))
        #self.tsmdt = tsmd.TargetSmartManipulationDataTemplate(self.tst)
        self.cmdt = cmd.CandidateManipulationDataTemplate(self.ct)
        self.IMPORT_TABLES = self.ct.TABLES.values()#+self.tst.TABLES.values()
        self.ACTUAL_TABLES = self.cmdt.TABLES.values()#+self.tsmdt.TABLES.values()
        self.UNIONS = self.cmdt.UNIONS.values()#+self.tsmdt.UNIONS.values()
