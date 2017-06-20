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
from PIL import Image
#from PIL.Image import open
import json
#from matplotlib import pyplot
from numpy import arange
import bisect
import colorsys
import ctypes
from pygame import mixer
#import screenshot

# Some api in the chain is translating the keystrokes to this octal string
# so instead of saying: ESCAPE = 27, we use the following.
ESCAPE = '\033'

mixer.init()

# Number of the glut window.
window = 0
shader = 0
texshader = 0
image_map = -1
imageID = []
imageTex = ''

wall_buffer = []
wall_image = []
tempval = 0

def loadImage(imageName):          # Function to load texture images
    #global texture
    image = Image.open(imageName)

    ix = image.size[0]
    iy = image.size[1]
    image = image.tostring("raw", "RGBX", 0, -1)

    # Create Texture
    ID = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D,ID)   # 2D texture (x and y size)

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


def DrawWall(wall_buffer, wall_image):     # Wall (background) drawing function
    wall_buffer.bind()
    glBindTexture(GL_TEXTURE_2D, wall_image)
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_TEXTURE_COORD_ARRAY)
    glVertexPointer(3,GL_FLOAT,20,wall_buffer)
    glTexCoordPointer(2,GL_FLOAT,20,wall_buffer+12)
    glDrawArrays(GL_QUADS, 0, 24)
    glDisableClientState(GL_TEXTURE_COORD_ARRAY)
    glDisableClientState(GL_VERTEX_ARRAY)
    glBindTexture(GL_TEXTURE_2D, 0)
    wall_buffer.unbind()

class Shape(object):
        def __init__(self):
            self.pos = []

        def add_block(self,x,y):
            self.pos.append([x,y])

        def draw(self,wall_buffer,wall_image):
            for i in range(len(self.pos)):
                glPushMatrix()
                glTranslatef(self.pos[i][0],self.pos[i][1],0.0)
                DrawWall(wall_buffer, wall_image)
                glPopMatrix()

shapes = []

