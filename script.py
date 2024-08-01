import cloudpickle as pickle
import palimpzest as pz
from pzworkloads.schemas import *


xls = pz.Dataset('biofabric-tiny', schema=pz.XLSFile)
patient_tables = xls.convert(pz.Table, desc="All tables in the file", cardinality="oneToMany")
patient_tables = patient_tables.filter("The table contains biometric information about the patient")
case_data = patient_tables.convert(CaseData, desc="The patient data in the table",cardinality="oneToMany")

dataset = case_data
policy = pz.MaxQuality()
engine = pz.StreamingSequentialExecution(
            allow_bonded_query=True,
            allow_code_synth=False,
            allow_token_reduction=False)

plan = engine.generate_plan(dataset=dataset, policy=policy)

# with open('computed_plan.pckl', 'wb') as f:
#     pickle.dump(plan, f)

# with open('computed_plan.pckl', 'rb') as f:
#     plan2 = pickle.load(f)

record_lst = []
while not engine.last_record:
    records, stats = engine.execute_stream()
    record_lst += records
    breakpoint()
