from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
import math
import random
import time
import numpy
from OpenGL.arrays import vbo
from OpenGL.GL import shaders
from OpenGLContext.arrays import *
from PIL import Image
from PIL.Image import open
import ctypes
#import winsound
from pygame import mixer

user32 = ctypes.windll.user32
mixer.init()
mixer.music.load('tng_warp_flash.mp3')  # Loading sound file

w = user32.GetSystemMetrics(0)  # Getting width of the monitor
h = user32.GetSystemMetrics(1)  # Getting height of the monitor
radius = [1,0.3, 0.5, 0.5, 0.4, 0.8, 0.7, 0.3, 0.3, 0.1, 0.1]  # Planetary body radii
dis = [1.8, 2.8, 3.8, 4.8, 6.8 , 8.8, 9.8, 10.8, 11.8, .8]  # Distance from Sun and Earth (for the moon)
year = [88,225,365,687,12*365,29*365,84*365,165*365,247*365,28]  # Time for one revolution around Sun and Earth (for the moon)

#print screensize

# Some api in the chain is translating the keystrokes to this octal string
# so instead of saying: ESCAPE = 27, we use the following.
ESCAPE = '\033'

# Number of the glut window.
window = 0
shader = 0
#imageID = -1
# A general OpenGL initialization function.  Sets all of the initial parameters.
imageID = []
orbit_vbo = []
planet_vbo = []

def InitGL(Width, Height):
    global shader, imageID
    VERTEX_SHADER = shaders.compileShader("""
        void main() {
            gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
            gl_TexCoord[0] = gl_MultiTexCoord0;
        }""", GL_VERTEX_SHADER)
    FRAGMENT_SHADER = shaders.compileShader("""
        uniform sampler2D sampler;
        void main() {
        gl_FragColor = texture2D(sampler, gl_TexCoord[0].xy);
         }""", GL_FRAGMENT_SHADER)
    shader = shaders.compileProgram(VERTEX_SHADER,FRAGMENT_SHADER)            # We call this right after our OpenGL window is created.
    glClearColor(0.0, 0.0, 0.0, 0.0)    # This Will Clear The Background Color To Black
    glClearDepth(1.0)                    # Enables Clearing Of The Depth Buffer
    glDepthFunc(GL_LESS)                # The Type Of Depth Test To Do
    glEnable(GL_DEPTH_TEST)                # Enables Depth Testing
    glShadeModel(GL_SMOOTH)                # Enables Smooth Color Shading

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()                    # Reset The Projection Matrix
                                        # Calculate The Aspect Ratio Of The Window
    #gluOrtho2D(0, Width, 0, Height)
    gluPerspective(45.0, float(Width)/float(Height), 0.1, 100.0)

    glMatrixMode(GL_MODELVIEW)

    glEnable(GL_TEXTURE_2D)
    shaders.glUseProgram(shader)
    glUniform1i(glGetUniformLocation(shader, "sampler"), 0);

    # Create Planets
    for i in range(10):                                               # Loading all planet textures
        imageID.append(loadImage('planet' + str(i) + '.jpg'))
        orbit_vbo.append(CreateOrbit(dis[i],(1,1,1)))                 # Loading orbit vertices to buffer
        planet_vbo.append(CreateSphere(15, radius[i]))                # Loading planet vertices to buffer
 
def saveFrame(tempval):        # Function to save frame 
    screenshot = glReadPixels( 0,0, (w-50), (h-50), GL_RGBA, GL_UNSIGNED_BYTE)
    im = Image.frombuffer("RGBA", ((w-50),(h-50)), screenshot, "raw", "RGBA", 0, 0)
    strng = 'img00'+str(tempval)+'.ppm'
    im.save(strng)

def frange (x,y,jump):    
    while x < y:
        yield x
        x += jump

def CreateOrbit(radius, color):       # Function to get orbit vertices
    vertices = []
    for angle in frange(0.0,2*math.pi,math.pi/90):
        vertices.append([(math.sin(angle) * radius), (math.cos(angle) * radius),0.0,color[0],color[1],color[2]])
    return vbo.VBO(array( vertices, 'f') )

def DrawOrbits(index):          # Drawing orbit function
    global orbit_vbo

    orbit_vbo[index].bind()
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_COLOR_ARRAY)
    glVertexPointer(3,GL_FLOAT,24,orbit_vbo[index])
    glColorPointer(3,GL_FLOAT,24,orbit_vbo[index]+12)
    glDrawArrays(GL_LINE_LOOP,0,180)
    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_COLOR_ARRAY)
    orbit_vbo[index].unbind()

