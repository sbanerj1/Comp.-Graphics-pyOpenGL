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
from matplotlib import pyplot
from numpy import arange
import bisect
import colorsys
#import screenshot

# Some api in the chain is translating the keystrokes to this octal string
# so instead of saying: ESCAPE = 27, we use the following.
ESCAPE = '\033'

# Number of the glut window.
window = 0
shader = 0
texshader = 0
image_map = -1
imageID = []
imageTex = ''

# mtl file parser function
def mtl_parser(filename):
    fd = open(filename,'r')
    mat_name = 0
    ambient = []
    diffusion = []
    specular = []
    shiny = []
    map_file = []

    for line in fd:
        if line[0] == 'n' and line[1] == 'e':
            i = 1
            while line[i] != ' ':
                i += 1
            i += 1
            temp = []
            while line[i] != '\n':
                temp.append(line[i])
                i += 1
            mat_name = ''.join(temp)

        elif line[0] == 'K' and line[1] == 'a':
            i = 1
            while line[i] != ' ':
                i += 1
            while line[i] == ' ':
                i += 1
            temp = []
            while line[i] != ' ':
                temp.append(line[i])
                i += 1
            t1 = float(''.join(temp))
            while line[i] == ' ':
                i += 1
            temp = []
            while line[i] != ' ':
                temp.append(line[i])
                i += 1
            t2 = float(''.join(temp))
            while line[i] == ' ':
                i += 1
            temp = []
            while line[i] != '\n':
                temp.append(line[i])
                i += 1
            t3 = float(''.join(temp))
            ambient = [(t1,t2,t3)]
            #print ambient

        elif line[0] == 'K' and line[1] == 'd':
            i = 1
            while line[i] != ' ':
                i += 1
            while line[i] == ' ':
                i += 1
            temp = []
            while line[i] != ' ':
                temp.append(line[i])
                i += 1
            t1 = float(''.join(temp))
            while line[i] == ' ':
                i += 1
            temp = []
            while line[i] != ' ':
                temp.append(line[i])
                i += 1
            t2 = float(''.join(temp))
            while line[i] == ' ':
                i += 1
            temp = []
            while line[i] != '\n':
                temp.append(line[i])
                i += 1
            t3 = float(''.join(temp))
            diffusion = [(t1,t2,t3)]
            #print diffusion
        elif line[0] == 'K' and line[1] == 's':
            i = 1
            while line[i] != ' ':
                i += 1
            while line[i] == ' ':
                i += 1
            temp = []
            while line[i] != ' ':
                temp.append(line[i])
                i += 1
            t1 = float(''.join(temp))
            while line[i] == ' ':
                i += 1
            temp = []
            while line[i] != ' ':
                temp.append(line[i])
                i += 1
            t2 = float(''.join(temp))
            while line[i] == ' ':
                i += 1
            temp = []
            while line[i] != '\n':
                temp.append(line[i])
                i += 1
            t3 = float(''.join(temp))
            specular = [(t1,t2,t3)]
            #print specular
        elif line[0] == 'N' and line[1] == 's':
            i = 1
            while line[i] != ' ':
                i += 1
            while line[i] == ' ':
                i += 1
            temp = []
            while line[i] != '\n':
                temp.append(line[i])
                i += 1
            t1 = float(''.join(temp))
            shiny = t1
            #print shiny
        elif line[0] == 'm' and line[1] == 'a':
            i = 1
            while line[i] != ' ':
                i += 1
            while line[i] == ' ':
                i += 1
            temp = []
            while line[i] != '\n':
                temp.append(line[i])
                i += 1
            map_file = ''.join(temp)
            #print map_file

    fd.close()
    return mat_name,ambient,diffusion,specular,shiny,map_file

