#     Copyright (c) 2023, Kevan White (Thyripian)
#     All rights reserved.

#     Redistribution and use in source and binary forms, with or without
#     modification, are permitted provided that the following conditions are met:
#       Compliance with MIT License clauses.

#     THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#     AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#     IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#     DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#     FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#     DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#     SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#     CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#     OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#     OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import networkx as nx

def create_network():
    try:
        """Create an empty network with no nodes and no edges."""
        return nx.Graph()
    except Exception as e:
        print("An error occurred:", str(e))
        raise
def add_node(G, node_for_adding, **attr):
    try:
        """Add a single node and update node attributes using key-value pairs."""
        return G.add_node(node_for_adding, **attr)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def add_edge(G, u_of_edge, v_of_edge, **attr):
    try:
        """Add an edge between u and v."""
        return G.add_edge(u_of_edge, v_of_edge, **attr)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def degree(G, nbunch=None, weight=None):
    try:
        """Return the degree of a node or nodes."""
        return G.degree(nbunch, weight)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def draw_network(G, *args, **kwargs):
    try:
        """Draw the graph G."""
        return nx.draw(G, *args, **kwargs)

    except Exception as e:
        print("An error occurred:", str(e))
        raise