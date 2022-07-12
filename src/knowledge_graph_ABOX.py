import pandas as pd
from rdflib.namespace import RDF, RDFS
from rdflib import Graph
from rdflib import Namespace
from rdflib import Literal


def create_ABOX_and_output_to_turtle(graph: Graph):
    '''
    Creates instances from csv files located in "/data/raw/knowledge-graph/" directory
    Outputs ABOX in turtle format.
    :return: None. Writes to turtle file.
    '''
    filepath = '../data/knowledge-graph/'

    analysis_type = pd.read_csv(f"{filepath}analysis_type.csv")
    resource_type = pd.read_csv(f"{filepath}resource_type.csv")
    task_resource = pd.read_csv(f"{filepath}task_resource.csv")
    resource_IP = pd.read_csv(f"{filepath}resource_IP.csv")
    task_schedule_date = pd.read_csv(f"{filepath}task_schedule_date.csv")
    task_submission_date = pd.read_csv(f"{filepath}task_submission_date.csv")
    task_type = pd.read_csv(f"{filepath}task_type.csv")
    task_user = pd.read_csv(f"{filepath}task_user.csv")
    user_info = pd.read_csv(f"{filepath}user_info.csv")
    task_resource = pd.read_csv(f"{filepath}task_resource.csv")

    KG = Namespace("http://www.IdleCompute/schema/")
    graph.bind("IC", KG)

    for index, row in analysis_type.iterrows():
        type_id = row['type_id']
        analysis_name = row['analysis_name']
        graph.add((KG[type_id], RDF.type, KG.analysistype))
        graph.add((KG[type_id], RDFS.label, Literal(analysis_name)))

    for index, row in task_resource.iterrows():
        task_id = row['task_id']
        resource_id = row['resource_id']
        graph.add((KG[task_id], KG.assignedto, KG[resource_id]))

    for index, row in task_user.iterrows():
        task_id = row['task_id']
        user_id = row['user_id']
        graph.add((KG[user_id], KG.submits, KG[task_id]))

    for index, row in resource_IP.iterrows():
        resource_id = row['resource_id']
        resource_IP = row['resource_IP']
        graph.add((KG[resource_id], RDFS.label, Literal(resource_IP)))

    for index, row in task_type.iterrows():
        task_id = row['task_id']
        type_id = row['type_id']
        graph.add((KG[task_id], KG.analysisType, KG[type_id]))

    for index, row in resource_type.iterrows():
        resource_id = row['resource_id']
        resource_type = row['resource_type']
        graph.add((KG[resource_id], KG.hasCapability, KG[resource_type]))

    graph.serialize(destination=f'../data/processed/ABOX.ttl')