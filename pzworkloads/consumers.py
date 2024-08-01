import os 
import cloudpickle
import dataclasses
import json
import time
from channels.generic.websocket import AsyncWebsocketConsumer
import palimpzest as pz
from .schemas import *




POLICY_MAP = {
    'mincost': pz.MinCost(),
    'maxquality': pz.MaxQuality(),
}

EXECUTION_ENGINE_MAP = {
    'streaming': pz.StreamingSequentialExecution,
    'nosentinel': pz.NoSentinelExecution,
    'sequential': pz.SequentialSingleThreadExecution,
    'parallel': pz.PipelinedParallelExecution,
}

def collection_dataset():
    papers = pz.Dataset("biofabric-pdf", schema=ScientificPaper)
    paperURLs = papers.convert(pz.URL, desc="The DOI url of the paper") 
    htmlDOI = paperURLs.map(pz.DownloadHTMLFunction())
    tableURLS = htmlDOI.convert(pz.URL, desc="The URLs of the XLS tables from the page", cardinality="oneToMany")
    # urlFile = pz.Dataset("biofabric-urls", schema=pz.TextFile)
    # tableURLS = urlFile.convert(pz.URL, desc="The URLs of the tables")
    binary_tables = tableURLS.map(pz.DownloadBinaryFunction())
    tables = binary_tables.convert(pz.File)
    xls = tables.convert(pz.XLSFile)
    patient_tables = xls.convert(pz.Table, desc="All tables in the file", cardinality="oneToMany")
    return patient_tables

def case_data_dataset():
    xls = pz.Dataset('biofabric-tiny', schema=pz.XLSFile)
    patient_tables = xls.convert(pz.Table, desc="All tables in the file", cardinality="oneToMany")
    patient_tables = patient_tables.filter("The table contains biometric information about the patient")
    case_data = patient_tables.convert(CaseData, desc="The patient data in the table",cardinality="oneToMany")
    return case_data

def reference_dataset():
    papers = pz.Dataset("bdf-usecase3-tiny", schema=ScientificPaper)
    # papers = papers.filter("The paper mentions phosphorylation of Exo1")
    references = papers.convert(Reference, desc="A paper cited in the reference section", cardinality="oneToMany")
    return references


DATASETS = {
    'biofabric-pdf': collection_dataset(),
    'biofabric-tiny': case_data_dataset(),
    'bdf-usecase3-tiny': reference_dataset(),
}


class ComputeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        data_source = text_data_json['data_source']
        policy = text_data_json['policy']
        execution_engine = text_data_json['execution_engine']
        
        pz_policy = POLICY_MAP[policy]
        engine = EXECUTION_ENGINE_MAP[execution_engine]
        dataset = DATASETS[data_source]

        engine = EXECUTION_ENGINE_MAP[execution_engine](
            allow_bonded_query=True,
            allow_code_synth=False,
            allow_token_reduction=False)
        
        plan = engine.generate_plan(dataset=dataset, policy=pz_policy)

        # for records,plan,stats in self.compute_data(data_source, engine):
        await self.send(text_data=json.dumps({
            'plan': repr(plan),
        }))
        with open('computed_plan.pckl', 'wb') as f:
            cloudpickle.dump((engine, plan), f)

        # for idx, (records, plan, stats) in enumerate(iterable):
        #     json_records = [r._asDict(include_bytes=False) for r in records]
        #     str_plan = repr(plan)
        #     dict_stats = dataclasses.asdict(stats)

        #     with open(f'tmp_{idx}.pkl', 'wb') as f:
        #         pickle.dump((json_records, str_plan, dict_stats), f)
        #     yield (json_records, str_plan, dict_stats)


class RunConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        plan = text_data_json['plan']

        with open('computed_plan.pckl', 'rb') as f:
            engine, plan = cloudpickle.load(f)

        for records, stats in self.run_plan(engine, plan):
            await self.send(text_data=json.dumps({
                'records': records,
                'stats':stats,
            }))

    def run_plan(self, engine, plan):
        
        iterable = (idx for idx in range(4))
        for idx in iterable:
            if os.path.exists(f'tmp_{idx}.pkl'):
                with open(f'tmp_{idx}.pkl', 'rb') as f:
                    tuple = cloudpickle.load(f)
                    records, _, stats = tuple
                yield (records, stats)

        # while not engine.last_record:
            # records, stats = engine.execute_stream()
            # yield records, self.plan, stats

        # Simulate running the computed plan
                #     iterable  =  pz.Execute(output,
        #                             policy = pz_policy,
        #                             nocache=True,
        #                             allow_sentinels = False,
        #                             allow_code_synth=False,
        #                             allow_token_reduction=False,
        #                             execution_engine=engine)