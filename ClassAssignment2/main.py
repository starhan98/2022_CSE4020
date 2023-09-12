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

def render():
    global dx, dy, totalx, totaly, M
    global azimuth, elevation
    global l,r,b,t,n,f
    global checkV, checkZ
    global farr, ironarr, eartharr, cuparr, humanarr

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
    # drawUnitCube()
    # drawCubeArray()
    drawGrid()

    # Lighting

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_LIGHT2)
    glEnable(GL_LIGHT3)
    glEnable(GL_NORMALIZE)

    # light position
    glPushMatrix()
    lightPos0 = (3.,4.,5.,1.)
    glLightfv(GL_LIGHT0, GL_POSITION, lightPos0)
    glPopMatrix()

    glPushMatrix()
    lightPos1 = (-3.,4.,5.,1.)
    glLightfv(GL_LIGHT1, GL_POSITION, lightPos1)
    glPopMatrix()

    glPushMatrix()
    lightPos2 = (-3.,4.,-5.,1.)
    glLightfv(GL_LIGHT2, GL_POSITION, lightPos2)
    glPopMatrix()

    glPushMatrix()
    lightPos3 = (3.,4.,-5.,1.)
    glLightfv(GL_LIGHT3, GL_POSITION, lightPos3)
    glPopMatrix()

    lightColor = (1., 1., 1., 1.)
    ambientColor = (.1, .1, .1, 1.)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightColor)
    glLightfv(GL_LIGHT0, GL_SPECULAR, lightColor)
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambientColor)

    lightColor1 = (1., 1., 0., 1.)
    ambientColor1 = (.1, .1, .1, 1.)
    glLightfv(GL_LIGHT1, GL_DIFFUSE, lightColor1)
    glLightfv(GL_LIGHT1, GL_SPECULAR, lightColor1)
    glLightfv(GL_LIGHT1, GL_AMBIENT, ambientColor1)    
    
    lightColor2 = (1., 0., 1., 1.)
    ambientColor2 = (.1, .1, .1, 1.)
    glLightfv(GL_LIGHT2, GL_DIFFUSE, lightColor2)
    glLightfv(GL_LIGHT2, GL_SPECULAR, lightColor2)
    glLightfv(GL_LIGHT2, GL_AMBIENT, ambientColor2)    
    
    lightColor3 = (0., 1., 1., 1.)
    ambientColor3 = (.1, .1, .1, 1.)
    glLightfv(GL_LIGHT3, GL_DIFFUSE, lightColor3)
    glLightfv(GL_LIGHT3, GL_SPECULAR, lightColor3)
    glLightfv(GL_LIGHT3, GL_AMBIENT, ambientColor3)
    
    objectColor = (1.,1.,1.,1.)
    specularColor = (1.,1.,1.,1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularColor)

    t = glfw.get_time()

    glPushMatrix()
    # glColor3ub(0, 0, 255)
    if checkH == 0:
        drawObject()
    if checkH == 1:
        farr = eartharr
        glRotatef(0.5*t*(180/np.pi), 0, 1, 0)
        
        glPushMatrix()
        glScalef(2,2,2)
        drawObject()
        glPopMatrix()

        glPushMatrix()
        farr = cuparr
        glTranslatef(8, 0, 0)
        glRotatef(t*(180/np.pi), 0, 1, 0)
        
        glPushMatrix()
        glScalef(.2, .2, .2)
        drawObject()
        glPopMatrix()

        glPushMatrix()
        farr = humanarr
        glTranslatef(1, np.sin(t) - 1, 1)

        glPushMatrix()
        drawObject()
        glPopMatrix()

        glPopMatrix()

        glPushMatrix()
        farr = humanarr
        glTranslatef(-1, np.sin(t) - 1, 1)

        glPushMatrix()
        drawObject()
        glPopMatrix()

        glPopMatrix()

        glPopMatrix()

        glPushMatrix()
        farr = cuparr
        glTranslatef(-8, 0, 0)
        glRotatef(-t*(180/np.pi), 0, 1, 0)
        
        glPushMatrix()
        glScalef(.2, .2, .2)
        drawObject()
        glPopMatrix()

        glPushMatrix()
        farr = humanarr
        glTranslatef(1, np.sin(-t) - 1, 1)

        glPushMatrix()
        drawObject()
        glPopMatrix()

        glPopMatrix()

        glPushMatrix()
        farr = humanarr
        glTranslatef(-1, np.sin(-t) - 1, 1)

        glPushMatrix()
        drawObject()
        glPopMatrix()

        glPopMatrix()

        glPopMatrix()

    glPopMatrix()

    glDisable(GL_LIGHTING)


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
    if key == glfw.KEY_V:
        if action == glfw.PRESS:
            # change perspective when V is pressed
            checkV = 1 - checkV
    elif key == glfw.KEY_Z:
        if action == glfw.PRESS:
            checkZ = 1 - checkZ
    elif key == glfw.KEY_H:
        if action == glfw.PRESS:
            checkH = 1 - checkH
            if checkH == 0:
                farr = np.array([])
            if hasinit == 0:
                hasinit = 1
                init_models()
    elif key == glfw.KEY_S:
        if action == glfw.PRESS:
            checkS = 1 - checkS
            # make_nnarr()
            if checkS == 0:
                narr = vnarr
            if checkS == 1:
                narr = nnarr
            if objOn == 1:
                make_farr()
                # print("make_farr called")
            

