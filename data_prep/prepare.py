
import sys
import os
import pandas as pd
import numpy as np

dry_run = False
if len(sys.argv) == 2:
    if sys.argv[1] in [1, "1", "True", "true", "T", "t", "yes", "Y", "Yes"]:
        dry_run = True
        print "Running dry run..."


if os.environ.get('USER') == "vagrant":
    repo_dir = os.path.dirname(
        os.path.dirname(os.path.realpath(__file__)))
else:
    repo_dir = os.path.realpath(".")


def read_csv(path):
    '''read csv using pandas
    '''
    return pd.read_csv(path, quotechar='\"',
                       na_values='', keep_default_na=False,
                       encoding='utf-8')


# load main data
data_csv = "{0}/data_prep/merged_data.csv".format(repo_dir)
data_raw_df = read_csv(data_csv)

# initialize treatment field as -1
# for each case:
#   actual treatments will be set to 1
#   actual controls will be set to 0
# then all remaining (-1) can be dropped
data_raw_df['treatment'] = -1

# add gef_id of -1 to random control points
# so we can match on field without nan errors
data_raw_df.loc[data_raw_df['type'] == 'rand', 'gef_id'] = -1

def clean_gef_id(val):
    try:
        return str(int(val))
    except:
        return -999

data_raw_df['gef_id'] = data_raw_df['gef_id'].apply(lambda z: clean_gef_id(z))
data_raw_df = data_raw_df.loc[data_raw_df['gef_id'] != -999]


# -----------------------------------------------------------------------------
# generate id lists for land, bio, prog, mfa, multicountry, multiagency

# load ancillary data
ancillary_01_csv = "{0}/raw_data/ancillary/CD_MFA_CD_projects_sheet.csv".format(repo_dir)
ancillary_02_csv = "{0}/raw_data/ancillary/CD_MFA_MFA_projects_sheet.csv".format(repo_dir)
ancillary_03_csv = "{0}/raw_data/ancillary/GEF_MFA_AidData_Ancillary.csv".format(repo_dir)
ancillary_04_csv = "{0}/raw_data/ancillary/gef_projects_160726.csv".format(repo_dir)

ancillary_01_df = read_csv(ancillary_01_csv)
ancillary_02_df = read_csv(ancillary_02_csv)
ancillary_03_df = read_csv(ancillary_03_csv)
ancillary_04_df = read_csv(ancillary_04_csv)


# -------------------------------------
# build land list

land_id_list_00 = list(data_raw_df.loc[data_raw_df['type'] == 'land', 'gef_id'])


# check GEF project records (if any column contains "LD")
cnames_01 = [i for i in list(ancillary_01_df.columns) if i != 'GEF ID']
matches_01 = ['LD' in list(ancillary_01_df.iloc[i])
              for i in range(len(ancillary_01_df))]
land_id_list_01 = list(ancillary_01_df.loc[matches_01, 'GEF ID'].astype('str'))


cnames_02 = [i for i in list(ancillary_02_df.columns) if i != 'GEF ID']
matches_02 = ['LD' in list(ancillary_02_df.iloc[i])
              for i in range(len(ancillary_02_df))]
land_id_list_02 = list(ancillary_02_df.loc[matches_02, 'GEF ID'].astype('str'))


# check aiddata ancillary ("Sub-Foci" column)
land_keywords = ["LD", "Sustainable", "SFM", "REDD", "LULUCF",
                 "Land", "Degradation", "Degredation", "Sustainable"]

raw_land_matches = ancillary_03_df['Sub-Foci'].str.contains('|'.join(land_keywords))
clean_land_matches = [
    False if np.isnan(x) else x
    for x in raw_land_matches
]
land_id_list_03 = list(ancillary_03_df.loc[clean_land_matches, 'GEF_ID']
    .astype('int').astype('str'))


# combine different land id lists
land_id_list = land_id_list_00 + land_id_list_01 + land_id_list_02 + land_id_list_03
land_id_list = list(set(land_id_list))
print 'land id count: {0}'.format(len(land_id_list))

# -------------------------------------
# build bio list

# check geocoded land degradation
bio_id_list_00 = list(data_raw_df.loc[data_raw_df['type'].isin(['bio', 'ext_bio']), 'gef_id'])


# check GEF project records (if any column contains "BD")
cnames_03 = [i for i in list(ancillary_01_df.columns) if i != 'GEF ID']
matches_03 = ['BD' in list(ancillary_01_df.iloc[i])
              for i in range(len(ancillary_01_df))]
bio_id_list_01 = list(ancillary_01_df.loc[matches_01, 'GEF ID'].astype('str'))


cnames_04 = [i for i in list(ancillary_02_df.columns) if i != 'GEF ID']
matches_04 = ['BD' in list(ancillary_02_df.iloc[i])
              for i in range(len(ancillary_02_df))]
bio_id_list_02 = list(ancillary_02_df.loc[matches_02, 'GEF ID'].astype('str'))


# check aiddata ancillary ("Sub-Foci" column)
bio_keywords = ["BD", "Biodiversity"]

raw_bio_matches = ancillary_03_df['Sub-Foci'].str.contains('|'.join(bio_keywords))
clean_bio_matches = [
    False if np.isnan(x) else x
    for x in raw_bio_matches
]
bio_id_list_03 = list(ancillary_03_df.loc[clean_bio_matches, 'GEF_ID']
    .astype('int').astype('str'))


