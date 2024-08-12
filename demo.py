import os 
with open(".env", "r") as f:
    for line in f:
        key, value = line.strip().split("=")
        os.environ[key] = value

import argparse
import cloudpickle
import palimpzest as pz
from pzworkloads.schemas import *
from pzworkloads import consumers

# Argument parser setup
parser = argparse.ArgumentParser(description='Choose the task to run.')
parser.add_argument('--policy', type=str, help='The policy to use', default='cost')
args = parser.parse_args()


class CaseData(pz.Schema):
    """An individual row extracted from a table containing medical study data."""
    case_submitter_id = pz.Field(desc="The ID of the case", required=True)
    age_at_diagnosis = pz.Field(desc="The age of the patient at the time of diagnosis", required=False)


class CaseData(pz.Schema):
    """An individual row extracted from a table containing medical study data."""
    case_submitter_id = pz.Field(desc="The ID of the case", required=True)
    age_at_diagnosis = pz.Field(desc="The age of the patient at the time of diagnosis", required=False)
    race = pz.Field(desc="An arbitrary classification of a taxonomic group that is a division of a species.", required=False)
    ethnicity = pz.Field(desc="Whether an individual describes themselves as Hispanic or Latino or not.", required=False)
    gender = pz.Field(desc="Text designations that identify gender.", required=False)
    vital_status = pz.Field(desc="The vital status of the patient", required=False)
    ajcc_pathologic_t = pz.Field(desc="Code of pathological T (primary tumor) to define the size or contiguous extension of the primary tumor (T), using staging criteria from the American Joint Committee on Cancer (AJCC).", required=False)
    ajcc_pathologic_n = pz.Field(desc="The codes that represent the stage of cancer based on the nodes present (N stage) according to criteria based on multiple editions of the AJCC's Cancer Staging Manual.", required=False)
    ajcc_pathologic_stage = pz.Field(desc="The extent of a cancer, especially whether the disease has spread from the original site to other parts of the body based on AJCC staging criteria.", required=False)
    tumor_grade = pz.Field(desc="Numeric value to express the degree of abnormality of cancer cells, a measure of differentiation and aggressiveness.", required=False)
    tumor_focality = pz.Field(desc="The text term used to describe whether the patient's disease originated in a single location or multiple locations.", required=False)
    tumor_largest_dimension_diameter = pz.Field(desc="The tumor largest dimension diameter.", required=False)
    primary_diagnosis = pz.Field(desc="Text term used to describe the patient's histologic diagnosis, as described by the World Health Organization's (WHO) International Classification of Diseases for Oncology (ICD-O).", required=False)
    morphology = pz.Field(desc="The Morphological code of the tumor, as described by the World Health Organization's (WHO) International Classification of Diseases for Oncology (ICD-O).", required=False)
    tissue_or_organ_of_origin = pz.Field(desc="The text term used to describe the anatomic site of origin, of the patient's malignant disease, as described by the World Health Organization's (WHO) International Classification of Diseases for Oncology (ICD-O).", required=False)
    study = pz.Field(desc="The last name of the author of the study, from the table name", required=False)


files = pz.Dataset('biofabric-tiny', schema=pz.XLSFile)
patient_tables = files.convert(pz.Table, desc="All tables in the file", cardinality="oneToMany")
patient_tables = patient_tables.filter("The table contains biometric information about the patient")
case_data = patient_tables.convert(CaseData, desc="The patient data in the table",cardinality="oneToMany")

policy = args.policy
if policy == 'cost':
    policy = pz.MinCost()
elif policy == 'quality':
    policy = pz.MaxQuality()
else:
    policy = pz.UserChoice()

engine = pz.StreamingSequentialExecution

iterable  =  pz.Execute(case_data,
                        allow_bonded_query=True,
                        allow_code_synth=False,
                        allow_token_reduction=False,
                        policy = policy,
                        execution_engine=engine)

for results, plan, stats in iterable:
    for r in results:
        print("Patient ID:", r.case_submitter_id, 
              "Age:", r.age_at_diagnosis, 
              "Diagnosis:", r.primary_diagnosis, flush=True)

print(stats)
