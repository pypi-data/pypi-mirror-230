"""**Graphs** provide a natural language interface to graph databases."""

from langchainmulti.graphs.arangodb_graph import ArangoGraph
from langchainmulti.graphs.falkordb_graph import FalkorDBGraph
from langchainmulti.graphs.hugegraph import HugeGraph
from langchainmulti.graphs.kuzu_graph import KuzuGraph
from langchainmulti.graphs.memgraph_graph import MemgraphGraph
from langchainmulti.graphs.nebula_graph import NebulaGraph
from langchainmulti.graphs.neo4j_graph import Neo4jGraph
from langchainmulti.graphs.neptune_graph import NeptuneGraph
from langchainmulti.graphs.networkx_graph import NetworkxEntityGraph
from langchainmulti.graphs.rdf_graph import RdfGraph

__all__ = [
    "MemgraphGraph",
    "NetworkxEntityGraph",
    "Neo4jGraph",
    "NebulaGraph",
    "NeptuneGraph",
    "KuzuGraph",
    "HugeGraph",
    "RdfGraph",
    "ArangoGraph",
    "FalkorDBGraph",
]
