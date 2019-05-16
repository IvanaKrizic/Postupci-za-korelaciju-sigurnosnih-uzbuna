file = open("dmz1_events.txt", "r")
out = open("dmz1_events_sorted.txt", "w")
lines = []
line = file.readline()
while (line):
	lines.append(line)
	print(line.split(",")[7])
	line=file.readline()

for line in sorted(lines, key=lambda line: line.split(",")[7]):
	out.write(line)


