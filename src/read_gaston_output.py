#ucitati node oznake iz aggregation.py
file1 = open("outnodes.txt", "r")
line1= file1.readline()
nodes = {}
while line1:
    s = line1.strip().split("|")
    addresses = s[1].split(",")
    del addresses[-1]
    nodes[s[0]] = set(addresses)
    line1 = file1.readline()

#ucitati edge oznake iz aggregation.py
file2 = open("outedges.txt", "r")
line2 = file2.readline()
edges = {}
while line2:
    str = line2.strip().split(",")
    edges[str[0]] = str[1]
    line2 = file2.readline()

file3 = open("./gaston-1.1/out.txt", "r")
output = open("freqPatterns.txt", "w")
line3 = file3.readline()
while line3:
    if line3.startswith("#"):
        num = line3.strip().split(" ")[1]
        line3 = file3.readline()
        patt = line3.strip().split(" ")[1]
        output.write("  Pattern #" + patt + " with frequency " + num + "\n")
        line3 = file3.readline()
        pNodes = {}
        while line3.startswith("v"):
            s = line3.strip().split(" ")
            node = s[1]
            label = s[2]
            pNodes[node] = label
            line3 = file3.readline()
        i = 1
        while line3.startswith("e"):
            s = line3.strip().split(" ")
            node1 = nodes[pNodes[s[1]]]
            node2 = nodes[pNodes[s[2]]]
            output.write("ATTACKCLASS: " + edges[s[3]] + "\n")
            output.write("SOURCE: " + ', '.join(node1) + "\n")
            output.write("DESTINATION: " + ', '.join(node2) + "\n")
            i = i + 1
            line3 = file3.readline()