# The main drawing function.
# Initializing stuff
frame_no = 0
days_frame = 1.0
flag = -1
sphere_list = 0
tempval = 0

def loadImage(imageName):          # Function to load texture images
    #global texture
    image = open(imageName)

    ix = image.size[0]
    iy = image.size[1]
    image = image.tobytes("raw", "RGBX", 0, -1)

    # Create Texture
    ID = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D,ID)   # 2d texture (x and y size)

    glPixelStorei(GL_UNPACK_ALIGNMENT,1)
    glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
    return ID

rot_ang = 90

def DrawPlanet(index):            # Function to draw the planets
    global planet_vbo, imageID

    id = imageID[index]
    glBindTexture(GL_TEXTURE_2D, id)

    planet_vbo[index].bind()
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_TEXTURE_COORD_ARRAY)
    glEnableClientState(GL_COLOR_ARRAY)
    glVertexPointer(3,GL_FLOAT,32,planet_vbo[index])
    glTexCoordPointer(2,GL_FLOAT,32,planet_vbo[index]+12)
    glColorPointer(3,GL_FLOAT,32,planet_vbo[index]+20)
    glDrawArrays(GL_QUADS,0,900)
    glDisableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_TEXTURE_COORD_ARRAY)
    glDisableClientState(GL_COLOR_ARRAY)
    planet_vbo[index].unbind()

def CreateSphere(facets, radius):       # Function to create 3D spherical shapes
    dtheta = (math.pi) / facets
    dphi = (2*math.pi)/ facets

    vertices = []
    for y in range(facets):
        theta = y*dtheta - (math.pi/2)
        for x in range(facets):
            phi = x*dphi
            a1 = theta, phi
            a2 = theta + dtheta, phi
            a3 = theta + dtheta, phi + dphi
            a4 = theta, phi + dphi

            for angle in [a1, a2, a3, a4]:
                x, y, z = angle_to_coords(angle[0], angle[1], radius)
                vertices.append([ x, y, z, angle[1]/(2*math.pi), sin(angle[0])/2.0 + 0.5, theta/(2*math.pi), phi/(2*math.pi), 1])

    return vbo.VBO(array( vertices, 'f') )

def angle_to_coords(theta, phi, radius):  # Function to return coordinates of point on sphere given angles and radius
    x = cos(theta) * cos(phi)
    y = cos(theta) * sin(phi)
    z = sin(theta)
    return x * radius, y * radius, z * radius

