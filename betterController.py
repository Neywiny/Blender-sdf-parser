from time import time
start = time()
import bpy
import math  
import bmesh
from mathutils import Euler
try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **kwargs):
        for val in iterable:
            yield val

def clearOrphans():
    for window in bpy.context.window_manager.windows:
        screen = window.screen

        for area in screen.areas:
            if area.type == 'OUTLINER':
                override = {'window': window, 'screen': screen, 'area': area}
                bpy.ops.outliner.orphans_purge(override)
                break

bpyscene = bpy.context.scene
#f = open("log.csv", "w")

#import gc
#gc.enable()
#import os
#os.system('cls')

path = "C:/Users/Dylan/Documents/Blender Projects/Molecule/"
settings = eval(open(path+'settings.txt').read())
atomProps = eval(open(path+'atomPropsTable.txt').read())

bpy.ops.object.select_all()
bpy.ops.object.delete()

def debug(*args):
  if True:
    print(*args)

if 'molecule' in bpy.data.collections:
    coll = bpy.data.collections['molecule']
else:
    coll = bpy.data.collections.new("molecule")
    bpyscene.collection.children.link(coll)

if 'Empty' not in bpy.data.objects:
    bpy.ops.object.empty_add(type='PLAIN_AXES')
    coll.objects.link(bpyscene.objects['Empty'])
empty = bpy.data.objects['Empty']

debug("deleting")
for child in empty.children:
    child.select_set(True)
    bpy.ops.object.delete()
debug('old objects deleted')

doubleSeparation = 0.1

for atom in atomProps.keys():
    mat = (bpy.data.materials.get(atom) or bpy.data.materials.new(atom))
    mat.diffuse_color = (atomProps[atom]['color'][0]/255.0, atomProps[atom]['color'][1]/255.0, atomProps[atom]['color'][2]/255.0, 255)
    atomProps[atom]['material'] = mat

bMat = (bpy.data.materials.get('bond') or bpy.data.materials.new('bond'))
bMat.diffuse_color = (0.5,0.5,0.5, 1)

debug("reading")
data = open(path+settings['file'],'r').read()
debug("read")

lData = list(data.split("\n"))

currAtom = 1
def cylinder_between(x1, y1, z1, x2, y2, z2, r):
  mesh = bpy.data.meshes.new("bond")
  dx = x2 - x1
  dy = y2 - y1
  dz = z2 - z1    
  dist = math.sqrt(dx**2 + dy**2 + dz**2)
  bm = bmesh.new()
  bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24, diameter1=r*2, diameter2=r*2, depth=dist)
#  bpy.ops.mesh.primitive_cylinder_add(
#      radius = r, 
#      depth = dist,
#      location = (dx/2 + x1, dy/2 + y1, dz/2 + z1)   
#  ) 
  center = ((x1 + x2)/2, (y1 + y2)/2, (z1 + z2)/2)
  center = (dx/2 + x1, dy/2 + y1, dz/2 + z1) 
  phi = math.atan2(dy, dx)
  theta = math.acos(dz/dist)
  bmesh.ops.rotate(bm, verts=bm.verts, cent=((0,0,0)), matrix=Euler((0, theta, phi), "XYZ").to_matrix())
  bmesh.ops.translate(bm, verts=bm.verts, vec = center)
#  bpy.context.object.rotation_euler[1] = theta 
#  bpy.context.object.rotation_euler[2] = phi
#  return bpy.context.object
  bm.to_mesh(mesh)
  bm.free()
  return mesh
def createAtom(aType,location):
    name = str(currAtom)
    # Create an empty mesh and the object.
    mesh = bpy.data.meshes.new(name)
#    ob = bpy.data.objects.new(name, mesh)

    # Construct the bmesh sphere and assign it to the blender mesh.
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=4, diameter=atomProps[aType]['size']/100.0)
    bmesh.ops.translate(bm, verts=bm.verts, vec = location)
    bm.to_mesh(mesh)
    bm.free()
    return mesh
#    return ob
def createBond(type, atom1, atom2):
    if type == '1':
        mesh = cylinder_between(atom1[0],atom1[1],atom1[2],atom2[0],atom2[1],atom2[2],0.05)
        bonds.append(mesh)
    elif type == '2':
        mesh1 = cylinder_between(atom1[0],atom1[1],atom1[2]+doubleSeparation,atom2[0],atom2[1],atom2[2]+doubleSeparation,0.05)
        mesh2 = cylinder_between(atom1[0],atom1[1],atom1[2]-doubleSeparation,atom2[0],atom2[1],atom2[2]-doubleSeparation,0.05)
        bonds.extend((mesh1, mesh2))
    elif type == '3':
        mesh1 = cylinder_between(atom1[0],atom1[1],atom1[2],atom2[0],atom2[1],atom2[2],0.05)
        mesh2 = cylinder_between(atom1[0],atom1[1],atom1[2]+doubleSeparation,atom2[0],atom2[1],atom2[2]+doubleSeparation,0.05)
        mesh3 = cylinder_between(atom1[0],atom1[1],atom1[2]-doubleSeparation,atom2[0],atom2[1],atom2[2]-doubleSeparation,0.05)
        bonds.extend((mesh1, mesh2, mesh3))
