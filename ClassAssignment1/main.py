import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

# toggle mode
left = 0
right = 0
scroll = 0
checkV = 0

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


def render():
    global dx, dy, totalx, totaly, M
    global azimuth, elevation
    global l,r,b,t,n,f
    global checkV

    # enable depth test (we'll see details later)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode( GL_FRONT_AND_BACK, GL_LINE )
    glLoadIdentity()

    # toggle perspective projection and orthogonal perspective projection
    if(checkV == 0):
        gluPerspective(angle, aspect, n, f)

    if(checkV == 1):
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
    drawUnitCube()
    drawCubeArray()
    drawGrid()

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

def key_callback(window, key, scancode, action, mods):
    global checkV
    if key == glfw.KEY_V:
        if action == glfw.PRESS:
            # change perspective when V is pressed
            checkV = 1 - checkV
        elif action == glfw.RELEASE:
            pass

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



def main():
    # Initialize the library
    if not glfw.init():
        return
    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(640, 640, "Class Assignment1", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.set_key_callback(window, key_callback)
    glfw.set_cursor_pos_callback(window, cursor_callback)
    glfw.set_mouse_button_callback(window, button_callback)
    glfw.set_scroll_callback(window, scroll_callback)

    # Make the window's context current
    glfw.make_context_current(window)

    # Loop until the user closes the window
    while not glfw.window_should_close(window):
        # Poll for and process events
        glfw.poll_events()
        # Render here, e.g. using pyOpenGL
        render()
        # Swap front and back buffers
        glfw.swap_buffers(window)

    glfw.terminate()
if __name__ == "__main__":
    main()
