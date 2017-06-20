from OpenGL.GL import glColor3f, glColor4f, glEnable, glDisable, GL_COLOR_MATERIAL
def glLibColor(color):
    if   len(color) == 3: glColor3f(color[0]/255.0,color[1]/255.0,color[2]/255.0)
    elif len(color) == 4: glColor4f(color[0]/255.0,color[1]/255.0,color[2]/255.0,color[3]/255.0)
def glLibColorMaterial(value):
    if value:glEnable(GL_COLOR_MATERIAL)
    else:glDisable(GL_COLOR_MATERIAL)
