import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import ctypes
import os

# toggle mode
left = 0
right = 0
scroll = 0
checkV = 0
checkZ = 0
checkH = 0
checkS = 0
checksp = 0
checkBox = 0

objOn = 0

# global variables
# init : save data of one movement before to get delta values
initx = 0
inity = 0
# delta : differences
dx = 0
dy = 0
# to accumulate results
totalx = 0
totaly = 0
zoom = 5
azimuth = 0
elevation = 0

# initial values
l = -1
r = 1
b = -1
t = 1
n = 1
f = 50
angle = 45
aspect = 1

# vertex and index array, vertex normal and vertex normal index array
varr = np.array([])
iarr = np.array([])
vnarr = np.array([])
vniarr = np.array([])
# face array, saves normal and vertex sequencially
farr = np.array([])
# face normal array, normal array(used in farr), new normal array(for Gouraud Shading)
fnarr = np.array([])
narr = np.array([])
nnarr = np.array([])

# face count / tri count / quad count / polygon count / vertex count / vertex normal count
fcount = 0
tcount = 0
qcount = 0
pcount = 0
vcount = 0
vncount = 0

# for heirachical model
eartharr = np.array([])
cuparr = np.array([])
humanarr = np.array([])
fnarr = np.array([])
snarr = np.array([])
hasinit = 0

fread = 1

# bvh rendering
offsets = np.array([])
chanTypes = [] 
chanData = np.array([])
chancnt = np.array([])
poplist = np.array([])
tpose = 1
framecnt = 0
t = 0

initData = np.array([])

def render():
    global dx, dy, totalx, totaly, M
    global azimuth, elevation
    global l,r,b,t,n,f
    global checkV, checkZ, checksp
    global farr, ironarr, eartharr, cuparr, humanarr
    global offsets, chanTypes, chanData, chancnt, poplist, tpose, initData
    global framecnt, t

    # enable depth test (we'll see details later)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)

    if checkZ == 0:
        glPolygonMode( GL_FRONT_AND_BACK, GL_FILL )
    if checkZ == 1:
        glPolygonMode( GL_FRONT_AND_BACK, GL_LINE )
    
    glLoadIdentity()

    # toggle perspective projection and orthogonal perspective projection
    if checkV == 0:
        gluPerspective(angle, aspect, n, f)
    if checkV == 1:
        glOrtho(l,r, b,t, n,f)

    # set camera + orbit + zoom
    glTranslatef(0, 0, -np.linalg.norm(np.array([-2,-2,-2]) * zoom))
    glRotatef(35.264 + elevation, 1, 0, 0)
    glRotatef(-45 + azimuth, 0, 1, 0)

    # get current transformation matrix
    M = glGetDoublev(GL_MODELVIEW_MATRIX)

    # pan
    glTranslate(M[0][0] * totalx + M[0][1] * totaly, M[1][0] * totalx + M[1][1] * totaly, M[2][0] * totalx + M[2][1] * totaly)
	
    drawFrame()

    glColor3ub(255, 255, 255)
    drawGrid()

    i = 0
    j = 0
    l = 0
    chanidx = 0

    glScalef(0.01,0.01,0.01)

    if tpose == 1:
        for i in range(len(offsets)):
            drawLine(offsets[i])
            glPushMatrix()
            glTranslatef(offsets[i][0],offsets[i][1],offsets[i][2])

            # if it is joint, not end site
            if poplist[i] == 0:
                for k in range(j, j + chancnt[chanidx]):
                    if chanTypes[k].upper() == 'XPOSITION':
                        glTranslatef(chanData[0][k],0,0)
                    elif chanTypes[k].upper() == 'YPOSITION':
                        glTranslatef(0,chanData[0][k],0)
                    elif chanTypes[k].upper() == 'ZPOSITION':
                        glTranslatef(0,0,chanData[0][k])
                    elif chanTypes[k].upper() == 'XROTATION':
                        glRotatef(0, 1,0,0)
                    elif chanTypes[k].upper() == 'YROTATION':
                        glRotatef(0, 0,1,0)
                    elif chanTypes[k].upper() == 'ZROTATION':
                        glRotatef(0, 0,0,1)
                j += chancnt[chanidx]
                chanidx += 1

                if checkBox == 1:
                    glPushMatrix()
                    v = np.array([0,0,1])
                    if i+1 < len(offsets):
                        l = np.sqrt(np.dot(offsets[i+1], offsets[i+1]))
                        if not l == 0:
                            norm = np.cross(v,offsets[i+1])
                            l2 = np.sqrt(np.dot(norm, norm))
                            theta = np.degrees(np.arcsin(l2/l))
                            glRotatef(theta, norm[0], norm[1], norm[2])
                    glTranslatef(0,0,l/2)
                    glScalef(5,5,l/2)

                    drawBox()
                    glPopMatrix()

            for l in range(poplist[i]):
                glPopMatrix()

    else:
        if checksp == 1:
            t += 1
        if t == framecnt:
            t = 0
        for i in range(len(offsets)):
            drawLine(offsets[i])
            glPushMatrix()
            glTranslatef(offsets[i][0],offsets[i][1],offsets[i][2])
            # if it is joint, not end site
            if poplist[i] == 0:
                for k in range(j, j + chancnt[chanidx]):
                    if chanTypes[k].upper() == 'XPOSITION':
                        glTranslatef(chanData[t][k],0,0)
                    elif chanTypes[k].upper() == 'YPOSITION':
                        glTranslatef(0,chanData[t][k],0)
                    elif chanTypes[k].upper() == 'ZPOSITION':
                        glTranslatef(0,0,chanData[t][k])
                    elif chanTypes[k].upper() == 'XROTATION':
                        glRotatef(chanData[t][k], 1,0,0)
                    elif chanTypes[k].upper() == 'YROTATION':
                        glRotatef(chanData[t][k], 0,1,0)
                    elif chanTypes[k].upper() == 'ZROTATION':
                        glRotatef(chanData[t][k], 0,0,1)
                j += chancnt[chanidx]
                chanidx += 1

                if checkBox == 1:
                    glPushMatrix()
                    v = np.array([0,0,1])
                    if i+1 < len(offsets):
                        l = np.sqrt(np.dot(offsets[i+1], offsets[i+1]))
                        if not l == 0:
                            norm = np.cross(v,offsets[i+1])
                            l2 = np.sqrt(np.dot(norm, norm))
                            theta = np.degrees(np.arcsin(l2/l))
                            glRotatef(theta, norm[0], norm[1], norm[2])
                    glTranslatef(0,0,l/2)
                    glScalef(5,5,l/2)

                    drawBox()
                    glPopMatrix()
                
            for l in range(poplist[i]):
                glPopMatrix()