au = 500
rot_l = 1
rot_m = 10
ang = 18
ang_y = 1
z_val = -24.0
flag = 1
frame_no = 0.0
frame_step = 0.1
gun_ang = 0
def DrawGLScene():        # Main rendering function for drawing frames
    global frame_no,frame_step,days_frame,flag,rot_l,rot_m,ang,z_val,year,frame_no, gun_ang
    #print frame_no

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    shaders.glUseProgram(shader)

    glTranslatef(0.0,0.0,z_val)
    glRotatef(ang,1.0,0.0,0.0)
    glRotatef(ang_y,0.0,0.0,1.0)

    glPushMatrix()

    glRotatef(-90,1,0,0)

    DrawPlanet(0)         # Drawing the Sun
    if flag == 1:
        DrawOrbits(0)     # Drawing the orbits around the Sun
        DrawOrbits(1)
        DrawOrbits(2)
        DrawOrbits(3)
        DrawOrbits(4)
        DrawOrbits(5)
        DrawOrbits(6)
        DrawOrbits(7)
        DrawOrbits(8)
    glPopMatrix()

    glPushMatrix()

    #glTranslatef(2,0,0)
    glRotatef(-90,1,0,0)   
    glRotatef(360*frame_no*(1.0/year[0]),0,0,1)
    glTranslatef(dis[0],0.0,0.0)
    #glRotatef(23.4,0.0,1.0,0.0)
    glRotatef(30 + rot_l,0.0,0.0,1.0)
    DrawPlanet(1)                       # Drawing Mercury
    rot_l += 0.01

    glPopMatrix()

    glPushMatrix()

    #glTranslatef(2,0,0)
    glRotatef(-90,1,0,0)
    glRotatef(360*frame_no*(1.0/year[1]),0,0,1)
    glTranslatef(dis[1],0.0,0.0)
    #glRotatef(23.4,0.0,1.0,0.0)
    glRotatef(30 + rot_l,0.0,0.0,1.0)
    DrawPlanet(2)                         # Drawing Venus
    rot_l += 0.01

    glPopMatrix()

    glPushMatrix()

    #glTranslatef(2,0,0)
    glRotatef(-90,1,0,0)
    glRotatef(360*frame_no*(1.0/year[2]),0,0,1)
    glTranslatef(dis[2],0.0,0.0)

    #glPushMatrix()
    #glRotatef(gun_ang,0.0,1.0,0.0)
    #glBegin(GL_LINES)
    #glVertex3f(0.0,0.0,0.0)
    #glVertex3f(-1.0,0.0,0.0)
    #glEnd()
    #glPopMatrix()

    glRotatef(23.4,0.0,1.0,0.0)
    glRotatef(30 + rot_l,0.0,0.0,1.0)
    DrawPlanet(3)                  # Drawing Earth
    rot_l += 0.01


    glPushMatrix()
    glRotatef(-90,1,0,0)
    glRotatef(360*frame_no*(1.0/year[9]),0,0,1)
    glTranslatef(dis[9],0.0,0.0)
    #glRotatef(23.4,0.0,1.0,0.0)
    glRotatef(30+rot_m,0.0,0.0,1.0)
    DrawPlanet(9)                   # Drawing the moon
    rot_m += 0.1

    glPopMatrix()
    glPopMatrix()

    glPushMatrix()

    #glTranslatef(2,0,0)
    glRotatef(-90,1,0,0)
    glRotatef(360*frame_no*(1.0/year[3]),0,0,1)
    glTranslatef(dis[3],0.0,0.0)
    #glRotatef(23.4,0.0,1.0,0.0)
    glRotatef(30 + rot_l,0.0,0.0,1.0)
    DrawPlanet(4)             # Drawing Mars
    rot_l += 0.01

    glPopMatrix()

    glPushMatrix()

    #glTranslatef(2,0,0)
    glRotatef(-90,1,0,0)
    glRotatef(360*frame_no*(1.0/year[4]),0,0,1)
    glTranslatef(dis[4],0.0,0.0)
    #glRotatef(23.4,0.0,1.0,0.0)
    glRotatef(30 + rot_l,0.0,0.0,1.0)
    DrawPlanet(5)              # Drawing Jupiter
    rot_l += 0.01

    glPopMatrix()

    glPushMatrix()

    #glTranslatef(2,0,0)
    glRotatef(-90,1,0,0)
    glRotatef(360*frame_no*(1.0/year[5]),0,0,1)
    glTranslatef(dis[5],0.0,0.0)
    #glRotatef(23.4,0.0,1.0,0.0)
    glRotatef(30 + rot_l,0.0,0.0,1.0)
    DrawPlanet(6)            # Drawing Saturn (couldn't find a proportionate Saturn ring texture though)
    rot_l += 0.01

    glPopMatrix()

    glPushMatrix()

    #glTranslatef(2,0,0)
    glRotatef(-90,1,0,0)
    glRotatef(360*frame_no*(1.0/year[6]),0,0,1)
    glTranslatef(dis[6],0.0,0.0)
    #glRotatef(23.4,0.0,1.0,0.0)
    glRotatef(30 + rot_l,0.0,0.0,1.0)
    DrawPlanet(7)             # Drawing Uranus
    rot_l += 0.01

    glPopMatrix()

    glPushMatrix()

    #glTranslatef(2,0,0)
    glRotatef(-90,1,0,0)
    glRotatef(360*frame_no*(1.0/year[7]),0,0,1)
    glTranslatef(dis[7],0.0,0.0)
    #glRotatef(23.4,0.0,1.0,0.0)
    glRotatef(30 + rot_l,0.0,0.0,1.0)
    DrawPlanet(8)    # Drawing Neptune
    rot_l += 0.01

    glPopMatrix()

    glPushMatrix()

    #glTranslatef(2,0,0)
    glRotatef(-90,1,0,0)
    glRotatef(360*frame_no*(1.0/year[8]),0,0,1)
    glTranslatef(dis[8],0.0,0.0)
    #glRotatef(23.4,0.0,1.0,0.0)
    glRotatef(30 + rot_l,0.0,0.0,1.0)
    DrawPlanet(9)      # Drawing Pluto
    rot_l += 0.01

    glPopMatrix()

    #glPopMatrix()
    #

    shaders.glUseProgram(0)

    frame_no += frame_step       # Counting frames
    glutSwapBuffers()

