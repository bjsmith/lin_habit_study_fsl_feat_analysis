from FeatAnalysisMain import FeatAnalysisMain

verbose=True
fam=FeatAnalysisMain(False)
fam.set_scripts_run_from_server(True)
structural_commands=fam.generate_fix_aroma_script(
    "/Users/benjaminsmith/Google Drive/lin-habit-study/analysis/generated_scripts/",
    level_one_timestamp="20170511T093930")

print(structural_commands)


fam.generate_script_to_create_new_preprocessed_cleaned_feat_dirs(
    "/Users/benjaminsmith/Google Drive/lin-habit-study/analysis/generated_scripts/",
    level_one_timestamp="20170511T093930")