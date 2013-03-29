import bpy
import time
import math

def clip(start, end):
    cam = bpy.data.objects['Camera']    
    cam.data.clip_start = start
    cam.data.clip_end = end
    


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
    cam.data.ortho_scale = 150


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
    cam.data.ortho_scale = 150


def moveAxial():
    cam = bpy.data.objects['Camera']
    cam.location = [math.floor(133/2), -150, math.floor(115/2)]
    
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
    cam.data.ortho_scale = 150



def renderV1():

    moveSag()

    render_x_res = 1280*4
    render_y_res = 720*4
    bpy.data.scenes['Scene'].render.resolution_x = render_x_res
    bpy.data.scenes['Scene'].render.resolution_y = render_y_res

    import os

    # the connectivity coordinate space is :
    # 133 x 81 x 115 
    # AP x ML X DV (SI)
    # Coronal , Sagittal , Axial
    
    shouldRender = 1
    offset = 10    
    spacing = 5
    v_start = 150 - 10 

    # for sagittal 
    for i in range(10, 20):
        #i = 0
        print(i)
        clip(v_start + (i*spacing), v_start + (i*spacing) +offset)
        
        if shouldRender:

            bpy.data.scenes['Scene'].render.filepath = os.path.abspath(os.path.curdir) + '/sag-auto-%03d-%03d.png' % (i  , i + offset )
            bpy.ops.render.render( write_still=True ) 
        
        else:
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)


renderV1()

#mencoder mf://*.png -mf w=800:h=600:fps=25:type=png -ovc lavc -lavcopts vcodec=mpeg4:mbd=2:trell -oac copy -o output.avi
    
    
#clip(0.00001, 500)

