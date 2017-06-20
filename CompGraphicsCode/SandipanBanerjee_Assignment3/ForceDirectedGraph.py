from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
import math
import random
from OpenGL.arrays import vbo
from OpenGL.GL import shaders
from OpenGLContext.arrays import *
import time
import json
from numpy import arange
import bisect
import colorsys

random.seed([1234])       # Seeded random

class Link(object):        # Link structure
    def __init__(self, target, weight):
        self.target = target
        self.weight = weight

class Node(object):         # Node structure
    def __init__(self,name,group):
        self.name = name
        self.group = group
        self.X = random.random()
        self.Y = random.random()
        self.links = []

    def dist(self, node):         # Euclidean Distance
        return math.sqrt((node.X-self.X)**2 + (node.Y-self.Y)**2)

# Some api in the chain is translating the keystrokes to this octal string
# so instead of saying: ESCAPE = 27, we use the following.
ESCAPE = '\033'

# Number of the glut window.
window = 0

fData = ""
with open ('graph.txt','r') as file:               # Reading graph data from file
    fData = file.read().replace('\n','')
graph = json.loads(fData)

nodes = []                                       # Putting into the nodes structure
for i in range(len(graph["nodes"])):
    node = Node(graph["nodes"][i]["name"], graph["nodes"][i]["group"])
    for link in graph["links"]:
        if link["source"] == i:
            node.links.append(Link(link["target"], link["value"]))
    nodes.append(node)

groups = []                                # Assigning random colors to each group
for i in range(len(graph["nodes"])):
    if len(groups) <= graph["nodes"][i]["group"]:
        r, g, b = random.random(), random.random(), random.random()
        vertices = []
        vertices.append([-0.5, -0.5, 0.0, r, g, b])
        vertices.append([0.5, -0.5, 0.0, r, g, b])
        vertices.append([0.5, 0.5, 0.0, r, g, b])

        vertices.append([0.5, 0.5, 0.0, r, g, b])
        vertices.append([-0.5, 0.5, 0.0, r, g, b])
        vertices.append([-0.5, -0.5, 0.0, r, g, b])

        groups.append( vbo.VBO(array( vertices, 'f') ) )

shader = 0
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
    gluPerspective(45.0, Width/Height, 0.1, 100.0)

    glMatrixMode(GL_MODELVIEW)

# The function called when our window is resized (which shouldn't happen if you enable fullscreen, below)
def ReSizeGLScene(Width, Height):
    if Height == 0:                        # Prevent A Divide By Zero If The Window Is Too Small
        Height = 1

    glViewport(0, 0, Width, Height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    #gluOrtho2D(0, Width, 0, Height)
    gluPerspective(45.0, Width/Height, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

# Function to get the easier range for drawing circles and spheres
def frange (x,y,jump):
    while x < y:
        yield x
        x += jump

# Function to draw the actual spheres with the shader
def DrawSphere(radius,color):
    vertices = []
    vertices.append([0.0, 0.0,0.0,color[0],color[1],color[2]])
    for angle in frange(0.0,2*math.pi,math.pi/36):
        vertices.append([(math.sin(angle) * radius), (math.cos(angle) * radius),0.0,color[0],color[1],color[2]])
    spherevbo = vbo.VBO(array( vertices, 'f') )
    spherevbo.bind()
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_COLOR_ARRAY)
    glVertexPointer(3,GL_FLOAT,24,spherevbo)
    glColorPointer(3,GL_FLOAT,24,spherevbo+12)
    glDrawArrays(GL_TRIANGLE_FAN,0,74)
    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_COLOR_ARRAY)
    spherevbo.unbind()

# Simulating nodes positioning till 5000 count (they become stable within that usually)
def SimulateStep():
    c1 = 2.0
    c2 = 1.0
    c3 = 1.0
    c4 = 0.01

    forces = []                  # Initializing force on each node
    for i in range(len(nodes)):
        forces.append({'x': 0.0, 'y':0.0})

    for i in range(len(nodes)):            # Calculating repulsive force on each node
        for j in range(len(nodes)):
            if j != i:
                dist = nodes[i].dist(nodes[j])
                forces[i]['x'] -= (nodes[j].X - nodes[i].X) / dist**3
                forces[i]['y'] -= (nodes[j].Y - nodes[i].Y) / dist**3
                forces[j]['x'] += (nodes[j].X - nodes[i].X) / dist**3
                forces[j]['y'] += (nodes[j].Y - nodes[i].Y) / dist**3

        for link in nodes[i].links:            # Calculating attractive force on each node
            target = nodes[link.target]

            dist = nodes[i].dist(target)
            val = (link.weight/2)+1            # Using value field in graph as a function of attraction 
            forces[i]['x'] += val*((target.X - nodes[i].X) / dist) * c1 * math.log(dist)
            forces[i]['y'] += val*((target.Y - nodes[i].Y) / dist) * c1 * math.log(dist)
            forces[link.target]['x'] -= val*((target.X - nodes[i].X) / dist) * c1 * math.log(dist)
            forces[link.target]['y'] -= val*((target.Y - nodes[i].Y) / dist) * c1 * math.log(dist)

    for i in range(len(nodes)):            # Setting the new position of each node
        nodes[i].X += c4 * forces[i]['x']
        nodes[i].Y += c4 * forces[i]['y']
        
    for i in range(len(nodes)):               # Checking for collision between two node centers and re-assigning in such a case
        for j in range(len(nodes)):
            if j!=i:
                dist = nodes[i].dist(nodes[j])
                if dist < 0.5:
                    nodes[i].X += 0.1
                    nodes[i].Y += 0.1
                    nodes[j].X -= 0.1
                    nodes[j].Y -= 0.1

