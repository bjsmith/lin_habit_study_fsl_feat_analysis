import glob
#import fnmatch
import numpy as np
import pandas
import os
three_col_files_dir='/Users/benjaminsmith/GDrive/lin-habit-study/Behavioral Data_all/three_col_20170730T223559'
fsf_dir='/Users/benjaminsmith/GDrive/lin-habit-study/analysis/generated_scripts/first_level_analysis20170905T152742'
#want to check to see what the EV files we generated look like. Do they "check out"

sub_evs=[]
#load EVs for that subject
sub_ev_len=pandas.DataFrame(columns=["fn","len"])


for fn in glob.glob(fsf_dir + '/*evs.csv'):
    print os.path.basename(fn)
    fn_csv=pandas.read_csv(fn)
    sub_evs.append(fn_csv)
    # see if the number of EVs is regular or short
    sub_ev_len=sub_ev_len.append(pandas.DataFrame(data=[{"fn": os.path.basename(fn).replace("_evs.csv",""), "len": len(fn_csv)}]))


sub_contrasts=[]
sub_contrasts_len=pandas.DataFrame(columns=["fn"])
#load the contrast file for that subject
for fn in glob.glob(fsf_dir + '/*contrasts.csv'):
    print os.path.basename(fn)
    fn_csv=pandas.read_csv(fn)
    #print(fn_csv)
    sub_contrasts.append(fn_csv)
    # see if the number of contrasts is regular or short
    sub_contrasts_len=sub_contrasts_len.append(pandas.DataFrame(
        data=[{
            "fn": os.path.basename(fn).replace("_contrasts.csv",""),
            "rows": fn_csv.shape[0],
            "cols":fn_csv.shape[1],
            "not_dummy_contrasts":sum(fn_csv.ContrastName!="DUMMY CONTRAST"),
            "dummy_contrast_cope_ids": str(fn_csv[fn_csv.ContrastName=="DUMMY CONTRAST"].Cope.tolist())
        }]))
    #also gotta record how many columns, which is important
merged_table=pandas.merge(sub_ev_len,sub_contrasts_len,on="fn")

# warn that to really test, we need to look to cross-reference if things are actually matched-up right
# (i.e., no mislabeled contrasts and so on)
#should suffice to take a look at the items with missing rows/cols, and check that their FSF files check out
#then we should be good to go.

#so number of cols (from sub_contrasts) should equal length of each EV plus some constant value.
max_ev_num=max(merged_table['len'])
max_contrast_table_cols=max(merged_table['cols'])
ev_extra_cols=max_contrast_table_cols-max_ev_num
assert all([float(n)==float(ev_extra_cols) for n in merged_table['cols']-merged_table['len']])

#and we should only be missing contrast rows for runs where there are missing EVs
assert all([n==max(merged_table['rows']) for n in merged_table[merged_table['len']==max_ev_num]['rows']])

print(merged_table)

print "if we reached here then we passed the sanity checks!"
print "if you just check a couple of the incomplete row FSF files to make sure names correspond wit hthe design then this check should be complete."



#for 329r1:
#EVS match the three col files in that they both omit precisely two files.
#missing is popcorn and mandms habit cue fractal
#so these seem to all check out. and the names of missing contrasts and missing EVs match.
