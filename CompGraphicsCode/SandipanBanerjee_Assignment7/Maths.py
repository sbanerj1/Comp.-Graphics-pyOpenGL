def ident(size):
    C = []
    for r in range(0, size):
        C.append([])
        for c in range(0, size):
            if c == r:
                C[r].append(1)
            else:
                C[r].append(0)
    return C
def swapRow(M, i, j):
    B = M[i]
    M[i] = M[j]
    M[j] = B
    return M
def multRow(k, M, row):
    if k == 0: raise MatrixError, "k cannot be equal to zero"
    for j in range(0, len(M[0])):
        M[row][j] *= k
    return M

def multRowAdd(k, M, source, dest):
    if k == 0: raise MatrixError, "k cannot be equal to zero"
    for j in range(0, len(M[0])):
        M[dest][j] += M[source][j] * k
    return M
def augment(M, B):
    for r in range(0, len(M)):
        for s in range(0, len(B[r])):
            M[r].append(B[r][s])
    return M
def rref(M, n = 0):
    if n >= len(M) or n > len(M):
        return M
    col = -1
    for i in range(n, len(M)):
        if M[i][n] <> 0:
            col = i
        if col != -1: break
    if col != n:
        swapRow(M, col, n)
    if M[n][n] != 1:
        #M[n][n] = int(M[n][n] * (1. / M[n][n]))
        multRow(1. / M[n][n], M, n)
    for i in range(0, len(M)):
        if i == n: continue
        if M[i][n] != 0:
            multRowAdd(-M[i][n], M, n, i)
    rref(M, n + 1)
    return M
def invert(A):
    l = len(A)
    A = augment(A, ident(l))
    A = rref(A)
    for i in range(0, l):
        A = delCol(A, 0)
    return A
def delCol(B, j):
    for r in range(0,len(B)):
        B[r].pop(j)
    return B