counter = 0
flag_edge = 1
flag_node = 1
flag_group = -1
curr_group = 0
def DrawGLScene():
    start = time.time()
    global counter, shader, groups

    if counter < 5000:               # Simulating for 5000 iterations (becomes stable within that)
        SimulateStep()
        counter += 1

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -50.0)

    shaders.glUseProgram(shader)
    
    #print 'blah ', groups[0]

    for i in range(len(nodes)):                      # Drawing the nodes for only each group and its connections
        if flag_node == 1 and flag_group == -1:
            glPushMatrix()
            
            glTranslatef(nodes[i].X, nodes[i].Y,0)
            
            groups[nodes[i].group].bind()
            
            glEnableClientState(GL_VERTEX_ARRAY)
            glEnableClientState(GL_COLOR_ARRAY)
            
            glVertexPointer(3,GL_FLOAT,24,groups[nodes[i].group])
            glColorPointer(3,GL_FLOAT,24,groups[nodes[i].group]+12)
            glDrawArrays(GL_TRIANGLES,0,6)
            
            glDisableClientState(GL_VERTEX_ARRAY)
            glDisableClientState(GL_COLOR_ARRAY)
            
            groups[nodes[i].group].unbind()
            
            glPopMatrix()
            
        if flag_group == 1:                       # Drawing all nodes
            for link in nodes[i].links:
                target = nodes[link.target]
                if nodes[i].group == curr_group or target.group == curr_group:
                    glPushMatrix()
                    
                    glTranslatef(nodes[i].X, nodes[i].Y,0)
                    
                    groups[nodes[i].group].bind()
                    
                    glEnableClientState(GL_VERTEX_ARRAY)
                    glEnableClientState(GL_COLOR_ARRAY)
                    
                    glVertexPointer(3,GL_FLOAT,24,groups[nodes[i].group])
                    glColorPointer(3,GL_FLOAT,24,groups[nodes[i].group]+12)
                    glDrawArrays(GL_TRIANGLES,0,6)
                    
                    glDisableClientState(GL_VERTEX_ARRAY)
                    glDisableClientState(GL_COLOR_ARRAY)
                    
                    groups[nodes[i].group].unbind()
                    
                    glPopMatrix()
        
        if flag_edge == 1:                           # Drawing the edges, thickness based on attraction value for each edge
            for link in nodes[i].links:
                glPushMatrix()
                target = nodes[link.target]
                temp = (link.weight/2)+1
                #print temp
                glLineWidth(temp)
                glColor3f(1.0, 1.0, 1.0)
                glBegin(GL_LINES)
                glVertex3f(nodes[i].X, nodes[i].Y, 0.0)
                glVertex3f(target.X, target.Y, 0.0)
                glEnd()
                glPopMatrix()

            #dist = nodes[i].dist(target)
            #forces[i]['x'] += ((target.X - nodes[i].X) / dist) * c1 * math.log(dist)
            #forces[i]['y'] += ((target.Y - nodes[i].Y) / dist) * c1 * math.log(dist)
            #forces[link.target]['x'] -= ((target.X - nodes[i].X) / dist) * c1 * math.log(dist)
            #forces[link.target]['y'] -= ((target.Y - nodes[i].Y) / dist) * c1 * math.log(dist)

    glutSwapBuffers()

    #while (time.time()-start) < 1.0/10.0:
    #    pass

def keyPressed(*args):
    global counter, flag_node, flag_edge, flag_group, curr_group
        
    if args[0] == 'n' or args[0] == 'N':            # Toggle node drawing
        flag_node = -(flag_node)
    
    if args[0] == 'e' or args[0] == 'E':            # Toggle edge drawing
        flag_edge = -(flag_edge)
    
    if args[0] == 'a' or args[0] == 'A':            # Draw entire graph
        flag_edge = 1
        flag_node = 1
        flag_group = -1
        
    if args[0] == 'g' or args[0] == 'G':            # Draw one group and its connections at a time and move to next group
        flag_group = -(flag_group)
        if curr_group < 11:
            curr_group += 1
        else:
            curr_group = 0
        
    if args[0] == 'r' or args[0] == 'R':            # Restart the whole process
        for i in range(len(nodes)):
            nodes[i].X = random.random()
            nodes[i].Y = random.random()

# Checking for left click in the Sun
button_down = False
'''
def mousePressed(*args):
    global button_down, flag
    if args[0] == GLUT_LEFT_BUTTON:
        if not button_down:
            print 'Clicked'
            button_down = True
        else:
            button_down = False
'''

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
    window = glutCreateWindow("Force Directed Graph")

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

    #glutMouseFunc (mousePressed)

    # Initialize our window.
    InitGL(800, 600)

    # Start Event Processing Engine
    glutMainLoop()
print "\nPress 'n' or 'N' to toggle drawing of nodes"
print "\nPress 'e' or 'E' to toggle drawing of edges"
print "\nPress 'g' or 'G' to draw one group of nodes and their connections at a time"
print "\nPress 'a' or 'A' to draw entire graph"
print "\nPress 'r' or 'R' to restart whole process"
main()
