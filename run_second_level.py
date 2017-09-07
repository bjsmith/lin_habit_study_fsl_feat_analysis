from FeatAnalysisMain import FeatAnalysisMain

verbose=True
fam=FeatAnalysisMain(False,version='20170730')
fam.set_scripts_run_from_server(True)
fam.fsf_second_level_analysis_template_location="lin-habit-study/analysis/second_level_template20170730_repeat.fsf"
fam.fsf_second_level_analysis_single_run_template_location="lin-habit-study/analysis/second_level_template_single_run_20170730_repeat.fsf"
structural_commands=fam.generate_second_level_script(
    "/Users/benjaminsmith/GDrive/lin-habit-study/analysis/generated_scripts/",
    first_level_timestamp='20170511T093930_cleaned'
    )

print(structural_commands)

#we'll generate command files for all subjects to keep it simple
#but only run specific ones that we need runs for. check out feat_analysis_firstlevel_test.py to determine which subjects
#we need single-run second-level analyses for.
structural_commands=fam.generate_second_level_script(
    "/Users/benjaminsmith/GDrive/lin-habit-study/analysis/generated_scripts/",
    first_level_timestamp='20170511T093930_cleaned',
    runid=1,
    subids=[329,331]
    )
print(structural_commands)


structural_commands=fam.generate_second_level_script(
    "/Users/benjaminsmith/GDrive/lin-habit-study/analysis/generated_scripts/",
    first_level_timestamp='20170511T093930_cleaned',
    runid=2,
    subids=[329,330,407,412]
    )
print(structural_commands)
