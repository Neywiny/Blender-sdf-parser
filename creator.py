print('-'*50)
import bpy,math,sys,os,time,mathutils
from mathutils import Euler
#bpy.ops.wm.console_toggle()
path = "C:/Users/Dylan/Documents/Blender Projects/Molecule/"
settings = eval(open(path+'settings.txt').read())
atomProps = eval(open(path+'atomPropsTable.txt').read())

def cylinder_between(x1, y1, z1, x2, y2, z2, r):
  dx = x2 - x1
  dy = y2 - y1
  dz = z2 - z1    
  dist = math.sqrt(dx**2 + dy**2 + dz**2)

  bpy.ops.mesh.primitive_cylinder_add(
      radius = r, 
      depth = dist,
      location = (dx/2 + x1, dy/2 + y1, dz/2 + z1)   
  ) 

  phi = math.atan2(dy, dx) 
  theta = math.acos(dz/dist) 

  bpy.context.object.rotation_euler[1] = theta 
  bpy.context.object.rotation_euler[2] = phi
  return bpy.context.object

bpy.ops.object.select_all()
bpy.ops.object.delete()
#if bpy.data.objects.get("Cube"): bpy.data.objects['Cube'].select = True
#bpy.ops.object.delete()
##if bpy.data.objects.get("Lamp"): bpy.data.objects['Lamp'].select = True
##bpy.ops.object.delete()
if 'Empty' not in bpy.data.objects:
    bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False)
empty = bpy.data.objects['Empty']
for child in empty.children:
    child.select = True
    bpy.ops.object.delete()
print('old objects deleted')

bpy.context.scene.frame_start,bpy.context.scene.frame_end = settings['start'],settings['end']
bpy.context.scene.frame_set(bpy.context.scene.frame_start)
empty.rotation_euler = (0.0,0.0,0.0)
empty.keyframe_insert(data_path="rotation_euler", index=-1)
bpy.context.scene.frame_set(bpy.context.scene.frame_end+1)
empty.rotation_euler = (6.28318530718 * settings['rotation']['x'],6.28318530718 * settings['rotation']['y'],6.28318530718 * settings['rotation']['z'])
empty.keyframe_insert(data_path="rotation_euler", index=-1)
for fc in empty.animation_data.action.fcurves:
    fc.extrapolation = 'LINEAR'
    
bpy.context.scene.render.filepath = path+"/OutputOpenGL/"
bpy.context.scene.render.resolution_x,bpy.context.scene.render.resolution_y = settings['resolution']['x'],settings['resolution']['y']
bpy.context.scene.render.resolution_percentage = 100

doubleSeparation = 0.1

for atom in atomProps.keys():
    mat = (bpy.data.materials.get(atom) or bpy.data.materials.new(atom))
    mat.diffuse_color=(atomProps[atom]['color'][0]/255.0,atomProps[atom]['color'][1]/255.0,atomProps[atom]['color'][2]/255.0)
    atomProps[atom]['material'] = mat
bMat = (bpy.data.materials.get('bond') or bpy.data.materials.new('bond'))
bMat.diffuse_color = (0.5,0.5,0.5)
data = open(path+settings['file'],'r').read()
lData = list(data.split("\n"))

def createAtom(aType,location):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4t,size=atomProps[aType]['size']/100.0,location=location)
    ob = bpy.context.object
    for polygon in ob.data.polygons:
        polygon.use_smooth = True
    if len(aType): ob.active_material = atomProps[aType]['material']
    ob.parent = empty
    ob.name = str(currAtom)
    
