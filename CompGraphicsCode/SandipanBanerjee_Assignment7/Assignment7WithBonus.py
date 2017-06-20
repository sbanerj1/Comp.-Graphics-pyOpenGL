from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import pygame
from pygame.locals import *
import sys
from math import *
from Maths import invert
from OpenGLLibrary import *
import math

import random
from OpenGL.arrays import vbo
from OpenGL.GL import shaders
from OpenGLContext.arrays import array
import time
from PIL import Image
#from PIL.Image import open
import json
from matplotlib import pyplot
from numpy import arange
import bisect
import colorsys

from math import cos
from pygame.locals import *
#import screenshot

pygame.init()

# Number of the glut window.
window = 0
shader = 0
texshader = 0
broccolishader = 0
imageID = -1
imageID1 = -1
imageTex = ''

color = [(1,1,0),(1,0,0),(0,1,0),(0,0,1),(1,1,1)]

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
shiny = -1.0
map_file = []

mat_name1 = 0
ambient1 = []
diffusion1 = []
specular1 = []
shiny1 = -1.0
map_file1 = []

def obj_parser(filename):
    global ambient, diffusion, specular, shiny, mat_name, map_file, mat_name1, ambient1, diffusion1, specular1, shiny1, map_file1
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
            if filename == 'pillow.obj':
                (mat_name1,ambient1,diffusion1,specular1,shiny1,map_file1) = mtl_parser(mtl_file)
                #print '> 1 ', mat_name1,ambient1,diffusion1,specular1,shiny1,map_file1
            else:
                (mat_name,ambient,diffusion,specular,shiny,map_file) = mtl_parser(mtl_file)
                #print 'else ',mat_name,ambient,diffusion,specular,shiny,map_file
            #print mat_name,ambient,diffusion,specular,shiny,map_file

    if filename == 'pillow.obj':
        result1 = []
        i = 0
        while i < (len(result)-4):
            result1.append(result[i])
            result1.append(result[i+1])
            result1.append(result[i+2])
            result1.append(result[i+2])
            result1.append(result[i+3])
            result1.append(result[i])
            i += 4
        result = result1
            
    return vbo.VBO( array(result, 'f') ), len(result), len(result[0]) * 4  # Returning data structures containing read data

(objBuffer, faces, size) = obj_parser('kia.obj')
(pillowBuffer, faces1, size1) = obj_parser('pillow.obj')

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

def DrawObject(buffer,len, size, id):          # Object (car) drawing function
    buffer.bind()
    
    if size == 12:
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3,GL_FLOAT,size,buffer)
        glDrawArrays(GL_TRIANGLES,0,len)
        glDisableClientState(GL_NORMAL_ARRAY)
    elif size == 20:
        glBindTexture(GL_TEXTURE_2D, id)
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
        glBindTexture(GL_TEXTURE_2D, id)
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

Screen = (800,600)
Window = glLibWindow(Screen,caption="Environment Mapping and Particle System Together!",multisample=True)
View = glLibView3D((0,0,Screen[0],Screen[1]),45)
View.set_view()

glLibTexturing(True)

ReflectionMapSize = 128
ReflectionMapView = glLibView3D((0,0,ReflectionMapSize,ReflectionMapSize),90)

Object = gluNewQuadric()
gluQuadricTexture(Object,True)

Camera = glLibCamera([0,0,7],[0,0,0])

import cubeobj
dlBox = cubeobj.get_list()

def DrawSphere(step,pos,size):
    glPushMatrix()
    glTranslatef(*pos)
    gluSphere(Object,size,step,step)
    glPopMatrix()

cubefaces = [GL_TEXTURE_CUBE_MAP_POSITIVE_X,
             GL_TEXTURE_CUBE_MAP_NEGATIVE_X,
             GL_TEXTURE_CUBE_MAP_POSITIVE_Y,
             GL_TEXTURE_CUBE_MAP_NEGATIVE_Y,
             GL_TEXTURE_CUBE_MAP_POSITIVE_Z,
             GL_TEXTURE_CUBE_MAP_NEGATIVE_Z]

def InitGraphics(Width, Height):
    glEnable(GL_DEPTH_TEST)
    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)

    glClearColor(0.5,0.5,0.5,1.0)
    
    global shader, texshader, imageID, ambient, diffusion, shiny, specular, wall_image, wall_buffer, broccolishader, imageID1
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
    shaders.glUseProgram(0)
    

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
    spot_light_direction = [0.0, 1.0, 0.0, 0.0]

    
    glLightf(GL_LIGHT1, GL_SPOT_CUTOFF, 90.0);
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
    
    imageID = loadImage(map_file)
    imageID1 = loadImage(map_file1)
    print imageID, imageID1

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
    