def init_models():
    global eartharr, cuparr, humanarr, farr, vnarr, nnarr, fnarr, snarr

    path = os.path.join(os.getcwd(), "earth.obj")
    handle_dropped_file(path)
    eartharr = farr
    
    path = os.path.join(os.getcwd(), "cup.obj")
    handle_dropped_file(path)
    cuparr = farr
    
    path = os.path.join(os.getcwd(), "human.obj")
    handle_dropped_file(path)
    humanarr = farr

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

def handle_dropped_file(str):
    global varr, iarr, vnarr, vniarr, narr
    global fcount, tcount, qcount, pcount, vcount, vncount
    global fread, objOn

    fread = 0

    # init
    varr = np.array([])
    iarr = np.array([])
    vnarr = np.array([])
    vniarr = np.array([])
    path = ""
    name = ""
    checkline = ""

    # face count / tri count / quad count / polygon count / vertex count / vertex normal count
    fcount = 0
    tcount = 0
    qcount = 0
    pcount = 0
    vcount = 0
    vncount = 0

    for c in str:
        path += c

    f = open(path, 'r')

    path = path.split('/')
    name = path[len(path) - 1]
    print(name)

    while True:
        line = f.readline()
        if not line: break
        checkline = line.split(' ')
        if checkline[0] == 'v':
            i = 1
            while checkline[i] == '':
                i += 1
            vcount += 1
            vertex = np.array([float(checkline[i]), float(checkline[i+1]), float(checkline[i+2])])
            varr = np.append(varr, vertex)
            
        elif checkline[0] == 'vn':
            i = 1
            while checkline[i] == '':
                i += 1
            vncount += 1
            vnormal = np.array([float(checkline[i]), float(checkline[i+1]), float(checkline[i+2])])
            vnarr = np.append(vnarr, vnormal)
            
        elif checkline[0] == 'f':
            fcount += 1
            for a in checkline:
                if a == '' or a == '\n':
                    checkline.remove(a)
            if(len(checkline) == 4):
                vpi = np.array([]) # vertex position index
                vni = np.array([]) # vertex normal index
                for s in checkline:
                    s = s.split('/')
                    if s[0] != 'f':
                        vpi = np.append(vpi, int(s[0]) - 1)
                        if len(s) > 2:
                            vni = np.append(vni, int(s[2]) - 1)
                iarr = np.append(iarr, vpi)
                vniarr = np.append(vniarr, vni)
                tcount += 1
            elif(len(checkline) == 5):
                m = checkline[1].split('/')
                for i in range(2, len(checkline) - 1):
                    vpi = np.array([]) # vertex position index
                    vni = np.array([]) # vertex normal index
                    vpi = np.append(vpi, int(m[0]) - 1)
                    if len(m) > 2:
                        vni = np.append(vni, int(m[2]) - 1)
                    s = checkline[i].split('/')
                    vpi = np.append(vpi, int(s[0]) - 1)
                    if len(s) > 2:
                        vni = np.append(vni, int(s[2]) - 1)
                    s = checkline[i+1].split('/')
                    vpi = np.append(vpi, int(s[0]) - 1)
                    if len(s) > 2:
                        vni = np.append(vni, int(s[2]) - 1)
                    iarr = np.append(iarr, vpi)
                    vniarr = np.append(vniarr, vni)
                
                qcount += 1
            elif(len(checkline) > 5):
                m = checkline[1].split('/')
                for i in range(2, len(checkline) - 1):
                    vpi = np.array([]) # vertex position index
                    vni = np.array([]) # vertex normal index
                    vpi = np.append(vpi, int(m[0]) - 1)
                    if len(m) > 2:
                        vni = np.append(vni, int(m[2]) - 1)
                    s = checkline[i].split('/')
                    vpi = np.append(vpi, int(s[0]) - 1)
                    if len(s) > 2:
                        vni = np.append(vni, int(s[2]) - 1)
                    s = checkline[i+1].split('/')
                    vpi = np.append(vpi, int(s[0]) - 1)
                    if len(s) > 2:
                        vni = np.append(vni, int(s[2]) - 1)
                    iarr = np.append(iarr, vpi)
                    vniarr = np.append(vniarr, vni)

                pcount += 1
            
    print("number of faces : ", fcount)
    print("number of faces with 3 vertices: ", tcount)
    print("number of faces with 4 vertices: ", qcount)
    print("number of faces with n vertices: ", pcount)
    varr = np.reshape(varr, (vcount, 3))
    varr = varr.astype(np.float32)
    vnarr = np.reshape(vnarr, (vncount, 3))
    vnarr = vnarr.astype(np.float32)
    iarr = np.reshape(iarr, (int(iarr.size/3), 3))
    iarr = iarr.astype(int)
    vniarr = np.reshape(vniarr, (int(vniarr.size/3), 3))
    vniarr = vniarr.astype(int)
    narr = vnarr
    f.close()
    make_farr()
    make_nnarr()
    fread = 1
    objOn = 1

