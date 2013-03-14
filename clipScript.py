import bpy
import time

def clip(start, end):
    cam = bpy.data.objects['Camera']    
    
    #print(cam.data.clip_start)
    
    cam.data.clip_start = start
    cam.data.clip_end = end
    
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
    
    
clip(0.00001, 500)