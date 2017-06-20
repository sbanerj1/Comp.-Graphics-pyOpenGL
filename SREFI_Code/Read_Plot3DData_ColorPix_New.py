import os
import sys
from shutil import copyfile
import glob
import random
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo
from OpenGL.GL import shaders
from OpenGL.arrays import vbo
from OpenGL.GL import shaders
from OpenGLContext.arrays import *
import sys
import math
import random
import cv2
from cv2 import cv
from PIL import Image
#from PIL.Image import open
import ctypes

# Some api in the chain is translating the keystrokes to this octal string
# so instead of saying: ESCAPE = 27, we use the following.
ESCAPE = '\033'
# Number of the glut window.
window = 0
shader = 0

user32 = ctypes.windll.user32
w1 = user32.GetSystemMetrics(0)  # Getting width of the monitor
h1 = user32.GetSystemMetrics(1)  # Getting height of the monitor

def compXYZ(min1,max1,lst1):
    min2 = min(lst1)
    max2 = max(lst1)
    lst2 = []
    diff2 = abs(max2 - min2)
    diff1 = abs(max1 - min1)
    for i in range(0,len(lst1)):
        diff = lst1[i] - min2
        val = min1 + diff*(diff1/diff2)
        lst2.append(val)
    return lst2

def compXYZ_Landmark(min1,max1,min2,max2,ind):
    diff2 = abs(max2 - min2)
    diff1 = abs(max1 - min1)
    diff = ind - min2
    ind1 = min1 + diff*(diff1/diff2)
    return ind1

min_x = -12.8
max_x = 12.8
min_y = -9.6
max_y = 9.6
max_z = -1.0
min_z = -10.0

f1 = open('02463d454.abs','r')
img = cv2.imread('02463d455.ppm')
h,w,d = img.shape
print h,w,d
cnt = 0
flag_lst = []
x_lst = []
y_lst = []
z_lst = []
for line in f1:
    if cnt == 3:
        fl = line.split(' ')
        #print len(fl), fl[0], fl[-2]
        for i in range(0,len(fl)-1):
            flag_lst.append(int(fl[i]))
        print len(flag_lst), flag_lst[0], flag_lst[-1]
    if cnt == 4:
        fl = line.split(' ')
        #print len(fl), fl[0], fl[-2]
        for i in range(0,len(fl)-1):
            x_lst.append(float(fl[i]))
        print len(x_lst), x_lst[0], x_lst[-1]
    if cnt == 5:
        fl = line.split(' ')
        #print len(fl), fl[0], fl[-2]
        for i in range(0,len(fl)-1):
            y_lst.append(float(fl[i]))
        print len(y_lst), y_lst[0], y_lst[-1]
    if cnt == 6:
        fl = line.split(' ')
        #print len(fl), fl[0], fl[-2]
        for i in range(0,len(fl)-1):
            z_lst.append(float(fl[i]))
        print len(z_lst), z_lst[0], z_lst[-1]
    cnt += 1
print 640*480

pts_lst = []
x_lst1 = []
y_lst1 = []
z_lst1 = []
x_lst2 = []
y_lst2 = []
z_lst2 = []
cnt = 0
cnt1 = 0
for j in range(0,h):
    for i in range(0,w):
        if flag_lst[cnt] == 1:
            pts_lst.append([x_lst[cnt],y_lst[cnt],z_lst[cnt],img[j][i][2],img[j][i][1],img[j][i][0]])
            x_lst1.append(x_lst[cnt])
            y_lst1.append(y_lst[cnt])
            z_lst1.append(z_lst[cnt])
            cnt1 += 1
        cnt += 1

print cnt1, len(pts_lst), pts_lst[0]

x_lst2 = compXYZ(min_x, max_x, x_lst1)
y_lst2 = compXYZ(min_y, max_y, y_lst1)
z_lst2 = compXYZ(min_z, max_z, z_lst1)

for i in range(0,len(pts_lst)):
    pts_lst[i][0] = x_lst2[i]
    pts_lst[i][1] = y_lst2[i]
    pts_lst[i][2] = z_lst2[i]

print len(pts_lst), pts_lst[0]

