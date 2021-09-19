# **********************************************************************
# PUCRS/FACIN
# COMPUTAÇÃO GRÁFICA
#
# Teste de colisão em OpenGL
#
# Marcio Sarroglia Pinho
# pinho@inf.pucrs.br
# **********************************************************************
from OpenGL.GL import glClearColor, glMatrixMode, glLoadIdentity, glOrtho, glColor3f, GL_COLOR_BUFFER_BIT, GL_MODELVIEW, GL_PROJECTION, glClear, glLineWidth, glViewport, GL_POLYGON, glVertex2f, glBegin, glEnd, GL_LINES
from OpenGL.GLUT import glutCreateWindow, glutDisplayFunc, glutIdleFunc, glutInit, glutInitDisplayMode, glutInitWindowPosition, glutInitWindowSize, glutKeyboardFunc, glutMainLoop, glutPostRedisplay, glutReshapeFunc, glutSpecialFunc, glutSwapBuffers, GLUT_KEY_DOWN, GLUT_KEY_LEFT, GLUT_KEY_RIGHT, GLUT_KEY_UP, GLUT_RGBA
from typing import List, Tuple, Union
import os
import sys
import time

from bounding_box import BoundingBox
from Linha import Linha
from Ponto import Ponto
from spatial_subdivision import Matrix


N_LINHAS = 20
MAX_X = 100

ContadorInt = 0
ContChamadas = 0

linhas = []

bounding_boxes: List[BoundingBox] = []  # Bounding boxes list, global
subdivision_matrix: Matrix  # Spatial subdivision matrix, global

# from random import seed
# seed(140)  # Debugging purposes only


# ********************************************************************** */
#                                                                        */
#  Calcula a interseccao entre 2 retas (no plano "XY" Z = 0)             */
#                                                                        */
# k : ponto inicial da reta 1                                            */
# l : ponto final da reta 1                                              */
# m : ponto inicial da reta 2                                            */
# n : ponto final da reta 2                                              */
#                                                                        */
# Retorna:                                                               */
# 0, se não houver interseccao ou 1, caso haja                           */
# int, valor do parâmetro no ponto de interseção (sobre a reta KL)       */
# int, valor do parâmetro no ponto de interseção (sobre a reta MN)       */
#                                                                        */
# ********************************************************************** */
def intersec2d(k: Ponto, l: Ponto, m: Ponto, n: Ponto) -> Tuple[int, Union[float, None], Union[float, None]]:
    det = (n.x - m.x) * (l.y - k.y)  -  (n.y - m.y) * (l.x - k.x)

    if (det == 0.0):
        return 0, None, None # não há intersecção

    s = ((n.x - m.x) * (m.y - k.y) - (n.y - m.y) * (m.x - k.x))/ det
    t = ((l.x - k.x) * (m.y - k.y) - (l.y - k.y) * (m.x - k.x))/ det

    return 1, s, t # há intersecção


# **********************************************************************
# HaInterseccao(k: Ponto, l: Ponto, m: Ponto, n: Ponto)
# Detecta interseccao entre os pontos
#
# **********************************************************************
def HaInterseccao(k: Ponto, l: Ponto, m: Ponto, n: Ponto) -> bool:
    ret, s, t = intersec2d(k,  l,  m,  n)

    if not ret or not s or not t:
        return False

    return s >= 0.0 and s <= 1.0 and  t >=0.0 and t <= 1.0


def draw_bounding_boxes():
    """
    Draw all bounding boxes
    """

    glColor3f(.7, .7, .7)
    for box in bounding_boxes:
        box.draw()