# obj file parser function
mat_name = 0
ambient = []
diffusion = []
specular = []
shiny = []
map_file = []
def obj_parser(filename):
    global image_map, ambient, diffusion, specular, shiny, mat_name, map_file
    # Initializing data structures
    vertices = []
    textures = []
    normals = []
    faces = []
    group_name = 0
    data_size = 0

    result = []

    bVertex = False
    for line in open(filename,'r'):
        #print filename
        if filename == 'cube.obj' and line[0] == 'v' and line[1] == 'n':
            parts = line.split(" ")
        elif filename == 'cube.obj':
            parts = line.split("  ")
        else:
            parts = line.split(" ")

        if bVertex and parts[0] != "v":
            bVertex = False
            mean = [0,0,0]
            for i in range(len(vertices)):
                mean[0] += vertices[i][0]
                mean[1] += vertices[i][1]
                mean[2] += vertices[i][2]
            mean[0] = mean[0]/len(vertices)
            mean[1] = mean[2]/len(vertices)
            mean[2] = mean[2]/len(vertices)

            #print mean

            for i in range(len(vertices)):
                vertices[i][0] = vertices[i][0] - mean[0]
                vertices[i][1] = vertices[i][1] - mean[1]
                vertices[i][2] = vertices[i][2] - mean[2]

        if parts[0] == "g":
            group_name = parts[1]
            #print group_name

        if parts[0] == "v":
            bVertex = True
            #print 'v ', parts
            vertices.append([float(parts[1]),float(parts[2]),float(parts[3])])

        if parts[0] == "vt":
            #print 'vt ',parts
            textures.append([float(parts[1]),float(parts[2])])

        elif parts[0] == "vn" and filename == "cube.obj":
            #print 'vn ',parts
            count = 0
            for i in range(len(parts)):
                if parts[i] == "":
                    count += 1
            for i in range(count):
                parts.remove("")
            #print 'new vn ', parts
            normals.append([float(parts[1]),float(parts[2]),float(parts[3])])

        if parts[0] == "vn":
            #print 'vn ',parts
            normals.append([float(parts[1]),float(parts[2]),float(parts[3])])

        if parts[0] == "f":
            for i in range(len(parts)-1):
                face = []
                face_parts = parts[i+1].split("/")

                if len(face_parts) >= 1:
                    fVertex = vertices[int(face_parts[0])-1]
                    face.append(fVertex[0])
                    face.append(fVertex[1])
                    face.append(fVertex[2])

                if len(face_parts) >= 2 and len(face_parts[1]) != 0:
                    fTexture = textures[int(face_parts[1])-1]
                    face.append(fTexture[0])
                    face.append(fTexture[1])

                if len(face_parts) == 3:
                    fNormal = normals[int(face_parts[2])-1]
                    face.append(fNormal[0])
                    face.append(fNormal[1])
                    face.append(fNormal[2])
                result.append(face)

        if line[0] == 'u' and line[1] == 's':
            i = 1
            while line[i] != ' ':
                i += 1
            while line[i] == ' ':
                i += 1
            temp = []
            while line[i] != '\n':
                temp.append(line[i])
                i += 1
            mat_name_specified = ''.join(temp)
            #print mat_name_specified

        elif line[0] == 'm' and line[1] == 't':
            i = 1
            while line[i]!=' ':
                i += 1
            i += 1
            temp = []
            while line[i]!='\n':
                temp.append(line[i])
                i += 1
            mtl_file = ''.join(temp)
            #print mtl_file
            (mat_name,ambient,diffusion,specular,shiny,map_file) = mtl_parser(mtl_file)
            image_map = map_file
            #print mat_name,ambient,diffusion,specular,shiny,map_file

    return vbo.VBO( array(result, 'f') ), len(result), len(result[0]) * 4  # Returning data structures containing read data

(objBuffer, faces, size) = obj_parser('kia.obj')
wall_buffer = []
wall_image = 0
tempval = 0

def loadImage(imageName):          # Function to load texture images
    #global texture
    image = Image.open(imageName)

    ix = image.size[0]
    iy = image.size[1]
    image = image.tobytes("raw", "RGBX", 0, -1)

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

def DrawObject(buffer,len, size):          # Object (car) drawing function
    buffer.bind()
    imageID = loadImage(map_file)
    if size == 12:
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3,GL_FLOAT,size,buffer)
        glDrawArrays(GL_TRIANGLES,0,len)
        glDisableClientState(GL_NORMAL_ARRAY)
    elif size == 20:
        glBindTexture(GL_TEXTURE_2D, imageID)
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        glVertexPointer(3,GL_FLOAT,size,buffer)
        glTexCoordPointer(2,GL_FLOAT,size,buffer+12)
        glDrawArrays(GL_TRIANGLES,0,len)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)
        glBindTexture(GL_TEXTURE_2D, 0)
    elif size == 24:
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glVertexPointer(3,GL_FLOAT,size,buffer)
        glNormalPointer(GL_FLOAT,size,buffer+12)
        glDrawArrays(GL_TRIANGLES,0,len)
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
    elif size == 32:
        glBindTexture(GL_TEXTURE_2D, imageID)
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glVertexPointer(3,GL_FLOAT,32,buffer)
        glTexCoordPointer(2,GL_FLOAT,32,buffer+12)
        glNormalPointer(GL_FLOAT,32,buffer+20)
        glDrawArrays(GL_TRIANGLES,0,len)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
        glBindTexture(GL_TEXTURE_2D, 0)
    buffer.unbind()

def DrawWall(wall_buffer, wall_image):     # Wall (background) drawing function
    wall_buffer.bind()
    glBindTexture(GL_TEXTURE_2D, wall_image)
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_TEXTURE_COORD_ARRAY)
    glVertexPointer(3,GL_FLOAT,20,wall_buffer)
    glTexCoordPointer(2,GL_FLOAT,20,wall_buffer+12)
    glDrawArrays(GL_TRIANGLES,0,6)
    glDisableClientState(GL_TEXTURE_COORD_ARRAY)
    glDisableClientState(GL_VERTEX_ARRAY)
    glBindTexture(GL_TEXTURE_2D, 0)
    wall_buffer.unbind()

