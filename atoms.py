colors = {'C':'(32,32,32)','O':'(240,0,0)','H':'(255,255,255)','N':'(143,143,255)','S':'(255,200,50)','P':'(255,165,0)','Cl':'(0,255,0)','Br':'(165,42,42)', 'Zn':'(165,42,42)','Na':'(0,0,255)','Fe':'(255,165,0)','Mg':'(42,128,42)','Ca':'(128,128,128)','Unknown':'(255,20,147)'}
f = open('atoms.csv')
rows = f.readlines()
f.close()
atoms = dict()
for row in rows:
    split = row.split(',')
    atoms[split[0]] = {'size':int(split[1])}
    if split[0] in colors.keys():
        atoms[split[0]]['color'] = eval(colors[split[0]])
    else:
        atoms[split[0]]['color'] = colors['Unknown']