def draw_spatial_subdivision():
    """
    Draw and colour cells

    First, fill with any colour all cells which don't have
    any lines.
    Second, draw the matrix grid.
    """

    # Fill cells
    glColor3f(.5, .5, .5)
    for x in range(subdivision_matrix.size_x):
        for y in range(subdivision_matrix.size_y):
            cell = subdivision_matrix.matrix[x][y]
            if len(cell.contained_lines) == 0:
                x1 = x * subdivision_matrix.cell_size.x
                y1 = y * subdivision_matrix.cell_size.y
                x2 = x1 + subdivision_matrix.cell_size.x
                y2 = y1 + subdivision_matrix.cell_size.y

                glBegin(GL_POLYGON)
                glVertex2f(x1, y1)
                glVertex2f(x1, y2)
                glVertex2f(x2, y2)
                glVertex2f(x2, y1)
                glEnd()

    # Draw grid
    glColor3f(.2, .2, 0)
    for x in range(subdivision_matrix.size_x + 1):
        glBegin(GL_LINES)
        glVertex2f(x * subdivision_matrix.cell_size.x, 0)
        glVertex2f(x * subdivision_matrix.cell_size.x, MAX_X)
        glEnd()
    for y in range(subdivision_matrix.size_y + 1):
        glBegin(GL_LINES)
        glVertex2f(0, y * subdivision_matrix.cell_size.y)
        glVertex2f(MAX_X, y * subdivision_matrix.cell_size.y)
        glEnd()


def check_collision_aabb(box_a: BoundingBox, box_b: BoundingBox) -> bool:
    """
    Check for collisions between two bounding boxes

    Args:
        box_a (BoundingBox): Bounding box A
        box_b (BoundingBox): Bounding box B

    Returns:
        bool: False if there's no collision, True otherwise
    """

    if abs(box_a.center[0] - box_b.center[0]) > box_a.half_length[0] + box_b.half_length[0] or \
        abs(box_a.center[1] - box_b.center[1]) > box_a.half_length[1] + box_b.half_length[1]:
        return False
    return True


# !!! -------------- Algorithm selection section -------------- !!!

def algo_init_aabb(line: Linha, index: int):
    """
    Initialize the AABB structures

    Args:
        line (Linha):
            Line whose bounding box is generated and appended to the
            global `bounding_boxes` list.
        index (int): Not used, added for compatibility
    """

    global bounding_boxes
    bounding_boxes.append(BoundingBox(line))


def calculate_intersection_aabb():
    """
    Calculate the intersection between all bounding boxes

    Iterates through all bounding boxes skipping those that
    have already been checked (`bounding_boxes[index_a + 1:]`).
    """

    global ContChamadas, ContadorInt, bounding_boxes
    glColor3f(1, 0, 0)
    for index_a, box_a in enumerate(bounding_boxes):
        for box_b in bounding_boxes[index_a + 1:]:
            if check_collision_aabb(box_a, box_b):
                ContChamadas += 1
                ContadorInt += 1
                box_a._line.desenhaLinha()
                box_b._line.desenhaLinha()


def use_aabb():
    """
    Use AABB as the collision detection algorithm

    Setup the script to run using the AABB collision algorithm.
    Set the global `algo_init`, `algo_draw` and `algo_calculate_intersection`
    functions to the specialized, local, AABB-related functions.
    """

    global algo_init, algo_draw, algo_calculate_intersection

    algo_init = algo_init_aabb
    algo_draw = draw_bounding_boxes
    algo_calculate_intersection = calculate_intersection_aabb


def algo_init_ss(line: Linha, index: int):
    """
    Initialize the SS structures

    Registers `line` and its index on the global subdivision matrix.

    Args:
        line (Linha):
            Used to calculate the spanned cells' coordinates only
        index (int):
            Line index to be registered on the necessary cells
    """

    global subdivision_matrix
    subdivision_matrix.register_line_on_cells(line, index)