def keyPressed(*args):
    global days_frame,z_val,flag, tempval, gun_ang, frame_step, frame_no
    # If q is pressed, kill everything.
    if args[0] == 'q' or args[0] == 'Q':
        print 'Goodbye planetary bodies!'
        glutDestroyWindow(window)
        sys.exit()

        # Function to zoom in
    if args[0] == '+':
        print 'Zooming in'
        z_val += 1

       # Function to speed up revolution of planets 
    if args[0] == 'w' or args[0] == 'W':
        print 'Speeding up!'
        frame_step += 0.05

       # Function to slow down the revolution of the planetary bodies (with a bound greater than 0)
    if args[0] == 'x' or args[0] == 'X':
        print 'Slowing down!'
        if frame_step < frame_no:
            if frame_step > 0.1:
                frame_step -= 0.05
         
         # Function to zoom out   
    if args[0] == '-':
        print 'Zooming out'
        z_val -= 1
        #sys.exit()

         # Toggling orbit drawing
    if args[0] == 'o' or args[0] == 'O':
        print 'Toggling orbit drawing'
        flag = -(flag)
        #sys.exit()

         # Saving frame as screenshot ppm files
    if args[0] == 's' or args[0] == 'S':
        print 'Saving frame as img00' + str(tempval) + '.ppm'
        saveFrame(tempval)
        tempval += 1

         # Playing explosion sound as stored above
    if args[0] == 'v' or args[0] == 'V':
        #winsound.PlaySound("SystemExit", winsound.SND_ALIAS)
        print ' Explosion!'
        mixer.music.play()

         # Pointing up missile gun (failed)
    #if args[0] == 'a' or args[0] == 'A':
      #  gun_ang += 1.0

         # Pointing down missile gun (failed)
    #if args[0] == 'd' or args[0] == 'D':
       # gun_ang -= 1.0

    # Euclidean distance measurer
def check_dist_sun(x,y):
    dist = sqrt((400 - x)**2 + (300 - y)**2)
    return dist

# Checking for left click in the Sun
button_down = False
pos = (0,0)
ration = (0,0)
def mousePressed(*args):                          # Function for dragging up or down the Orrery
    global button_down, flag,pos,w,h,ang,ang_y    # Click at any place and drag the cursor
    if args[0] == GLUT_LEFT_BUTTON:               # Orrery moves up or down based on where you released the button (up or down from start)
        if not button_down:
            button_down = True
            pos = (int(args[2]),int(args[3]))
            #print 'pos 1', pos
        else:
            button_down = False
            pos = (int(args[2])-pos[0],int(args[3])-pos[1])
            #print 'pos ',pos
            ratio = (float(pos[0])/(w-50),float(pos[1])/(h-50))
            #print 'ratio ',ratio
            ang += ang*ratio[0]
            ang_y += 30*ratio[1]

def mouseMotion(x,y):
    pass

def ReSizeGLScene(Width, Height):
    if Height == 0:                        # Prevent A Divide By Zero If The Window Is Too Small
        Height = 1
    glViewport(0, 0, Width, Height)        # Reset The Current Viewport And Perspective Transformation
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(Width)/float(Height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

def main():
    global window,h,w
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
    glutInitWindowSize(w-50, h-50)

    # the window starts at the upper left corner of the screen
    glutInitWindowPosition(0, 0)

    # Okay, like the C version we retain the window id to use when closing, but for those of you new
    # to Python (like myself), remember this assignment would make the variable local and not global
    # if it weren't for the global declaration at the start of main.
    window = glutCreateWindow("3D Orrery by Sandipan Banerjee!")

        # Register the drawing function with glut, BUT in Python land, at least using PyOpenGL, we need to
    # set the function pointer and invoke a function to actually register the callback, otherwise it
    # would be very much like the C version of the code.
    glutDisplayFunc (DrawGLScene)

    # Uncomment this line to get full screen.
    #glutFullScreen()

    # When we are doing nothing, redraw the scene.
    glutIdleFunc(DrawGLScene)

    # Register the function called when our window is resized.
    glutReshapeFunc (ReSizeGLScene)

    # Register the function called when the keyboard is pressed.
    glutKeyboardFunc (keyPressed)

    glutMouseFunc (mousePressed)
    glutMotionFunc (mouseMotion)

    # Initialize our window.
    InitGL(800, 600)

    # Start Event Processing Engine
    glutMainLoop()

# Print message to console, and kick off the main to get it rolling.
print '\n3D Orrery! With the Sun, all the nine planets and the Moon'
print 'The planets have a size, velocity and orbit range commensurate to that of their actual values.'
print "Hit '+' to zoom in"
print "Hit '-' to zoom out"
print "Hit 'W' or 'w' to increase days per frame"
print "Hit 'X' or 'x' to decrease days per frame (but always > 0)"
print "Hit 'O' or 'o' to toggle drawing/undrawing of orbits"
print "Hit 'S' or 's' to save the current frame as a PPM image"
print "Hit 'V' or 'v' to play explosion sound"
print 'Left click on any position on the screen, drag mouse and let go to change angular orientation of the orrery'
print "Hit 'q' or 'Q' key to quit."
main()