# A general OpenGL initialization function.  Sets all of the initial parameters.
def InitGL(Width, Height):
    global shader, texshader, imageID, ambient, diffusion, shiny, specular, wall_image, wall_buffer, shapes

    # Single Block
    single_block = Shape()
    single_block.add_block(0, 0)
    shapes.append(single_block)

    # Two blocks
    side_by_side_shape = Shape()
    side_by_side_shape.add_block(0, 0)
    side_by_side_shape.add_block(2, 0)
    shapes.append(side_by_side_shape)

    # Three blocks

    # Side by Side
    three_side_by_side = Shape()
    three_side_by_side.add_block(0, 0)
    three_side_by_side.add_block(2, 0)
    three_side_by_side.add_block(4, 0)
    shapes.append(three_side_by_side)

    # Top left

    three_top_left = Shape()
    three_top_left.add_block(0,0)
    three_top_left.add_block(0,2)
    three_top_left.add_block(2,0)
    shapes.append(three_top_left)

    # Top right

    three_top_right = Shape()
    three_top_right.add_block(0,0)
    three_top_right.add_block(2,0)
    three_top_right.add_block(2,2)
    shapes.append(three_top_right)

    # Four blocks

    # Side by side

    four_side_by_side = Shape()
    four_side_by_side.add_block(0, 0)
    four_side_by_side.add_block(2, 0)
    four_side_by_side.add_block(4, 0)
    four_side_by_side.add_block(6, 0)
    shapes.append(four_side_by_side)

    # Square

    four_square = Shape()
    four_square.add_block(0,0)
    four_square.add_block(0,2)
    four_square.add_block(2,2)
    four_square.add_block(2,0)
    shapes.append(four_square)

    # Top left

    four_top_left = Shape()
    four_top_left.add_block(0,0)
    four_top_left.add_block(2,0)
    four_top_left.add_block(4,0)
    four_top_left.add_block(0,2)
    shapes.append(four_top_left)

    # Top mid

    four_top_mid = Shape()
    four_top_mid.add_block(0,0)
    four_top_mid.add_block(2,0)
    four_top_mid.add_block(4,0)
    four_top_mid.add_block(2,2)
    shapes.append(four_top_mid)

    # Top right

    four_top_right = Shape()
    four_top_right.add_block(0,0)
    four_top_right.add_block(2,0)
    four_top_right.add_block(4,0)
    four_top_right.add_block(4,2)
    shapes.append(four_top_right)



    VERTEX_SHADER = shaders.compileShader("""
        varying vec3 normal;
        varying vec4 ecPos, ambientGlobal;

        // Point Light
        varying vec4 pDiffuse, pAmbient;
        varying vec3 pHalfVector;

        // Spot Light
        varying vec4 sDiffuse, sAmbient;
        varying vec3 sHalfVector;

        void main()
        {
            // General Parameters
            ecPos = gl_ModelViewMatrix * gl_Vertex;
            normal = normalize(gl_NormalMatrix * gl_Normal);
            ambientGlobal = gl_LightModel.ambient * gl_FrontMaterial.ambient;

            // Point Light Parameters
            pHalfVector = gl_LightSource[0].halfVector.xyz;
            pAmbient = gl_FrontMaterial.ambient * gl_LightSource[0].ambient;
            pDiffuse = gl_FrontMaterial.diffuse * gl_LightSource[0].diffuse;

            // Spot Light Parameters
            sHalfVector = gl_LightSource[1].halfVector.xyz;
            sAmbient = gl_FrontMaterial.ambient * gl_LightSource[1].ambient;
            sDiffuse = gl_FrontMaterial.diffuse * gl_LightSource[1].diffuse;

            gl_Position = ftransform();
            gl_TexCoord[0] = gl_MultiTexCoord0;
        }""", GL_VERTEX_SHADER)

    FRAGMENT_SHADER = shaders.compileShader("""
        uniform sampler2D sampler;
        varying vec3 normal;
        varying vec4 ecPos, ambientGlobal;

        // Point Light
        uniform int pEnable;
        varying vec4 pDiffuse, pAmbient;
        varying vec3 pHalfVector;

        // Spot Light
        uniform int sEnable;
        varying vec4 sDiffuse, sAmbient;
        varying vec3 sHalfVector;

        void main()
        {
            vec3 n = normalize(normal);

            // Point Light Code
            vec4 pColor = vec4(0.0);
            if( pEnable == 1 ){
                vec3 lightDir = vec3(gl_LightSource[0].position-ecPos);

                float dist = length(lightDir);
                float NdotL = max(dot(n,normalize(lightDir)),0.0);
                if (NdotL > 0.0) {
                    float att = 1.0 / (gl_LightSource[0].constantAttenuation + gl_LightSource[0].linearAttenuation * dist + gl_LightSource[0].quadraticAttenuation * dist * dist);
                    pColor += att * (pDiffuse * NdotL + pAmbient);

                    vec3 halfV = normalize(pHalfVector);
                    float NdotHV = max(dot(n,halfV),0.0);
                    pColor += att * gl_FrontMaterial.specular * gl_LightSource[0].specular * pow(NdotHV,gl_FrontMaterial.shininess);
                }
            }

            // Spot Light Code
            vec4 sColor = vec4(0.0);
            if( sEnable == 1 ){
                vec3 lightDir = vec3(gl_LightSource[1].position-ecPos);

                float dist = length(lightDir);
                float NdotL = max(dot(n,normalize(lightDir)),0.0);
                if (NdotL > 0.0) {
                    float spotEffect = dot(normalize(gl_LightSource[1].spotDirection), normalize(-lightDir));
                    if (spotEffect > gl_LightSource[1].spotCosCutoff) {
                        float spotEffect = pow(spotEffect, gl_LightSource[1].spotExponent);
                        float att = spotEffect / (gl_LightSource[1].constantAttenuation + gl_LightSource[1].linearAttenuation * dist + gl_LightSource[1].quadraticAttenuation * dist * dist);
                        sColor += att * (sDiffuse * NdotL + sAmbient);

                        vec3 halfV = normalize(sHalfVector);
                        float NdotHV = max(dot(n,halfV),0.0);
                        sColor += att * gl_FrontMaterial.specular * gl_LightSource[1].specular * pow(NdotHV,gl_FrontMaterial.shininess);
                    }
                }
            }

            // Combine
            gl_FragColor = texture2D(sampler, gl_TexCoord[0].xy) * (ambientGlobal + pColor + sColor);
         }""", GL_FRAGMENT_SHADER)
    shader = shaders.compileProgram(VERTEX_SHADER,FRAGMENT_SHADER)

    shaders.glUseProgram(shader)
    glUniform1i(glGetUniformLocation(shader, "sampler"), 0);
    glUniform1i(glGetUniformLocation(shader, "pEnable"), 1);
    glUniform1i(glGetUniformLocation(shader, "sEnable"), 1);

    light_ambient = [0.0, 0.0, 0.0, 1.0]
    light_diffuse = [1.0, 1.0, 1.0, 1.0]
    light_specular = [1.0, 1.0, 1.0, 1.0]
    light_position = [0.0, 0.0, 0.0, 1.0]

    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient);
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse);
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular);
    glLightfv(GL_LIGHT0, GL_POSITION, light_position);

    spot_light_ambient = [0.0, 0.0, 0.0, 1.0]
    spot_light_diffuse = [0.0, 1.0, 0.0, 1.0]
    spot_light_specular = [0.0, 1.0, 0.0, 1.0]
    spot_light_direction = [0.0, 0.0, -1.0, 0.0]

    glLightf(GL_LIGHT1, GL_SPOT_CUTOFF, 5.0);
    glLightfv(GL_LIGHT1, GL_AMBIENT, spot_light_ambient);
    glLightfv(GL_LIGHT1, GL_DIFFUSE, spot_light_diffuse);
    glLightfv(GL_LIGHT1, GL_SPECULAR, spot_light_specular);
    glLightfv(GL_LIGHT1, GL_SPOT_DIRECTION, spot_light_direction);


    glClearColor(0.0, 0.0, 0.0, 0.0)    # This Will Clear The Background Color To Black
    glClearDepth(1.0)                    # Enables Clearing Of The Depth Buffer
    glDepthFunc(GL_LESS)                # The Type Of Depth Test To Do
    glEnable(GL_DEPTH_TEST)                # Enables Depth Testing
    glShadeModel(GL_SMOOTH)                # Enables Smooth Color Shading
    glDisable(GL_CULL_FACE)
    #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    #glEnableTexture()
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()                    # Reset The Projection Matrix
                                        # Calculate The Aspect Ratio Of The Window
    gluPerspective(45.0, float(Width)/float(Height), 0.1, 100.0)

    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_TEXTURE_2D)

    # Setup the wall
    wall_data = [

        [-1.0, -1.0,  1.0, 0.0, 0.0],
        [ 1.0, -1.0,  1.0, 1.0, 0.0],
        [1.0,  1.0,  1.0, 1.0, 1.0],

        [-1.0,  1.0,  1.0, 0.0, 1.0],
        [-1.0, -1.0, -1.0, 1.0, 0.0],
        [-1.0,  1.0, -1.0, 1.0, 1.0],

        [1.0,  1.0, -1.0, 0.0, 1.0],
        [1.0, -1.0, -1.0, 0.0, 0.0],
        [-1.0,  1.0, -1.0, 0.0, 1.0],

        [-1.0,  1.0,  1.0, 0.0, 0.0],
        [1.0,  1.0,  1.0, 1.0, 0.0],
        [1.0,  1.0, -1.0, 1.0, 1.0],

        [-1.0, -1.0, -1.0, 1.0, 1.0],
        [1.0, -1.0, -1.0, 0.0, 1.0],
        [1.0, -1.0,  1.0, 0.0, 0.0],

        [-1.0, -1.0,  1.0, 1.0, 0.0],
        [1.0, -1.0, -1.0, 1.0, 0.0],
        [1.0,  1.0, -1.0, 1.0, 1.0],

        [1.0,  1.0,  1.0, 0.0, 1.0],
        [1.0, -1.0,  1.0, 0.0, 0.0],
        [-1.0, -1.0, -1.0, 0.0, 0.0],

        [-1.0, -1.0,  1.0, 1.0, 0.0],
        [-1.0,  1.0,  1.0, 1.0, 1.0],
        [-1.0,  1.0, -1.0, 0.0, 1.0]

    ]

    wall_image.append(loadImage("brick1.jpg"))
    #wall_image.append(loadImage("brick2.jpg"))
    wall_image.append(loadImage("brick3.jpg"))
    wall_buffer = vbo.VBO( array(wall_data, 'f') )

