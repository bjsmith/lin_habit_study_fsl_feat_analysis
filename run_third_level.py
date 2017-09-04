from FeatAnalysisMain import FeatAnalysisMain

verbose=True
fam=FeatAnalysisMain(False)
fam.set_scripts_run_from_server(True)
fam.fsf_third_level_analysis_template_location="lin-habit-study/analysis/third_level_template20170628.fsf"
structural_commands=fam.generate_third_level_script(
    "/Users/benjaminsmith/Google Drive/lin-habit-study/analysis/generated_scripts/")

print(structural_commands)