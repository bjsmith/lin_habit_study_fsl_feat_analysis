from FeatAnalysisMain import FeatAnalysisMain

verbose=True
fam=FeatAnalysisMain(False,version='20170730')
fam.set_scripts_run_from_server(True)
fam.fsf_first_level_analysis_template_location = "lin-habit-study/analysis/first_level_template20170730"
structural_commands=fam.generate_first_level_script(
    "/Users/benjaminsmith/GDrive/lin-habit-study/analysis/generated_scripts/",
    preprocessing_timestamp='20170511T093930_cleaned')

print(structural_commands)