def drawUnitCube():
    glBegin(GL_QUADS)
    glVertex3f( 0.5, 0.5,-0.5)
    glVertex3f(-0.5, 0.5,-0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f( 0.5, 0.5, 0.5)

    glVertex3f( 0.5,-0.5, 0.5)
    glVertex3f(-0.5,-0.5, 0.5)
    glVertex3f(-0.5,-0.5,-0.5)
    glVertex3f( 0.5,-0.5,-0.5)

    glVertex3f( 0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(-0.5,-0.5, 0.5)
    glVertex3f( 0.5,-0.5, 0.5)

    glVertex3f( 0.5,-0.5,-0.5)
    glVertex3f(-0.5,-0.5,-0.5)
    glVertex3f(-0.5, 0.5,-0.5)
    glVertex3f( 0.5, 0.5,-0.5)

    glVertex3f( 0.5,-0.5,-0.5)
    glVertex3f(-0.5,-0.5,-0.5)
    glVertex3f(-0.5, 0.5,-0.5)
    glVertex3f( 0.5, 0.5,-0.5)

    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5,-0.5)
    glVertex3f(-0.5,-0.5,-0.5)
    glVertex3f(-0.5,-0.5, 0.5)

    glVertex3f( 0.5, 0.5,-0.5)
    glVertex3f( 0.5, 0.5, 0.5)
    glVertex3f( 0.5,-0.5, 0.5)
    glVertex3f( 0.5,-0.5,-0.5)
    glEnd()

def drawBox():
    varr = np.array([
            ( -0.5773502691896258 , 0.5773502691896258 ,  0.5773502691896258 ),
            ( -1 ,  1 ,  1 ), # v0
            ( 0.8164965809277261 , 0.4082482904638631 ,  0.4082482904638631 ),
            (  1 ,  1 ,  1 ), # v1
            ( 0.4082482904638631 , -0.4082482904638631 ,  0.8164965809277261 ),
            (  1 , -1 ,  1 ), # v2
            ( -0.4082482904638631 , -0.8164965809277261 ,  0.4082482904638631 ),
            ( -1 , -1 ,  1 ), # v3
            ( -0.4082482904638631 , 0.4082482904638631 , -0.8164965809277261 ),
            ( -1 ,  1 , -1 ), # v4
            ( 0.4082482904638631 , 0.8164965809277261 , -0.4082482904638631 ),
            (  1 ,  1 , -1 ), # v5
            ( 0.5773502691896258 , -0.5773502691896258 , -0.5773502691896258 ),
            (  1 , -1 , -1 ), # v6
            ( -0.8164965809277261 , -0.4082482904638631 , -0.4082482904638631 ),
            ( -1 , -1 , -1 ), # v7
            ], 'float32')
    iarr = np.array([
            (0,2,1),
            (0,3,2),
            (4,5,6),
            (4,6,7),
            (0,1,5),
            (0,5,4),
            (3,6,2),
            (3,7,6),
            (1,2,6),
            (1,6,5),
            (0,7,3),
            (0,4,7),
            ])
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glNormalPointer(GL_FLOAT, 6*varr.itemsize, varr)
    glVertexPointer(3, GL_FLOAT, 6*varr.itemsize, ctypes.c_void_p(varr.ctypes.data + 3*varr.itemsize))
    glDrawElements(GL_TRIANGLES, iarr.size, GL_UNSIGNED_INT, iarr)


def drawCubeArray():
    for i in range(5):
        for j in range(5):
            for k in range(5):
                glPushMatrix()
                glTranslatef(i, j, -k-1)
                glScalef(.5,.5,.5)
                drawUnitCube()
                glPopMatrix()

# draw grid
def drawGrid():
    glBegin(GL_LINES)
    for i in range(-50, 51):
        glVertex3fv(np.array([-50.,0.,i]))
        glVertex3fv(np.array([ 50.,0.,i]))
    for i in range(-50, 51):
        glVertex3fv(np.array([i,0.,-50.]))
        glVertex3fv(np.array([i,0., 50.]))
    glEnd()

def drawLine(offset):
    glBegin(GL_LINES)
    glVertex3fv(np.array([0,0,0]))
    glVertex3fv(offset)
    glEnd()

def drawFrame():
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex3fv(np.array([0.,0.,0.]))
    glVertex3fv(np.array([1.,0.,0.]))
    glColor3ub(0, 255, 0)
    glVertex3fv(np.array([0.,0.,0.]))
    glVertex3fv(np.array([0.,1.,0.]))
    glColor3ub(0, 0, 255)
    glVertex3fv(np.array([0.,0.,0]))
    glVertex3fv(np.array([0.,0.,1.]))
    glEnd()

def drawObject():
    global farr

    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)

    glNormalPointer(GL_FLOAT, 6*farr.itemsize, farr)
    glVertexPointer(3, GL_FLOAT, 6*farr.itemsize, ctypes.c_void_p(farr.ctypes.data + 3*farr.itemsize))

    glDrawArrays(GL_TRIANGLES, 0, int(farr.size/6))

