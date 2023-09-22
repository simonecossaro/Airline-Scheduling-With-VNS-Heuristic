import random


class Neighborhood:
    def __init__(self, flights):
        self.flights = flights

    def neighborhood(self, P):
        r = random.randint(0,3)
        if r == 0:
            return self.cross(P)
        elif r == 1:
            return self.insert(P)
        elif r == 2:
            return self.swap(P)
        elif r == 3:
            return self.delete(P)

    def cross(self, P):
        n1 = random.randint(0, len(P) - 1)
        for n2 in range(len(P)):
            if n1 != n2:
                for u in range(1, len(P[n1])):
                    for v in range(1, len(P[n2])):
                        if self.con(P[n1][u - 1], P[n2][v]) and self.con(P[n2][v - 1], P[n1][u]):
                            P2 = P
                            P2[n1][u] = P[n2][v]
                            P2[n2][v] = P[n1][u]
                            return P2

    def insert(self, P):
        n1 = random.randint(0, len(P) - 1)
        for n2 in range(len(P)):
            if n1 != n2:
                for u in range(1, len(P[n1])):
                    for v in range(1, len(P[n2])):
                        for w in range(0, len(P[n2]) - 1):
                            if (v != w and self.con(P[n1][u - 1], P[n2][v]) and self.con(P[n2][w], P[n1][u])
                                    and self.arr(P[n2][v - 1]) == self.dep(P[n2][w + 1])):
                                P2 = P
                                x = P[n2][v:w + 1]
                                for i in range(len(x)):
                                    P2[n2].remove(x[i])
                                for i in range(len(x)):
                                    P2[n1].insert(u + i, x[i])
                                return P2

    def swap(self, P):
        n1 = random.randint(0, len(P) - 1)
        for n2 in range(len(P)):
            if n1 != n2:
                for u in range(1, len(P[n1]) - 1):
                    for v in range(1, len(P[n2]) - 1):
                        if (self.con(P[n1][u - 1], P[n2][v]) and self.con(P[n2][v], P[n1][u + 1])
                                and self.con(P[n2][v - 1], P[n1][u]) and self.con(P[n1][u], P[n2][v + 1])):
                            P2 = P
                            P2[n1][u] = P[n2][v]
                            P2[n2][v] = P[n1][u]
                            return P2

    def delete(self, P):
        n1 = random.randint(0, len(P) - 1)
        for u in range(len(P[n1])):
            if self.is_optional(P[n1][u]):
                for n2 in range(len(P)):
                    if n1 != n2:
                        for v1 in range(len(P[n2]) - 1):
                            if self.dep(P[n1][u]) == self.dep(P[n2][v1]):
                                for v2 in range(v1, len(P[n2])):
                                    if self.arr(P[n1][u]) == self.dep(P[n2][v2]):
                                        P2 = P
                                        P2[n1].remove(P[n1][u])
                                        for i in range(v1, v2 + 1):
                                            P2[n1].insert(u + (i - v1), P[n2][i])
                                        return P2

    def dep(self, f):
        return self.flights[self.flights.nid == f].iloc[0, 7]

    def arr(self, f):
        return self.flights[self.flights.nid == f].iloc[0, 8]

    def con(self, f1, f2):
        if self.arr(f1) == self.dep(f2):
            return True
        return False

    def is_optional(self, f):
        if self.flights[self.flights.nid == f].iloc[0, 23] == 0:
            return True
        return False