def calculate_intersection_ss():
    """
    Calculate the intersection between lines using the subdivision matrix

    Iterates through all lines on the global `linhas` array and calculates
    each line's possible intersection set. A set `Set[int]` is used for its
    guarenteed uniqueness (an entry can be added only once).
    """

    global ContChamadas, ContadorInt, linhas, subdivision_matrix
    glColor3f(1, 0, 0)
    for index_a, linha_a in enumerate(linhas):
        candidate_set = subdivision_matrix.generate_candidates(index_a, linhas)

        for index_b, linha_b in enumerate(linhas):
            if index_b in candidate_set:
                ContChamadas += 1
                if HaInterseccao(Ponto(linha_a.x1, linha_a.y1), Ponto(linha_a.x2, linha_a.y2), Ponto(linha_b.x1, linha_b.y1), Ponto(linha_b.x2, linha_b.y2)):
                    ContadorInt += 1
                    linha_a.desenhaLinha()
                    linha_b.desenhaLinha()


def use_ss():
    """
    Use spatial subdivision (S.S.) as the collision detection algorithm

    Setup the script to run using the S.S. collision algorithm.
    Set the global `algo_init`, `algo_draw` and `algo_calculate_intersection`
    functions to the specialized, local, S.S.-related functions.
    """

    global algo_init, algo_draw, algo_calculate_intersection

    algo_init = algo_init_ss
    algo_draw = draw_spatial_subdivision
    algo_calculate_intersection = calculate_intersection_ss


def algo_init_original(line: Linha, index: int):
    """
    Not used, added for compatibility

    Args:
        line (Linha): Not used, added for compatibility
        index (int): Not used, added for compatibility
    """

    pass


def calculate_intersection_original():
    """
    Calculate the intersection between all lines

    Iterates through all lines and calculate each line's intersection
    with every other line (including those that have already been
    visited). This is the original implementation.
    """

    global ContChamadas, ContadorInt, linhas
    # Original implementation
    glColor3f(1, 0, 0)
    PA, PB, PC, PD = Ponto(), Ponto(), Ponto(), Ponto()
    for i in range(N_LINHAS):
        PA.set(linhas[i].x1, linhas[i].y1)
        PB.set(linhas[i].x2, linhas[i].y2)
        for j in range(N_LINHAS):
            PC.set(linhas[j].x1, linhas[j].y1)
            PD.set(linhas[j].x2, linhas[j].y2)
            ContChamadas += 1
            if HaInterseccao(PA, PB, PC, PD):
                ContadorInt += 1
                linhas[i].desenhaLinha()
                linhas[j].desenhaLinha()


def use_original():
    """
    Use brute force as the collision detection algorithm

    Setup the script to run using a brute force collision algorithm.
    Set the global `algo_init`, `algo_draw` and `algo_calculate_intersection`
    functions to the specialized, local, brute force-related functions.
    """

    global algo_init, algo_draw, algo_calculate_intersection

    algo_init = algo_init_original
    algo_draw = lambda: None
    algo_calculate_intersection = calculate_intersection_original


def algo_init_original2(line: Linha, index: int):
    """
    Not used, added for compatibility

    Args:
        line (Linha): Not used, added for compatibility
        index (int): Not used, added for compatibility
    """

    pass


def calculate_intersection_original2():
    """
    Calculate the intersection between all lines

    Iterates through all lines and calculate each line's intersection
    with every other line (excluding those that have already been
    visited).
    """

    global ContChamadas, ContadorInt, linhas
    # Original implementation (improved)
    glColor3f(1, 0, 0)
    for index_a, linha_a in enumerate(linhas):  # Nova implementação mais otimizada
        for linha_b in linhas[index_a:]:
            ContChamadas += 1

            if HaInterseccao(Ponto(linha_a.x1, linha_a.y1), Ponto(linha_a.x2, linha_a.y2), Ponto(linha_b.x1, linha_b.y1), Ponto(linha_b.x2, linha_b.y2)):
                ContadorInt += 1
                linha_a.desenhaLinha()
                linha_b.desenhaLinha()


