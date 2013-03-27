import bpy
import time

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


def clip(start, end):
    cam = bpy.data.objects['Camera']    
    
    #print(cam.data.clip_start)
    
    cam.data.clip_start = start
    cam.data.clip_end = end
    

moveAxial()

shouldRender = 0
offset = 30
v_start = 150
# for sagittal 
#for i in range(0, 134):
if True:
    i = 38
    print(i)
    clip(v_start + i, v_start + i +offset)
    
    if shouldRender:
        bpy.data.scenes['Scene'].render.filepath = '/Users/stonerri/MNA/render/sag-%03d.png' % i  
        bpy.ops.render.render( write_still=True ) 
        
    else:
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

#mencoder mf://*.png -mf w=800:h=600:fps=25:type=png -ovc lavc -lavcopts vcodec=mpeg4:mbd=2:trell -oac copy -o output.avi
    
    
#clip(0.00001, 500)