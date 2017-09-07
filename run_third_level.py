from FeatAnalysisMain import FeatAnalysisMain

verbose=True
fam=FeatAnalysisMain(False,version='20170730')
fam.set_scripts_run_from_server(True)
fam.fsf_first_level_analysis_template_location = "lin-habit-study/analysis/first_level_template20170730"
fam.fsf_third_level_analysis_template_location = "lin-habit-study/analysis/third_level_template20170730.fsf"
structural_commands=fam.generate_third_level_script(
    "/Users/benjaminsmith/GDrive/lin-habit-study/analysis/generated_scripts/",
    first_level_script_output_location="/Users/benjaminsmith/GDrive/lin-habit-study/analysis/generated_scripts/first_level_analysis20170905T152742",
    second_level_location='/expdata/bensmith/lin-habit-study/data/second_level/analysis20170906T143454/',#sub348_second_level.gfeat/cope6.feat/'
    second_level_single_run_location_list = [
        '/expdata/bensmith/lin-habit-study/data/second_level/analysis_single_run_1_20170906T143454/',
        '/expdata/bensmith/lin-habit-study/data/second_level/analysis_single_run_2_20170906T143454/']
    )

print(structural_commands)