def key_callback(window, key, scancode, action, mods):
    global checkV, checkZ, checkH, checkS, objOn
    global hasinit, farr, narr, vnarr, nnarr
    global checksp, tpose, checkBox

    if key == glfw.KEY_V:
        if action == glfw.PRESS:
            # change perspective when V is pressed
            checkV = 1 - checkV
    elif key == glfw.KEY_Z:
        if action == glfw.PRESS:
            checkZ = 1 - checkZ
    elif key == glfw.KEY_SPACE:
        if action == glfw.PRESS:
            checksp = 1 - checksp
            tpose = 0
    elif key == glfw.KEY_1:
        if action == glfw.PRESS:
            checkBox = 0
    elif key == glfw.KEY_2:
        if action == glfw.PRESS:
            checkBox = 1

def cursor_callback(window, xpos, ypos):
    global left, right, initx, inity, dx, dy, totalx, totaly, azimuth, elevation
    # when mouse left button is clicked
    if left == 1:
        # set initial values for initx and inity
        if initx == 0 and inity == 0:
            initx = xpos
            inity = ypos
        # get the difference of mouse coordinate after moving
        dx = xpos - initx
        dy = ypos - inity
        # save new initx and inity to use in next cursor_callback
        initx = xpos
        inity = ypos
        # make the world turn 180 degrees when moving end to end of the window
        azimuth += (dx / 640 * 180)
        elevation += (dy / 640 * 180)

    # when mouse right button is clicked
    if right == 1:
        # set initial values
        if initx == 0 and inity == 0:
            initx = xpos
            inity = ypos
        # get difference
        dx = xpos - initx
        dy = ypos - inity
        # divide differences by 100, otherwise panning occurs in too big range
        dx /= 100
        dy /= 100
        # save new init values
        initx = xpos
        inity = ypos
        # accumulate all movements
        totalx += dx
        totaly -= dy
        

