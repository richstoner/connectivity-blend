print("Hello")

from mathutils import Vector
import bpy
import glob
import csv
import math
import struct
import os
import urllib.request

w=1
def clearAllCurves():
         
    # gather list of items of interest.
    candidate_list = [item.name for item in bpy.data.objects if item.type == "CURVE"]
     
    # select them only.
    for object_name in candidate_list:
      bpy.data.objects[object_name].select = True
     
    # remove all selected.
    bpy.ops.object.delete()
     
    # remove the meshes, they have no users anymore.
    for item in bpy.data.meshes:
        bpy.data.meshes.remove(item)
    
    print('Cleared curves')
    
def clearAllMeshes():
        # gather list of items of interest.
    candidate_list = [item.name for item in bpy.data.objects if item.type == "MESH"]
     
    # select them only.
    for object_name in candidate_list:
      bpy.data.objects[object_name].select = True
     
    # remove all selected.
    bpy.ops.object.delete()
     
    # remove the meshes, they have no users anymore.
    for item in bpy.data.meshes:
        bpy.data.meshes.remove(item)
    
    print('Cleared meshes')
    
def makeMaterial(name, diffuse, specular, alpha):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = diffuse
    mat.diffuse_shader = 'LAMBERT' 
    mat.diffuse_intensity = 1.0 
    mat.specular_color = specular
    mat.specular_shader = 'COOKTORR'
    mat.specular_intensity = 0.5
    mat.alpha = alpha
    mat.ambient = 1
    return mat

def setMaterial(ob, mat):
    me = ob.data
    me.materials.append(mat)

def printSummary():
    
    for object in bpy.data.objects:
#        print(object.type)
        if object.type == 'CAMERA':
            print('Camera location: ' + str(object.location))
        if object.type == 'LAMP':
            print('Sun location: ' + str(object.location))

def setSun():
    
    rx = 0
    ry = 180
    rz = 180
    
    pi = 3.14159265
    sun = bpy.data.objects['Sun']
    sun.location = [math.floor(133/2), math.floor(81/2), 0]
    sun.rotation_mode = 'XYZ'
    sun.rotation_euler[0] = rx*(pi/180.0)
    sun.rotation_euler[1] = ry*(pi/180.0)
    sun.rotation_euler[2] = rz*(pi/180.0)
    sun.data.distance = 500
    sun.data.falloff_type = 'CONSTANT'
        


def moveSag():
    cam = bpy.data.objects['Camera']
    cam.location = [math.floor(133/2), math.floor(81/2), -150]
    
    rx = 0
    ry = 180
    rz = 180
    
    pi = 3.14159265
    
    cam.rotation_mode = 'XYZ'
    cam.rotation_euler[0] = rx*(pi/180.0)
    cam.rotation_euler[1] = ry*(pi/180.0)
    cam.rotation_euler[2] = rz*(pi/180.0)
    #cam.data.type = 'PERSP'
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = 250


def moveCoronal():
    cam = bpy.data.objects['Camera']
    cam.location = [-150, math.floor(81/2), math.floor(115/2)]
    
    rx = 0
    ry = 90
    rz = 180
    
    pi = 3.14159265
    
    cam.rotation_mode = 'XYZ'
    cam.rotation_euler[0] = rx*(pi/180.0)
    cam.rotation_euler[1] = ry*(pi/180.0)
    cam.rotation_euler[2] = rz*(pi/180.0)
    #cam.data.type = 'PERSP'
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = 250


def moveAxial():
    cam = bpy.data.objects['Camera']
    cam.location = [math.floor(133/2), -115, math.floor(115/2)]
    
    rx = 90
    ry = 0
    rz = 0
    
    pi = 3.14159265
    
    cam.rotation_mode = 'XYZ'
    cam.rotation_euler[0] = rx*(pi/180.0)
    cam.rotation_euler[1] = ry*(pi/180.0)
    cam.rotation_euler[2] = rz*(pi/180.0)
    #cam.data.type = 'PERSP'
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = 250