# combine different land id lists
bio_id_list = bio_id_list_00 + bio_id_list_01 + bio_id_list_02 + bio_id_list_03
bio_id_list = list(set(bio_id_list))
print 'bio id count: {0}'.format(len(bio_id_list))

# -------------------------------------
# build prog and mfa lists

prog_id_list = list(set(data_raw_df.loc[data_raw_df['type'] == "prog", 'gef_id']))

mfa_id_list = list(set(data_raw_df.loc[data_raw_df['type'] == "mfa", 'gef_id']))

# -------------------------------------
# build multi country and multi agency lists
multicountry_id_list = list(set(ancillary_04_df.loc[ancillary_04_df["Country"].isin(["Regional", "Global"]), 'GEF_ID'].astype('int').astype('str')))

multiagency_id_list = list(set(ancillary_04_df.loc[~ancillary_04_df["Secondary agency(ies)"].isnull(), 'GEF_ID'].astype('int').astype('str')))


# -----------------------------------------------------------------------------


data_df = data_raw_df.copy(deep=True)


# add multicountry and multiagency fields
data_df['multicountry'] = [int(i) for i in data_df['gef_id'].isin(multicountry_id_list)]
data_df['multiagency'] = [int(i) for i in data_df['gef_id'].isin(multiagency_id_list)]

# assign random multicountry and multiagency to controls
data_df.loc[data_df['type'] == 'rand', 'multicountry'] = np.random.randint(2, size=len(data_df['type'] == 'rand'))
data_df.loc[data_df['type'] == 'rand', 'multiagency'] = np.random.randint(2, size=len(data_df['type'] == 'rand'))


# assign random year 2002-2013 to controls
import random
data_df.loc[data_df['type'] == 'rand', 'transactions_start_year'] = (
    data_df.loc[data_df['type'] == 'rand'].apply(
        lambda z: random.randint(2002, 2013), axis=1
    )
)



# attempt to find year for non controls

stage_00 = (
    (data_df['type'] != 'rand')
    & (data_df['transactions_start_year'] == ' ')
)
data_df.loc[stage_00, 'transactions_start_year'] = float('nan')

def date_to_year(d):
    partial = d.split('-')[2]
    if int(partial) > 20:
        y = '19'+ str(partial)
    else:
        y = '20' + str(partial)
    return y


stage_01 = (
    (data_df['type'] != 'rand')
    & (data_df['transactions_start_year'].isnull())
    & (~data_df['Actual date of implementation start'].isnull())
)

data_df.loc[stage_01, 'transactions_start_year'] = data_df.loc[stage_01]['Actual date of implementation start'].apply(lambda z: date_to_year(z))


stage_02 = (
    (data_df['type'] != 'rand')
    & (data_df['transactions_start_year'].isnull())
    & (data_df['Type acronym'].isin(['MSP', 'EA']))
    & (~data_df['Date of CEO approval (MSP / EA)'].isnull())
)

data_df.loc[stage_02, 'transactions_start_year'] = data_df.loc[stage_02]['Date of CEO approval (MSP / EA)'].apply(lambda z: date_to_year(z))


stage_03 = (
   (data_df['type'] != 'rand')
    & (data_df['transactions_start_year'].isnull())
    & (data_df['Type acronym'].isin(['FP']))
    & (~data_df['Date of CEO endorsement (FSP)'].isnull())
)

data_df.loc[stage_03, 'transactions_start_year'] = data_df.loc[stage_03]['Date of CEO endorsement (FSP)'].apply(lambda z: date_to_year(z))


stage_04 = (
    (data_df['type'] != 'rand')
    & (data_df['transactions_start_year'].isnull())
    & (~data_df['Date of project approval'].isnull())
)

data_df.loc[stage_04, 'transactions_start_year'] = data_df.loc[stage_04]['Date of project approval'].apply(lambda z: date_to_year(z))


# add year = 2012 to non control still missing year
stage_05 = (
    (data_df['type'] != 'rand')
    & (data_df['transactions_start_year'].isnull())
)

data_df.loc[stage_05, 'transactions_start_year'] = 2012


# drop location type = PCLI PCLD CONT
data_df = data_df.loc[~data_df['location_type_code'].isin(['PCLI', 'PCLD', 'CONT'])]

# drop start year > 2013
data_df['transactions_start_year'] = data_df['transactions_start_year'].astype('int')
data_df = data_df.loc[data_df['transactions_start_year'] <= 2013]


# drop projects that are not prog and not in gef sheet of mfa, sfa land, or sfa bio
gef_valid = read_csv("{0}/raw_data/ancillary/valid_mfa_and_sfa.csv".format(repo_dir))

mfa_valid = list(set(gef_valid['mfa'][gef_valid['mfa'].notnull()].astype('int').astype('str')))
ld_valid = list(set(gef_valid['ld'][gef_valid['ld'].notnull()].astype('int').astype('str')))
bio_valid = list(set(gef_valid['bio'][gef_valid['bio'].notnull()].astype('int').astype('str')))

total_valid = list(set(mfa_valid + ld_valid + bio_valid))

data_df = data_df.loc[(data_df['type'].isin(['prog', 'rand'])) | (data_df['gef_id'].isin(total_valid))]


# -------------------------------------

data_df_out = "{0}/data_prep/analysis_cases/base_data.csv".format(repo_dir)
data_df.to_csv(data_df_out, index=False, encoding='utf-8')

# -----------------------------------------------------------------------------