import networkx as nx
import pandas as pd
import gurobipy as gb


class FeasibleSolutionSearcher:
    def __init__(self, airline):
        self.airline = airline
        self.routes_graph = self.create_routes_graph()

    def search(self):
        D = self.routes_graph
        edge_index_dict = dict()
        index_edge_dict = dict()
        D_edges = list()
        counter = 0
        for e in D.edges():
            D_edges.append(list([e[0], e[1]]))
            edge_index_dict[e] = counter
            index_edge_dict[counter] = e
            counter += 1
        A0 = self.createA0(D)
        # integer problem for finding feasible solution
        ip = gb.Model()
        ip.Params.LogToConsole = 0
        X = ip.addVars([a for a in range(len(D.edges()))], vtype=gb.GRB.BINARY)
        # (1)
        for v in D.nodes():
            if D.in_degree(v) != 0 and D.out_degree(v) != 0:
                ip.addConstr(gb.quicksum(X[edge_index_dict[(a, v)]] for a in D.predecessors(v)) == gb.quicksum(
                    X[edge_index_dict[(v, a)]] for a in D.successors(v)))
        # (2)
        for v in D.nodes():
            if D.in_degree(v) != 0:
                ip.addConstr(gb.quicksum(X[edge_index_dict[(a, v)]] for a in D.predecessors(v)) == 1)
        # (3)
        ip.addConstr(gb.quicksum(X[edge_index_dict[a]] for a in A0) <= len(D_edges))
        ip.optimize()
        D2 = nx.Graph()
        for i in range(len(X)):
            if X[i].x == 1:
                D2.add_edge(D_edges[i][0], D_edges[i][1])
        feasible_solution = list()
        for i in nx.connected_components(D2):
            feasible_solution.append(list(i))
        return feasible_solution

    def createA0(self, D):
        instant = pd.to_datetime('2014-09-12 ' + str(23) + ':05:00')
        A0 = list()
        for e in D.edges():
            if ((pd.to_datetime(self.airline.flights[self.airline.flights.nid == e[0]].iloc[0, 11]) <= instant)
                    and (pd.to_datetime(self.airline.flights[self.airline.flights.nid == e[1]].iloc[0, 11]) > instant)):
                A0.append(e)
        return A0

    def create_routes_graph(self):
        D = nx.DiGraph()
        for i in range(len(self.airline.routes)):
            for j in range(len(self.airline.routes[i]) - 1):
                D.add_edge(self.airline.routes[i][j], self.airline.routes[i][j + 1])
        return D