# A general OpenGL initialization function.  Sets all of the initial parameters.
def InitGL(Width, Height):
    global shader, texshader, imageID, ambient, diffusion, shiny, specular, wall_image, wall_buffer
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

    TEX_VERTEX_SHADER = shaders.compileShader("""
        void main() {
            gl_Position = ftransform();
            gl_TexCoord[0] = gl_MultiTexCoord0;
        }""", GL_VERTEX_SHADER)

    TEX_FRAGMENT_SHADER = shaders.compileShader("""
        uniform float zoom_level, zoom_x, zoom_y;
        uniform sampler2D sampler;
        void main() {
            vec2 coord = gl_TexCoord[0].xy;
            coord.x = coord.x - (zoom_level * (coord.x - (coord.x * zoom_x + zoom_x)));
            coord.y = coord.y - (zoom_level * (coord.y - (coord.y * zoom_y + zoom_y)));
            gl_FragColor = texture2D(sampler, coord);
         }""", GL_FRAGMENT_SHADER)
    texshader = shaders.compileProgram(TEX_VERTEX_SHADER,TEX_FRAGMENT_SHADER)

    shaders.glUseProgram(texshader)
    glUniform1f(glGetUniformLocation(texshader, "zoom_level"), 0.0);
    glUniform1f(glGetUniformLocation(texshader, "zoom_x"), 0.32);
    glUniform1f(glGetUniformLocation(texshader, "zoom_y"), 0.38);

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

    material_specular = [specular[0][0], specular[0][1], specular[0][2], 1.0]
    material_shininess = [ shiny ]
    material_ambient = [ambient[0][0], ambient[0][1], ambient[0][2], 1.0]
    material_diffuse = [diffusion[0][0], diffusion[0][1], diffusion[0][2], 1.0]
    glMaterialfv(GL_FRONT, GL_SPECULAR, material_specular)
    glMaterialfv(GL_FRONT, GL_SHININESS, material_shininess)
    glMaterialfv(GL_FRONT, GL_AMBIENT, material_ambient)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, material_diffuse)


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
        [-1.0, -1.0,  1.0,  0.0,  0.0],
        [ 1.0, -1.0,  1.0,  1.0,  0.0],
        [ 1.0,  1.0,  1.0,  1.0,  1.0],

        [ 1.0,  1.0,  1.0,  1.0,  1.0],
        [-1.0,  1.0,  1.0,  0.0,  1.0],
        [-1.0, -1.0,  1.0,  0.0,  0.0]
    ]

    wall_image = loadImage("CH.jpg")
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

counter = 0
zoom_value = -50.0
ang = 0.0

texture_zoom = 0.0
texture_zoom_dir = 1.0

# Main drawing function
def DrawGLScene():
    start = time.time()
    global counter, shader,zoom_value, button_down, ang, size, texshader, texture_zoom, texture_zoom_dir, wall_buffer, wall_image

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()                    # Reset The View
    shaders.glUseProgram(texshader)

    glPushMatrix()
    glTranslatef(0.0,0.0,-50.0)
    glScalef(15.0, 15.0, 1.0)
    DrawWall(wall_buffer, wall_image)
    glPopMatrix()

    #imageTex = 'CH.jpg'
    #print imageTex
    shaders.glUseProgram(shader)
    glPushMatrix()
    glTranslatef(0.0,-5.0,zoom_value+12.0)
    glRotatef(ang,0.0,1.0,0.0)
    DrawObject(objBuffer, faces, size)
    glPopMatrix()

    glutSwapBuffers()
    counter += 1
    #varr2 = time.time()
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
    shaders.glUseProgram(0)

    # Making sure we have 30 frames per second, otherwise it passes
    while (time.time()-start) < 1.0/60.0:
        pass

    #print 'Frame No. ', frame_no

spot_light = 1
point_light = 1

def keyPressed(*args):
    global zoom_value, shader, spot_light, point_light, tempval, spot_ang
    # If q is pressed, kill everything.
    if args[0] == 'q' or args[0] == 'Q':
        glutDestroyWindow(window)
        sys.exit()

    if args[0] == 'i' or args[0] == 'I':
        zoom_value += 1

    if args[0] == 'o' or args[0] == 'O':
        if zoom_value > -100.0:
            zoom_value -= 1

    if args[0] == 's' or args[0] == 'S':
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
    window = glutCreateWindow("Assignment 5 with texturing and lighting - Sandipan Banerjee")

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
print '\nAssignment 5 with texturing and lighting'
print "Hit 'i' or 'I' to zoom in (car)"
print "Hit 'o' or 'O' to zoom out (car)"
print "Hit 's' or 'S' to turn the spot light source on/off"
print "Hit 'p' or 'P' to turn the point light source on/off"
print "Hit 'f' or 'F' to save current frame into ppm file"
print 'Click and hold the left click button on the mouse to rotate the car in anti clockwise direction'
print "Hit 'q' or 'Q' key to quit."
main()
