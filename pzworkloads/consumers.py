import asyncio
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
    'nosentinel': pz.SequentialSingleThreadNoSentinelExecution,
    'sequential': pz.SequentialSingleThreadSentinelExecution,
    'parallel': pz.PipelinedParallelSentinelExecution,
}

def collection_dataset():
    # papers = pz.Dataset("biofabric-pdf", schema=ScientificPaper)
    # paperURLs = papers.convert(pz.URL, desc="The DOI url of the paper") 
    # htmlDOI = paperURLs.map(pz.DownloadHTMLFunction())
    # tableURLS = htmlDOI.convert(pz.URL, desc="The URLs of the XLS tables from the page", cardinality="oneToMany")
    urlFile = pz.Dataset("biofabric-urls", schema=pz.TextFile)
    tableURLS = urlFile.convert(pz.URL, desc="The URLs of the tables")
    tables = tableURLS.convert(pz.File, udf=pz.utils.udfs.url_to_file)
    xls = tables.convert(pz.XLSFile, udf = pz.utils.udfs.file_to_xls)
    patient_tables = xls.convert(pz.Table, udf=pz.utils.udfs.xls_to_tables, cardinality=pz.Cardinality.ONE_TO_MANY)
    return patient_tables

def case_data_dataset():
    xls = pz.Dataset('biofabric-tiny', schema=pz.XLSFile)
    patient_tables = xls.convert(pz.Table, udf=pz.utils.udfs.xls_to_tables, cardinality=pz.Cardinality.ONE_TO_MANY)
    patient_tables = patient_tables.filter("The table contains biometric information about the patient")
    case_data = patient_tables.convert(CaseData, desc="The patient data in the table",cardinality="oneToMany")
    return case_data

def reference_dataset():
    papers = pz.Dataset("bdf-usecase3-tiny", schema=ScientificPaper)
    papers = papers.filter("The paper mentions phosphorylation of Exo1")
    references = papers.convert(Reference, desc="A paper cited in the reference section", cardinality="oneToMany")
    return references


DATASETS = {
    'collection': collection_dataset(),
    'casedata': case_data_dataset(),
    'reference': reference_dataset(),
}

TASKS = {
    'collection': """papers = pz.Dataset("biofabric-pdf", schema=ScientificPaper)
paperURLs = papers.convert(pz.URL, desc="The DOI url of the paper") 
htmlDOI = paperURLs.map(pz.DownloadHTMLFunction())
tableURLS = htmlDOI.convert(pz.URL, desc="The URLs of the XLS tables from the page", cardinality="oneToMany")
binary_tables = tableURLS.map(pz.DownloadBinaryFunction())
tables = binary_tables.convert(pz.File)
xls = tables.convert(pz.XLSFile)
patient_tables = xls.convert(pz.Table, desc="All tables in the file", cardinality="oneToMany")
""",
    'casedata': """xls = pz.Dataset('biofabric-tiny', schema=pz.XLSFile)
patient_tables = xls.convert(pz.Table, desc="All tables in the file", cardinality="oneToMany")
patient_tables = patient_tables.filter("The table contains biometric information about the patient")
case_data = patient_tables.convert(CaseData, desc="The patient data in the table",cardinality="oneToMany")
""",
    'reference': """papers = pz.Dataset("bdf-usecase3-tiny", schema=ScientificPaper)
papers = papers.filter("The paper mentions phosphorylation of Exo1")
references = papers.convert(Reference, desc="A paper cited in the reference section", cardinality="oneToMany")""",
}

class TaskDescriptionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        task_id = text_data_json['task_id']

        # Fetch the task description based on the task_id
        task_description = TASKS[task_id].replace('\n', '<br>')

        await self.send(text_data=json.dumps({
            'task_description': task_description
        }))


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
        with open(f'cache/computed_plan_{policy}.pkl', 'wb') as f:
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
        task = text_data_json['task']
        plan = text_data_json['plan']
        usecache = text_data_json['use_cache']
        policystr = text_data_json['policy']
        
        with open(f'cache/computed_plan_{policystr}.pkl', 'rb') as f:
            engine, plan = cloudpickle.load(f)

        finished = False
        start_time = time.time()
        input_records = engine.get_input_records()
        for idx, record in enumerate(input_records):
            if usecache and os.path.exists(f'cache/records/{task}_{policystr}_{idx}.pkl'):
                with open(f'cache/records/{task}_{policystr}_{idx}.pkl', 'rb') as f:
                    output_records = cloudpickle.load(f)
                with open(f'cache/stats/{task}_{policystr}_{idx}.pkl', 'rb') as f:
                    stats = cloudpickle.load(f)
                if idx == len(input_records) - 1:
                    finished = True
            else:
                output_records = engine.execute_opstream(plan, record)
                if idx == len(input_records) - 1:
                    total_time = time.time() - start_time
                    engine.plan_stats.finalize(total_time)
                    finished = True
                stats = engine.plan_stats

                with open(f'cache/records/{task}_{policystr}_{idx}.pkl', 'wb') as f:
                    cloudpickle.dump(output_records, f)
                with open(f'cache/stats/{task}_{policystr}_{idx}.pkl', 'wb') as f:
                    cloudpickle.dump(stats, f)

            if len(output_records) > 0:
                await self.send(text_data=json.dumps({
                    'schema': output_records[0].schema.fieldNames(),
                    'records': [{name:getattr(r,name) for name in r.schema.fieldNames()} for r in output_records],
                    'stats':str(stats),
                    'finished':finished,
                    # 'stats':dataclasses.asdict(stats),
                }))
            else:
                await self.send(text_data=json.dumps({
                    'schema': [],
                    'records': [],
                    'stats':str(stats),
                    'finished':finished,
                    # 'stats':dataclasses.asdict(stats),
                }))
            # await asyncio.sleep(5)
        await self.close()


class FileListConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        task = data.get('task')
        directory = f'cache/dataset/{task}/'  # Adjust the path based on the selected task
        files = []

        for filename in os.listdir(directory):
            if filename.endswith('.pdf'):
                file_type = 'pdf'
            elif filename.endswith('.xlsx') or filename.endswith('.xls'):
                file_type = 'excel'
            elif filename.endswith('.docx') or filename.endswith('.doc'):
                file_type = 'word'
            else:
                file_type = 'generic'

            files.append({
                'name': filename,
                'type': file_type,
            })

        await self.send(text_data=json.dumps({'files': files}))