f2 = open('02463d455.txt','r')
d_lst = []
d_cnt = 0
for line in f2:
    d_x = int(line.split(',')[0])
    d_y = int(line.split(',')[1].split('\n')[0])
    ind = w*d_y + d_x
    if flag_lst[ind] == 1:
        x_new = compXYZ_Landmark(min_x,max_x,min(x_lst1),max(x_lst1),x_lst[ind])
        y_new = compXYZ_Landmark(min_y,max_y,min(y_lst1),max(y_lst1),y_lst[ind])
        z_new = compXYZ_Landmark(min_z,max_z,min(z_lst1),max(z_lst1),z_lst[ind])
        #print x_new,y_new,z_new
        d_lst.append([x_new,y_new,z_new])
        d_cnt += 1
    else:
        ind1 = ind
        ind2 = ind
        while flag_lst[ind1] != 1 and flag_lst[ind2] != 1:
            ind1 += 1
            ind2 -= 1
        if flag_lst[ind1] == 1:
            ind = ind1
            x_new = compXYZ_Landmark(min_x, max_x, min(x_lst1), max(x_lst1), x_lst[ind])
            y_new = compXYZ_Landmark(min_y, max_y, min(y_lst1), max(y_lst1), y_lst[ind])
            z_new = compXYZ_Landmark(min_z, max_z, min(z_lst1), max(z_lst1), z_lst[ind])
            d_lst.append([x_new, y_new, z_new])
            d_cnt += 1
            print 'right'
        elif flag_lst[ind2] == 1:
            ind = ind2
            x_new = compXYZ_Landmark(min_x, max_x, min(x_lst1), max(x_lst1), x_lst[ind])
            y_new = compXYZ_Landmark(min_y, max_y, min(y_lst1), max(y_lst1), y_lst[ind])
            z_new = compXYZ_Landmark(min_z, max_z, min(z_lst1), max(z_lst1), z_lst[ind])
            d_lst.append([x_new, y_new, z_new])
            d_cnt += 1
            print 'left'

print 'Found landmarks ', d_cnt, len(d_lst)
    #print d_x, d_y, ind, flag_lst[ind]
    #, x_lst[ind], y_lst[ind], z_lst[ind]
    #print pts_lst[w*d_y+d_x]


def saveFrame(tempval):        # Function to save frame
    screenshot = glReadPixels( 0,0, (640), (480), GL_RGBA, GL_UNSIGNED_BYTE)
    im = Image.frombuffer("RGBA", ((640),(480)), screenshot, "raw", "RGBA", 0, 0)
    strng = 'img00'+str(tempval)+'.png'
    im.save(strng)

def InitGL(Width, Height):
    global shader
    VERTEX_SHADER = shaders.compileShader("""
            varying vec4 vertex_color;
        void main() {
        gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
        vertex_color = gl_Color;
         }""", GL_VERTEX_SHADER)
    FRAGMENT_SHADER = shaders.compileShader("""
            varying vec4 vertex_color;
        void main() {
        gl_FragColor = vertex_color;
         }""", GL_FRAGMENT_SHADER)
    shader = shaders.compileProgram(VERTEX_SHADER,
                                    FRAGMENT_SHADER)  # We call this right after our OpenGL window is created.
    glClearColor(0.0, 0.0, 0.0, 0.0)  # This Will Clear The Background Color To Black
    glClearDepth(1.0)  # Enables Clearing Of The Depth Buffer
    glDepthFunc(GL_LESS)  # The Type Of Depth Test To Do
    glEnable(GL_DEPTH_TEST)  # Enables Depth Testing
    glShadeModel(GL_SMOOTH)  # Enables Smooth Color Shading

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()  # Reset The Projection Matrix
    # Calculate The Aspect Ratio Of The Window
    gluOrtho2D(0, Width, 0, Height)
    #gluOrtho2D(-Width/2, Width/2, -Height/2, Height/2)
    # gluPerspective(45.0, float(Width)/float(Height), 0.1, 100.0)

    glMatrixMode(GL_MODELVIEW)

# The function called when our window is resized (which shouldn't happen if you enable fullscreen, below)
def ReSizeGLScene(Width, Height):
    if Height == 0:                        # Prevent A Divide By Zero If The Window Is Too Small
        Height = 1

    glViewport(0, 0, Width, Height)        # Reset The Current Viewport And Perspective Transformation
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    #gluOrtho2D(0, Width, 0, Height)
    gluPerspective(45.0, float(Width)/float(Height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

def DrawSphere(radius,color):
    vertices = []
    vertices.append([0.0, 0.0,0.0,color[0],color[1],color[2]])
    for angle in range(0,360,5):
        vertices.append([(math.sin(angle) * radius), (math.cos(angle) * radius),0.0,color[0],color[1],color[2]])
    spherevbo = vbo.VBO(array( vertices, 'f') )
    spherevbo.bind()
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_COLOR_ARRAY)
    glVertexPointer(3,GL_FLOAT,24,spherevbo)
    glColorPointer(3,GL_FLOAT,24,spherevbo+12)
    glDrawArrays(GL_TRIANGLE_FAN,0,72)
    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_COLOR_ARRAY)
    spherevbo.unbind()

