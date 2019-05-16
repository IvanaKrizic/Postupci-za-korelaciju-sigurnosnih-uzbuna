import datetime

class Alert:
    def __init__(self, sourceIP, destinationIP, attackClass, timestamp):
        self.sourceIP = sourceIP
        self.destinationIP = destinationIP
        self.attackClass = attackClass
        self.timestamp = timestamp


class Node:
    def __init__(self, IPaddresses, inEdges, outEdges):
        self.IPaddresses = IPaddresses
        self.inEdges = inEdges
        self.outEdges = outEdges


class Edge:
    def __init__(self, sourceNode, destNode, attackClass):
        self.sourceNode = sourceNode
        self.destNode = destNode
        self.attackClass = attackClass


class Pattern:
    def __init__(self, pNodes, pEdges, Vlabel, Elabel, lastModified):
        self.pNodes = pNodes
        self.pEdges = pEdges
        self.Vlabel = Vlabel
        self.Elabel = Elabel
        self.lastModified = lastModified


def generalization():
    for p in stablePatterns:
        test = True
        while test:
            test = False
            currentPattern = stablePatterns[p]
            OneToMany(currentPattern)
            removeNodes(currentPattern)
            x = joinNodes(currentPattern)
            ManyToOne(currentPattern)
            removeNodes(currentPattern)
            y = joinNodes(currentPattern)
            if x or y:
                test = True

def removeNodes(pattern):

    delNodes = set()
    for node in pattern.pNodes:
        currentNode = pattern.pNodes[node]
        if len(currentNode.inEdges) == 0 and len(currentNode.outEdges) == 0:
            delNodes.add(node)

    for x in delNodes:
        pattern.pNodes.pop(x)


def joinNodes(pattern):
    deleted = False
    deleteNode = 0
    for node1 in pattern.pNodes:
        for node2 in pattern.pNodes:
            if node1 != node2 and pattern.pNodes[node1].IPaddresses == pattern.pNodes[node2].IPaddresses:
                # premjesti node2 ulazne u node1 izlazne
                for i in pattern.pNodes[node2].inEdges:
                    edge2 = pattern.pEdges[i]
                    duplicate = False
                    for j in pattern.pNodes[node1].inEdges:
                        edge1 = pattern.pEdges[j]
                        if edge1.attackClass == edge2.attackClass and edge1.sourceNode == edge2.sourceNode:
                            duplicate = True
                            break
                    if not duplicate:
                        newEdge = Edge(edge2.sourceNode, node1, edge2.attackClass)
                        pattern.pEdges[pattern.Elabel] = newEdge
                        pattern.pNodes[node1].inEdges.add(pattern.Elabel)
                        pattern.pNodes[edge2.sourceNode].outEdges.add(pattern.Elabel)
                        pattern.Elabel = pattern.Elabel + 1

                # premjesti node2 izlazne u node1 izlazne
                for i in pattern.pNodes[node2].outEdges:
                    edge2 = pattern.pEdges[i]
                    duplicate = False
                    for j in pattern.pNodes[node1].outEdges:
                        edge1 = pattern.pEdges[j]
                        if edge1.attackClass == edge2.attackClass and edge1.destNode == edge2.destNode:
                            duplicate = True
                            break
                    if not duplicate:
                        newEdge = Edge(node1, edge2.destNode, edge2.attackClass)
                        pattern.pEdges[pattern.Elabel] = newEdge
                        pattern.pNodes[node1].outEdges.add(pattern.Elabel)
                        pattern.pNodes[edge2.destNode].inEdges.add(pattern.Elabel)
                        pattern.Elabel = pattern.Elabel + 1
                # obrisi node2
                for x in pattern.pNodes[node2].inEdges:
                    pattern.pNodes[pattern.pEdges[x].sourceNode].outEdges.difference_update(set([x]))
                    pattern.pEdges.pop(x)
                for x in pattern.pNodes[node2].outEdges:
                    pattern.pNodes[pattern.pEdges[x].destNode].inEdges.difference_update(set([x]))
                    pattern.pEdges.pop(x)
                deleteNode = node2
                deleted = True
                break

        if deleted:
            break

    if not deleted:
        return deleted
    pattern.pNodes.pop(deleteNode)
    return deleted

