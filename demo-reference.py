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

class ScientificPaper(pz.PDFFile):
   """Represents a scientific research paper, which in practice is usually from a PDF file"""
   paper_title = pz.Field(desc="The title of the paper. This is a natural language title, not a number or letter.", required=True)
   paper_year = pz.Field(desc="The year the paper was published. This is a number.", required=False)
   paper_author = pz.Field(desc="The name of the first author of the paper", required=True)
   paper_journal = pz.Field(desc="The name of the journal the paper was published in", required=True)
   paper_subject = pz.Field(desc="A summary of the paper contribution in one sentence", required=False)
   paper_doiURL = pz.Field(desc="The DOI URL for the paper", required=True)

class Reference(pz.Schema):
    """ Represents a reference to another paper, which is cited in a scientific paper"""
    reference_index = pz.Field(desc="The index of the reference in the paper", required=True)
    reference_title = pz.Field(desc="The title of the paper being cited", required=True)
    reference_first_author = pz.Field(desc="The author of the paper being cited", required=True)
    reference_year = pz.Field(desc="The year in which the cited paper was published", required=True)

## Define workload
papers = pz.Dataset("bdf-usecase3-tiny", schema=ScientificPaper)
papers = papers.filter("The paper mentions phosphorylation of Exo1")
references = papers.convert(Reference, desc="A paper cited in the reference section", cardinality="oneToMany")

policy = args.policy
if policy == 'cost':
    policy = pz.MinCost()
elif policy == 'quality':
    policy = pz.MaxQuality()
else:
    policy = pz.UserChoice()

engine = pz.StreamingSequentialExecution

iterable  =  pz.Execute(references,
                        allow_bonded_query=True,
                        allow_code_synth=False,
                        allow_token_reduction=False,
                        policy = policy,
                        execution_engine=engine)

for results, plan, stats in iterable:
    for r in results:
        if r.reference_title:
            print(f"{r.reference_first_author}, '{r.reference_title}', {r.reference_year}", flush=True)

print(stats)
