
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
import math
import random
# Some api in the chain is translating the keystrokes to this octal string
# so instead of saying: ESCAPE = 27, we use the following.
ESCAPE = '\033'

# Number of the glut window.
window = 0

# A general OpenGL initialization function.  Sets all of the initial parameters. 
def InitGL(Width, Height):				# We call this right after our OpenGL window is created.
    glClearColor(0.0, 0.0, 0.0, 0.0)	# This Will Clear The Background Color To Black
    glClearDepth(1.0)					# Enables Clearing Of The Depth Buffer
    glDepthFunc(GL_LESS)				# The Type Of Depth Test To Do
    glEnable(GL_DEPTH_TEST)				# Enables Depth Testing
    glShadeModel(GL_SMOOTH)				# Enables Smooth Color Shading
	
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()					# Reset The Projection Matrix
										# Calculate The Aspect Ratio Of The Window
    gluOrtho2D(0, Width, 0, Height)
    #gluPerspective(45.0, float(Width)/float(Height), 0.1, 100.0)

    glMatrixMode(GL_MODELVIEW)

# The function called when our window is resized (which shouldn't happen if you enable fullscreen, below)
def ReSizeGLScene(Width, Height):
    if Height == 0:						# Prevent A Divide By Zero If The Window Is Too Small 
	    Height = 1

    glViewport(0, 0, Width, Height)		# Reset The Current Viewport And Perspective Transformation
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, Width, 0, Height)
    #gluPerspective(45.0, float(Width)/float(Height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

# The main drawing function. 
#Initializing the ball position and velocity and bar position (Sandipan)
score = 0
fail = 0
xPos = 320.0
ball_x = 320
ball_y = 240
vel_x = random.uniform(-0.3, 0.3)
vel_y = random.uniform(-0.3, 0.3)
def DrawGLScene():
    global ball_x,ball_y,vel_x,vel_y,xPos,score,fail
    # Clear The Screen And The Depth Buffer
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()					# Reset The View 
    
    glPushMatrix()
    if ball_x < 21.0:             # If ball hits left wall (Sandipan)
        vel_x = -vel_x
    if ball_x > 619.0:            # If ball hits right wall (Sandipan)
        vel_x = -vel_x
    if ball_y < 21.0:             # If ball goes below (Sandipan)
        fail += 1
        print 'Score = ',score
        print 'Fails = ',fail
        vel_y = random.uniform(-0.3, 0.3)
        vel_x = random.uniform(-0.3, 0.3)
        ball_x = 320
        ball_y = 240
    if ball_y > 459.0:            # If ball hits top (Sandipan)
        vel_y = -vel_y
    if ball_x > (xPos-100) and ball_x < (xPos + 100) and ball_y <= 41:          # If ball hits bar (Sandipan)
        #vel_x = -vel_x
        vel_y = -vel_y
        score += 1
        print 'score ', score
    ball_x += vel_x
    ball_y += vel_y
    glTranslatef(ball_x,ball_y,0)
    glBegin(GL_TRIANGLE_FAN)          # Creating the ball (Sandipan)
    x1 = 0
    y1 = 0
    radius = 20
    glVertex2f(x1, y1)
    for angle in range(0,360,5):
        glVertex2f(x1 + math.sin(angle) * radius, y1 + math.cos(angle) * radius)
    glEnd()
    glPopMatrix()
    
    glTranslatef(xPos, 0.0, 0.0)  # translation of the bar
    
    # Draw a square (quadrilateral)
    glBegin(GL_QUADS)                   # Start drawing a 4 sided polygon
    glVertex2f(-100, 20)          # Top Left
    glVertex2f(100, 20)           # Top Right
    glVertex2f(100, -20)          # Bottom Right
    glVertex2f(-100, -20)         # Bottom Left
    glEnd()                             # We are done with the polygon
    
    #  since this is double buffered, swap the buffers to display what just got drawn. 
    glutSwapBuffers()

# The function called whenever a key is pressed. Note the use of Python tuples to pass in: (key, x, y)  
def keyPressed(*args):
    global xPos,vel_x,vel_y,fail
	# If escape is pressed, kill everything.
    if args[0] == ESCAPE or fail == 5:
        print 'Game Over!'
        glutDestroyWindow(window)
        sys.exit()
    elif args[0] == 'd' and xPos < 540:        # Pressing d bar goes right (Sandipan)
        xPos += 10
        #print 'right ',xPos
    elif args[0] == 'a' and xPos > 100:        # Pressing a bar goes left (Sandipan)
        xPos -= 10
        #print 'left ',xPos
    elif args[0] == 's':                       # Pressing s ball velocity goes down (Sandipan)
        vel_x = vel_x*(0.8)
        vel_y = vel_y*(0.8)
        #print 'velocity down'
    elif args[0] == 'w':                       # Pressing w ball velocity goes up (Sandipan)
        vel_x = vel_x*(1.2)
        vel_y = vel_y*(1.2)
        #print 'velocity up'
    

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
	window = glutCreateWindow("Sandipan's Pong Game")

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
print "Hit ESC key to quit."
main()
    	
