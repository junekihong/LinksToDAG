

filename = "link_analysis_coarse_table.tex"
newfilename = "link_table_filtered.tex"
newfilename2 = "link_table_filtered_part2.tex"


f = open(filename)

new = open(newfilename, "w")
new2 = open(newfilename2, "w")

i = 0
newlines = 0

for line in f:
    i += 1

    if i < 12:
        if "tabular" in line:
            new.write("\\begin{tabular}{|l|l|l|l|l|l|}\n")
            new2.write("\\begin{tabular}{|l|l|}\n")
        elif "Label" in line:
            new.write("Label & Rightward & Multiheaded & CoNLL Match & CoNLL Dir Match\\\\\\hline\n")
            new2.write("Label & CoNLL Label\\\\\\hline\n")
        else:
            new.write(line)
            new2.write(line)
        continue

    if not i < 123:
        new.write(line)
        new2.write(line)
        continue



    line = line.strip()
    line = line.split("&")

    total_num = int(line[2].split()[1].replace("(","").replace(")","").split("/")[1])

    if total_num > 1450:
        
        
        line2 = [line[0], line[-1]]
        line = line[:-1]

        line = "&".join(line) + " \\\\"
        line2 = "&".join(line2)

        print >> new, line
        print >> new2, line2
        newlines += 1
        #print newlines, total_num, line
        