def make_farr():
    global farr, varr, iarr, narr, vniarr
    farr = np.hstack([narr[vniarr.flatten(), :], varr[iarr.flatten(), :]]).flatten().reshape(-1, 3).astype(np.float32)

def make_nnarr():
    global varr, iarr, fnarr, nnarr
    nnarr = np.zeros(varr.size).reshape(-1, 3).astype(np.float32)

    for i in iarr:
        v0 = varr[i[1]] - varr[i[0]]
        v1 = varr[i[2]] - varr[i[0]]
        n = np.cross(v0, v1)
        n = n / np.sqrt(np.dot(n, n))
        fnarr = np.append(fnarr, n)
    
    fnarr = np.reshape(fnarr, (-1, 3)).astype(np.float32)
    
    for i in fnarr:
        for j in range(int(iarr.size/3)):
            for k in range(3):
                nnarr[iarr[j][k]] += i

    for n in nnarr:
        n = n / np.sqrt(np.dot(n, n))

def main():
    global fread
    # Initialize the library
    if not glfw.init():
        return
    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(640, 640, "Class Assignment2", None, None)
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
        # Render here, e.g. using pyOpenGL
        if fread == 1:
            render()
        # Swap front and back buffers
        glfw.swap_buffers(window)

    glfw.terminate()
if __name__ == "__main__":
    main()
