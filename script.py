import os 
with open(".env", "r") as f:
    for line in f:
        key, value = line.strip().split("=")
        os.environ[key] = value

import cloudpickle
import palimpzest as pz
from pzworkloads.schemas import *


xls = pz.Dataset('biofabric-tiny', schema=pz.XLSFile)
patient_tables = xls.convert(pz.Table, desc="All tables in the file", cardinality="oneToMany")
patient_tables = patient_tables.filter("The table contains biometric information about the patient")
case_data = patient_tables.convert(CaseData, desc="The patient data in the table",cardinality="oneToMany")

dataset = case_data
policy = pz.MinCost()
engine = pz.StreamingSequentialExecution(
            allow_bonded_query=True,
            allow_code_synth=False,
            allow_token_reduction=False)

plan = engine.generate_plan(dataset=dataset, policy=policy)

with open('cache/computed_plan.pckl', 'wb') as f:
    cloudpickle.dump(plan, f)


record_lst = []

# input_records = engine.get_input_records()
# for idx, record in enumerate(input_records):
    # print("Iteration number: ", idx+1, "out of", len(input_records))
    # output_records = engine.execute_opstream(plan, record)
    # record_lst += output_records
    # with open(f'cache/records_{idx}.pkl', 'wb') as f:
        # cloudpickle.dump((output_records),f)
    # with open(f'cache/stats_{idx}.pkl', 'wb') as f:
    #     cloudpickle.dump((output_records),f)

for i in range(10):
    if os.path.exists(f'cache/records_{i}.pkl'):
        with open(f'cache/records_{i}.pkl', 'rb') as f:
            records = cloudpickle.load(f)
        record_lst += records

print(record_lst)
