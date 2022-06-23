# TBOX definition
from rdflib.namespace import RDFS, RDF
from rdflib import Namespace
from rdflib import Literal


def create_TBOX(graph):
    '''
    Function used to create all instances needed for TBOX
    :return: None. Creates RDFlip graph
    '''
    # Namespace means that we can just use "KG" as an "alias" for the URI
    KG = Namespace("http://www.IdleCompute/schema/")
    # binding is what adds the @prefix to the turtle file to make it easier to read in the output.
    graph.bind("IC", KG)

    graph.add((KG.Task, RDF.type, RDFS.Class))
    graph.add((KG.Task, RDFS.label, Literal("Task")))

    graph.add((KG.analysisType, RDFS.domain, KG.Task))
    graph.add((KG.analysisType, RDFS.range, KG.Model))
    graph.add((KG.analysisType, RDFS.label, Literal("Analysis Type")))
    graph.add((KG.Model, RDFS.label, Literal("Model")))

    graph.add((KG.A1, RDFS.subClassOf, KG.Model))
    graph.add((KG.A1, RDFS.label, Literal("XGBoost")))
    graph.add((KG.A2, RDFS.subClassOf, KG.Model))
    graph.add((KG.A2, RDFS.label, Literal("Linear Regression")))
    graph.add((KG.A3, RDFS.subClassOf, KG.Model))
    graph.add((KG.A3, RDFS.label, Literal("Random Forest")))
    graph.add((KG.A4, RDFS.subClassOf, KG.Model))
    graph.add((KG.A4, RDFS.label, Literal("Decision Tree")))
    graph.add((KG.A5, RDFS.subClassOf, KG.Model))
    graph.add((KG.A5, RDFS.label, Literal("SVC")))

    graph.add((KG.assignedTo, RDFS.domain, KG.Task))
    graph.add((KG.assignedTo, RDFS.range, KG.Resource))
    graph.add((KG.assignedTo, RDFS.label, Literal("assignedTo")))

    graph.add((KG.User, RDF.type, RDFS.Class))
    graph.add((KG.User, RDFS.label, Literal("User")))

    graph.add((KG.submits, RDFS.domain, KG.User))
    graph.add((KG.submits, RDFS.range, KG.Task))
    graph.add((KG.submits, RDFS.label, Literal("submits")))
    graph.add((KG.User, RDFS.label, Literal("User")))
    graph.add((KG.Task, RDFS.label, Literal("Task")))

    graph.add((KG.hasCapability, RDFS.domain, KG.Resource))
    graph.add((KG.hasCapability, RDFS.range, KG.ResourceType))
    graph.add((KG.Resource, RDFS.label, Literal("Resource")))
    graph.add((KG.ResourceType, RDFS.label, Literal("Resource Type")))


def output_graph_to_turtle(graph_name, filename):
    """
    Function will export the graph to a ".ttl" file and store it in data/processed directory.

    :param graph_name: RDFlib graph containing relations
    :param filename: desired output filename
    :return: None. Writes to new file.
    """
    graph_name.serialize(destination=f'../data/processed/{filename}.ttl')


def create_TBOX_and_output_to_turtle(graph):
    '''
    Main function used to create graphs and output TBOX in turtle format to /data/processed/TBOX.ttl
    :return: None.
    '''
    create_TBOX(graph)
    output_graph_to_turtle(graph, "TBOX")