def deleteEdges(edges, s):
    pattern = edges[0]
    if s == "OneToMany":
        pattern.pNodes[edges[1]].outEdges = pattern.pNodes[edges[1]].outEdges - edges[3]
        for n in edges[2]:
            pattern.pNodes[n].inEdges = pattern.pNodes[n].inEdges - edges[3]
    elif s == "ManyToOne":
        pattern.pNodes[edges[1]].inEdges = pattern.pNodes[edges[1]].inEdges - edges[3]
        for n in edges[2]:
            pattern.pNodes[n].outEdges = pattern.pNodes[n].outEdges - edges[3]

    for e in edges[3]:
        pattern.pEdges.pop(e)


def createNodes(nodes, s):
    pattern = nodes[0]

    ipadd = set()
    for label in nodes[2]:
        ipadd.update(pattern.pNodes[label].IPaddresses)

    if s == "OneToMany":
        pattern.pNodes[nodes[1]].outEdges.add(pattern.Elabel)
        newEdge = Edge(nodes[1], pattern.Vlabel, nodes[3])
        newNode = Node(ipadd, set([pattern.Elabel]), set([]))
    elif s == "ManyToOne":
        pattern.pNodes[nodes[1]].inEdges.add(pattern.Elabel)
        newEdge = Edge(pattern.Vlabel, nodes[1], nodes[3])
        newNode = Node(ipadd, set([]), set([pattern.Elabel]))

    pattern.pNodes[pattern.Vlabel] = newNode
    pattern.pEdges[pattern.Elabel] = newEdge
    pattern.Vlabel = pattern.Vlabel + 1
    pattern.Elabel = pattern.Elabel + 1


def OneToMany(p):
    nodes = []
    edges = []
    for node in p.pNodes:
        currentNode = p.pNodes[node]
        visited = set()
        for x in currentNode.outEdges:
            generalize = []
            deledges = set()
            generalize.append(p.pEdges[x].destNode)
            deledges.add(x)
            if p.pEdges[x].attackClass not in visited:
                visited.add(p.pEdges[x].attackClass)
                for y in currentNode.outEdges:
                    if x != y and p.pEdges[x].attackClass == p.pEdges[y].attackClass:
                        generalize.append(p.pEdges[y].destNode)
                        deledges.add(y)
            if len(generalize) > 1:
                nodes.append((p, node, set(generalize), p.pEdges[x].attackClass))
                edges.append((p, node, set(generalize), deledges))

    for x in nodes:
        createNodes(x, "OneToMany")
    for y in edges:
        deleteEdges(y, "OneToMany")


def ManyToOne(p):
    nodes = []
    edges = []
    for node in p.pNodes:
        currentNode = p.pNodes[node]
        visited = set()
        for x in currentNode.inEdges:
            generalize = []
            deledges = set()
            m = p.pEdges[x].sourceNode
            generalize.append(m)
            deledges.add(x)
            if p.pEdges[x].attackClass not in visited:
                visited.add(p.pEdges[x].attackClass)
                for y in currentNode.inEdges:
                    if x != y and p.pEdges[x].attackClass == p.pEdges[y].attackClass:
                        generalize.append(p.pEdges[y].sourceNode)
                        deledges.add(y)
            if len(generalize) > 1:
                nodes.append((p, node, set(generalize), p.pEdges[x].attackClass))
                edges.append((p, node, set(generalize), deledges))

    for x in nodes:
        createNodes(x, "ManyToOne")
    for y in edges:
        deleteEdges(y, "ManyToOne")

#key u hash table su i sourceip i destip, a value je (pattern, node)
patternHashTable = {}
activePatterns = {}
stablePatterns = {}
file = open("inputfiles/dmz1_events_sorted.txt", "r")
line = file.readline()
plabel= 0
stableplabel = 0
time = input("Enter keep active period: ")
keepActive = datetime.timedelta(seconds = time)

