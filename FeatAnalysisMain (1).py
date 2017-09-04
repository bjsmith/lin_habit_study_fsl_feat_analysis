import csv
import glob
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

    fsf_second_level_analysis_template_location=None
    fsf_second_level_path=None
    fsf_second_level_run_script_filename=None

    fsf_third_level_analysis_template_location=None
    fsf_third_level_path = None
    fsf_third_level_run_script_filename = None

    fsf_generated_scripts_run_location=None


    timestamp = None  # ''

    def __init__(self, run_on_server=False):
        self.timestamp = get_timestamp()

        self.msmserverben_remote = '/Users/benjaminsmith/msmserver-ben/'
        self.msmserverben_local = '/expdata/bensmith/'

        self.msmserver_remote = '/Users/benjaminsmith/msmserver/'
        self.msmserver_local = '/expdata/xfgavin/MSM/'


        self.run_on_server=run_on_server

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
        self.subject_data_table_filepath = self.msmserver_ben_location + 'lin-habit-study/analysis/PreprocessingIndex.csv'
        reader = csv.DictReader(open(self.subject_data_table_filepath))
        subject_data_table = []
        for row in reader:
            subject_data_table.append(row)
        self.subject_data_table=subject_data_table

        self.contrast_data_table_filepath = self.msmserver_ben_location + 'lin-habit-study/analysis/copelist.csv'
        reader = csv.DictReader(open(self.contrast_data_table_filepath, 'rU'), quoting=csv.QUOTE_NONE)
        contrast_data_table = []
        for row in reader:
            contrast_data_table.append(row)
        self.contrast_data_table = contrast_data_table

        #v2 is the same as the original, but includes slice-timing.
        self.fsf_preprocessing_template_location = "lin-habit-study/analysis/preprocessing_template_v2.fsf"
        self.fsf_preprocessing_path = "lin-habit-study/preprocessed_subject_data/"
        self.fsf_preprocessing_run_script_filename = "preprocess_all" + self.timestamp + ".sh"

        self.fsf_preprocessing_template_location = "lin-habit-study/analysis/preprocessing_template_v2.fsf"

        self.fsf_first_level_analysis_template_location = "lin-habit-study/analysis/first_level_template.fsf"
        self.fsf_first_level_path = "lin-habit-study/data/first_level/"
        self.fsf_first_level_run_script_filename = "first_level_all" + self.timestamp + ".sh"
        self.fsf_generated_scripts_run_location= "lin-habit-study/analysis/generated_scripts/"

        #second level
        self.fsf_second_level_analysis_template_location="lin-habit-study/analysis/second_level_template.fsf"
        self.fsf_second_level_path="lin-habit-study/data/second_level/"
        self.fsf_second_level_run_script_filename = "second_level_all" + self.timestamp + ".sh"

        self.fsf_third_level_analysis_template_location="lin-habit-study/analysis/third_level_template.fsf"
        self.fsf_third_level_path = "lin-habit-study/data/third_level/"
        self.fsf_third_level_run_script_filename = "third_level_all" + self.timestamp + ".sh"

    def set_scripts_run_from_server(self,scripts_run_from_server):
        if(scripts_run_from_server):
            self.msmserver_script_location = self.msmserver_local
            self.msmserver_ben_script_location = self.msmserverben_local
        else:
            self.msmserver_script_location = self.msmserver_remote
            self.msmserver_ben_script_location = self.msmserverben_remote



    def get_structural_bet_cmd(self,structural_img):
        print("This function has not been adapted to change location of local or remote")
        return 'bet2 "'+ structural_img + '" "' + structural_img + '_brain"'
    def generate_third_level_script(self, script_output_location):
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

            if str(contrast_dict["Cope"]) in ['2','3','4']:
                print "...skipping this contrast because not all subjects have this."
                continue
            # save the template values
            subj_template_vars = {}
            # make the dictionary more accessible

            contrast_feat_label='contrast' + contrast_dict["Cope"].zfill(2) +"_" + contrast_dict["ContrastName"]

            third_level_subj_instance_path=self.fsf_third_level_path + third_level_folder + "/" +contrast_feat_label
            #fsf_to_run.append(
            #    "mkdir " + self.msmserver_ben_script_location + second_level_subj_instance_path)

            subj_template_vars['{outputdir}']=third_level_subj_instance_path
            subj_template_vars['{cope_n}'] = 'cope' + contrast_dict["Cope"]

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

    def generate_second_level_script(self, script_output_location):
        # load the template
        #values to enter:
        #IncludeHabitTrained
        #IncludeHabitUntrained
        #IncludeNovelTrained
        #IncludeNovelUntrained
        with open(self.msmserver_ben_location + self.fsf_second_level_analysis_template_location, "r") as myfile:
            fsf_file_contents = myfile.read()

        fsf_to_run = []

        second_level_folder = "analysis" + self.timestamp
        # create subject folder
        fsf_to_run.append(
            "mkdir " + self.msmserver_ben_script_location + self.fsf_second_level_path + second_level_folder + "/")

        #iterate through subjects
        for subj_key in range(0, len(self.subject_data_table)):
            subj_dict = self.subject_data_table[subj_key]

            print "sub" + subj_dict["SubID"]

            # save the template values
            subj_template_vars = {}
            # make the dictionary more accessible

            subj_feat_label='sub' + subj_dict["SubID"] + "_second_level"

            second_level_subj_instance_path=self.fsf_second_level_path + second_level_folder + "/" +subj_feat_label + "/"
            #fsf_to_run.append(
            #    "mkdir " + self.msmserver_ben_script_location + second_level_subj_instance_path)

            subj_template_vars['{second_level_folder}']=second_level_folder
            subj_template_vars['{subj_feat_label}'] = subj_feat_label
            #FSL seems to put first-level-output in the same folder as preprocessing, no matter how much I tried to make it different
            #so the run1, first-level feat folder is going to be the relevant preprocessing folder.
            #remember these indices for these folders are n+1 of the nth run because the first foodchoicetesting feat is
            #a different kind of task.
            subj_template_vars['{run1featfolder}']=(
                'sub' + subj_dict["SubID"] + '_foodchoicetesting' + str(2) + '_20170227T141913.feat'
            )
            subj_template_vars['{run2featfolder}'] = (
                'sub' + subj_dict["SubID"] + '_foodchoicetesting' + str(3) + '_20170227T141913.feat'
            )
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

            output_dir = "second_level_analysis" + self.timestamp + "/"
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

        f = open(script_output_location + self.fsf_second_level_run_script_filename, 'w')
        f.write('\n'.join([f for f in fsf_to_run]))

        return self.fsf_second_level_run_script_filename


    def generate_first_level_script(self,script_output_location):

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

        # load the template
        with open(self.msmserver_ben_location + self.fsf_first_level_analysis_template_location, "r") as myfile:
            fsf_file_contents = myfile.read()

        fsf_to_run = []

        #iterate through subjects
        for subj_key in range(0, len(self.subject_data_table)):
            subj_dict = self.subject_data_table[subj_key]

            print "sub" + subj_dict["SubID"]

            # save the template values
            subj_template_vars = {}
            # make the dictionary more accessible

            # replace template variables with new variables
            # first do subject-level vars
            subj_template_vars['{structural_image_filepath}'] = subj_dict["Main_structural_image"]

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
                    'sub' + subj_dict["SubID"] + '_foodchoicetesting' + str(run_file_index) + '_20170227T141913.feat')

                #then get the total volcount.
                # - total volumes coded {volcount}
                sub_run_preprocessed_data_nii=(
                    self.msmserver_ben_location + self.fsf_preprocessing_path
                    +sub_run_preprocessed_data_folder+"/filtered_func_data.nii.gz")
                vol_count = check_output(["fslnvols", sub_run_preprocessed_data_nii]).replace("\n", "")
                subj_run_template_vars['{volcount}'] = vol_count

                #get the each run's three-column directory to go with the run's pre-processed data directories

                #and then populate volcount, outputdir, feat dir, and ev file paths
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

                output_dir = "first_level_analysis" + self.timestamp + "/"
                if not os.path.exists(script_output_location + output_dir):
                    os.makedirs(script_output_location + output_dir)
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

    def get_structural_bet_cmd_script(self):
        structural_bet_cmd = '\n'.join([self.get_structural_bet_cmd(r['Main_structural_image']) for r in self.subject_data_table])

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
            subj_template_vars['{brain_extracted_structural_image_file_path}']=self.msmserver_ben_script_location + subj_dict['Main_structural_image'] + '_brain'

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
                fsf_filename= (self.fsf_generated_scripts_run_location +
                                'sub' + subj_dict["SubID"] + "run" + str(run_num+1) + ".fsf")

                fsf_to_run.append(fsf_filename)
                f = open(script_output_location + fsf_filename, 'w')
                f.write(cur_subj_run_fsf_file_contents)
                f.close()

        f = open(script_output_location+ self.fsf_preprocessing_run_script_filename, 'w')
        f.write('\n'.join(["feat "+f for f in fsf_to_run]))

        return self.fsf_preprocessing_run_script_filename





