from FeatAnalysisMain import FeatAnalysisMain

verbose=True
fam=FeatAnalysisMain(False)
fam.set_scripts_run_from_server(True)
structural_commands=fam.generate_preprocessing_script("/Users/benjaminsmith/GDrive/lin-habit-study/analysis/generated_scripts/")

print(structural_commands)