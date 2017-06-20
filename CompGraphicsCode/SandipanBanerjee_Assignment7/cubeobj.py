from OpenGL.GL import *
from OpenGLLibrary import *
EnvironmentBox = [0,0,0,0,0,0]
filts = ["filter","mipmap","mipmap filter"]
EnvironmentBox[0] = glLibTexture('yneg.jpg',filters=filts)
EnvironmentBox[1] = glLibTexture('ypos.jpg',filters=filts)
EnvironmentBox[2] = glLibTexture('zneg.jpg',filters=filts)
EnvironmentBox[3] = glLibTexture('zpos.jpg',filters=filts)
EnvironmentBox[4] = glLibTexture('xneg.jpg',filters=filts)
EnvironmentBox[5] = glLibTexture('xpos.jpg',filters=filts)

box = glGenLists(1)
glNewList(box, GL_COMPILE)
iBoxSize = 500
glBindTexture(GL_TEXTURE_2D,EnvironmentBox[2])
glBegin(GL_QUADS)
# Front Face
glNormal3f( 0.0, 0.0, -1.0)
glTexCoord2f(1.0, 1.0); glVertex3f(-iBoxSize, -iBoxSize,  iBoxSize)
glTexCoord2f(0.0, 1.0); glVertex3f( iBoxSize, -iBoxSize,  iBoxSize)
glTexCoord2f(0.0, 0.0); glVertex3f( iBoxSize,  iBoxSize,  iBoxSize)
glTexCoord2f(1.0, 0.0); glVertex3f(-iBoxSize,  iBoxSize,  iBoxSize)
glEnd()
glBindTexture(GL_TEXTURE_2D,EnvironmentBox[3])
glBegin(GL_QUADS)
# Back Face
glNormal3f( 0.0, 0.0, 1.0)
glTexCoord2f(1.0, 0.0); glVertex3f( iBoxSize,  iBoxSize, -iBoxSize)
glTexCoord2f(1.0, 1.0); glVertex3f( iBoxSize, -iBoxSize, -iBoxSize)
glTexCoord2f(0.0, 1.0); glVertex3f(-iBoxSize, -iBoxSize, -iBoxSize)
glTexCoord2f(0.0, 0.0); glVertex3f(-iBoxSize,  iBoxSize, -iBoxSize)
glEnd()
glBindTexture(GL_TEXTURE_2D,EnvironmentBox[1])
glBegin(GL_QUADS)
# Top Face
glNormal3f( 0.0, -1.0, 0.0)
glTexCoord2f(0.0, 1.0); glVertex3f(-iBoxSize,  iBoxSize, -iBoxSize)
glTexCoord2f(0.0, 0.0); glVertex3f(-iBoxSize,  iBoxSize,  iBoxSize)
glTexCoord2f(1.0, 0.0); glVertex3f( iBoxSize,  iBoxSize,  iBoxSize)
glTexCoord2f(1.0, 1.0); glVertex3f( iBoxSize,  iBoxSize, -iBoxSize)
glEnd()
glBindTexture(GL_TEXTURE_2D,EnvironmentBox[0])
glBegin(GL_QUADS)
# Bottom Face
glNormal3f( 0.0, 1.0, 0.0)
glTexCoord2f(1.0, 1.0); glVertex3f( iBoxSize, -iBoxSize,  iBoxSize)
glTexCoord2f(0.0, 1.0); glVertex3f(-iBoxSize, -iBoxSize,  iBoxSize)
glTexCoord2f(0.0, 0.0); glVertex3f(-iBoxSize, -iBoxSize, -iBoxSize)
glTexCoord2f(1.0, 0.0); glVertex3f( iBoxSize, -iBoxSize, -iBoxSize)
glEnd()
glBindTexture(GL_TEXTURE_2D,EnvironmentBox[5])
glBegin(GL_QUADS)
# Right face
glNormal3f(-1.0, 0.0, 0.0)
glTexCoord2f(1.0, 0.0); glVertex3f( iBoxSize,  iBoxSize,  iBoxSize)
glTexCoord2f(1.0, 1.0); glVertex3f( iBoxSize, -iBoxSize,  iBoxSize)
glTexCoord2f(0.0, 1.0); glVertex3f( iBoxSize, -iBoxSize, -iBoxSize)
glTexCoord2f(0.0, 0.0); glVertex3f( iBoxSize,  iBoxSize, -iBoxSize)
glEnd()
glBindTexture(GL_TEXTURE_2D,EnvironmentBox[4])
glBegin(GL_QUADS)
# Left Face
glNormal3f( 1.0, 0.0, 0.0)
glTexCoord2f(0.0, 0.0); glVertex3f(-iBoxSize,  iBoxSize,  iBoxSize)
glTexCoord2f(1.0, 0.0); glVertex3f(-iBoxSize,  iBoxSize, -iBoxSize)
glTexCoord2f(1.0, 1.0); glVertex3f(-iBoxSize, -iBoxSize, -iBoxSize)
glTexCoord2f(0.0, 1.0); glVertex3f(-iBoxSize, -iBoxSize,  iBoxSize)
glEnd()
glEndList()
def get_list():
    return box
