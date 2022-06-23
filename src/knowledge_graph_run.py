from knowledge_graph_TBOX import *
from knowledge_graph_ABOX import *
from rdflib import Graph

IdleComputeGraph = Graph()
create_TBOX_and_output_to_turtle(IdleComputeGraph)
create_ABOX_and_output_to_turtle(IdleComputeGraph)