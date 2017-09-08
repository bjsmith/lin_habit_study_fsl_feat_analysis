from FeatAnalysisMain import FeatAnalysisMain

verbose=True
fam=FeatAnalysisMain(False,version='20170908_olddesigntest')
fam.set_scripts_run_from_server(True)
fam.fsf_first_level_analysis_template_location = "lin-habit-study/analysis/first_level_template20170908_olddesigntest"
fam.ev_files_location="lin-habit-study/analysis/three_col_20170503T124040/"
fam.fsf_preprocessing_path="lin-habit-study/preprocessed_subject_data/june2016replication/"
structural_commands=fam.generate_first_level_script(
    "/Users/benjaminsmith/GDrive/lin-habit-study/analysis/generated_scripts/",
    preprocessing_timestamp='20170511T093930_cleaned',subids=[330])

print(structural_commands)