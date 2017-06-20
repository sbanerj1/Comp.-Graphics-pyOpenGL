from OpenGL.GL import *
from OpenGL.GLU import *
import os
import pygame
from pygame.locals import *
from math import *
pygame.init()
def glLibTexturing(value):
    if value:glEnable(GL_TEXTURE_2D)
    else:glDisable(GL_TEXTURE_2D)
def glLibTexture(surface,filters=[]):
    if type(surface) == type(""):
        surface = pygame.image.load(os.path.join(*surface.split("/"))).convert_alpha()
    data = pygame.image.tostring(surface,"RGBA",True)
    width,height = surface.get_size()
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D,texture)
    #Mag filter
    if "filter" in filters: glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
    else:                   glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST)
    #Min filter
    if "mipmap" in filters:
        if "mipmap blend" in filters:
            if "filter" in filters: mipmap_param = GL_NEAREST_MIPMAP_LINEAR
            else:                   mipmap_param = GL_LINEAR_MIPMAP_LINEAR
        else:
            if "filter" in filters: mipmap_param = GL_NEAREST_MIPMAP_NEAREST
            else:                   mipmap_param = GL_LINEAR_MIPMAP_NEAREST
        glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,mipmap_param)
        glPixelStoref(GL_UNPACK_ALIGNMENT,1)
        gluBuild2DMipmaps(GL_TEXTURE_2D,3,width,height,GL_RGBA,GL_UNSIGNED_BYTE,data)
    else:
        if "filter" in filters: glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)
        else:                   glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,width,height,0,GL_RGBA,GL_UNSIGNED_BYTE,data)
    #Return
    return texture
def glLibSelectTexture(texture):
    glBindTexture(GL_TEXTURE_2D,texture)