while line:
    splitted = line.split(",")
    currentAlert = Alert(splitted[9], splitted[12], splitted[37], datetime.datetime.strptime(splitted[7], '%Y-%m-%d %H:%M:%S'))
    insert = False

    movePatt = set()
    for p in activePatterns:
        if currentAlert.timestamp - activePatterns[p].lastModified > keepActive:
            # prebaci iz active u stable
            movePatt.add(p)
            stablePatterns[stableplabel] = activePatterns[p]
            stableplabel = stableplabel + 1
            # makni sve iz hashtablea
            delPatt = set()
            for hash in patternHashTable:
                if patternHashTable[hash][0] == p:
                    delPatt.add(hash)

            for delp in delPatt:
                patternHashTable.pop(delp)

    for move in movePatt:
        activePatterns.pop(move)

    if currentAlert.sourceIP in patternHashTable:
        insert = True
        currentPattern = activePatterns[patternHashTable[currentAlert.sourceIP][0]]
        if currentAlert.destinationIP in patternHashTable and patternHashTable[currentAlert.destinationIP][0] == patternHashTable[currentAlert.sourceIP][0]:
                newEdge = Edge(patternHashTable[currentAlert.sourceIP][1], patternHashTable[currentAlert.destinationIP][1], currentAlert.attackClass)
                currentPattern.pEdges[currentPattern.Elabel] = newEdge
                srcNode = currentPattern.pNodes[patternHashTable[currentAlert.sourceIP][1]]
                dstNode = currentPattern.pNodes[patternHashTable[currentAlert.destinationIP][1]]
                srcNode.outEdges.add(currentPattern.Elabel)
                dstNode.inEdges.add(currentPattern.Elabel)
                currentPattern.Elabel = currentPattern.Elabel + 1
        else:
            newNode = Node(set([currentAlert.destinationIP]), set([currentPattern.Elabel]), set([]))
            newEdge = Edge(patternHashTable[currentAlert.sourceIP][1], currentPattern.Vlabel, currentAlert.attackClass)
            currentPattern.pNodes[currentPattern.Vlabel] = newNode
            currentPattern.pEdges[currentPattern.Elabel] = newEdge
            srcNode = currentPattern.pNodes[patternHashTable[currentAlert.sourceIP][1]]
            srcNode.outEdges.add(currentPattern.Elabel)
            patternHashTable[currentAlert.destinationIP] = (patternHashTable[currentAlert.sourceIP][0],
                                                            currentPattern.Vlabel)
            currentPattern.Vlabel = currentPattern.Vlabel + 1
            currentPattern.Elabel = currentPattern.Elabel + 1

        currentPattern.lastModified = currentAlert.timestamp

    elif currentAlert.destinationIP in patternHashTable:
        insert = True
        currentPattern = activePatterns[patternHashTable[currentAlert.destinationIP][0]]
        if currentAlert.sourceIP in patternHashTable and \
                patternHashTable[currentAlert.destinationIP][0] == patternHashTable[currentAlert.sourceIP][0]:
            newEdge = Edge(patternHashTable[currentAlert.sourceIP][1], patternHashTable[currentAlert.destinationIP][1],
                           currentAlert.attackClass)
            currentPattern.pEdges[currentPattern.Elabel] = newEdge
            srcNode = currentPattern.pNodes[patternHashTable[currentAlert.sourceIP][1]]
            dstNode = currentPattern.pNodes[patternHashTable[currentAlert.destinationIP][1]]
            srcNode.outEdges.add(currentPattern.Elabel)
            dstNode.inEdges.add(currentPattern.Elabel)
            currentPattern.Elabel = currentPattern.Elabel + 1
        else:
            newNode = Node(set([currentAlert.sourceIP]), set([]), set([currentPattern.Elabel]))
            newEdge = Edge(currentPattern.Vlabel, patternHashTable[currentAlert.destinationIP][1],
                           currentAlert.attackClass)
            currentPattern.pNodes[currentPattern.Vlabel] = newNode
            currentPattern.pEdges[currentPattern.Elabel] = newEdge
            dstNode = currentPattern.pNodes[patternHashTable[currentAlert.destinationIP][1]]
            dstNode.inEdges.add(currentPattern.Elabel)
            patternHashTable[currentAlert.sourceIP] = (patternHashTable[currentAlert.destinationIP][0], currentPattern.Vlabel)
            currentPattern.Vlabel = currentPattern.Vlabel + 1
            currentPattern.Elabel = currentPattern.Elabel + 1

        currentPattern.lastModified = currentAlert.timestamp

    if not insert:
        pattNodes = dict()
        pattEdges = dict()

        pattNodes[0] = Node(set([currentAlert.sourceIP]), set(), set([0]))
        pattNodes[1] = Node(set([currentAlert.destinationIP]), set([0]), set())
        pattEdges[0] = Edge(0, 1, currentAlert.attackClass)

        # hashiraj alert po srcu
        patternHashTable[currentAlert.sourceIP] = (plabel, 0)
        # hashiraj alert po dest
        patternHashTable[currentAlert.destinationIP] = (plabel, 1)
        # stvori novi pattern
        activePatterns[plabel] = Pattern(pattNodes, pattEdges, 2, 1, currentAlert.timestamp)  # sljedeci vlabel je 2, slj elabel je 1
        plabel = plabel + 1

    line = file.readline()

