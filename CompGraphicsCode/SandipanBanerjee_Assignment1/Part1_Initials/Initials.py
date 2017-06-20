
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo
from OpenGL.GL import shaders
import sys
import math
import random
# Some api in the chain is translating the keystrokes to this octal string
# so instead of saying: ESCAPE = 27, we use the following.
ESCAPE = '\033'

# Number of the glut window.
window = 0
shader = 0

# A general OpenGL initialization function.  Sets all of the initial parameters. 
def InitGL(Width, Height):                # We call this right after our OpenGL window is created.
    global shader 
    VERTEX_SHADER = shaders.compileShader("""#version 120
        void main() {
        gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
         }""", GL_VERTEX_SHADER)
    FRAGMENT_SHADER = shaders.compileShader("""#version 120
        void main() {
        gl_FragColor = vec4( 0, 1, 0, 1 );
         }""", GL_FRAGMENT_SHADER)
    shader = shaders.compileProgram(VERTEX_SHADER,FRAGMENT_SHADER)
    
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

# The main drawing function. 
def DrawGLScene():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    glTranslatef(-1.0, 0.0, -10.0)
    
    global shader
    shaders.glUseProgram(shader)
    
    # Drawing the 'S' with triangles (Sandipan)
    
    glBegin(GL_TRIANGLES)
    glVertex2i(0, 0)
    glVertex2i(0,1)
    glVertex2i(-1,0)
    
    glVertex2i(-1,0)
    glVertex2i(0,1)
    glVertex2i(-1,1)
    
    glVertex2i(-1,1)
    glVertex2i(0,1)
    glVertex2i(0,2)
    
    glVertex2i(0,1)
    glVertex2i(1,1)
    glVertex2i(1,2)
    
    glVertex2i(1,2)
    glVertex2i(0,2)
    glVertex2i(0,1)
    
    glVertex2i(0,-1)
    glVertex2i(1,-1)
    glVertex2i(1,0)
    
    glVertex2i(1,0)
    glVertex2i(0,0)
    glVertex2i(0,-1)
    
    glVertex2i(1,-1)
    glVertex2i(0,-1)
    glVertex2i(0,-2)
    
    glVertex2i(-1,-2)
    glVertex2i(0,-2)
    glVertex2i(0,-1)
    
    glVertex2i(0,-1)
    glVertex2i(-1,-1)
    glVertex2i(-1,-2)
    glEnd()
    
    # Drawing top half of the 'B' with lines (Sandipan)
    
    glBegin(GL_LINES)
    glVertex2f(2, 0)
    glVertex2f(2, 2)
    glVertex2f(2,2)
    glVertex2f(3,2)
    glVertex2f(3,2)
    glVertex2f(4,1.5)
    glVertex2f(4,1.5)
    glVertex2f(4,0.5)
    glVertex2f(4,0.5)
    glVertex2f(3,0)
    glVertex2f(3,0)
    glVertex2f(2,0)
    glEnd()
    
    # Drawing bottom half of the 'B' with points (Sandipan)
    
    glBegin(GL_POINTS)
    i = -0.1
    while i > (-2.1):
        glVertex2f(2,i)
        i = i - 0.1
    i = 2.1
    while i < 3.1:
        glVertex2f(i,-2)
        i = i + 0.1
    i = 3.1
    j = -1.9
    flag = 1
    while i < 4.1:
        glVertex2f(i,j)
        i = i + 0.1
        if flag % 2 == 0:
            j += 0.1
        flag += 1
    while j < (-0.4):
        glVertex2f(i,j)
        j = j + 0.1
    flag = 1
    #print i,j
    while i > 3.0:
        glVertex2f(i,j)
        i = i - 0.1
        if flag % 2 == 0:
            j += 0.1
        flag += 1
    glEnd()
    shaders.glUseProgram( 0 )
    
    #  since this is double buffered, swap the buffers to display what just got drawn. 
    glutSwapBuffers()

# The function called whenever a key is pressed. Note the use of Python tuples to pass in: (key, x, y)  
def keyPressed(*args):
    # If escape is pressed, kill everything.
    if args[0] == ESCAPE:
        glutDestroyWindow(window)
        sys.exit()

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
    window = glutCreateWindow("(S)andipan (B)anerjee's initials")

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

    # Initialize our window. 
    InitGL(640, 480)

    # Start Event Processing Engine    
    glutMainLoop()

# Print message to console, and kick off the main to get it rolling.
print "(S)andipan (B)anerjee's initials"
print "Hit ESC key to quit."
main()
        