def button_callback(window, button, action, mod):
    global left, right, initx, inity
    if button == glfw.MOUSE_BUTTON_LEFT:
        if action == glfw.PRESS:
            # set init values to current cursor position
            initx = glfw.get_cursor_pos(window)[0]
            inity = glfw.get_cursor_pos(window)[1]
            # toggle left on
            left = 1
        elif action == glfw.RELEASE:
            # toggle left off
            left = 0
    if button == glfw.MOUSE_BUTTON_RIGHT:
        if action == glfw.PRESS:
            # set init values to current cursor position
            initx = glfw.get_cursor_pos(window)[0]
            inity = glfw.get_cursor_pos(window)[1]
            # toggle right on 
            right = 1
        elif action == glfw.RELEASE:
            # toggle right off
            right = 0
    
def scroll_callback(window, xoffset, yoffset):
    global zoom
    # accumulate zoom results after dividing by 100, otherwise it moves so fast
    zoom -= yoffset / 100
    # limit value of zoom between 0 and 100
    zoom = np.clip(zoom, 0, 100)

def drop_callback(window, paths):
    for i in range(len(paths)):
        handle_dropped_file(paths[i])

def handle_dropped_file(s):
    global offsets, chanTypes, chanData, chancnt, poplist
    global framecnt, t

    path = ''

    totalChannel = 0
    jointNames = [] 
    framecnt = 0
    fps = 0
    offsets = np.array([])
    chanTypes = [] 
    chanData = np.array([])
    chancnt = np.array([])
    poplist = np.array([])

    pushcnt = 0
    popcnt = 0
    endcnt = 0
    t = 0    

    for c in s:
        path += c

    f = open(path, 'r')

    path = path.split('/')
    name = path[len(path) - 1]
    print(name)

    while True:
        line = f.readline()
        if not line: break

        # trim on both side
        line = line.strip()

        checkline = line.split()
        if checkline[0] == 'HIERARCHY':
            pass
        
        elif checkline[0] == 'ROOT' or checkline[0] == 'JOINT':
            jointNames.append(checkline[1])
            
        elif checkline[0] == 'CHANNELS':
            n = int(checkline[1])
            totalChannel += n
            chancnt = np.append(chancnt, int(n))
            for i in range(2, len(checkline)):
                chanTypes = np.append(chanTypes, checkline[i])

        elif checkline[0] == 'OFFSET':
            poplist = np.append(poplist, popcnt)
            popcnt = 0
            for i in range(1, len(checkline)):
                offsets = np.append(offsets, float(checkline[i]))

        elif checkline[0] == 'End':
            jointNames.append(checkline[1])            
            endcnt += 1

        elif checkline[0] == 'MOTION':
            poplist = np.append(poplist, popcnt)
            
        elif checkline[0] == 'Frames:':
            framecnt = int(checkline[1])

        elif checkline[0] == 'Frame':
            fps = 1 / float(checkline[2])
        
        elif checkline[0] == '{':
            pushcnt += 1
        
        elif checkline[0] == '}':
            popcnt += 1
        
        else:
            checkline = line.split()
            for i in checkline:
                chanData = np.append(chanData, float(i))

    offsets = np.reshape(offsets, (len(jointNames), 3))
    chanData = np.reshape(chanData, (framecnt, chanTypes.size))
    chancnt = chancnt.astype(int)
    poplist = poplist.astype(int)
    poplist = np.delete(poplist, 0)

    print('Number of frames: ' + str(framecnt))
    print('Frames per second: ' + str(int(fps)))
    print('Number of joints: ' + str((len(jointNames) - endcnt)))

    for i in range(len(jointNames)):
        if not jointNames[i] == 'Site':
            print(jointNames[i])

def main():
    global fread
    # Initialize the library
    if not glfw.init():
        return
    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(640, 640, "Class Assignment3", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.set_key_callback(window, key_callback)
    glfw.set_cursor_pos_callback(window, cursor_callback)
    glfw.set_mouse_button_callback(window, button_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    glfw.set_drop_callback(window, drop_callback)

    # Make the window's context current
    glfw.make_context_current(window)

    # Loop until the user closes the window
    while not glfw.window_should_close(window):
        # Poll for and process events
        glfw.poll_events()
        glfw.swap_interval(1)
        # Render here, e.g. using pyOpenGL
        if fread == 1:
            render()
        # Swap front and back buffers
        glfw.swap_buffers(window)

    glfw.terminate()
if __name__ == "__main__":
    main()