# prebaci ostatak iz active u stable
movePatt = set()
for p in activePatterns:
    movePatt.add(p)
    stablePatterns[stableplabel] = activePatterns[p]
    stableplabel = stableplabel + 1
    delPatt = set()
    for hash in patternHashTable:
        if patternHashTable[hash][0] == p:
            delPatt.add(hash)

    for delp in delPatt:
        patternHashTable.pop(delp)

for move in movePatt:
    activePatterns.pop(move)

generalization()

"""
for pat in stablePatterns:
    for n in stablePatterns[pat].pNodes:
        print(pat, n,  stablePatterns[pat].pNodes[n].inEdges)

    for e in stablePatterns[pat].pEdges:
        m = stablePatterns[pat].pEdges[e]
        print(e, m.sourceNode, m.destNode, m.attackClass)


for pat in stablePatterns:
    for n in stablePatterns[pat].pNodes:
        print(pat, n,  stablePatterns[pat].pNodes[n].IPaddresses)

    for e in stablePatterns[pat].pEdges:
        m = stablePatterns[pat].pEdges[e]
        print(e, m.sourceNode, m.destNode, m.attackClass)
"""
inputNodes = {}
inputNodeLabel = 0
inputEdges = {}
inputEdgeLabel = 0
input = open("gaston-1.1/data.txt", "w")

pattenrdict = {}

for p in stablePatterns:
    input.write("t # " + str(p) + "\n")
    i = 0
    nod = {}
    for v in stablePatterns[p].pNodes:
        sortedTuple = tuple(sorted(stablePatterns[p].pNodes[v].IPaddresses))
        if sortedTuple not in inputNodes:
            inputNodes[sortedTuple] = inputNodeLabel
            inputNodeLabel = inputNodeLabel + 1
        nod[v] = i
        input.write("v " + str(i) + " " + str(inputNodes[sortedTuple]) + "\n")
        i = i + 1

    pattenrdict[p] = nod

    for e in stablePatterns[p].pEdges:
        ine = sorted(tuple(stablePatterns[p].pNodes[v].IPaddresses))
        oute = sorted(tuple(stablePatterns[p].pNodes[v].IPaddresses))
        if stablePatterns[p].pEdges[e].attackClass not in inputEdges:
            inputEdges[stablePatterns[p].pEdges[e].attackClass] = inputEdgeLabel
            inputEdgeLabel = inputEdgeLabel + 1
        input.write("e " + str(pattenrdict[p][stablePatterns[p].pEdges[e].sourceNode]) + " " + \
                    str(pattenrdict[p][stablePatterns[p].pEdges[e].destNode]) + " " + \
                                   str(inputEdges[stablePatterns[p].pEdges[e].attackClass]) + "\n")

output = open("outnodes.txt", "w")
outDict = {}
for x in inputNodes:
    outDict[inputNodes[x]] = x

for y in outDict:
    output.write(str(y) + "|")
    for m in outDict[y]:
        output.write(str(m) + ",")
    output.write("\n")

outputedges = open("outedges.txt", "w")
for x in inputEdges:
    outputedges.write(str(inputEdges[x]) + "," + str(x) + "\n")

file.close()