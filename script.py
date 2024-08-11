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
parser.add_argument('--task', type=str, default='biofabric-tiny', help='The task to run')
parser.add_argument('--policy', type=str, help='The policy to use', default='cost')
args = parser.parse_args()

task = args.task
# Use the task argument
if task == 'casedata':
    dataset = consumers.case_data_dataset()
elif task == "reference":
    dataset = consumers.reference_dataset()
elif task == "collection":
    dataset = consumers.collection_dataset()
else:
    raise NotImplementedError(f"Task {task} not implemented")

policy = args.policy
if policy == 'cost':
    policy = pz.MinCost()
elif policy == 'quality':
    policy = pz.MaxQuality()
else:
    policy = pz.UserChoice()

engine = pz.StreamingSequentialExecution(
            allow_bonded_query=True,
            allow_code_synth=False,
            allow_token_reduction=False)

plan = engine.generate_plan(dataset=dataset, policy=policy)
with open('cache/computed_plan.pckl', 'wb') as f:
    cloudpickle.dump(plan, f)


record_lst = []

input_records = engine.get_input_records()
for idx, record in enumerate(input_records):
    print("Iteration number: ", idx+1, "out of", len(input_records))
    output_records = engine.execute_opstream(plan, record)
    record_lst += output_records
    with open(f'cache/records/{task}_{idx}.pkl', 'wb') as f:
        cloudpickle.dump((output_records),f)
    with open(f'cache/stats/{task}_{idx}.pkl', 'wb') as f:
        cloudpickle.dump((output_records),f)

# for i in range(10):
    # if os.path.exists(f'cache/records_{i}.pkl'):
        # with open(f'cache/records_{i}.pkl', 'rb') as f:
            # records = cloudpickle.load(f)
        # record_lst += records

print(record_lst)