def createBond(type,atom1,atom2):
    if type == '1':
        avg = (atom1.location+atom2.location)/2
        ob = cylinder_between(atom1.location[0],atom1.location[1],atom1.location[2],atom2.location[0],atom2.location[1],atom2.location[2],0.05)
        ob.parent = empty
        ob.active_material = bMat
        ob.select = False
    elif type == '2':
        ob1 = cylinder_between(atom1.location[0],atom1.location[1],atom1.location[2]+doubleSeparation,atom2.location[0],atom2.location[1],atom2.location[2]+doubleSeparation,0.05)
        ob1.parent = empty
        ob1.active_material = bMat
        ob2 = cylinder_between(atom1.location[0],atom1.location[1],atom1.location[2]-doubleSeparation,atom2.location[0],atom2.location[1],atom2.location[2]-doubleSeparation,0.05)
        ob2.parent = empty
        ob2.active_material = bMat
        ob1.select = ob2.select = False
    elif type == '3':
        ob1 = cylinder_between(atom1.location[0],atom1.location[1],atom1.location[2],atom2.location[0],atom2.location[1],atom2.location[2],0.05)
        ob1.parent = empty
        ob1.active_material = bMat
        ob2 = cylinder_between(atom1.location[0],atom1.location[1],atom1.location[2]+doubleSeparation,atom2.location[0],atom2.location[1],atom2.location[2]+doubleSeparation,0.05)
        ob2.parent = empty
        ob2.active_material = bMat
        ob3 = cylinder_between(atom1.location[0],atom1.location[1],atom1.location[2]-doubleSeparation,atom2.location[0],atom2.location[1],atom2.location[2]-doubleSeparation,0.05)
        ob3.parent = empty
        ob3.active_material = bMat
        ob1.select = ob2.select = ob3.select = False
        
print('creation start')
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
oldPercent = 200
print('0---------------------25----------------------50----------------------75---------------------100')
for index,line in enumerate(lData[4:] if V3000 else lData[3:]):
    if V3000:
        if line == 'M  V30 END BOND':
            break
        split = line.split()
        if '.' in line:
            t1 = time.time()
            if oldPercent == 200:
                oldPercent = 0
            createAtom(split[3],tuple(map(float,split[4:7])))
            currAtom += 1
            print("atom",time.time()-t1)
        elif not '.' in line and (not 'END' in line) and (not 'BEGIN' in line) and (not 'COUNTS' in line):
            t1 = time.time()
            if oldPercent == 200:
                oldPercent = 0
            atom1,atom2,type = split[4],split[5],split[3]
            atom1,atom2 = bpy.data.objects[atom1],bpy.data.objects[atom2]
            createBond(type,atom1,atom2)
            print("bond",time.time()-t1)
    elif not pdb:
        if '.' in line:
            if oldPercent == 200:
                oldPercent = 0
            createAtom(line[31:35].strip(),(float(line[3:10]),float(line[13:20]),float(line[23:30])))
            currAtom += 1
        elif not '.' in line:
            if oldPercent == 200:
                oldPercent = 0
            atom1,atom2,type = line[0:3],line[3:6],line[8].strip().lstrip()
            atom1,atom2 = atom1.lstrip().strip(),atom2.lstrip().strip()
            atom1,atom2 = bpy.data.objects[atom1],bpy.data.objects[atom2]
            createBond(type,atom1,atom2)
    elif pdb:
        if (line.startswith("ATOM") or line.startswith("HETATM")) and (line[77:79].strip() != "aeroiugb"):
            if oldPercent == 200:
                oldPercent = 0
            createAtom(line[76:78].strip().capitalize(),(float(line[31:39]),float(line[39:47]),float(line[47:54])))
    newPercent = (index*100)/mLine
    if newPercent > oldPercent + 1:
        #print(newPercent,oldPercent,index)
        #print('.', end='', flush = True)
        oldPercent = newPercent
print('\ncreation done')
average = mathutils.Vector((0,0,0))
for child in empty.children: average += (child.location)/ len(empty.children)
for child in empty.children: child.location -= average
maxV = max(map(lambda x: x.location,empty.children))
maxL = max(map(lambda x: x.location.length,empty.children))
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        area.spaces[0].show_only_render = True
        area.spaces[0].show_world = True
        area.spaces[0].viewport_shade = "TEXTURED"
bpy.context.scene.world.horizon_color = (0, 0, 0)
for material in bpy.data.materials:
    if not material.users or '.' in material.name:
        bpy.data.materials.remove(material,do_unlink=True)
if not bpy.data.objects.get("Camera"):
    bpy.ops.object.camera_add()
cam = bpy.data.objects["Camera"]
cam.rotation_euler = (1.5708,0,4.71239)
cam.location = (-3*maxL,0,0)
bpy.context.scene.objects.active = cam
bpy.context.object.data.type = 'ORTHO'
bpy.context.object.data.ortho_scale = 2*maxL+1#45.6
bpy.context.scene.camera = cam
cam.select = False

#bpy.ops.render.opengl(animation=False, sequencer=False, write_still=True, view_context=True)
#bpy.ops.render.opengl(animation=True, sequencer=False, write_still=True, view_context=True)
#bpy.ops.wm.quit_blender()
