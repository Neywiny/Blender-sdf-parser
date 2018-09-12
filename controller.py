data = open('C:/Users/Dylan/Documents/Blender Projects/Molecule/cocaine3.sdf','r').read()
lData = list(data.split("\n"))
currAtom = 1
V3000 = 'V3000' in lData[3]
for line in lData[4:]:
    if V3000:
        line = line.split()
        if len(line) == 8:
            print(line[3],(float(line[4]),float(line[5]),float(line[6])))
            currAtom += 1
        elif len(line) == 5:
            atom1,atom2 = line[4],line[5]
            print(line[3],atom1,atom2)
        else:
            print len(line)
    else:
        if '.' in line:
            createAtom(line[31:35].strip(),(float(line[3:10]),-float(line[13:20]),float(line[23:30])))
            currAtom += 1
        elif not '.' in line:
            atom1,atom2,type = line[0:3],line[3:6],line[8].strip().lstrip()
            atom1,atom2 = atom1.lstrip().strip(),atom2.lstrip().strip()
            atom1,atom2 = bpy.data.objects[atom1],bpy.data.objects[atom2]
            createBond(type,atom1,atom2)
