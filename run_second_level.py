from FeatAnalysisMain import FeatAnalysisMain

verbose=True
fam=FeatAnalysisMain(False,version='20170730')
fam.set_scripts_run_from_server(True)
structural_commands=fam.generate_second_level_script(
    "/Users/benjaminsmith/GDrive/lin-habit-study/analysis/generated_scripts/",
    first_level_timestamp='20170511T093930_cleaned'
    )
#foodchoicetesting3_20170511T093930_cleaned.feat
print(structural_commands)