def ReSizeGLScene(Width, Height):
    if Height == 0:                        # Prevent A Divide By Zero If The Window Is Too Small
        Height = 1

    glViewport(0, 0, Width, Height)        # Reset The Current Viewport And Perspective Transformation
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(Width)/float(Height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    
def saveFrame(tempval):
    screenshot = glReadPixels( 0,0, 800, 600, GL_RGBA, GL_UNSIGNED_BYTE)
    im = Image.frombuffer("RGBA", (800,600), screenshot, "raw", "RGBA", 0, 0)
    strng = 'img00'+str(tempval)+'.ppm'
    im.save(strng)

counter = 0
zoom_value = -50.0
ang = 0.0

zoom_value1 = -50.0
ang1 = 0.0
bonus = 1

texture_zoom = 0.0
texture_zoom_dir = 1.0
    
def DrawSphereNew(radius,color): 
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
    
def RenderToTextureData():
    x,y,width,height = glGetIntegerv(GL_VIEWPORT)
    glPixelStorei(GL_PACK_ALIGNMENT, 4)
    glPixelStorei(GL_PACK_ROW_LENGTH, 0)
    glPixelStorei(GL_PACK_SKIP_ROWS, 0)
    glPixelStorei(GL_PACK_SKIP_PIXELS, 0)
    data = glReadPixels(0,0,width,height,GL_RGB,GL_UNSIGNED_BYTE)
    if type(data) != type(""):
        data = data.tostring()
    return data
def UpdateCubeMaps(pos):
    x,y,z=pos
    ReflectionMapView.set_view()
    for i in xrange(0,6,1):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        if   i == 0: gluLookAt(x,y,z, 1, 0, 0,0,-1,0)
        elif i == 1: gluLookAt(x,y,z,-1, 0, 0,0,-1,0)
        elif i == 2: gluLookAt(x,y,z, 0, 1, 0,0,0,1)
        elif i == 3: gluLookAt(x,y,z, 0,-1, 0,0,0,-1)
        elif i == 4: gluLookAt(x,y,z, 0, 0, 1,0,-1,0)
        elif i == 5: gluLookAt(x,y,z, 0, 0,-1,0,-1,0)
        DrawReflectees()
        glEnable(GL_TEXTURE_CUBE_MAP)
        glTexImage2D(cubefaces[i],0,GL_RGB,ReflectionMapSize,ReflectionMapSize,0,GL_RGB,GL_UNSIGNED_BYTE,RenderToTextureData())
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glDisable(GL_TEXTURE_CUBE_MAP)
def DrawReflectees():
    glCallList(dlBox)
ReflectorPos = [0,0,0]
def DrawReflectors():
    glEnable(GL_TEXTURE_CUBE_MAP)
    glEnable(GL_TEXTURE_GEN_S)
    glEnable(GL_TEXTURE_GEN_T)
    glEnable(GL_TEXTURE_GEN_R)
    glTexGeni(GL_S, GL_TEXTURE_GEN_MODE, GL_REFLECTION_MAP)
    glTexGeni(GL_T, GL_TEXTURE_GEN_MODE, GL_REFLECTION_MAP)
    glTexGeni(GL_R, GL_TEXTURE_GEN_MODE, GL_REFLECTION_MAP)

    view = glGetFloatv(GL_MODELVIEW_MATRIX)
    view = [[view[0][0],view[0][1],view[0][2]],
            [view[1][0],view[1][1],view[1][2]],
            [view[2][0],view[2][1],view[2][2]]]
    viewinv = invert(view)
    texmat = [[viewinv[0][0],viewinv[0][1],viewinv[0][2],0],
              [viewinv[1][0],viewinv[1][1],viewinv[1][2],0],
              [viewinv[2][0],viewinv[2][1],viewinv[2][2],0],
              [            0,            0,            0,1]]
    glMatrixMode(GL_TEXTURE)
    glPushMatrix()
    glMultMatrixf(texmat)
    glMatrixMode(GL_MODELVIEW)
    
    DrawSphere(40,ReflectorPos,0.75)
##    glPushMatrix()
##    glTranslatef(*ReflectorPos)
##    glutSolidTeapot(1.0)
##    glPopMatrix()

    glMatrixMode(GL_TEXTURE)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    
    glDisable(GL_TEXTURE_GEN_S)
    glDisable(GL_TEXTURE_GEN_T)
    glDisable(GL_TEXTURE_GEN_R)
    glDisable(GL_TEXTURE_CUBE_MAP)

inx = 0
pos_x = [-3.0,3.0]
pos_y = [-3.0,3.0]

class Ball(object):
    def __init__(self, pos_x, pos_y, pos_z, radius, color, inx, acc_x, acc_y):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.pos_z = pos_z
        self.acc_x = acc_x
        self.acc_y = acc_y
        self.radius = radius
        self.color = color
        self.inx = inx
        
    def update(self):
        if self.pos_x < -6.0 or self.pos_y < -6.0 or self.pos_x > 6.0 or self.pos_y > 6.0:
            self.acc_x = -self.acc_x
            self.acc_y = -self.acc_y
        self.pos_x += self.acc_x
        self.pos_y += self.acc_y
        #print self.acc_x, self.acc_y, self.pos_x, self.pos_y
        self.radius -= 0.002
        
    def check_radius(self):
        return self.radius < 0
    
    def return_inx(self):
        return self.inx
    
    def setter(self, pos_x, pos_y, rad, acc_x, acc_y, inx, color):
        self.radius = rad
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.acc_x = acc_x
        self.acc_y = acc_y
        self.color = color
        self.inx = inx
        
    def Draw(self):
        glTranslatef(self.pos_x, self.pos_y, self.pos_z)
        DrawSphereNew(self.radius, self.color)

balls = []

for i in range(100):
    balls.append(Ball(pos_x[0],pos_y[0],-10.0,0.5,color[inx], 0, random.uniform(-0.05,0.05),random.uniform(-0.05,0.05)))


def Draw():
    start = time.time()
    global balls,inx, bonus, imageID1,counter, shader,zoom_value, zoom_value1, button_down, ang, ang1, size, texshader, texture_zoom, texture_zoom_dir, wall_buffer, wall_image, imageID
    UpdateCubeMaps(ReflectorPos)
    View.set_view()
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    Camera.set_camera()
    
    glDisable(GL_LIGHT0)
    glDisable(GL_LIGHT1)
    
    DrawReflectors()
    DrawReflectees()
    
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    
    shaders.glUseProgram(texshader)

    glPushMatrix()
    glTranslatef(6.0,6.0,-20.0)
    glScalef(3.0, 3.0, 1.0)
    DrawWall(wall_buffer, wall_image)
    glPopMatrix()
    
    shaders.glUseProgram(0)
    
    shaders.glUseProgram(shader)
    
    if len(specular)>0:
        #print 'Here'
        material_specular = [specular[0][0], specular[0][1], specular[0][2], 1.0]
        #material_specular = [1.0,1.0,1.0, 1.0]
        glMaterialfv(GL_FRONT, GL_SPECULAR, material_specular)
    if shiny > -20.0:
        #print 'Shiny'
        material_shininess = [ shiny ]
        glMaterialfv(GL_FRONT, GL_SHININESS, material_shininess)
    if len(ambient) > 0:
        material_ambient = [ambient[0][0], ambient[0][1], ambient[0][2], 1.0]
        #material_ambient = [1.0, 1.0, 1.0, 1.0]
        glMaterialfv(GL_FRONT, GL_AMBIENT, material_ambient)
    if len(diffusion) > 0:
        material_diffuse = [diffusion[0][0], diffusion[0][1], diffusion[0][2], 1.0]
        #material_diffuse = [1.0,1.0,1.0, 1.0]
        glMaterialfv(GL_FRONT, GL_DIFFUSE, material_diffuse)
    
    glPushMatrix()
    glTranslatef(-15.0,-5.0,zoom_value+12.0)
    glRotatef(ang,0.0,1.0,0.0)
    #glScalef(5.0,-2.0,1.0)
    DrawObject(objBuffer, faces, size, imageID)
    glPopMatrix()

    
    if len(specular)>0:
            #print 'Here'
            #material_specular = [specular[0][0], specular[0][1], specular[0][2], 1.0]
        material_specular = [1.0,1.0,1.0, 1.0]
        glMaterialfv(GL_FRONT, GL_SPECULAR, material_specular)
    if shiny > -20.0:
            #print 'Shiny'
        material_shininess = [ 10.0 ]
        glMaterialfv(GL_FRONT, GL_SHININESS, material_shininess)
    if len(ambient) > 0:
            #material_ambient = [ambient[0][0], ambient[0][1], ambient[0][2], 1.0]
        material_ambient = [1.0, 1.0, 1.0, 1.0]
        glMaterialfv(GL_FRONT, GL_AMBIENT, material_ambient)
    if len(diffusion) > 0:
            #material_diffuse = [diffusion[0][0], diffusion[0][1], diffusion[0][2], 1.0]
        material_diffuse = [1.0,1.0,1.0, 1.0]
        glMaterialfv(GL_FRONT, GL_DIFFUSE, material_diffuse)
        
    glPushMatrix()
    glScalef(0.3,0.3,1.0)
    glTranslatef(25.0,-30.0,zoom_value1+12)
    glRotatef(ang1,0.0,1.0,0.0)
    #glScalef(5.0,-2.0,1.0)
    DrawObject(pillowBuffer, faces1, size1, imageID1)
    glPopMatrix()
        
    shaders.glUseProgram(0)
    
    if bonus ==1 :
            for i in range(len(balls)):
                balls[i].Draw()
                balls[i].update()
                if balls[i].check_radius():
                    temp = balls[i].return_inx()
                    if temp < 4:
                        temp += 1
                        if temp == 1:
                            tx = pos_x[1]
                            ty = pos_y[0]
                        elif temp == 2:
                            tx = pos_x[0]
                            ty = pos_y[1]
                        elif temp == 3:
                            tx = pos_x[1]
                            ty = pos_y[1]
                        elif temp == 4:
                            tx = pos_x[1] + 1.0
                            ty = pos_y[1] - 1.0
                    else:
                        temp = 0
                        tx = pos_x[0]
                        ty = pos_y[0]
                    balls[i].setter(tx,ty,0.5,random.uniform(-0.05,0.05),random.uniform(-0.05,0.05),temp,color[temp])
            
    pygame.display.flip()
    
    counter += 1
    #varr2 = time.time(

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
    
camerarot = [0,0]
def TakeScreenshot():
    data = RenderToTextureData()
##    surface = pygame.image.fromstring(data,(ReflectionMapSize,ReflectionMapSize),'RGB',1)
    surface = pygame.image.fromstring(data,(Screen[0],Screen[1]),'RGB',1)
    surface = pygame.transform.smoothscale(surface,(Screen[0]/2,Screen[1]/2))
    counter = 1
    while True:
        try:pygame.image.load('00' + str(counter)+".png");counter+=1;continue
        except:pass
        pygame.image.save(surface,'00' + str(counter)+".png")
        break
radius = 7
spot_light = 1
point_light = 1
def GetInput():
    global camerarot,radius, zoom_value, shader, spot_light, point_light, tempval, spot_ang, zoom_value1, ang1, ang, bonus
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_q):
            pygame.quit(); sys.exit()
        
        if event.type == KEYDOWN:
            if event.key == K_i:
                zoom_value += 1
                
            elif event.key == K_o:
                if zoom_value > -100.0:
                    zoom_value -= 1
                    
            elif event.key == K_w:
                zoom_value1 += 1
                
            elif event.key == K_r:
                ang += 1.0
                
            elif event.key == K_t:
                ang1 += 1.0
                
            elif event.key == K_b:
                bonus = -bonus
                
            elif event.key == K_x:
                if zoom_value1 > -100.0:
                    zoom_value1 -= 1
                    
            elif event.key == K_s:
                shaders.glUseProgram(shader)
                loc = glGetUniformLocation(shader, "sEnable")
                if spot_light == 1:
                    spot_light = 0
                else:
                    spot_light = 1
                glUniform1i(loc, spot_light)
                shaders.glUseProgram(0)
                
            elif event.key == K_p:
                shaders.glUseProgram(shader)
                loc = glGetUniformLocation(shader, "pEnable")
                if point_light == 1:
                    point_light = 0
                else:
                    point_light = 1
                glUniform1i(loc, point_light)
                shaders.glUseProgram(0)
            
            elif event.key == K_f:
                TakeScreenshot()
                
            elif event.key == K_a:
                radius -= 1
                
            elif event.key == K_d:
                radius += 1
                
    mpress = pygame.mouse.get_pressed()
    mrel = pygame.mouse.get_rel()
    if mpress[0]:
        camerarot[1] += mrel[0]
        camerarot[0] -= mrel[1]
    pos = [radius*cos(radians(camerarot[1]+90))*cos(radians(camerarot[0])),
           radius*sin(radians(camerarot[0])),
           radius*sin(radians(camerarot[1]+90))*cos(radians(camerarot[0]))]
    Camera.set_target_pos(pos)
def Update():
    Camera.update()
def main():
    InitGraphics(800,600)
    while True:
        GetInput()
        Update()
        Draw()
print '\nAssignment 7 with mesh objects, animated wall, environment mapping and particle system (bonus)'
print 'Hold the left click button and drag the mouse around to change the perspective of the reflecting sphere'
print "Hit 'a' or 'A' to zoom in to the whole scene (increase reflecting sphere radius)"
print "Hit 'd' or 'D' to zoom out of the whole scene (increase reflecting sphere radius)"
print "Hit 'i' or 'I' to zoom in car"
print "Hit 'o' or 'O' to zoom out car"
print "Hit 'w' or 'W' to zoom in pillow"
print "Hit 'x' or 'X' to zoom out pillow"
print "Hit 's' or 'S' to turn the spot light source on/off"
print "Hit 'p' or 'P' to turn the point light source on/off"
print "Hit 'f' or 'F' to save current frame into .png file"
print "Hit 'r' or 'R' to rotate the car in anti clockwise direction"
print "Hit 't' or 'T' to rotate the pillow in anti clockwise direction"
print "Press 'b' or 'B' to toggle between generating particle system drawing on/off (Bonus)"
print "Hit 'q' or 'Q' key to quit."
if __name__ == '__main__': main()