debug('creation start')
atoms = dict()
bonds = list()
locations = dict()
currAtom = 1
for line in lData:
    if 'V2000' in line:
        V3000 = pdb = False
        mLine = len(lData)
        lData = list(filter(lambda x: len(x) > 0, lData))
        break
    elif 'V3000' in line:
        V3000 = True
        mLine = lData.index("M  END")
        break
if settings['file'].endswith('pdb'):
    V3000 = False
    pdb = True
for index, line in enumerate(tqdm(lData[4:] if V3000 else lData[3:], ascii=True, total=mLine, disable=False)):
    if V3000:
        if line == 'M  V30 END BOND':
            break
        split = line.split()
        if '.' in line:
            t1 = time()
            if split[3] in atoms:
                atoms[split[3]].append(createAtom(split[3],tuple(map(float,split[4:7]))))
            else:
                atoms[split[3]] = [createAtom(split[3],tuple(map(float,split[4:7])))]
            locations[str(currAtom)] = tuple(map(float,split[4:7]))
            #f.write(f"{currAtom}, {time()-t1}\n")
            currAtom += 1
        elif not '.' in line and (not 'END' in line) and (not 'BEGIN' in line) and (not 'COUNTS' in line):
            t1 = time()
            atom1,atom2,type = split[4],split[5],split[3]
            atom1,atom2 = locations[atom1], locations[atom2]
            createBond(type,atom1,atom2)
            #f.write(f"bond, {time()-t1}\n")
    elif not pdb:
        if '.' in line:
            type = line[31:35].strip()
            x,y,z = float(line[3:10]),float(line[13:20]),float(line[23:30])
            if type in atoms:
                atoms[type].append(createAtom(type,(x,y,z)))
            else:
                atoms[type] = [createAtom(type,(x,y,z))]
            locations[str(currAtom)] = (x,y,z)
            currAtom += 1
        elif not '.' in line:
            atom1,atom2,type = line[0:3],line[3:6],line[8].strip().lstrip()
            atom1,atom2 = atom1.lstrip().strip(),atom2.lstrip().strip()
            atom1,atom2 = locations[atom1], locations[atom2]
            createBond(type,atom1,atom2)
    elif pdb:
        if (line.startswith("ATOM") or line.startswith("HETATM")) and (line[77:79].strip() != "aeroiugb"):
            createAtom(line[76:78].strip().capitalize(),(float(line[31:39]),float(line[39:47]),float(line[47:54])))
debug("merging")
for aType in tqdm(atoms.keys(), ascii=True):
    mesh = bpy.data.meshes.new(aType)
    ob = bpy.data.objects.new(aType, mesh)
    bm = bmesh.new()
    for atom in atoms[aType]:
        #bm.from_mesh(atom.data)
        bm.from_mesh(atom)
    bm.to_mesh(mesh)
    bm.free()
    ob.active_material = atomProps[aType]['material']
    ob.parent = empty
    atoms[aType] = ob
debug("done merging, now displaying")
for aType in tqdm(atoms.keys(), ascii=True):
    atom = atoms[aType]
    # Add the object into the scene.
    coll.objects.link(atom)
    
    #bpyscene.objects.active = atom
    atom.select_set(True)
    bpy.ops.object.shade_smooth()
    atom.select_set(False)
debug("merging bonds")
name = "bonds"
mesh = bpy.data.meshes.new(name)
bondsObject = bpy.data.objects.new(name, mesh)
bm = bmesh.new()
for bond in bonds:
    bm.from_mesh(bond)
bm.to_mesh(mesh)
bm.free()
#bondsObject.active_material = atomProps[name]['material']
bondsObject.parent = empty
debug("done merging bonds, now displaying bonds")
# Add the object into the scene.
coll.objects.link(bondsObject)
bondsObject.select_set(True)
bpy.ops.object.shade_smooth()
bondsObject.select_set(False)
bondsObject.active_material = bMat
atoms["H"].select_set(True)
bpy.ops.object.origin_set(type="ORIGIN_CENTER_OF_VOLUME")
for child in empty.children:
  pass
  if child.name != "H":
    child.location -= atoms["H"].location
atoms["H"].location = (0,0,0)
debug("clearing orphans")
clearOrphans()
debug(time() - start)
#f.close()