rot = 0
tempval = 1
# The main drawing function.
def DrawGLScene():
    global rot
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    glTranslatef(0.0, 0.0, -20.0)
    glRotatef(rot, 0, 1, 0)
    global shader
    shaders.glUseProgram(shader)

    glBegin(GL_POINTS)
    cnt = 0
    for i in range(0,len(pts_lst)):
        glColor3f(pts_lst[i][3]/255.0,pts_lst[i][4]/255.0,pts_lst[i][5]/255.0)
        glVertex3f(pts_lst[i][0],pts_lst[i][1],pts_lst[i][2])
    # for i in range(0,len(d_lst)):
    #     glColor3f(0,1,0)
    #     glVertex3f(d_lst[i][0],d_lst[i][1],d_lst[i][2])
    glEnd()

    for i in range(0,len(d_lst)):
        glPushMatrix()
        glTranslatef(d_lst[i][0], d_lst[i][1], d_lst[i][2])
        DrawSphere(0.5, (0,1,0))
        glPopMatrix()

    # posx, posy = d_lst[0][0], d_lst[0][1]
    # sides = 32
    # radius = 0.5
    # glBegin(GL_POLYGON)
    # for i in range(100):
    #     cosine = radius * math.cos(i * 2 * math.pi / sides) + posx
    #     sine = radius * math.sin(i * 2 * math.pi / sides) + posy
    #     glVertex2f(cosine, sine)
    #
    # shaders.glUseProgram(0)
    # glEnd()

    #  since this is double buffered, swap the buffers to display what just got drawn.
    glutSwapBuffers()

# The function called whenever a key is pressed. Note the use of Python tuples to pass in: (key, x, y)
def keyPressed(*args):
    global rot, tempval
    # If escape is pressed, kill everything.
    if args[0] == ESCAPE:
        glutDestroyWindow(window)
        sys.exit()
    if args[0] == 'l' or args[0] == 'L':
        print 'Turning left!'
        rot += 30.0
    if args[0] == 'r' or args[0] == 'R':
        print 'Turning right!'
        rot -= 30.0
    if args[0] == 's' or args[0] == 'S':
        print 'Saving frame as img00' + str(tempval) + '.png'
        saveFrame(tempval)
        tempval += 1

def main():
    global window
    # For now we just pass glutInit one empty argument. I wasn't sure what should or could be passed in (tuple, list, ...)
    # Once I find out the right stuff based on reading the PyOpenGL source, I'll address this.
    glutInit(())

    # Select type of Display mode:
    #  Double buffer
    #  RGBA color
    # Alpha components supported
    # Depth buffer
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)

    # get a 640 x 480 window
    glutInitWindowSize(640, 480)

    # the window starts at the upper left corner of the screen
    glutInitWindowPosition(0, 0)

    # Okay, like the C version we retain the window id to use when closing, but for those of you new
    # to Python (like myself), remember this assignment would make the variable local and not global
    # if it weren't for the global declaration at the start of main.
    window = glutCreateWindow("Bowyer 3D Face")

    # Register the drawing function with glut, BUT in Python land, at least using PyOpenGL, we need to
    # set the function pointer and invoke a function to actually register the callback, otherwise it
    # would be very much like the C version of the code.
    glutDisplayFunc(DrawGLScene)

    # Uncomment this line to get full screen.
    # glutFullScreen()

    # When we are doing nothing, redraw the scene.
    glutIdleFunc(DrawGLScene)

    # Register the function called when our window is resized.
    glutReshapeFunc(ReSizeGLScene)

    # Register the function called when the keyboard is pressed.
    glutKeyboardFunc(keyPressed)

    # Initialize our window.
    InitGL(640, 480)

    # Start Event Processing Engine
    glutMainLoop()


# Print message to console, and kick off the main to get it rolling."
print "Hit ESC key to quit."
main()