# The function called when our window is resized (which shouldn't happen if you enable fullscreen, below)
def ReSizeGLScene(Width, Height):
    if Height == 0:                        # Prevent A Divide By Zero If The Window Is Too Small
        Height = 1

    glViewport(0, 0, Width, Height)        # Reset The Current Viewport And Perspective Transformation
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(Width)/float(Height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

   # Function to save frame to ppm image
def saveFrame(tempval):
    screenshot = glReadPixels( 0,0, 800, 600, GL_RGBA, GL_UNSIGNED_BYTE)
    im = Image.frombuffer("RGBA", (800,600), screenshot, "raw", "RGBA", 0, 0)
    strng = 'img00'+str(tempval)+'.ppm'
    im.save(strng)

def glut_print( x,  y, z, font,  text, r,  g , b , a):

    blending = False
    if glIsEnabled(GL_BLEND) :
        blending = True

    #glEnable(GL_BLEND)
    glColor3f(1,1,1)
    glWindowPos3f(x,y,z)
    for ch in text :
        glutBitmapCharacter( font , ctypes.c_int( ord(ch) ) )

    if not blending :
        glDisable(GL_BLEND)

counter = 0
zoom_value = -50.0
ang = 0.0

texture_zoom = 0.0
texture_zoom_dir = 1.0

val_x = 0.0
val_y = 9.0
acc_y = -0.01
acc_x = 0.0
cnt = 0
ang1 = 0.0
ind = int(random.uniform(0,9))
val_z = -30.0
lim_y = -9.0
max_y = -9.0

floor_shape = []
floor_pos = []
floor_rot = []
floor_range = []

range_x = []
range_z = []
gm_cnt = 0
score = 0
view_flag = 1

# Main drawing function
def DrawGLScene():
    start = time.time()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    if view_flag == 1:
        #print 'I am here ba'
        glViewport(0, 0, 800, 600)
        glLoadIdentity()
        draw_scene()
        
    elif view_flag == -1:
        #print 'Here re'
        
        # left
        glViewport(0, 0, 400, 600)
        glLoadIdentity();
        gluLookAt(30.0, 0.0, 0.0, 0.0, 0.0, -30.0, 0.0, 1.0, 0.0)
        draw_scene();
    
        # right
        glViewport(400, 0, 400, 600);
        glLoadIdentity();
        gluLookAt(0.0, 30.0, 0.0, 0.0, 0.0, -30.0, 0.0, 1.0, 0.0)
        draw_scene();


    glutSwapBuffers()

    # Making sure we have 60 frames per second, otherwise it passes
    while (time.time()-start) < 1.0/60.0:
        pass

def draw_scene():
    flag_val = -1
    global val_x, gm_cnt, score, max_y, lim_y, val_z, ind, floor_range, floor_shape, floor_pos, floor_rot, cnt, ang1, val_y, acc_y, acc_x, counter, shader,zoom_value, button_down, ang, size, texshader, texture_zoom, texture_zoom_dir, wall_buffer, wall_image

    shaders.glUseProgram(texshader)

    #print 'lim_y ', lim_y

    if max_y < 9.0:
        if counter == 1:
            mixer.music.load('Ttrs - Tetris.mp3')
            mixer.music.play()
            pass

        glPushMatrix()
        glTranslatef(val_x,val_y,val_z)
        glRotatef(ang,0.0,0.0,1.0)
        glRotatef(ang1,0.0,1.0,0.0)
        #glScalef(2.0, 2.0, 2.0)
        shapes[ind].draw(wall_buffer, wall_image[1])
        glPopMatrix()

        if ind == 0:
            range_x = [val_x, val_x]
            range_z = [val_z, val_z]
        elif ind == 1 and (ang == 0.0 and ang1 == 0.0):
            range_x = [val_x, val_x + 2.0]
            range_z = [val_z, val_z]
        elif ind == 1 and (ang == 0.0 and ang1 == 90.0):
            range_x = [val_x, val_x]
            range_z = [val_z - 2.0, val_z]
        elif ind == 1 and ang == 90.0:
            range_x = [val_x, val_x]
            range_z = [val_z, val_z]
        elif ind == 2 and (ang == 0.0 and ang1 == 0.0):
            range_x = [val_x, val_x + 4.0]
            range_z = [val_z, val_z]
        elif ind == 2 and (ang == 0.0 and ang1 == 90.0):
            range_x = [val_x, val_x]
            range_z = [val_z - 4.0, val_z]
        elif ind == 2 and ang == 90.0:
            range_x = [val_x, val_x]
            range_z = [val_z, val_z]
        elif ind == 3 and (ang == 0.0 and ang1 == 0.0):
            range_x = [val_x, val_x + 2.0]
            range_z = [val_z, val_z]
        elif ind == 3 and (ang == 0.0 and ang1 == 90.0):
            range_x = [val_x, val_x]
            range_z = [val_z - 2.0, val_z]
        elif ind == 3 and ang == 90.0:
            range_x = [val_x - 2.0, val_x]
            range_z = [val_z, val_z]
        elif ind == 4 and (ang == 0.0 and ang1 == 0.0):
            range_x = [val_x, val_x + 2.0]
            range_z = [val_z, val_z]
        elif ind == 4 and (ang == 0.0 and ang1 == 90.0):
            range_x = [val_x, val_x]
            range_z = [val_z - 2.0, val_z]
        elif ind == 4 and ang == 90.0:
            range_x = [val_x - 2.0, val_x]
            range_z = [val_z, val_z]
        elif ind == 5 and (ang == 0.0 and ang1 == 0.0):
            range_x = [val_x, val_x + 6.0]
            range_z = [val_z, val_z]
        elif ind == 5 and (ang == 0.0 and ang1 == 90.0):
            range_x = [val_x, val_x]
            range_z = [val_z - 6.0, val_z]
        elif ind == 5 and ang == 90.0:
            range_x = [val_x, val_x]
            range_z = [val_z, val_z]
        elif ind == 6 and ang1 == 0.0:
            range_x = [val_x, val_x + 2.0]
            range_z = [val_z, val_z]
        elif ind == 6 and ang1 == 90.0:
            range_x = [val_x, val_x]
            range_z = [val_z - 2.0, val_z]
        elif ind == 7 and (ang == 0.0 and ang1 == 0.0):
            range_x = [val_x, val_x + 4.0]
            range_z = [val_z, val_z]
        elif ind == 7 and (ang == 0.0 and ang1 == 90.0):
            range_x = [val_x, val_x]
            range_z = [val_z - 4.0, val_z]
        elif ind == 7 and ang == 90.0:
            range_x = [val_x - 2.0, val_x]
            range_z = [val_z, val_z]
        elif ind == 8 and (ang == 0.0 and ang1 == 0.0):
            range_x = [val_x, val_x + 4.0]
            range_z = [val_z, val_z]
        elif ind == 8 and (ang == 0.0 and ang1 == 90.0):
            range_x = [val_x, val_x]
            range_z = [val_z - 4.0, val_z]
        elif ind == 8 and ang == 90.0:
            range_x = [val_x - 2.0, val_x]
            range_z = [val_z, val_z]
        elif ind == 9 and (ang == 0.0 and ang1 == 0.0):
            range_x = [val_x, val_x + 4.0]
            range_z = [val_z, val_z]
        elif ind == 9 and (ang == 0.0 and ang1 == 90.0):
            range_x = [val_x, val_x]
            range_z = [val_z - 4.0, val_z]
        elif ind == 9 and ang == 90.0:
            range_x = [val_x - 2.0, val_x]
            range_z = [val_z, val_z]


        #imageTex = 'CH.jpg'
        #print imageTex
        '''
        shaders.glUseProgram(shader)
        glPushMatrix()
        glTranslatef(0.0,-5.0,zoom_value+12.0)
        glRotatef(ang,0.0,1.0,0.0)
        DrawObject(objBuffer, faces, size)
        glPopMatrix()
        '''

        if len(floor_shape) > 0:
            for i in range(len(floor_shape)):
                if max_y < floor_pos[i][1]:
                    max_y = floor_pos[i][1]

                #if flag_x == 1 and flag_z == 1:
                if ((floor_range[i][0] <= range_x[0] <= floor_range[i][1]) or (floor_range[i][0] <= range_x[1] <= floor_range[i][1]) or (range_x[0] <= floor_range[i][0] <= range_x[1]) or (range_x[0] <= floor_range[i][1] <= range_x[1])) and ((floor_range[i][2] <= range_z[0] <= floor_range[i][3]) or (floor_range[i][2] <= range_z[1] <= floor_range[i][3]) or (range_z[0] <= floor_range[i][2] <= range_z[1]) or (range_z[0] <= floor_range[i][3] <= range_z[1])):
                    #print 'I am here mate! ', range_x, range_z, floor_range[i]
                    flag_val = i
                else:
                    #print 'Nope'
                    lim_y = -9.0

                glPushMatrix()
                glTranslatef(floor_pos[i][0],floor_pos[i][1],floor_pos[i][2])
                glRotatef(floor_rot[i][0],0.0,0.0,1.0)
                glRotatef(floor_rot[i][1],0.0,1.0,0.0)
                #glScalef(2.0, 2.0, 2.0)
                shapes[floor_shape[i]].draw(wall_buffer, wall_image[0])
                glPopMatrix()

            if flag_val > -1:
                i = flag_val
                if floor_shape[i] == 0:
                    lim_y = floor_pos[i][1] + 2.0
                elif floor_shape[i] == 1 and floor_rot[i][0] == 0.0:
                    lim_y = floor_pos[i][1] + 2.0
                elif floor_shape[i] == 1 and floor_rot[i][0] == 90.0:
                    lim_y = floor_pos[i][1] + 4.0
                elif floor_shape[i] == 2 and floor_rot[i][0] == 0.0:
                    lim_y = floor_pos[i][1] + 2.0
                elif floor_shape[i] == 2 and floor_rot[i][0] == 90.0:
                    lim_y = floor_pos[i][1] + 6.0
                elif floor_shape[i] == 3:
                    lim_y = floor_pos[i][1] + 4.0
                elif floor_shape[i] == 4:
                    lim_y = floor_pos[i][1] + 4.0
                elif floor_shape[i] == 5 and floor_rot[i][0] == 0.0:
                    lim_y = floor_pos[i][1] + 2.0
                elif floor_shape[i] == 5 and floor_rot[i][0] == 90.0:
                    lim_y = floor_pos[i][1] + 8.0
                elif floor_shape[i] == 6:
                    lim_y = floor_pos[i][1] + 4.0
                elif floor_shape[i] == 7 and floor_rot[i][0] == 0.0:
                    lim_y = floor_pos[i][1] + 4.0
                elif floor_shape[i] == 7 and floor_rot[i][0] == 90.0:
                    lim_y = floor_pos[i][1] + 6.0
                elif floor_shape[i] == 8 and floor_rot[i][0] == 0.0:
                    lim_y = floor_pos[i][1] + 4.0
                elif floor_shape[i] == 8 and floor_rot[i][0] == 90.0:
                    lim_y = floor_pos[i][1] + 6.0
                elif floor_shape[i] == 9 and floor_rot[i][0] == 0.0:
                    lim_y = floor_pos[i][1] + 4.0
                elif floor_shape[i] == 9 and floor_rot[i][0] == 90.0:
                    lim_y = floor_pos[i][1] + 6.0

        #print 'lim_y ', lim_y
        counter += 1


        if val_y > lim_y:
            val_y = val_y + acc_y

        if val_y < lim_y:
            if cnt == 0:
                mixer.music.load('Ttrs - Land.mp3')
                mixer.music.play()
                pass
            floor_shape.append(ind)
            floor_pos.append([val_x, val_y, val_z])
            floor_rot.append([ang, ang1])
            floor_range.append([range_x[0], range_x[1], range_z[0], range_z[1]])
            score += 1
            print 'Score ', score
            val_y = 9.0
            val_x = 0.0
            val_z = -30.0
            acc_y = -0.01
            ang = 0.0
            ang1 = 0.0
            lim_y = -9.0
            range_x = []
            range_z = []
            cnt == 0
            ind = int(random.uniform(0,8))

    else:
        for i in range(len(floor_shape)):
                glPushMatrix()
                glTranslatef(floor_pos[i][0],floor_pos[i][1],floor_pos[i][2])
                glRotatef(floor_rot[i][0],0.0,0.0,1.0)
                glRotatef(floor_rot[i][1],0.0,1.0,0.0)
                #glScalef(2.0, 2.0, 2.0)
                shapes[floor_shape[i]].draw(wall_buffer, wall_image[0])
                glPopMatrix()
        if gm_cnt == 0:
            print 'Game Over!!!'
            print 'Your score ', score
            mixer.music.load('Ttrs - GameOverTengen.mp3')
            mixer.music.play()
           # glut_print( 0.0 , 0.0 , -30.0,  GLUT_BITMAP_9_BY_15 , "GAME OVER!!!" , 1.0 , 1.0 , 1.0 , 1.0 )
            gm_cnt += 1


    '''
    if val_x < 6.0 and val_x > -6.0:
        print 'I am here'
        val_x = val_x + acc_x
    '''
    #varr2 = time.time()
    '''
    if button_down:
        ang += 0.25

    texture_zoom += texture_zoom_dir * 1.0/(60.0 * 5.0);

    if texture_zoom >= 1.0:
        texture_zoom = 1.0
        texture_zoom_dir = -texture_zoom_dir

    if texture_zoom <= 0.0:
        texture_zoom = 0.0
        texture_zoom_dir = -texture_zoom_dir

    shaders.glUseProgram(texshader)
    glUniform1f(glGetUniformLocation(texshader, "zoom_level"), texture_zoom);
    '''
    shaders.glUseProgram(0)

spot_light = 1
point_light = 1

def keyPressed(*args):
    global zoom_value, view_flag, lim_y, max_y, shader, ang, spot_light, point_light, tempval, spot_ang, val_x, val_y, val_z, acc_y, acc_x, ang1, score, gm_cnt, floor_range, floor_shape, floor_pos, floor_rot, range_x, range_z
    # If q is pressed, kill everything.
    if args[0] == 'q' or args[0] == 'Q':
        glutDestroyWindow(window)
        sys.exit()

    if args[0] == 'r' or args[0] == 'R':
        mixer.music.load('Ttrs - ClearLine.mp3')
        mixer.music.play()
        val_y = 9.0
        val_x = 0.0
        val_z = -30.0
        acc_y = -0.01
        ang = 0.0
        ang1 = 0.0
        lim_y = -9.0
        range_x = []
        range_z = []
        cnt == 0
        floor_range = []
        floor_pos = []
        floor_shape = []
        floor_rot = []
        gm_cnt = 0
        score = 0
        max_y = -9.0


    if args[0] == 'n' or args[0] == 'N':
        mixer.music.load('Ttrs - Rotate.mp3')
        mixer.music.play()
        if ang1 == 0.0:
            if ang == 0.0:
                ang = 90.0
            else:
                ang = 0.0
        elif ang1 == 90.0:
            ang1 = 0.0
            if ang == 0.0:
                ang = 90.0
            else:
                ang = 0.0

    if args[0] == 'm' or args[0] == 'M':
        mixer.music.load('Ttrs - Rotate.mp3')
        mixer.music.play()
        if ang == 0.0:
            if ang1 == 0.0:
                ang1 = 90.0
            else:
                ang1 = 0.0
        elif ang == 90.0:
            ang = 0.0
            if ang1 == 0.0:
                ang1 = 90.0
            else:
                ang1 = 0.0

    if args[0] == 'a' or args[0] == 'A':
        mixer.music.load('Ttrs - Move.mp3')
        mixer.music.play()
        if val_x > -12.0:
            val_x -= 0.5

    if args[0] == 'd' or args[0] == 'D':
        mixer.music.load('Ttrs - Move.mp3')
        mixer.music.play()
        if val_x < 12.0:
            val_x += 0.5

    if args[0] == 's' or args[0] == 'S':
        mixer.music.load('Ttrs - Move.mp3')
        mixer.music.play()
        if val_z > -40.0:
            val_z -= 2.0

    if args[0] == 'w' or args[0] == 'W':
        mixer.music.load('Ttrs - Move.mp3')
        mixer.music.play()
        if val_z < -30.0:
            val_z += 2.0

    if args[0] == '+':
         if val_y > - 9.0:
             acc_y -= 0.05

    if args[0] == '-':
         if val_y > - 9.0 and acc_y < -0.06:
             acc_y += 0.05

    if args[0] == 'v' or args[0] == 'V':
        view_flag = -(view_flag)

    '''
    if args[0] == 'l' or args[0] == 'L':
        shaders.glUseProgram(shader)
        loc = glGetUniformLocation(shader, "sEnable")
        if spot_light == 1:
            spot_light = 0
        else:
            spot_light = 1
        glUniform1i(loc, spot_light)
        shaders.glUseProgram(0)

    if args[0] == 'p' or args[0] == 'P':
        shaders.glUseProgram(shader)
        loc = glGetUniformLocation(shader, "pEnable")
        if point_light == 1:
            point_light = 0
        else:
            point_light = 1
        glUniform1i(loc, point_light)
        shaders.glUseProgram(0)
    '''
    if args[0] == 'f' or args[0] == 'F':
        print 'Saving frame as img00' + str(tempval) + '.ppm'
        saveFrame(tempval)
        tempval += 1

button_down = False

def mousePressed(*args):
    global button_down,ang
    if args[0] == GLUT_LEFT_BUTTON:
        if not button_down:
            button_down = True
            #ang += 1.0
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
    window = glutCreateWindow("3D Tetris - Sandipan Banerjee")

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
print '\nFinal Project - 3D Tetris'
print "Hit 'v' or 'V' to change view"
print "Hit 'r' or 'R' to reset"
print "Hit 'a' or 'A' to move block left"
print "Hit 'd' or 'D' to move block right"
print "Hit 'w' or 'W' to move block nearer to the viewer"
print "Hit 's' or 'S' to move block further away from the viewer"
print "Hit '+' to increase block velocity"
print "Hit '-' to decrease block velocity"
print "Hit 'n' or 'N' to rotate block in Z direction"
print "Hit 'm' or 'M' to rotate block in Y direction"
print "Hit 'f' or 'F' to save current frame as a ppm file"
print "Hit 'q' or 'Q' key to quit."
main()
