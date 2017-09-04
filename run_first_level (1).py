from FeatAnalysisMain import FeatAnalysisMain

verbose=True
fam=FeatAnalysisMain(False)
fam.set_scripts_run_from_server(True)
structural_commands=fam.generate_first_level_script("/Users/benjaminsmith/Google Drive/lin-habit-study/analysis/generated_scripts/")

print(structural_commands)