def use_original2():
    """
    Use brute force (improved) as the collision detection algorithm

    Setup the script to run using a brute force collision algorithm.
    Set the global `algo_init`, `algo_draw` and `algo_calculate_intersection`
    functions to the specialized, local, brute force-related functions.
    """

    global algo_init, algo_draw, algo_calculate_intersection

    algo_init = algo_init_original2
    algo_draw = lambda: None
    algo_calculate_intersection = calculate_intersection_original2


# Dictionary that defines the algorithm that will be used during execution
possible_intersection_algorithms = {
    'aabb': use_aabb,
    'ss': use_ss,
    'original': use_original,
    'original2': use_original2,
}

cell_size = (16, 16)  # Default cell size (used on the SS algorithm)
if len(sys.argv) > 1:  # If an algorithm code was passed via CLI...
    algo_ = sys.argv[1]
    if not algo_ or not algo_.lower() in possible_intersection_algorithms:
        algo_ = 'aabb'

    if algo_ == 'ss':
        # Try to get size from CLI input
        # Size format: x,y
        try:
            cell_size = tuple(map(lambda s: int(s), sys.argv[2].split(',')[:2]))
            print(cell_size)
        except:
            cell_size = (16, 16)
else:  # Fail, need to pass algorithm
    algo_init = lambda: None
    algo_draw = lambda: None
    algo_calculate_intersection = lambda: None
    print('Please provide a supported algorithm from the list:', ', '.join(possible_intersection_algorithms.keys()))
    exit(1)

algo_init = lambda: None  # Reset generic functions
algo_draw = lambda: None  # Reset generic functions
algo_calculate_intersection = lambda: None  # Reset generic functions

possible_intersection_algorithms[algo_.lower()]()  # Setup algorithm variables and callables


# **********************************************************************
#  init()
#  Inicializa os parâmetros globais de OpenGL
#/ **********************************************************************
def init():
    global linhas, bounding_boxes, subdivision_matrix, cell_size

    # Define a cor do fundo da tela (PRETO)
    glClearColor(0, 0, 0, 1.0)

    linhas = [Linha() for _ in range(N_LINHAS)]
    bounding_boxes = []
    subdivision_matrix = Matrix((MAX_X, MAX_X), (cell_size[0], cell_size[1]))

    for index, linha in enumerate(linhas):
        linha.geraLinha(MAX_X, 10)
        algo_init(linha, index)  # Call generic init() function for any algorithm


# **********************************************************************
#  reshape( w: int, h: int )
#  trata o redimensionamento da janela OpenGL
#
# **********************************************************************
def reshape(w: int, h: int):
    # Reseta coordenadas do sistema antes the modificala
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    # Define os limites lógicos da área OpenGL dentro da Janela
    glOrtho(0, 100, 0, 100, 0, 1)

    # Define a área a ser ocupada pela área OpenGL dentro da Janela
    glViewport(0, 0, w, h)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


# **********************************************************************
# DesenhaLinhas()
# Desenha as linha na tela
#
# **********************************************************************
def DesenhaLinhas():
    glColor3f(0, 1, 0)
    for linha in linhas:
        linha.desenhaLinha()


# **********************************************************************
# DesenhaCenario()
# Desenha o cenario
#
# **********************************************************************
def DesenhaCenario():
    global ContChamadas, ContadorInt
    ContChamadas, ContadorInt = 0, 0
    # Desenha as linhas do cenário
    glLineWidth(2)

    algo_calculate_intersection()  # Call generic calculate_intersection() function


# **********************************************************************
# display()
# Funcao que exibe os desenhos na tela
#
# **********************************************************************
def display():
    # Limpa a tela com a cor de fundo
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    algo_draw()  # Call generic draw() function

    DesenhaLinhas()
    DesenhaCenario()

    glutSwapBuffers()