def addRootGroup(list_of_roots):

    group_indexes = [11]

    print("there are %d roots" % len(list_of_roots))

    #for rootgroup in list_of_roots[group_indexes]:
    for group_in in group_indexes:
        
        if group_in > len(list_of_roots):
            break
        
        rootgroup = list_of_roots[group_in].split('\\')[1]
        
        urlstring = 'http://localhost:8888/series/%s' % rootgroup 

        url = urllib.request.urlopen(urlstring)
        mybytes = url.read()
        
        colorstring = mybytes.decode("utf8")
        url.close()
   
        print(colorstring)
        
        csplit = colorstring.split(',')
        r = float(csplit[0])
        g = float(csplit[1])
        b = float(csplit[2])
        
        mtlname = rootgroup + '.mtl'
        
        red = makeMaterial(mtlname, (r,g,b), (1,1,1), 1)
            
        i = 0
        print(rootgroup)
        
        group_list = glob.glob(binary_location + '/' + rootgroup + '*')
        
        for mes in group_list:    
            
            if i % 100 == 0: print(i)
            vec_list = []    
            
            import os
            f = open(mes,'rb')
            filesize =  os.fstat(f.fileno()).st_size
            
            for k in range(0,int(filesize/12)):    
                vals = struct.unpack('fff', f.read(12))
                vec = Vector(vals)
                vec_list.append(vec)
            
                
            def MakePolyLine(objname, curvename, cList):  
                curvedata = bpy.data.curves.new(name=curvename, type='CURVE')  
                curvedata.dimensions = '3D'  
                curvedata.bevel_depth = 0.025
                   
                objectdata = bpy.data.objects.new(objname, curvedata)  
                objectdata.location = (0,0,0) #object origin  
                bpy.context.scene.objects.link(objectdata)  
              
                polyline = curvedata.splines.new('POLY')  
                polyline.points.add(len(cList)-1)  
                for num in range(len(cList)):  
                    x, y, z = cList[num]  
                    polyline.points[num].co = (x, y, z, w)
                    
                                    
                    
            MakePolyLine("%s-%04d" % (rootgroup,i), "%s-%04d" % (rootgroup,i), vec_list)
            ob = bpy.data.objects.get("%s-%04d" % (rootgroup,i))
                  
            ob.select = True
       
            i+=1


        # combine group
        

#        bpy.context.scene.objects.active = bpy.context.selected_objects[0]
        bpy.context.scene.objects.active = bpy.data.objects[("%s-0000" % (rootgroup))]
        bpy.ops.object.join()
        bpy.data.curves[("%s-0000" % (rootgroup))].bevel_depth = 0.025
        setMaterial(bpy.context.active_object, red)
        
        
        bpy.ops.object.select_all( action='DESELECT' )

        
add_cube = bpy.ops.mesh.primitive_cube_add

        

bpy.ops.object.select_all( action='DESELECT' )

binary_location = '/Users/Administrator/connectivity-blend/bindata'
raw_location = '/Users/Administrator/connectivity-blend/rawdata'

list_of_binmesh = glob.glob(binary_location + '/*')
list_of_roots = []

for mes in list_of_binmesh:
    ms = mes.split('/')[-1].split('.')[0].split('-')[0]

    if ms not in list_of_roots:
        list_of_roots.append(ms)    
    
print(list_of_roots[0])
      
clearAllMeshes()
clearAllCurves()
addRootGroup(list_of_roots)

layerList = [False]*20
layerList[0] = True

import math
shouldAddCube = 0

if shouldAddCube:
    add_cube(location=(0, 0, 0,), layers=layerList)
    ob = bpy.data.objects['Cube']
    print(ob.location)

    space = [133, 81, 115]

    ob.scale = [133/2, 81/2, 115/2]
    
    ob.location = [math.floor(133/2), math.floor(81/2), math.floor(115/2)]

printSummary()
#moveCoronal()
#moveSag()
moveAxial()
setSun()

