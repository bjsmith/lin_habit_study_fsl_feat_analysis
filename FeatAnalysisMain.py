import csv
import numpy
import pandas
import glob
import copy
import os
from BenSmithUtils import *
from subprocess import call
from subprocess import check_output

class FeatAnalysisMain(object):
    msmserverben_remote = None  # '/home/ben/msmserver-ben/'
    msmserverben_local = None  # '/expdata/bensmith/'

    msmserver_remote = None  # '/home/ben/msmserver/'
    msmserver_local = None  # '/expdata/xfgavin/MSM/'

    msmserver_location = ''
    msmserver_ben_location = ''

    raw_data_location=None

    run_on_server=None

    subject_data_table=None
    subject_data_table_filepath=None

    contrast_data_table = None
    contrast_data_table_filepath = None

    fsf_preprocessing_template_location=None
    fsf_preprocessing_path=None

    fsf_first_level_analysis_template_location=None
    fsf_first_level_path=None
    fsf_first_level_run_script_filename = None

    fsl_aroma_copy_script_filename=None
    fsl_aroma_script_filename=None

    fsf_second_level_analysis_template_location=None
    fsf_second_level_analysis_single_run_template_location = None
    fsf_second_level_path=None
    fsf_second_level_run_script_filename=None

    fsf_third_level_analysis_template_location=None
    fsf_third_level_path = None
    fsf_third_level_run_script_filename = None

    fsf_generated_scripts_run_location=None


    timestamp = None  # ''

    def __init__(self, run_on_server=False,version='20170511'):
        self.timestamp = get_timestamp()

        self.benlocalmachine = '/Users/benjaminsmith/GDrive/'

        self.msmserverben_remote = '/Users/benjaminsmith/msmserver-ben/'
        self.msmserverben_local = '/expdata/bensmith/'

        self.msmserver_remote = '/Users/benjaminsmith/msmserver/'
        self.msmserver_local = '/expdata/xfgavin/MSM/'


        self.run_on_server=run_on_server
        self.version=version

        if self.run_on_server:
            print("run on server")
            self.msmserver_location = self.msmserver_local
            self.msmserver_ben_location = self.msmserverben_local
        else:
            self.msmserver_location = self.msmserver_remote
            self.msmserver_ben_location = self.msmserverben_remote

        self.msmserver_script_location =self.msmserver_location
        self.msmserver_ben_script_location = self.msmserver_ben_location

        self.raw_data_location='lin-habit-study/raw_data/'

        #load information file
        self.subject_data_table_filepath = self.benlocalmachine + 'lin-habit-study/analysis/PreprocessingIndex.csv'
        reader = csv.DictReader(open(self.subject_data_table_filepath,'rU'))
        subject_data_table = []
        for row in reader:
            if(row["ExcludeSubject"]!="TRUE"):
                subject_data_table.append(row)
        self.subject_data_table=subject_data_table

        self.contrast_data_table_filepath = self.benlocalmachine + 'lin-habit-study/analysis/contrast_list_'+version+'.csv'
        reader = csv.DictReader(open(self.contrast_data_table_filepath, 'rU'), quoting=csv.QUOTE_NONE)
        contrast_data_table = []
        for row in reader:
            contrast_data_table.append(row)
        self.contrast_data_table = contrast_data_table

        self.ev_data_table_filepath = self.benlocalmachine + 'lin-habit-study/analysis/ev_list_'+version+'.csv'
        reader = csv.DictReader(open(self.ev_data_table_filepath, 'rU'), quoting=csv.QUOTE_NONE)
        ev_data_table = []
        for row in reader:
            ev_data_table.append(row)
        self.ev_data_table = ev_data_table

        #v2 is the same as the original, but includes slice-timing.
        self.fsf_preprocessing_template_location = "lin-habit-study/analysis/preprocessing_template_v3.fsf"
        self.fsf_preprocessing_path = "lin-habit-study/preprocessed_subject_data/"
        self.fsf_preprocessing_run_script_filename = "preprocess_all" + self.timestamp + ".sh"

        self.fsf_first_level_analysis_template_location = "lin-habit-study/analysis/first_level_template.fsf"
        self.fsf_first_level_path = "lin-habit-study/data/first_level/"
        self.fsf_first_level_run_script_filename = "first_level_all" + self.timestamp + ".sh"
        self.fsf_generated_scripts_run_location= "lin-habit-study/analysis/generated_scripts/"
        self.ev_files_location="lin-habit-study/analysis/three_col_20170730T223559/"

        self.fsl_aroma_copy_script_filename ="aroma_script_copy" + self.timestamp + ".sh"
        self.fsl_aroma_script_filename="aroma_script" + self.timestamp + ".sh"
        #second level
        self.fsf_second_level_analysis_template_location="lin-habit-study/analysis/second_level_template20170506.fsf"
        self.fsf_second_level_analysis_single_run_template_location = "lin-habit-study/analysis/second_level_template20170506.fsf"
        self.fsf_second_level_path="lin-habit-study/data/second_level"
        self.fsf_second_level_run_script_filename = "second_level_all" + self.timestamp + ".sh"
        self.fsf_second_level_run_single_run_script_filename = "second_level_all_single_run_{runid}_" + self.timestamp + ".sh"

        self.fsf_third_level_analysis_template_location=""
        self.fsf_third_level_path = "lin-habit-study/data/third_level/"
        self.fsf_third_level_run_script_filename = "third_level_all" + self.timestamp + ".sh"

    def set_scripts_run_from_server(self,scripts_run_from_server):
        if(scripts_run_from_server):
            self.msmserver_script_location = self.msmserver_local
            self.msmserver_ben_script_location = self.msmserverben_local
        else:
            self.msmserver_script_location = self.msmserver_remote
            self.msmserver_ben_script_location = self.msmserverben_remote



    def get_structural_bet_cmd(self,structural_img,suffix_to_use="_brain_0_3_B"):
        print("This function has not been adapted to change location of local or remote")

        return 'bet "'+ structural_img + '" "' + structural_img + suffix_to_use +'" -f 0.3 -B'

    def generate_third_level_script(self, script_output_location,first_level_script_output_location,
                                    #first_level_location,
                                    #first_level_timestamp,
                                    second_level_location,
                                    second_level_single_run_location_list):
        # load the template
        #values to enter:
        #IncludeHabitTrained
        #IncludeHabitUntrained
        #IncludeNovelTrained
        #IncludeNovelUntrained
        with open(self.msmserver_ben_location + self.fsf_third_level_analysis_template_location, "r") as myfile:
            fsf_file_contents = myfile.read()

        fsf_to_run = []

        third_level_folder = "analysis" + self.timestamp
        # create subject folder
        fsf_to_run.append(
            "mkdir " + self.msmserver_ben_script_location + self.fsf_third_level_path + third_level_folder + "/")


        #iterate through contrasts
        for contrast_key in range(0, len(self.contrast_data_table)):

            contrast_dict = self.contrast_data_table[contrast_key]

            print "contrast" + contrast_dict["Cope"]

            #for each contrast
            #for each subject*run
            #find out if any subject*run is missing this contrast.

            subj_include_list=pandas.DataFrame(columns=["subID","Run1Include","Run2Include","CopeName"])
            contrast_csv_dict={}
            contrast_val = contrast_dict["Cope"]
            for subID in [s['SubID'] for s in self.subject_data_table]:#glob.glob(first_level_file_location + '/*evs.csv'):
                data_to_use_for_subject = ''
                run_is_not_dummy=[]
                subj_include_list=subj_include_list.append(pandas.DataFrame(data=[{"subID": subID}]))
                for runid in [1,2]:
                    #look up the relevant contrast file
                    #store it in an array for future use if we haven't already done so.
                    if (contrast_csv_dict.has_key(subID)==False):
                        contrast_csv_dict[subID]={}
                    if contrast_csv_dict[subID].has_key(runid)==False:
                        contrast_csv_dict[subID][runid]=None
                    if contrast_csv_dict[subID][runid] is None:
                        contrast_csv_dict[subID][runid] = pandas.read_csv(first_level_script_output_location + '/' + str(subID) + "_" + str(runid) + "_contrasts.csv")

                    fn_csv=contrast_csv_dict[subID][runid]


                    #if that file even exists for the run, which it should, do we have a Cope number that is not marked "DUMMY CONTRAST"
                    #now check this cope
                    cope_name=fn_csv.query('Cope=='+contrast_val).ContrastName.item()
                    # throw an error if we don't have a number at all; they should all exist, marked "DUMMY CONTRAST"
                    # if the subject has only one run with this contrast, then just include that run only
                    # if the subject has no runs with this contrast, then exclude that subject from the contrast.
                    #print (subj_include_list)
                    subj_include_list.loc[subj_include_list.subID == subID, "CopeName"] = cope_name
                    if cope_name=='DUMMY CONTRAST':
                        print "subject " + str(subID) + " run " + str(runid) + " does not include contrast " + str(contrast_val)
                        run_is_not_dummy.append(False)
                        subj_include_list.loc[subj_include_list.subID==subID,"Run" + str(runid) + "Include"]=False
                    else:
                        run_is_not_dummy.append(True)
                        subj_include_list.loc[subj_include_list.subID == subID, "Run" + str(runid) + "Include"] = True
                #OK now we have the run data...

            included_subs = subj_include_list.query('Run1Include==True or Run2Include==True')
            excluded_subs = subj_include_list.query('Run1Include==False and Run2Include==False')
            if(len(excluded_subs)>0):
                print "The following subjects are excluded from contrast "+contrast_val+" altogether"
                print(excluded_subs)
            featdirlist=""
            ev_input_list=""
            group_membership_list=""
            #loop through the subjects, by index, in included_subs

            for si in range(0,len(included_subs)):
                featdirlist=featdirlist+"\n" + "# 4D AVW data or FEAT directory ("+str(si+1)+")" + "\n"
                featdirlist=featdirlist+"set feat_files("+str(si+1)+")" + " \""
                # and check whether for this subject, we have both runs
                included_sub=included_subs.iloc[si]
                if(included_sub["Run1Include"] and included_sub["Run2Include"]):
                    featdirlist = featdirlist + second_level_location + "sub" + included_sub["subID"]+"_second_level.gfeat/cope" + contrast_dict["Cope"] + ".feat\""
                    #record the title of the COPE; do it here because we know in this case there is no DummyContrast
                    contrast_title = included_sub.CopeName.replace("_"," ")#not sure if it is necessary to use the underscore char, but just in case.
                #one of the runs is missing
                elif (sum([included_sub["Run1Include"],included_sub["Run2Include"]])==1):
                    if((included_sub["Run1Include"]) and not included_sub["Run2Include"]):
                        #it's run 1
                        missing_run=2
                        retained_run=1
                    elif ((not included_sub["Run1Include"]) and included_sub["Run2Include"]):
                        #it's run 2
                        missing_run = 1
                        retained_run = 2
                    print "For contrast " + contrast_val + ", subject " + included_sub['subID'] + " is missing run " + str(missing_run)
                    #http://msm.fmri.cn/expdata/bensmith/lin-habit-study/preprocessed_subject_data/sub336_foodchoicetesting2_20170511T093930_cleaned.feat/report_log.html
                    featdirlist = featdirlist + second_level_single_run_location_list[retained_run-1] + "sub" + included_sub[
                        "subID"] + "_second_level.gfeat/cope" + contrast_dict["Cope"] + ".feat\""
                else:
                    raise Exception("should have fit one of the above categories")
                featdirlist = featdirlist + "\n"
                ev_input_list = ev_input_list + "\n# Higher-level EV value for EV 1 and input " + str(si+1 ) + "\n"
                ev_input_list = ev_input_list + "\nset fmri(evg" + str(si+1) + ".1) 1"

                group_membership_list = group_membership_list +"\n# Group membership for input " + str(si+1)
                group_membership_list = group_membership_list   +"\nset fmri(groupmem." + str(si+1) + ") 1\n"


            #if str(contrast_dict["Cope"]) in ['2','3','4']:
            #    print "...skipping this contrast because not all subjects have this."
            #    continue
            # save the template values

            subj_template_vars = {}
            # make the dictionary more accessible

            contrast_feat_label='contrast' + contrast_dict["Cope"].zfill(2) +"_" + str(contrast_dict["ContrastName"]).replace(" ","_")

            third_level_subj_instance_path=self.fsf_third_level_path + third_level_folder + "/" +contrast_feat_label
            #fsf_to_run.append(
            #    "mkdir " + self.msmserver_ben_script_location + second_level_subj_instance_path)

            subj_template_vars['{volcount}'] = len(included_subs)
            subj_template_vars['{outputdir}']=third_level_subj_instance_path
            subj_template_vars['{cope_n}'] = 'cope' + contrast_dict["Cope"]
            subj_template_vars['{featdirlist}'] = featdirlist
            subj_template_vars['{ev_input_list}'] = ev_input_list
            subj_template_vars['{group_membership_list}'] = group_membership_list
            subj_template_vars['{contrast_title}'] = contrast_title



            cur_contrast_fsf_file_contents = fsf_file_contents
            for key, value in subj_template_vars.iteritems():
                cur_contrast_fsf_file_contents = cur_contrast_fsf_file_contents.replace(key, str(value))

            output_dir = "third_level_analysis" + self.timestamp + "/"
            if not os.path.exists(script_output_location + output_dir):
                os.makedirs(script_output_location + output_dir)
            #create the FSF directory.

            # save the fsf file
            fsf_filename = (output_dir +
                            'contrast' + contrast_dict["Cope"].zfill(2) + ".fsf")

            fsf_to_run.append("feat " + self.msmserver_ben_script_location+ self.fsf_generated_scripts_run_location + fsf_filename)
            f = open(script_output_location+ fsf_filename, 'w')
            f.write(cur_contrast_fsf_file_contents)
            f.close()



        f = open(script_output_location + self.fsf_third_level_run_script_filename, 'w')
        f.write('\n'.join([f for f in fsf_to_run]))

        return self.fsf_third_level_run_script_filename

    def generate_second_level_script(self, script_output_location,first_level_timestamp='20170227T141913',runid=None,
                                     subids=[]):
        #only pass in runid if you want a single-level run.
        #this is for the subjects who have some missing data
        #we want to generate a second-level for them with just particular runs



        fsf_to_run = []

        if runid is None:
            second_level_folder = "analysis" + self.timestamp
            output_dir = "second_level_analysis" + self.timestamp + "/"
            # load the template
            with open(self.msmserver_ben_location + self.fsf_second_level_analysis_template_location, "r") as myfile:
                fsf_file_contents = myfile.read()
            run_indicator=""
        else: #single-run
            second_level_folder = "analysis" + "_single_run_" + str(runid) + "_" + self.timestamp
            output_dir = "second_level_analysis_single_run_" + str(runid) + "_" + self.timestamp + "/"
            with open(self.msmserver_ben_location + self.fsf_second_level_analysis_single_run_template_location, "r") as myfile:
                fsf_file_contents = myfile.read()
            run_indicator = "_single_run_" + str(runid)
        # create subject folder that the final results go into.
        second_level_results_path = self.msmserver_ben_script_location + self.fsf_second_level_path + "/"+ second_level_folder + "/"
        fsf_to_run.append(
            "mkdir " + second_level_results_path)

        #iterate through subjects
        for subj_key in range(0, len(self.subject_data_table)):
            subj_dict = self.subject_data_table[subj_key]

            print "sub" + subj_dict["SubID"]

            if len(subids) > 0:  # we passed in a list of subids in; use it to restrict the list.
                if not subids.__contains__(int(subj_dict["SubID"])):
                    continue # do not process this subject because it's not in the list of subids

            # save the template values
            subj_template_vars = {}
            # make the dictionary more accessible

            subj_feat_label='sub' + subj_dict["SubID"] + "_second_level"

            second_level_subj_instance_path=self.fsf_second_level_path  +"/"+ second_level_folder + "/" +subj_feat_label + "/"
            #fsf_to_run.append(
            #    "mkdir " + self.msmserver_ben_script_location + second_level_subj_instance_path)

            subj_template_vars['{second_level_folder}']=second_level_folder
            subj_template_vars['{subj_feat_label}'] = subj_feat_label
            #FSL seems to put first-level-output in the same folder as preprocessing, no matter how much I tried to make it different
            #so the run1, first-level feat folder is going to be the relevant preprocessing folder.
            #remember these indices for these folders are n+1 of the nth run because the first foodchoicetesting feat is
            #a different kind of task.
            if runid is None:
                subj_template_vars['{run1featfolder}']=(
                    'sub' + subj_dict["SubID"] + '_foodchoicetesting' + str(2) + '_'+first_level_timestamp+'.feat'
                )
                subj_template_vars['{run2featfolder}'] = (
                    'sub' + subj_dict["SubID"] + '_foodchoicetesting' + str(3) + '_'+first_level_timestamp+'.feat'
                )
            elif runid==1:
                subj_template_vars['{runnfeatfolder}']=(
                    'sub' + subj_dict["SubID"] + '_foodchoicetesting' + str(2) + '_'+first_level_timestamp+'.feat'
                )
            elif runid==2:
                subj_template_vars['{runnfeatfolder}'] = (
                    'sub' + subj_dict["SubID"] + '_foodchoicetesting' + str(3) + '_'+first_level_timestamp+'.feat'
                )
            else:
                raise Exception("Invalid runid " + runid)
            #the rule is that if one or both sessions had to be excluded, then for the subject, we don't include the contrast that only includes that session
            #in the second level analysis.
            #because it would be meaningless [in actuality, I rigged those contrasts, in those cases where the session was excluded
            #to include EVERYTHING, so it'd be super problematic.
            subj_template_vars['{IncludeHabitTrained}']=str(int(subj_dict["HabitTrainedSessionsToExclude"]==""))
            subj_template_vars['{IncludeHabitUntrained}'] =str(int(subj_dict["HabitUntrainedSessionsToExclude"]==""))
            subj_template_vars['{IncludeNovelTrained}'] = str(int(subj_dict["NovelTrainedSessionsToExclude"]==""))
            subj_template_vars['{IncludeNovelUntrained}'] = str(int(subj_dict["NovelUntrainedSessionsToExclude"]==""))

            cur_subj_fsf_file_contents = fsf_file_contents
            for key, value in subj_template_vars.iteritems():
                cur_subj_fsf_file_contents = cur_subj_fsf_file_contents.replace(key, str(value))


            if not os.path.exists(script_output_location + output_dir):
                os.makedirs(script_output_location + output_dir)
            #create the FSF directory.

            # save the fsf file
            fsf_filename = (output_dir +
                            'sub' + subj_dict["SubID"] + ".fsf")

            fsf_to_run.append("feat " + self.msmserver_ben_script_location+ self.fsf_generated_scripts_run_location + fsf_filename)
            f = open(script_output_location+ fsf_filename, 'w')
            f.write(cur_subj_fsf_file_contents)
            f.close()


        if runid is None:
            run_script_filename=self.fsf_second_level_run_script_filename
        else:
            run_script_filename = self.fsf_second_level_run_single_run_script_filename.replace("{runid}",str(runid))

        f = open(script_output_location + run_script_filename, 'w')
        f.write('\n'.join([f for f in fsf_to_run]))

        return self.fsf_second_level_run_script_filename

    def generate_first_level_script(self,script_output_location,preprocessing_timestamp='20170227T141913',subids=[]):

        #changing between runs:
        # - output directory {outputdir}
        # - total volumes [must change] coded {volcount}
        # - total voxels [no need to change; https://www.jiscmail.ac.uk/cgi-bin/webadmin?A2=fsl;c3a7dbc3.1403]
        # - feat dir {preprocessed_feat_folder}
        # - EV file paths for each EV {subid}, {three_col_run_folder}
        #changing between subjects
        # - as for changing between runs, plus:
        # - structural image path
        #that's it!

        #create basic direcotry
        output_dir = "first_level_analysis" + self.timestamp + "/"
        if not os.path.exists(script_output_location + output_dir):
            os.makedirs(script_output_location + output_dir)

        # load the template
        with open(self.benlocalmachine + self.fsf_first_level_analysis_template_location +".fsf", "r") as myfile:
            fsf_file_contents = myfile.read()

        #load the other templates
        with open(self.benlocalmachine + self.fsf_first_level_analysis_template_location + "_ev.fsf",
                  "r") as myfile:
            fsf_ev_template_file_contents = myfile.read()
        with open(self.benlocalmachine + self.fsf_first_level_analysis_template_location + "_ev_level2orthogonalisation.fsf",
                  "r") as myfile:
            fsf_ev_level2_template_file_contents = myfile.read()
        with open(self.benlocalmachine + self.fsf_first_level_analysis_template_location + "_contrastsection1.fsf",
                  "r") as myfile:
            fsf_contrastsection1_template_file_contents = myfile.read()
        with open(self.benlocalmachine + self.fsf_first_level_analysis_template_location + "_contrastsection2.fsf",
                  "r") as myfile:
            fsf_contrastsection2_template_file_contents = myfile.read()
        with open(self.benlocalmachine + self.fsf_first_level_analysis_template_location + "_contrastsection1_level2.fsf",
                  "r") as myfile:
            fsf_contrastsection1_level2_template_file_contents = myfile.read()
        with open(self.benlocalmachine + self.fsf_first_level_analysis_template_location + "_contrastsection2_level2.fsf",
                  "r") as myfile:
            fsf_contrastsection2_level2_template_file_contents = myfile.read()
        with open(self.benlocalmachine + self.fsf_first_level_analysis_template_location + "_maskmap.fsf",
                  "r") as myfile:
            fsf_maskmap_template_file_contents = myfile.read()
        with open(self.benlocalmachine + self.fsf_first_level_analysis_template_location + "_maskmap_level2.fsf",
                  "r") as myfile:
            fsf_maskmap_level2_template_file_contents = myfile.read()

        fsf_to_run = []

        #iterate through subjects
        for subj_key in range(0, len(self.subject_data_table)):
            subj_dict = self.subject_data_table[subj_key]

            # some subjects have been specified, so only run those
            if len(subids) > 0:  # we passed in a list of subids in; use it to restrict the list.
                if not subids.__contains__(int(subj_dict["SubID"])):
                    continue # do not process this subject because it's not in the list of subids

            print "sub" + subj_dict["SubID"]

            # save the template values
            subj_template_vars = {}
            # make the dictionary more accessible

            # replace template variables with new variables
            # first do subject-level vars
            subj_template_vars['{structural_image_filepath}'] = str(subj_dict["Main_structural_image_brain"]).replace(".nii.gz","")

            vprint(subj_dict)
            #newrules
            #we want to get the list of runs from this subject's pre-processing directory that fit the pattern

            #create subject folder
            fsf_to_run.append(
                "mkdir " + self.msmserver_ben_script_location + self.fsf_first_level_path + 'sub' + subj_dict["SubID"])
            # iterate through the two selected runs and their matching three-column files
            for run in [1,2]:
                subj_run_template_vars = {}
                # we're only looking at the latter 2; the first foodchoicetesting file was actually a different task.
                # so we add 1 to the run number to get the correct foodchoicetesting file.
                run_file_index=run+1
                sub_run_preprocessed_data_folder=(
                    'sub' + subj_dict["SubID"] + '_foodchoicetesting' + str(run_file_index) + '_' + preprocessing_timestamp + '.feat')

                #then get the total volcount.
                # - total volumes coded {volcount}
                sub_run_preprocessed_data_nii=(
                    self.msmserver_ben_location + self.fsf_preprocessing_path
                    +sub_run_preprocessed_data_folder+"/filtered_func_data.nii.gz")
                vol_count = check_output(["fslnvols", sub_run_preprocessed_data_nii]).replace("\n", "")
                if vol_count==0:
                    print "warning: volcount is zero for subject " + subj_dict["SubID"] + ", run "+str(run)
                subj_run_template_vars['{volcount}'] = vol_count

                # if there is no data for the EV then we cannot actually create an EV for this subject*run.
                # we need to avoid creating it; we actually need to EDIT the EV list and contrast list for this run
                # then save the custom EV list/contrast list.
                run_ev_data_table = copy.deepcopy(self.ev_data_table)
                run_contrast_data_table = copy.deepcopy(self.contrast_data_table)
                #before we create any templates we should go through the EVs
                evs_to_remove=[]

                for ev_i in range(0, (len(run_ev_data_table))):
                    ev_name="EV"+str(ev_i+1)
                    ev_length = self.check_ev_length(subj_dict["SubID"], run, self.ev_data_table[ev_i]["EVFilename"])
                    if (ev_length==0):  # we have no actual data for this EV.

                        # delete the EV from the EV list
                        evs_to_remove.append(ev_i)
                        #remove that EV from consideration in the contrast list
                        contrasts_to_remove = []

                        for contrast_i in range(0, len(run_contrast_data_table)):
                            if (str(subj_dict["SubID"]) == '403' and contrast_i==15):
                                print subj_dict["SubID"]
                            #delete the EV from the contrast record, but don't remove the contrast just yet
                            contrast_current = run_contrast_data_table[contrast_i]
                            contrast_val=contrast_current[ev_name]

                            del run_contrast_data_table[contrast_i][ev_name]

                            #print 'k:' + k
                            #print 'contrast_current:' + str(contrast_current)
                            remaining_ev_ids=[k for k in contrast_current if k[0:2]=="EV"]
                            remaining_ev_vals=[float(contrast_current[ev]) for ev in remaining_ev_ids]

                            #if all the remaining EVS in contrast are 0
                            if all([i==0 for i in remaining_ev_vals]):
                                #mark the contrast itself for removal
                                contrasts_to_remove.append(contrast_i)
                            # if it's left the contrast 'unbalanced', i.e., there are positive and negative values that do not add up to 0
                            elif (round(sum(remaining_ev_vals),2)!=0 and
                                    max(remaining_ev_vals)>0 and
                                    min(remaining_ev_vals) < 0
                                  ):

                                #we need to rebalance somehow.
                                #let's focus on making all the negative columns add up to the sum of the positive values
                                pos_vals_total= sum([i for i in remaining_ev_vals if i>0])
                                neg_val_count=len([i for i in remaining_ev_vals if i <0])
                                neg_share=pos_vals_total/neg_val_count
                                for i in remaining_ev_ids:
                                    if float(contrast_current[i]) < 0:
                                        contrast_current[i] = str(-neg_share)
                                #[contrast_i[("EV" + i)]=neg_share for i in range(0, len(run_ev_data_table)) if
                                # contrast_i[("EV" + i)] < 0]
                            evs_remaining =  [x for x in range(0, (len(run_ev_data_table))) if evs_to_remove.__contains__(x)]
                            #we can compare with the original.
                            #so, look to see if the contrast as it originally stood had both pos and neg ev regressors.
                            orig_pos_regressor_count=len([self.contrast_data_table[contrast_i]["EV" + str(ev_i+1)]>0 for i in range(0, len(run_ev_data_table))])
                            orig_neg_regressor_count = len(
                                [self.contrast_data_table[contrast_i]["EV" + str(i + 1)] < 0 for i in
                                 range(0, len(run_ev_data_table))])
                            # and whether it still does.
                            current_pos_regressor_count = len(
                                [self.contrast_data_table[contrast_i]["EV" + str(i + 1)] > 0 for i in
                                 range(0, len(run_ev_data_table))])
                            current_neg_regressor_count = len(
                                [self.contrast_data_table[contrast_i]["EV" + str(i + 1)] < 0 for i in
                                 range(0, len(run_ev_data_table))])

                            #If this contrast used to have pos and neg ev regressors, and no longer does, then delete it.
                            if ((orig_pos_regressor_count>0 and orig_neg_regressor_count>0) and (
                                current_pos_regressor_count==0 or current_neg_regressor_count==0
                            )):
                                contrasts_to_remove.append(contrast_i)

                            #otherwise, I think we are good...
                        contrasts_to_remove.sort(reverse=True) #have to start at the highest, otherwise the indices are messed up!
                        print(contrasts_to_remove)

                        #we actually won't remove the contrasts for now; we'll wait and rather than remove them,
                        #relabel the ones that we need to delete and make sure they have some kind of dummy EV in them.
                        for contrast_i in contrasts_to_remove:
                            #run_contrast_data_table.remove(run_contrast_data_table[contrast_i])
                            run_contrast_data_table[contrast_i]['ContrastName']='DUMMY CONTRAST'
                            #give this contrast all ONES for the first four
                            #just a nonsensical EV.
                            for ev_in_contrast in [("EV" + str(i + 1)) for i in range(0, 3)]:
                                print ev_in_contrast
                                run_contrast_data_table[contrast_i][ev_in_contrast]=1

                if (len(evs_to_remove)>1):
                    print ("warning: evs_to_remove greater than 1; evs_to_remove=" + str(len(evs_to_remove)) + ". what to do?")
                #delete EVs marked for removal

                # if we're removing more than one, this is going to be problematic, beccause after removing one, the indices will be all messed up!
                #the elegant solution is to start from the *highest* index, https://stackoverflow.com/questions/497426/deleting-multiple-elements-from-a-list
                evs_to_remove.sort(reverse=True)
                print(evs_to_remove)
                for ev_i in evs_to_remove:
                    run_ev_data_table.remove(run_ev_data_table[ev_i])

                #whatever the situation, we should save the EV file that is specific to this run so that it can be
                #referred to when generating round 2.

                with open(script_output_location + output_dir + subj_dict["SubID"] + "_" + str(run) + "_evs.csv", 'wb') as csvfile:
                    spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                    spamwriter.writerow([k for k in run_ev_data_table[0]])
                    for ev_row in run_ev_data_table:
                        spamwriter.writerow([ev_row[k] for k in ev_row])

                with open(script_output_location + output_dir + subj_dict["SubID"] + "_" + str(run) + "_contrasts.csv", 'wb') as csvfile:
                    spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                    spamwriter.writerow([k for k in run_contrast_data_table[0]])
                    for ev_row in run_contrast_data_table:
                        if[ev_row['ContrastName']!='DUMMY CONTRAST']:
                            spamwriter.writerow([ev_row[k] for k in ev_row])

                # i think that is probably the correct way to address this problem!

                #populate with data


                #to replace template vars within nested templates we will need to work recursively.
                #Need to create some templates:

                #loop through EVs
                ev_firstlevel=""
                for ev_n in range(0, (len(run_ev_data_table))):
                    # got to collect data on whether we *can* create each EV.

                    ev_firstlevel_ev_n=fsf_ev_template_file_contents
                    ev_firstlevel_ev_n=ev_firstlevel_ev_n.replace("{ev_n}",str(ev_n+1)).replace("{ev_name}",run_ev_data_table[ev_n]["EVName"])
                    ev_firstlevel_ev_n=ev_firstlevel_ev_n.replace("{ev_filepath}",run_ev_data_table[ev_n]["EVFilename"])
                    ev_secondlevel = ""
                    for ev_n_level2 in range(0,(len(run_ev_data_table)+1)):
                        fsf_ev_level2_ev_n=fsf_ev_level2_template_file_contents
                        fsf_ev_level2_ev_n=fsf_ev_level2_ev_n.replace("{ev_n}",str(ev_n+1)).replace("{ev_level2_n}",str(ev_n_level2))
                        ev_secondlevel=ev_secondlevel+fsf_ev_level2_ev_n

                    ev_firstlevel_ev_n=ev_firstlevel_ev_n.replace("{ev_level2orthogonalisation}",ev_secondlevel)

                    ev_firstlevel=ev_firstlevel+ev_firstlevel_ev_n

                #loop through contrasts

                # Contrast section 1
                contrast_section1_level1=""
                for contrast_n in range(0,len(run_contrast_data_table)):
                    #get from template
                    contrast_section1_level1_n=fsf_contrastsection1_template_file_contents
                    #get the contrast level 2, looping through EVs in the contrast table.
                    contrast_section1_level2=""
                    # contrast section 1, second level (EV list)
                    for element_n_level2 in range(0,len(run_ev_data_table)*2):

                        contrast_section1_level2_n=fsf_contrastsection1_level2_template_file_contents
                        contrast_section1_level2_n =contrast_section1_level2_n.replace("{element_n}",str(element_n_level2+1))

                        #now we need the contrast details from the table.
                        #only for ODD elements.
                        #made a mistake here; prior to 8 SEP 2017 this was set to "only EVEN" elements.
                        #That is wrong - it's using the temporal derivative, which was neever intended to be itself measured!
                        contrast_ev_match=0
                        if ((element_n_level2 +1) % 2)==0:
                            #just enter zero.
                            contrast_ev_match=0
                        else:
                            #look up what this EV was numbered originally
                            #because that's still how it's referred to in the contrast table.
                            #print "."
                            #if(subj_dict["SubID"]=='407' and contrast_n==29 and element_n_level2==21):
                            #    print element_n_level2
                            #ev_original_id = run_ev_data_table[(element_n_level2+1)/2-1]['EVN']
                            ev_original_id = run_ev_data_table[(element_n_level2 + 1) / 2]['EVN']
                            #print str((element_n_level2+1)/2-1) + ", " + ev_original_id
                            #print [x for x in run_ev_data_table[(element_n_level2+1)/2-1]]
                            #print [x for x in run_contrast_data_table[contrast_n]]
                            contrast_ev_match=run_contrast_data_table[contrast_n]["EV" + str(ev_original_id)]

                        contrast_section1_level2_n = contrast_section1_level2_n.replace("{contrast_n_element_n_match}",
                                                                                        str(contrast_ev_match))
                        contrast_section1_level2=contrast_section1_level2+contrast_section1_level2_n

                        # add the level two contrast*ev entry to the contrast entry and
                        #add the contrast ID and other details.

                    contrast_section1_level1_n = contrast_section1_level1_n.replace(
                        "{contrastsection1_level2}",
                        contrast_section1_level2
                    ).replace(
                        "{contrast_n}",
                        str(contrast_n + 1)).replace(
                        "{contrast_name}",run_contrast_data_table[contrast_n]["ContrastName"])
                    contrast_section1_level1=contrast_section1_level1+contrast_section1_level1_n


                #Contrast section 2
                #contrast section 2, second level (EV list)

                contrast_section2_level1 = ""
                for contrast_n in range(0, len(run_contrast_data_table)):
                    # get from template
                    contrast_section2_level1_n = fsf_contrastsection2_template_file_contents
                    # get the contrast level 2, looping through EVs in the contrast table.
                    contrast_section2_level2 = ""
                    for element_n_level2 in range(0, len(run_ev_data_table)):
                        contrast_section2_level2_n = fsf_contrastsection2_level2_template_file_contents
                        contrast_section2_level2_n = contrast_section2_level2_n.replace("{element_n}",
                                                                                        str(element_n_level2 + 1))

                        # now we need the contrast details from the table.
                        ev_original_id = run_ev_data_table[element_n_level2]['EVN']
                        contrast_ev_match = run_contrast_data_table[contrast_n][
                            ("EV" + str(ev_original_id))]

                        contrast_section2_level2_n = contrast_section2_level2_n.replace("{contrast_n_element_n_match}",
                                                                                        str(contrast_ev_match))
                        contrast_section2_level2 = contrast_section2_level2 + contrast_section2_level2_n

                        # add the level two contrast*ev entry to the contrast entry and
                        # add the contrast ID and other details.

                    contrast_section2_level1_n = contrast_section2_level1_n.replace(
                        "{contrastsection2_level2}",
                        contrast_section2_level2
                    ).replace(
                        "{contrast_n}",
                        str(contrast_n + 1)).replace(
                        "{contrast_name}", run_contrast_data_table[contrast_n]["ContrastName"])
                    contrast_section2_level1 = contrast_section2_level1 + contrast_section2_level1_n

                #mask map
                maskmap=""
                for maskmap_n in range(0,len(run_contrast_data_table)):
                    #mask map (second level)
                    #EV, first level
                    #EV, second level (orthogonalization)
                    for contrast_n in range(0,len(run_contrast_data_table)):
                        if(maskmap_n!=contrast_n):
                            maskmap_text_n=fsf_maskmap_template_file_contents.replace(
                                "{mask_n}",str(maskmap_n+1)
                            ).replace(
                                "{contrast_n}",str(contrast_n+1)
                            )
                            maskmap=maskmap+maskmap_text_n


                #populate the nested templates
                subj_run_template_vars['{ev_template}'] = ev_firstlevel
                subj_run_template_vars['{contrast_section1}'] = contrast_section1_level1
                subj_run_template_vars['{contrast_section2}'] = contrast_section2_level1
                subj_run_template_vars['{maskmap}'] = maskmap

                # get the each run's three-column directory to go with the run's pre-processed data directories


                #and then populate volcount, outputdir, feat dir, and ev file paths
                subj_run_template_vars['{ev_orig_count}'] = len(run_ev_data_table)
                subj_run_template_vars['{ev_real_count}'] = len(run_ev_data_table)*2
                subj_run_template_vars['{contrast_count}'] = len(run_contrast_data_table)

                # - output directory {outputdir}
                subj_run_template_vars['{outputdir}'] = (
                    'sub' + subj_dict["SubID"] + '/' + 'run' + str(run) + '_' + self.timestamp)

                # - feat dir {preprocessed_feat_folder}
                subj_run_template_vars['{preprocessed_feat_folder}'] = sub_run_preprocessed_data_folder

                # - EV file paths for each EV {subid}, {three_col_run_folder}
                subj_run_template_vars['{subid}']=subj_dict["SubID"]
                subj_run_template_vars['{three_col_run_folder}'] = 'food_choice_testing_run' + str(run)

                cur_subj_run_fsf_file_contents = fsf_file_contents

                # write the template vars into a mock FSF file.
                for key, value in subj_run_template_vars.iteritems():
                    cur_subj_run_fsf_file_contents = cur_subj_run_fsf_file_contents.replace(key, str(value))

                for key, value in subj_template_vars.iteritems():
                    cur_subj_run_fsf_file_contents = cur_subj_run_fsf_file_contents.replace(key, str(value))


                #create the FSF directory.

                fsf_to_run.append(
                    "mkdir " + self.msmserver_ben_script_location + self.fsf_first_level_path
                    + 'sub' + subj_dict["SubID"] + '/' + 'run' + str(run) + '_' + self.timestamp)
                # save the fsf file
                fsf_filename = (output_dir +
                                'sub' + subj_dict["SubID"] + "run" + str(run) + ".fsf")

                fsf_to_run.append("feat " + self.msmserver_ben_script_location+ self.fsf_generated_scripts_run_location + fsf_filename)
                f = open(script_output_location+ fsf_filename, 'w')
                f.write(cur_subj_run_fsf_file_contents)
                f.close()

        f = open(script_output_location + self.fsf_first_level_run_script_filename, 'w')
        f.write('\n'.join([f for f in fsf_to_run]))

        return self.fsf_first_level_run_script_filename

        #first_level_script=get_first_level_script()
        #run first level script

    def get_structural_bet_cmd_copy_script(self):
        #need to create a copy of the main structural images to sit next to the brain-extracted images.
        structural_bet_cmd = "\n".join(
            ["cp " + r['Main_structural_image'] + ".nii.gz " + r['Main_structural_image_brain'].replace("_brain","") + ".nii.gz" for r in
             self.subject_data_table]
        )
        return structural_bet_cmd

    def get_structural_bet_cmd_script(self):
        structural_bet_cmd = '\n'.join([self.get_structural_bet_cmd(r['Main_structural_image'],"_brain_0_3_B") for r in self.subject_data_table])
        #structural_bet_cmd='\n'.join([r['Main structural image'] for r in self.subject_data_table])
        return structural_bet_cmd

    #http://stackoverflow.com/questions/20252669/get-files-from-directory-argument-sorting-by-size
    def get_files_with_sizes(self, search_string, reverse=False):
        """ Return list of file paths in directory sorted by file size """

        # Get list of files
        filepaths = []
        for filename in glob.glob(search_string):
            if os.path.isfile(filename):
                filepaths.append(filename)

        # Re-populate list with filename, size tuples
        filepaths=[(fp,os.path.getsize(fp)) for fp in filepaths]

        # Sort list by file size
        # If reverse=True sort from largest to smallest
        # If reverse=False sort from smallest to largest
        filepaths.sort(key=lambda filename: filename[1], reverse=reverse)

        return filepaths

    def get_volcount(self, nii_filepath):
        """ Return list of file paths in directory sorted by file size """


        # Get list of files
        filepaths = []
        for filename in glob.glob(search_string):
            if os.path.isfile(filename):
                filepaths.append(filename)

        # Re-populate list with filename, size tuples
        filepaths=[(fp,os.path.getsize(fp)) for fp in filepaths]

        # Sort list by file size
        # If reverse=True sort from largest to smallest
        # If reverse=False sort from smallest to largest
        filepaths.sort(key=lambda filename: filename[1], reverse=reverse)

        return filepaths

    def check_ev_length(self,subid,run_num, ev_name):
        ev_filepath=self.benlocalmachine + self.ev_files_location  + str(subid) + "/food_choice_testing_run"+str(run_num)  +"/" + ev_name + ".txt"

        if os.path.exists(ev_filepath):
            with open(ev_filepath,"r") as myfile:
                ev_text = myfile.read()
            return(len(ev_text))
        else:
            return 0

    def generate_script_to_create_new_preprocessed_cleaned_feat_dirs(self, script_output_location, level_one_timestamp):
        script_text = []
        for subj_key in range(0, len(self.subject_data_table)):
            subj_dict = self.subject_data_table[subj_key]
            for run_num in [2, 3]:

                #uncleaned folder
                uncleaned_feat_path=(self.msmserverben_local + self.fsf_preprocessing_path +
                "sub" + subj_dict["SubID"] + "_foodchoicetesting" + str(run_num) + "_" + level_one_timestamp +
                ".feat")

                #cleaned folder
                cleaned_feat_path=(self.msmserverben_local + self.fsf_preprocessing_path +
                "sub" + subj_dict["SubID"] + "_foodchoicetesting" + str(run_num) + "_" + level_one_timestamp +
                "_cleaned.feat")

                #copy the feat file
                command_folder_copy = ("cp -r " + uncleaned_feat_path + " " + cleaned_feat_path)

                script_text.append(command_folder_copy)

                #delete the uncleaned filtered_func_data
                command_file_del = ("rm -r " + cleaned_feat_path + "/filtered_func_data.nii.gz")
                script_text.append(command_file_del)

                #copy the new ICA cleaned data.
                command_file_ica = ("cp " + cleaned_feat_path + "/ICA_AROMA/denoised_func_data_nonaggr.nii.gz " +
                cleaned_feat_path + "/filtered_func_data.nii.gz")
                script_text.append(command_file_ica)

        f = open(script_output_location + self.fsl_aroma_copy_script_filename, 'w')
        f.write('\n'.join([f for f in script_text]))
        return script_text

    def generate_fix_aroma_script(self, script_output_location, level_one_timestamp):
        script_text=[]
        for subj_key in range(0, len(self.subject_data_table)):
            subj_dict = self.subject_data_table[subj_key]
            for run_num in [2,3]:
                command=("/usr/bin/python2.7 " + self.msmserverben_local +"lin-habit-study/ICA-AROMA-master/ICA_AROMA.py -feat " +
                         self.msmserverben_local + self.fsf_preprocessing_path +
                         "sub" + subj_dict["SubID"] + "_foodchoicetesting"+str(run_num) + "_" + level_one_timestamp +
                         ".feat" +
                         " -out " + self.msmserverben_local + self.fsf_preprocessing_path +
                         "sub" + subj_dict["SubID"] + "_foodchoicetesting"+str(run_num) + "_" + level_one_timestamp +
                         ".feat/ICA_AROMA/")

                script_text.append(command)
        f = open(script_output_location + self.fsl_aroma_script_filename, 'w')
        f.write('\n'.join([f for f in script_text]))
        return script_text

    def generate_preprocessing_script(self,script_output_location):
        #load the template
        with open (self.msmserver_ben_location + self.fsf_preprocessing_template_location, "r") as myfile:
            fsf_file_contents=myfile.read()

        fsf_to_run=[]

        for subj_key in range(0,len(self.subject_data_table)):
            subj_dict = self.subject_data_table[subj_key]

            print "sub"+subj_dict["SubID"]

            #save the template values
            subj_template_vars={}
            #make the dictionary more accessible

            # replace template variables with new variables
            #first do subject-level vars
            subj_template_vars['{brain_extracted_structural_image_file_path}']=self.msmserver_ben_script_location + subj_dict['Main_structural_image_brain']

            vprint(subj_dict)
            #iterate through foodchoicetesting runs...
            #we're going to get the list of runs from each dir
            dirList = self.get_files_with_sizes(
                self.msmserver_ben_location + self.raw_data_location + subj_dict["Dir"] + '/*Foodchoicetestings*')

            # files should be at least 13MB
            dirList = [d for d in dirList if d[1] > (13 * pow(10, 6))]

            # get the lesser of three files or the number that exist here.
            foodchoicetesting_run_count = min(len(dirList), 3)

            # this comes in order of sizes, but just in case
            dirList.sort(key=lambda f: f[1], reverse=True)

            #cut it down to the right length
            dirList = dirList[0:foodchoicetesting_run_count]
            # now we've cut it down, re-arrange in proper order.
            dirList.sort(key=lambda f: f[0], reverse=False)


            #for each foodchoicetesting file (though for no more than 3...)
            for run_num in range(foodchoicetesting_run_count):
                subj_run_template_vars={}

                subj_run_template_vars['{output_folder}'] = "sub" + subj_dict["SubID"] + "_foodchoicetesting"+str(run_num+1) + "_" + self.timestamp

                foodchoicetesting_filepath=dirList[run_num][0]

                #get volcount
                vol_count=check_output(["fslnvols",foodchoicetesting_filepath]).replace("\n","")
                subj_run_template_vars['{VOLCOUNT}'] = vol_count

                print "   " + foodchoicetesting_filepath + "\t" +vol_count

                subj_run_template_vars['{foodchoicetesting_raw_file_path}'] = \
                    self.msmserver_ben_script_location + \
                    self.raw_data_location + subj_dict["Dir"] + "/" + \
                    os.path.basename(foodchoicetesting_filepath)

                cur_subj_run_fsf_file_contents = fsf_file_contents

                #write the template vars into a mock FSF file.
                for key, value in subj_run_template_vars.iteritems():
                    cur_subj_run_fsf_file_contents = cur_subj_run_fsf_file_contents.replace(key, str(value))

                for key, value in subj_template_vars.iteritems():
                    cur_subj_run_fsf_file_contents = cur_subj_run_fsf_file_contents.replace(key, str(value))

                output_dir="preprocessing"+ self.timestamp + "/"
                if not os.path.exists(script_output_location + output_dir):
                    os.makedirs(script_output_location + output_dir)

                #save the fsf file

                #this should contain just the filename and immediate output dir.
                fsf_filename= (output_dir + 'sub' + subj_dict["SubID"] + "run" + str(run_num+1) + ".fsf")

                #this should contain a full server-relative path.
                fsf_to_run.append(self.msmserver_ben_script_location + self.fsf_generated_scripts_run_location + fsf_filename)
                f = open(script_output_location + fsf_filename, 'wb')
                f.write(cur_subj_run_fsf_file_contents)
                f.close()

        f = open(script_output_location+ self.fsf_preprocessing_run_script_filename, 'w')
        f.write('\n'.join(["feat "+f for f in fsf_to_run]))

        return self.fsf_preprocessing_run_script_filename





