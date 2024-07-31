import os 
import pickle
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
        
        for records,plan,stats in self.compute_data(data_source, policy, execution_engine):
            await self.send(text_data=json.dumps({
                'records': records,
                'plan': plan,
                'stats': stats
            }))

    def compute_data(sel, data_source, policy, execution_engine):
        pz_policy = POLICY_MAP[policy]
        engine = EXECUTION_ENGINE_MAP[execution_engine]

        iterable = (idx for idx in range(4))
        for idx in iterable:
            if os.path.exists(f'tmp_{idx}.pkl'):
                with open(f'tmp_{idx}.pkl', 'rb') as f:
                    tuple = pickle.load(f)
                    records, plan, stats = tuple
                yield (records, plan, stats)

        # if data_source == 'biofabric-pdf':
        #     papers = pz.Dataset("biofabric-pdf", schema=ScientificPaper)
        #     paperURLs = papers.convert(pz.URL, desc="The DOI url of the paper") 
        #     htmlDOI = paperURLs.map(pz.DownloadHTMLFunction())
        #     tableURLS = htmlDOI.convert(pz.URL, desc="The URLs of the XLS tables from the page", cardinality="oneToMany")
        #     # urlFile = pz.Dataset("biofabric-urls", schema=pz.TextFile)
        #     # tableURLS = urlFile.convert(pz.URL, desc="The URLs of the tables")
        #     binary_tables = tableURLS.map(pz.DownloadBinaryFunction())
        #     tables = binary_tables.convert(pz.File)
        #     xls = tables.convert(pz.XLSFile)
        #     patient_tables = xls.convert(pz.Table, desc="All tables in the file", cardinality="oneToMany")

        #     output = patient_tables
        #     iterable  =  pz.Execute(patient_tables,
        #                                     policy = pz_policy,
        #                                     nocache=True,
        #                                     allow_code_synth=False,
        #                                     allow_token_reduction=False,
        #                                     execution_engine=engine)


        # elif data_source == 'biofabric-tiny':
        #     xls = pz.Dataset('biofabric-tiny', schema=pz.XLSFile)
        #     patient_tables = xls.convert(pz.Table, desc="All tables in the file", cardinality="oneToMany")
        #     patient_tables = patient_tables.filter("The table contains biometric information about the patient")
        #     case_data = patient_tables.convert(CaseData, desc="The patient data in the table",cardinality="oneToMany")

        #     iterable  =  pz.Execute(case_data,
        #                                     policy = pz_policy,
        #                                     nocache=True,
        #                                     allow_code_synth=False,
        #                                     allow_token_reduction=False,
        #                                     execution_engine=engine)


        # elif data_source == 'bdf-usecase3-tiny':
        #     papers = pz.Dataset("bdf-usecase3-tiny", schema=ScientificPaper)
        #     # papers = papers.filter("The paper mentions phosphorylation of Exo1")
        #     references = papers.convert(Reference, desc="A paper cited in the reference section", cardinality="oneToMany")

        #     output = references
        #     iterable  =  pz.Execute(output,
        #                             policy = pz_policy,
        #                             nocache=True,
        #                             allow_sentinels = False,
        #                             allow_code_synth=False,
        #                             allow_token_reduction=False,
        #                             execution_engine=engine)


        # for idx, (records, plan, stats) in enumerate(iterable):
        #     json_records = [r._asDict(include_bytes=False) for r in records]
        #     str_plan = repr(plan)
        #     dict_stats = dataclasses.asdict(stats)

        #     with open(f'tmp_{idx}.pkl', 'wb') as f:
        #         pickle.dump((json_records, str_plan, dict_stats), f)
        #     yield (json_records, str_plan, dict_stats)