from FeatAnalysisMain import FeatAnalysisMain

fam=FeatAnalysisMain(False)
fam.set_scripts_run_from_server(True)
structural_commands=fam.get_structural_bet_cmd_script()

additional_commands=fam.get_structural_bet_cmd_copy_script()

print(structural_commands)

print additional_commands