# **********************************************************************
# animate()
# Funcao chama enquanto o programa esta ocioso
# Calcula o FPS e numero de interseccao detectadas, junto com outras informacoes
#
# **********************************************************************
# Variaveis Globais
nFrames, TempoTotal, AccumDeltaT = 0, 0, 0
oldTime = time.time()


def animate():
    global nFrames, TempoTotal, AccumDeltaT, oldTime

    nowTime = time.time()
    dt = nowTime - oldTime
    oldTime = nowTime

    AccumDeltaT += dt
    TempoTotal += dt
    nFrames += 1

    if AccumDeltaT > 1.0/60:  # fixa a atualização da tela em 60Hz
        AccumDeltaT = 0
        glutPostRedisplay()

    if TempoTotal > 5.0:
        print(f'Tempo Acumulado: {TempoTotal} segundos.')
        print(f'Nros de Frames sem desenho: {int(nFrames)}')
        print(f'FPS(sem desenho): {int(nFrames/TempoTotal)}')

        TempoTotal = 0
        nFrames = 0

        print(f'Contador de Intersecoes Existentes: {ContadorInt}')
        print(f'Contador de Chamadas: {ContChamadas}')


# **********************************************************************
#  keyboard ( key: int, x: int, y: int )
#
# **********************************************************************
ESCAPE = b'\x1b'
def keyboard(*args):
    #print (args)
    # If escape is pressed, kill everything.

    if args[0] == ESCAPE:   # Termina o programa qdo
        os._exit(0)         # a tecla ESC for pressionada

    if args[0] == b' ':
        init()

    # Força o redesenho da tela
    glutPostRedisplay()


# **********************************************************************
#  arrow_keys ( a_keys: int, x: int, y: int )
#
# **********************************************************************
def arrow_keys(a_keys: int, x: int, y: int):
    if a_keys == GLUT_KEY_UP:         # Se pressionar UP
        pass
    if a_keys == GLUT_KEY_DOWN:       # Se pressionar DOWN
        pass
    if a_keys == GLUT_KEY_LEFT:       # Se pressionar LEFT
        pass
    if a_keys == GLUT_KEY_RIGHT:      # Se pressionar RIGHT
        pass

    glutPostRedisplay()


def mouse(button: int, state: int, x: int, y: int):
    glutPostRedisplay()


def mouseMove(x: int, y: int):
    glutPostRedisplay()


if __name__ == '__main__':
    # ***********************************************************************************
    # Programa Principal
    # ***********************************************************************************

    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA)

    # Define o tamanho inicial da janela grafica do programa
    glutInitWindowSize(650, 500)
    # Cria a janela na tela, definindo o nome da
    # que aparecera na barra de título da janela.
    glutInitWindowPosition(100, 100)
    wind = glutCreateWindow("Algorimos de Cálculo de Colisão")

    # executa algumas inicializações
    init()

    # Define que o tratador de evento para
    # o redesenho da tela. A funcao "display"
    # será chamada automaticamente quando
    # for necessário redesenhar a janela
    glutDisplayFunc(display)
    glutIdleFunc(animate)

    # o redimensionamento da janela. A funcao "reshape"
    # Define que o tratador de evento para
    # será chamada automaticamente quando
    # o usuário alterar o tamanho da janela
    glutReshapeFunc(reshape)

    # Define que o tratador de evento para
    # as teclas. A funcao "keyboard"
    # será chamada automaticamente sempre
    # o usuário pressionar uma tecla comum
    glutKeyboardFunc(keyboard)

    # Define que o tratador de evento para
    # as teclas especiais(F1, F2,... ALT-A,
    # ALT-B, Teclas de Seta, ...).
    # A funcao "arrow_keys" será chamada
    # automaticamente sempre o usuário
    # pressionar uma tecla especial
    glutSpecialFunc(arrow_keys)

    #glutMouseFunc(mouse)
    #glutMotionFunc(mouseMove)

    try:
        # inicia o tratamento dos eventos
        glutMainLoop()
    except SystemExit:
        pass
