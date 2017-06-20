
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
import math
import random
from OpenGL.arrays import vbo
from OpenGL.GL import shaders
from OpenGLContext.arrays import *

# Some api in the chain is translating the keystrokes to this octal string
# so instead of saying: ESCAPE = 27, we use the following.
ESCAPE = '\033'

# Number of the glut window.
window = 0
shader = 0
# A general OpenGL initialization function.  Sets all of the initial parameters. 
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
    shader = shaders.compileProgram(VERTEX_SHADER,FRAGMENT_SHADER)            # We call this right after our OpenGL window is created.
    glClearColor(0.0, 0.0, 0.0, 0.0)    # This Will Clear The Background Color To Black
    glClearDepth(1.0)                    # Enables Clearing Of The Depth Buffer
    glDepthFunc(GL_LESS)                # The Type Of Depth Test To Do
    glEnable(GL_DEPTH_TEST)                # Enables Depth Testing
    glShadeModel(GL_SMOOTH)                # Enables Smooth Color Shading
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()                    # Reset The Projection Matrix
                                        # Calculate The Aspect Ratio Of The Window
    gluOrtho2D(0, Width, 0, Height)
    #gluPerspective(45.0, float(Width)/float(Height), 0.1, 100.0)

    glMatrixMode(GL_MODELVIEW)

# The function called when our window is resized (which shouldn't happen if you enable fullscreen, below)
def ReSizeGLScene(Width, Height):
    if Height == 0:                        # Prevent A Divide By Zero If The Window Is Too Small 
        Height = 1

    glViewport(0, 0, Width, Height)        # Reset The Current Viewport And Perspective Transformation
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, Width, 0, Height)
    #gluPerspective(45.0, float(Width)/float(Height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    
    # Function to draw the actual spheres with the shader
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
    
# The main drawing function. 
# Initializing stuff 
frame_no = 0
days_frame = 1.0
flag = -1
def DrawGLScene():
    global frame_no,days_frame,flag
    #print frame_no
    if flag == 1:
        glPolygonMode( GL_FRONT_AND_BACK, GL_LINE );
    elif flag == -1:
        glPolygonMode( GL_FRONT_AND_BACK, GL_FILL );
    frame_no += days_frame
    # Clear The Screen And The Depth Buffer
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()                    # Reset The View 
    
    global shader
    shaders.glUseProgram(shader)
    
    glTranslatef(400,300,0)
            # Creating the bodies 
    y1 = [0,0,0,0,0]
    x1 = [0,70,134,190,30]
    color = [(1,1,0),(1,0,0),(0,1,0),(0,0,1),(1,1,1)]
    rotate_days = [1,88,225,365,27]
    radius = [50,13,20,21,8]
    i = 0
    glPushMatrix()
    DrawSphere(radius[0],color[0])
    glPopMatrix()
    
    glPushMatrix()
    glRotate(frame_no*(1.0/rotate_days[1]),0.0,0.0,1.0)
    glTranslatef(x1[1], y1[1],0.0)
    DrawSphere(radius[1],color[1])
    #glBegin(GL_POINTS)
    #glVertex2f(x1[1],y1[1])
    #glEnd
    
    glPopMatrix()
    
    glPushMatrix()
    glRotate(frame_no*(1.0/rotate_days[2]),0.0,0.0,1.0)
    glTranslatef(x1[2], y1[2],0.0)
    DrawSphere(radius[2],color[2])
    glPopMatrix()
    
    glPushMatrix()
    glRotate(frame_no*(1.0/rotate_days[3]),0.0,0.0,1.0)
    glTranslatef(x1[3], y1[3],0.0)
    DrawSphere(radius[3],color[3])
    
    glPushMatrix()                   # For the moon
    glRotate(frame_no*(1.0/rotate_days[4]),0.0,0.0,1.0)
    glTranslatef(x1[4], y1[4],0.0)
    DrawSphere(radius[4],color[4])
    glPopMatrix()
    glPopMatrix()
     
    glutSwapBuffers()

def keyPressed(*args):
    global days_frame
    # If q is pressed, kill everything.
    if args[0] == 'q' or args[0] == 'Q':
        print 'Goodbye planetary bodies!'
        glutDestroyWindow(window)
        sys.exit()
        
        # Increasing days/frame
    if args[0] == '+':
        print 'Increasing number of days per frame.'
        days_frame += 1
        #sys.exit()
        
         # Decreasing days/frame
    if args[0] == '-' and days_frame > 1:
        print 'Decreasing number of days per frame.'
        days_frame -= 1
        #sys.exit()
    
    # Euclidean distance measurer
def check_dist_sun(x,y):
    dist = sqrt((400 - x)**2 + (300 - y)**2)
    return dist

# Checking for left click in the Sun
button_down = False
def mousePressed(*args):
    global button_down, flag
    if args[0] == GLUT_LEFT_BUTTON: 
        if not button_down and check_dist_sun(int(args[2]),int(args[3])) < 50:
            print 'Changing planetary body fill orientation.'
            button_down = True
            flag = -(flag)
        else:
            button_down = False
    

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
    glutInitWindowSize(800, 600)
    
    # the window starts at the upper left corner of the screen 
    glutInitWindowPosition(0, 0)
    
    # Okay, like the C version we retain the window id to use when closing, but for those of you new
    # to Python (like myself), remember this assignment would make the variable local and not global
    # if it weren't for the global declaration at the start of main.
    window = glutCreateWindow("2D Orrery!")
    
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
    
    # Initialize our window. 
    InitGL(800, 600)
    
    # Start Event Processing Engine    
    glutMainLoop()

# Print message to console, and kick off the main to get it rolling.
print '\n2D Orrery! Yellow Sun, Red Mercury, Green Venus, Blue Earth and White Moon.'
print 'The planets have a size and orbit range commensurate to that of their actual values.'
print "Hit '+' to increase days per frame"
print "Hit '-' to decrease days per frame (but always above zero)"
print 'Left click inside the Sun to change the fill orientation of the bodies'
print "Hit 'q' or 'Q' key to quit."
main()
        
