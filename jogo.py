import pygame
import math
import random

pygame.init()

WIDTH  = 900
HEIGHT = 700
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("F1 Grid Racer")

ZOOM   = 2.0
VIRT_W = int(WIDTH  / ZOOM)
VIRT_H = int(HEIGHT / ZOOM)
virtual = pygame.Surface((VIRT_W, VIRT_H))

clock = pygame.time.Clock()
FPS   = 60

CARRO_W    = 34
CARRO_H    = 17
OBST_W     = 28
OBST_H     = 28

imagem_carro         = pygame.image.load("Carro.png").convert_alpha()
imagem_carro         = pygame.transform.scale(imagem_carro, (CARRO_W, CARRO_H))
imagem_obstaculo     = pygame.image.load("Obstaculo.png").convert_alpha()
imagem_obstaculo     = pygame.transform.scale(imagem_obstaculo, (OBST_W, OBST_H))
imagem_obs_movel     = pygame.image.load("Obstaculo_movel.png").convert_alpha()
imagem_obs_movel     = pygame.transform.scale(imagem_obs_movel, (OBST_W, OBST_H))

fonte_grande  = pygame.font.SysFont("Arial", 18, bold=True)
fonte_media   = pygame.font.SysFont("Arial", 13, bold=True)
fonte_pequena = pygame.font.SysFont("Arial", 10)

LARGURA_PISTA  = 100
LARGURA_FAIXA  = LARGURA_PISTA // 3
ESPACO_OBST    = 30

COR_GRAMA    = (34,  100, 34)
COR_ASFALTO  = (55,  55,  55)
COR_FAIXA    = (200, 200, 200)
COR_BORDA    = (255, 255, 255)
COR_LARGADA  = (255,  50,  50)

def calcular_normal(ax, ay, bx, by):
    """Retorna o vetor normal (perpendicular) de um segmento."""
    dx = bx - ax
    dy = by - ay
    comprimento = math.hypot(dx, dy)
    if comprimento == 0:
        return 0.0, 0.0
    nx = -dy / comprimento
    ny =  dx / comprimento
    return nx, ny

def aplicar_camera(mundo_x, mundo_y, cam_x, cam_y):
    """Converte coordenada do mundo para coordenada da tela."""
    tela_x = mundo_x - cam_x
    tela_y = mundo_y - cam_y
    return tela_x, tela_y

def escalar_vertices(lista_vertices, margem):
    """Centraliza e escala uma lista de vertices para caber na tela."""
    lista_x = []
    lista_y = []
    for vertice in lista_vertices:
        lista_x.append(vertice[0])
        lista_y.append(vertice[1])

    span_x = max(lista_x) - min(lista_x)
    span_y = max(lista_y) - min(lista_y)

    if span_x == 0 or span_y == 0:
        return lista_vertices

    escala_x = (WIDTH - 2 * margem) / span_x
    escala_y = (HEIGHT - 2 * margem) / span_y
    escala   = min(escala_x, escala_y)

    offset_x = (WIDTH  - span_x * escala) / 2 - min(lista_x) * escala
    offset_y = (HEIGHT - span_y * escala) / 2 - min(lista_y) * escala

    resultado = []
    for vertice in lista_vertices:
        novo_x = vertice[0] * escala + offset_x
        novo_y = vertice[1] * escala + offset_y
        resultado.append((novo_x, novo_y))
    return resultado

def vertices_para_segmentos(lista_vertices):
    """Converte lista de vertices em lista de segmentos fechados."""
    segmentos = []
    n = len(lista_vertices)
    for i in range(n):
        inicio = lista_vertices[i]
        fim    = lista_vertices[(i + 1) % n]
        segmentos.append((inicio, fim))
    return segmentos

def rotacionar_vertices(lista_vertices, vezes):
    """Rotaciona 90 graus no sentido horario 'vezes' vezes."""
    resultado = lista_vertices
    for i in range(vezes):
        novo = []
        for vertice in resultado:
            x = vertice[0]
            y = vertice[1]
            novo.append((y, -x))
        resultado = novo
    return resultado

SEP = 5


def layout_retangulo():
    w    = random.randint(8, 12)
    h    = random.randint(5, 8)
    bump = random.randint(2, 3)
    lado = random.choice(["top", "bottom", "left", "right"])

    if lado == "top":
        vertices = [
            (0, 0), (w//2-1, 0), (w//2-1, -bump),
            (w//2+1, -bump), (w//2+1, 0), (w, 0), (w, h), (0, h)
        ]
    elif lado == "bottom":
        vertices = [
            (0, 0), (w, 0), (w, h), (w//2+1, h),
            (w//2+1, h+bump), (w//2-1, h+bump), (w//2-1, h), (0, h)
        ]
    elif lado == "left":
        vertices = [
            (0, 0), (w, 0), (w, h), (0, h),
            (0, h//2+1), (-bump, h//2+1), (-bump, h//2-1), (0, h//2-1)
        ]
    else:
        vertices = [
            (0, 0), (w, 0), (w, h//2-1), (w+bump, h//2-1),
            (w+bump, h//2+1), (w, h//2+1), (w, h), (0, h)
        ]

    vertices = escalar_vertices(vertices, 80)
    return vertices_para_segmentos(vertices)


def layout_U():
    w  = random.randint(10, 14)
    h  = random.randint(8,  12)
    bw = SEP + random.randint(1, 2)

    vertices = [
        (0, 0), (bw, 0), (bw, h - SEP),
        (w - bw, h - SEP), (w - bw, 0),
        (w, 0), (w, h), (0, h)
    ]
    rotacao  = random.choice([0, 1, 2, 3])
    vertices = rotacionar_vertices(vertices, rotacao)
    vertices = escalar_vertices(vertices, 80)
    return vertices_para_segmentos(vertices)


def layout_L():
    w  = random.randint(8, 12)
    h  = random.randint(6,  9)
    bw = SEP + random.randint(1, 2)
    bh = SEP + random.randint(1, 2)

    vertices = [
        (0, 0), (w, 0), (w, bh), (bw, bh), (bw, h), (0, h)
    ]
    rotacao  = random.choice([0, 1, 2, 3])
    vertices = rotacionar_vertices(vertices, rotacao)
    vertices = escalar_vertices(vertices, 80)
    return vertices_para_segmentos(vertices)


def layout_S():
    w  = random.randint(6, 9)
    h  = SEP + random.randint(2, 3)
    dx = SEP + random.randint(2, 4)

    vertices = [
        (0, 0), (w, 0), (w, h), (w + dx, h),
        (w + dx, h * 2), (dx, h * 2), (dx, h), (0, h)
    ]
    if random.choice([True, False]):
        espelhado = []
        for v in vertices:
            espelhado.append((-v[0], v[1]))
        vertices = espelhado

    vertices = escalar_vertices(vertices, 80)
    return vertices_para_segmentos(vertices)


def layout_Z():
    w  = random.randint(8, 12)
    h  = random.randint(5,  8)
    dy = SEP + random.randint(2, 4)

    vertices = [
        (0, 0), (w, 0), (w, dy),
        (w + SEP, dy), (w + SEP, dy + h),
        (0, dy + h), (0, dy),
        (-SEP, dy), (-SEP, 0)
    ]
    rotacao  = random.choice([0, 1, 2, 3])
    vertices = rotacionar_vertices(vertices, rotacao)
    vertices = escalar_vertices(vertices, 80)
    return vertices_para_segmentos(vertices)


def layout_C():
    w  = random.randint(8, 12)
    h  = random.randint(8, 12)
    bw = SEP + random.randint(1, 2)
    bh = SEP + random.randint(1, 2)

    vertices = [
        (bw, 0), (w, 0), (w, h), (bw, h),
        (bw, h - bh), (0, h - bh), (0, bh), (bw, bh)
    ]
    rotacao  = random.choice([0, 1, 2, 3])
    vertices = rotacionar_vertices(vertices, rotacao)
    vertices = escalar_vertices(vertices, 80)
    return vertices_para_segmentos(vertices)

def gerar_circuito():
    numero = random.randint(0, 5)
    if numero == 0:
        return layout_retangulo()
    elif numero == 1:
        return layout_U()
    elif numero == 2:
        return layout_L()
    elif numero == 3:
        return layout_S()
    elif numero == 4:
        return layout_Z()
    else:
        return layout_C()

def segmentos_para_pontos(segmentos):
    """Expande lista de segmentos em lista densa de pontos."""
    pontos = []
    passo  = 5
    for segmento in segmentos:
        ax = segmento[0][0]
        ay = segmento[0][1]
        bx = segmento[1][0]
        by = segmento[1][1]
        distancia = math.hypot(bx - ax, by - ay)
        steps     = int(distancia / passo)
        if steps < 2:
            steps = 2
        for s in range(steps):
            t = s / steps
            px = ax + (bx - ax) * t
            py = ay + (by - ay) * t
            pontos.append((px, py))
    return pontos

def verificar_curva(pontos, indice, janela, limite_angulo):
    """Retorna True se o ponto estiver perto de uma curva."""
    n = len(pontos)
    for offset in range(-janela, janela + 1):
        i  = (indice + offset) % n
        p1 = pontos[i]
        p2 = pontos[(i + 1) % n]
        p3 = pontos[(i + 2) % n]

        dx1 = p2[0] - p1[0]
        dy1 = p2[1] - p1[1]
        ang1 = math.degrees(math.atan2(-dy1, dx1))

        dx2 = p3[0] - p2[0]
        dy2 = p3[1] - p2[1]
        ang2 = math.degrees(math.atan2(-dy2, dx2))

        diferenca = abs((ang2 - ang1 + 180) % 360 - 180)
        if diferenca > limite_angulo:
            return True
    return False

def calcular_saida(faixas_bloqueadas):
    """Retorna quais faixas estao livres dado o bloqueio."""
    todas = [0, 1, 2]
    livres = set()
    for faixa in todas:
        if faixa not in faixas_bloqueadas:
            livres.add(faixa)
    return livres

def gerar_obstaculos(pontos, voltas):
    """Distribui obstaculos ao longo da pista respeitando as regras."""
    duplos  = [[0, 1], [1, 2], [0, 2]]
    simples = [[0], [1], [2]]

    obstaculos       = []
    n                = len(pontos)
    indice           = ESPACO_OBST * 2
    historico_saidas = []

    chance_movel = 0.10 + voltas * 0.08
    if chance_movel > 0.60:
        chance_movel = 0.60

    while indice < n:
        if not verificar_curva(pontos, indice, 7, 12):

            saida_proibida = None
            if len(historico_saidas) >= 2:
                if historico_saidas[-1] == historico_saidas[-2]:
                    saida_proibida = historico_saidas[-1]

            numero_sorteado = random.random()
            if numero_sorteado < chance_movel:
                eh_movel = True
            else:
                eh_movel = False

            if eh_movel:
                faixas = random.choice(simples)
            else:
                if random.choice([True, False]):
                    candidatos = []
                    for combo in duplos:
                        saida = calcular_saida(combo)
                        if saida != saida_proibida:
                            candidatos.append(combo)
                    if len(candidatos) == 0:
                        candidatos = duplos
                    faixas = random.choice(candidatos)
                else:
                    candidatos = []
                    for combo in simples:
                        saida = calcular_saida(combo)
                        if saida != saida_proibida:
                            candidatos.append(combo)
                    if len(candidatos) == 0:
                        candidatos = simples
                    faixas = random.choice(candidatos)

            saida_atual = calcular_saida(faixas)
            historico_saidas.append(saida_atual)
            if len(historico_saidas) > 2:
                historico_saidas.pop(0)

            if eh_movel:
                faixa_inicial = faixas[0]
            else:
                faixa_inicial = 1

            offset_inicial = (faixa_inicial - 1) * LARGURA_FAIXA

            obstaculo = {
                "indice":     indice,
                "faixas":     list(faixas),
                "movel":      eh_movel,
                "faixa_real": faixa_inicial,
                "off_alvo":   offset_inicial,
                "off_real":   float(offset_inicial),
                "direcao":    random.choice([-1, 1]),
                "timer":      0.0,
                "intervalo":  max(1.5 - voltas * 0.15, 0.4),
            }
            obstaculos.append(obstaculo)

        indice = indice + ESPACO_OBST + random.randint(0, 20)

    return obstaculos

def atualizar_obstaculos(obstaculos, dt):
    """Move obstaculos moveis entre faixas com animacao suave."""
    for obs in obstaculos:
        if obs["movel"] == False:
            continue

        diferenca   = obs["off_alvo"] - obs["off_real"]
        obs["off_real"] = obs["off_real"] + diferenca * 0.12

        obs["timer"] = obs["timer"] + dt
        if obs["timer"] >= obs["intervalo"]:
            obs["timer"] = 0.0

            nova_faixa = obs["faixa_real"] + obs["direcao"]

            if nova_faixa < 0 or nova_faixa > 2:
                obs["direcao"] = obs["direcao"] * -1
                nova_faixa = obs["faixa_real"] + obs["direcao"]

            obs["faixa_real"] = nova_faixa
            obs["off_alvo"]   = (nova_faixa - 1) * LARGURA_FAIXA
            obs["faixas"]     = [nova_faixa]

def desenhar_obstaculos(superficie, pontos, obstaculos, cam_x, cam_y):
    """Desenha cada obstaculo na pista usando sprites."""
    n = len(pontos)
    for obs in obstaculos:
        indice = obs["indice"]
        p1     = pontos[indice]
        p2     = pontos[(indice + 1) % n]
        dx     = p2[0] - p1[0]
        dy     = p2[1] - p1[1]
        c      = math.hypot(dx, dy)
        if c == 0:
            continue
        nx = -dy / c
        ny =  dx / c
        angulo = math.degrees(math.atan2(-dy, dx))

        if obs["movel"]:
            sprite = imagem_obs_movel
        else:
            sprite = imagem_obstaculo

        if obs["movel"]:
            off  = obs["off_real"]
            mx   = p1[0] + nx * off
            my   = p1[1] + ny * off
            sx, sy = aplicar_camera(mx, my, cam_x, cam_y)
            rotacionado = pygame.transform.rotate(sprite, angulo)
            rect = rotacionado.get_rect()
            rect.centerx = int(sx)
            rect.centery  = int(sy)
            superficie.blit(rotacionado, rect)
        else:
            for faixa in obs["faixas"]:
                off  = (faixa - 1) * LARGURA_FAIXA
                mx   = p1[0] + nx * off
                my   = p1[1] + ny * off
                sx, sy = aplicar_camera(mx, my, cam_x, cam_y)
                rotacionado = pygame.transform.rotate(sprite, angulo)
                rect = rotacionado.get_rect()
                rect.centerx = int(sx)
                rect.centery  = int(sy)
                superficie.blit(rotacionado, rect)

def verificar_colisao(carro_x, carro_y, carro_indice, pontos, obstaculos):
    """Retorna True se o carro colidiu com algum obstaculo."""
    n = len(pontos)
    for obs in obstaculos:
        indice    = obs["indice"]
        distancia = (indice - carro_indice) % n

        if distancia > 30 or distancia == 0:
            continue

        p1 = pontos[indice]
        p2 = pontos[(indice + 1) % n]
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        c  = math.hypot(dx, dy)
        if c == 0:
            continue

        nx = -dy / c
        ny =  dx / c
        fx =  dx / c
        fy =  dy / c

        if obs["movel"]:
            off = obs["off_real"]
            ox  = p1[0] + nx * off
            oy  = p1[1] + ny * off
            ddx = carro_x - ox
            ddy = carro_y - oy
            dist_lateral     = abs(ddx * nx + ddy * ny)
            dist_longitudinal = abs(ddx * fx + ddy * fy)
            if dist_lateral < LARGURA_FAIXA / 2 - 2 and dist_longitudinal < 20:
                return True
        else:
            for faixa in obs["faixas"]:
                off = (faixa - 1) * LARGURA_FAIXA
                ox  = p1[0] + nx * off
                oy  = p1[1] + ny * off
                ddx = carro_x - ox
                ddy = carro_y - oy
                dist_lateral      = abs(ddx * nx + ddy * ny)
                dist_longitudinal = abs(ddx * fx + ddy * fy)
                if dist_lateral < LARGURA_FAIXA / 2 - 2 and dist_longitudinal < 20:
                    return True
    return False

def desenhar_pista(superficie, segmentos, cam_x, cam_y):
    """Desenha o asfalto, bordas, faixas e linha de largada."""
    hw = LARGURA_PISTA / 2

    for segmento in segmentos:
        ax = segmento[0][0]
        ay = segmento[0][1]
        bx = segmento[1][0]
        by = segmento[1][1]
        nx, ny = calcular_normal(ax, ay, bx, by)

        canto1 = aplicar_camera(ax + nx * hw, ay + ny * hw, cam_x, cam_y)
        canto2 = aplicar_camera(bx + nx * hw, by + ny * hw, cam_x, cam_y)
        canto3 = aplicar_camera(bx - nx * hw, by - ny * hw, cam_x, cam_y)
        canto4 = aplicar_camera(ax - nx * hw, ay - ny * hw, cam_x, cam_y)
        pygame.draw.polygon(superficie, COR_ASFALTO, [canto1, canto2, canto3, canto4])

    for segmento in segmentos:
        vx = segmento[1][0]
        vy = segmento[1][1]
        sx, sy = aplicar_camera(vx, vy, cam_x, cam_y)
        pygame.draw.rect(superficie, COR_ASFALTO,
                         (int(sx - hw), int(sy - hw),
                          int(LARGURA_PISTA), int(LARGURA_PISTA)))

    recuo = hw
    for segmento in segmentos:
        ax = segmento[0][0]
        ay = segmento[0][1]
        bx = segmento[1][0]
        by = segmento[1][1]
        nx, ny = calcular_normal(ax, ay, bx, by)

        distancia = math.hypot(bx - ax, by - ay)
        if distancia == 0:
            continue
        fx = (bx - ax) / distancia
        fy = (by - ay) / distancia

        ax2 = ax + fx * recuo
        ay2 = ay + fy * recuo
        bx2 = bx - fx * recuo
        by2 = by - fy * recuo

        for sinal in [1, -1]:
            p1 = aplicar_camera(ax2 + nx * hw * sinal, ay2 + ny * hw * sinal, cam_x, cam_y)
            p2 = aplicar_camera(bx2 + nx * hw * sinal, by2 + ny * hw * sinal, cam_x, cam_y)
            pygame.draw.line(superficie, COR_BORDA,
                             (int(p1[0]), int(p1[1])),
                             (int(p2[0]), int(p2[1])), 4)

    for segmento in segmentos:
        ax = segmento[0][0]
        ay = segmento[0][1]
        bx = segmento[1][0]
        by = segmento[1][1]
        nx, ny = calcular_normal(ax, ay, bx, by)

        distancia = math.hypot(bx - ax, by - ay)
        steps     = int(distancia / 6)
        if steps < 2:
            steps = 2

        for sinal_faixa in [-1, 1]:
            fw = (LARGURA_PISTA / 6) * sinal_faixa
            for s in range(0, steps, 2):
                t1 = s / steps
                t2 = (s + 1) / steps
                if t2 > 1.0:
                    t2 = 1.0
                sx1, sy1 = aplicar_camera(
                    ax + (bx - ax) * t1 + nx * fw,
                    ay + (by - ay) * t1 + ny * fw,
                    cam_x, cam_y)
                sx2, sy2 = aplicar_camera(
                    ax + (bx - ax) * t2 + nx * fw,
                    ay + (by - ay) * t2 + ny * fw,
                    cam_x, cam_y)
                pygame.draw.line(superficie, COR_FAIXA,
                                 (int(sx1), int(sy1)),
                                 (int(sx2), int(sy2)), 2)

    ax = segmentos[0][0][0]
    ay = segmentos[0][0][1]
    bx = segmentos[0][1][0]
    by = segmentos[0][1][1]
    nx, ny = calcular_normal(ax, ay, bx, by)
    p1 = aplicar_camera(ax + nx * hw, ay + ny * hw, cam_x, cam_y)
    p2 = aplicar_camera(ax - nx * hw, ay - ny * hw, cam_x, cam_y)
    pygame.draw.line(superficie, COR_LARGADA,
                     (int(p1[0]), int(p1[1])),
                     (int(p2[0]), int(p2[1])), 6)

class Carro(pygame.sprite.Sprite):
    def __init__(self, segmentos):
        pygame.sprite.Sprite.__init__(self)

        self.segmentos    = segmentos
        self.pontos       = segmentos_para_pontos(segmentos)
        self.total_pontos = len(self.pontos)
        self.indice       = 0
        self.progresso    = 0.0

        self.vel_base    = 28.0
        self.velocidade  = self.vel_base

        self.faixa       = 1
        self.faixa_real  = 1.0

        self.angulo      = 0.0
        self.pontuacao   = 0
        self.metros_acum = 0.0
        self.voltas      = 0
        self.vel_kmh_real  = 0
        self.metros_ultimo = 0.0

        # Pre-calcula pontos das 3 faixas com offset ja aplicado
        # Assim cada faixa tem sua propria trajetoria suave, identica a central
        offsets = [-LARGURA_FAIXA, 0.0, LARGURA_FAIXA]
        self.pontos_faixa = []
        n = self.total_pontos
        for off in offsets:
            lista = []
            for i in range(n):
                p1 = self.pontos[i]
                p2 = self.pontos[(i + 1) % n]
                dx = p2[0] - p1[0]
                dy = p2[1] - p1[1]
                comp = math.hypot(dx, dy)
                if comp > 0:
                    nx = -dy / comp
                    ny =  dx / comp
                else:
                    nx = 0.0
                    ny = 0.0
                lista.append((p1[0] + nx * off, p1[1] + ny * off))
            self.pontos_faixa.append(lista)

        self.x = self.pontos_faixa[1][0][0]
        self.y = self.pontos_faixa[1][0][1]

        self.angulos_pista = []
        for i in range(n):
            p1 = self.pontos[i]
            p2 = self.pontos[(i + 1) % n]
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            ang = math.degrees(math.atan2(-dy, dx))
            self.angulos_pista.append(ang)

    def mudar_faixa(self, direcao):
        nova_faixa = self.faixa + direcao
        if nova_faixa < 0:
            nova_faixa = 0
        if nova_faixa > 2:
            nova_faixa = 2
        self.faixa = nova_faixa

    def update(self):
        n = self.total_pontos

        self.faixa_real = self.faixa_real + (self.faixa - self.faixa_real) * 0.12

        passo = self.velocidade / 60.0
        metros_antes     = self.metros_acum
        self.metros_acum = self.metros_acum + passo * 5.0 / 50.0
        self.pontuacao   = int(self.metros_acum)
        self.progresso   = self.progresso + passo

        metros_neste_frame = self.metros_acum - metros_antes
        self.vel_kmh_real  = int(metros_neste_frame * FPS * 3.6)

        while self.progresso >= 1.0:
            self.progresso = self.progresso - 1.0
            self.indice    = (self.indice + 1) % n
            if self.indice == 0:
                self.voltas     = self.voltas + 1
                self.velocidade = self.vel_base + self.voltas * 3.0

        idx_a = self.indice
        idx_b = (self.indice + 1) % n
        t     = self.progresso

        # Detecta curvatura a frente
        look       = 12
        ang_atual  = self.angulos_pista[self.indice]
        ang_frente = self.angulos_pista[(self.indice + look) % n]
        diff_curva = (ang_frente - ang_atual + 180) % 360 - 180
        em_curva   = abs(diff_curva) > 15

        # Em curva: segue diretamente os pontos da faixa destino (sem interpolacao)
        # Isso garante que o carro nunca sai dos limites de sua faixa
        if em_curva:
            faixa_idx = int(round(self.faixa_real))
            if faixa_idx < 0:
                faixa_idx = 0
            if faixa_idx > 2:
                faixa_idx = 2
            pa = self.pontos_faixa[faixa_idx][idx_a]
            pb = self.pontos_faixa[faixa_idx][idx_b]
            cx = pa[0] + (pb[0] - pa[0]) * t
            cy = pa[1] + (pb[1] - pa[1]) * t
        else:
            # Em reta: interpola suavemente entre faixas (troca de faixa fluida)
            if self.faixa_real <= 1.0:
                t_f  = self.faixa_real
                pa_a = self.pontos_faixa[0][idx_a]
                pb_a = self.pontos_faixa[0][idx_b]
                pa_b = self.pontos_faixa[1][idx_a]
                pb_b = self.pontos_faixa[1][idx_b]
            else:
                t_f  = self.faixa_real - 1.0
                pa_a = self.pontos_faixa[1][idx_a]
                pb_a = self.pontos_faixa[1][idx_b]
                pa_b = self.pontos_faixa[2][idx_a]
                pb_b = self.pontos_faixa[2][idx_b]

            cx_a = pa_a[0] + (pb_a[0] - pa_a[0]) * t
            cy_a = pa_a[1] + (pb_a[1] - pa_a[1]) * t
            cx_b = pa_b[0] + (pb_b[0] - pa_b[0]) * t
            cy_b = pa_b[1] + (pb_b[1] - pa_b[1]) * t
            cx   = cx_a + (cx_b - cx_a) * t_f
            cy   = cy_a + (cy_b - cy_a) * t_f

        p1 = self.pontos[self.indice]
        p2 = self.pontos[(self.indice + 1) % n]
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        angulo_alvo = math.degrees(math.atan2(-dy, dx))
        diff_angulo = (angulo_alvo - self.angulo + 180) % 360 - 180
        self.angulo = self.angulo + diff_angulo * 0.18

        self.x = cx
        self.y = cy

    def desenhar(self, superficie, cam_x, cam_y):
        sx, sy = aplicar_camera(self.x, self.y, cam_x, cam_y)
        rotacionado = pygame.transform.rotate(imagem_carro, self.angulo)
        rect = rotacionado.get_rect()
        rect.centerx = int(sx)
        rect.centery  = int(sy)
        superficie.blit(rotacionado, rect)

def desenhar_hud(superficie, carro):
    painel = pygame.Surface((140, 62), pygame.SRCALPHA)
    painel.fill((0, 0, 0, 160))
    superficie.blit(painel, (6, 6))

    if carro.vel_kmh_real == 0:
        texto_vel = fonte_grande.render("  -- km/h", True, (255, 220, 0))
    else:
        texto_vel = fonte_grande.render("  " + str(carro.vel_kmh_real) + " km/h", True, (255, 220, 0))

    texto_volta = fonte_media.render("  Volta: " + str(carro.voltas + 1), True, (255, 255, 255))
    texto_pts   = fonte_media.render("  " + str(carro.pontuacao) + " metros", True, (255, 255, 255))

    superficie.blit(texto_vel,   (6,  8))
    superficie.blit(texto_volta, (6, 32))
    superficie.blit(texto_pts,   (6, 48))

    labels = ["< ESQ", "CENTRO", "DIR >"]
    for i in range(3):
        if i == carro.faixa:
            cor = (255, 220, 0)
        else:
            cor = (120, 120, 120)
        texto = fonte_pequena.render(labels[i], True, cor)
        superficie.blit(texto, (VIRT_W // 2 - 75 + i * 55, VIRT_H - 18))

    instrucoes = fonte_pequena.render("A = esq   D = dir   R = novo circuito", True, (180, 180, 180))
    superficie.blit(instrucoes, (VIRT_W // 2 - instrucoes.get_width() // 2, VIRT_H - 30))

def desenhar_game_over(superficie, pontuacao, voltas):
    """Desenha a tela de fim de jogo."""
    overlay = pygame.Surface((VIRT_W, VIRT_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    superficie.blit(overlay, (0, 0))

    fonte_go = pygame.font.SysFont("Arial", 38, bold=True)
    fonte_gm = pygame.font.SysFont("Arial", 20, bold=True)
    fonte_gp = pygame.font.SysFont("Arial", 14)

    t1 = fonte_go.render("GAME OVER",                      True, (220, 30,  30))
    t2 = fonte_gm.render(str(pontuacao) + " metros",       True, (255, 255, 255))
    t3 = fonte_gm.render("Voltas: " + str(voltas),         True, (255, 255, 255))
    t4 = fonte_gp.render("R = jogar de novo   M = menu",   True, (180, 180, 180))

    superficie.blit(t1, (VIRT_W // 2 - t1.get_width() // 2, VIRT_H // 2 - 75))
    superficie.blit(t2, (VIRT_W // 2 - t2.get_width() // 2, VIRT_H // 2 - 20))
    superficie.blit(t3, (VIRT_W // 2 - t3.get_width() // 2, VIRT_H // 2 + 10))
    superficie.blit(t4, (VIRT_W // 2 - t4.get_width() // 2, VIRT_H // 2 + 50))

maior_recorde     = 0
tela_atual        = "menu"
vel_inicial_kmh   = 10
ambiente_escolhido = "Aleatorio"
ambiente_atual     = "Terra"

OPCOES_VELOCIDADE  = [10, 14, 18, 22]
OPCOES_AMBIENTE    = ["Aleatorio", "Terra", "Mar", "Lua", "Marte"]

CORES_AMBIENTE = {
    "Terra": (25,  150, 48),
    "Mar":   (20,  60,  140),
    "Lua":   (130, 130, 130),
    "Marte": (201, 73,  50),
}


def kmh_para_vel_base(kmh):
    return kmh * 2.8


def sortear_ambiente():
    opcoes = ["Terra", "Mar", "Lua", "Marte"]
    return random.choice(opcoes)


segmentos  = None
carro      = None
obstaculos = None
game_over  = False
voltas_ant = 0
cam_x      = 0
cam_y      = 0


def iniciar_partida():
    global segmentos, carro, obstaculos, game_over, voltas_ant, cam_x, cam_y, ambiente_atual
    segmentos  = gerar_circuito()
    carro      = Carro(segmentos)
    carro.vel_base   = kmh_para_vel_base(vel_inicial_kmh)
    carro.velocidade = carro.vel_base
    obstaculos = gerar_obstaculos(carro.pontos, voltas=0)
    game_over  = False
    voltas_ant = 0
    cam_x      = carro.x - VIRT_W // 2
    cam_y      = carro.y - VIRT_H // 2
    if ambiente_escolhido == "Aleatorio":
        ambiente_atual = sortear_ambiente()
    else:
        ambiente_atual = ambiente_escolhido


def desenhar_botao(superficie, texto, cx, cy, largura, altura, fonte):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    rect = pygame.Rect(cx - largura // 2, cy - altura // 2, largura, altura)
    if rect.collidepoint(mouse_x, mouse_y):
        cor_fundo = (80, 80, 160)
    else:
        cor_fundo = (40, 40, 100)
    pygame.draw.rect(superficie, cor_fundo, rect, border_radius=10)
    pygame.draw.rect(superficie, (150, 150, 255), rect, 2, border_radius=10)
    label = fonte.render(texto, True, (255, 255, 255))
    superficie.blit(label, (cx - label.get_width() // 2, cy - label.get_height() // 2))
    return rect


def desenhar_menu(superficie):
    superficie.fill((20, 20, 40))

    fonte_titulo  = pygame.font.SysFont("Arial", 48, bold=True)
    fonte_botao   = pygame.font.SysFont("Arial", 26, bold=True)
    fonte_recorde = pygame.font.SysFont("Arial", 18)

    titulo = fonte_titulo.render("Corrida Insana!", True, (255, 220, 0))
    superficie.blit(titulo, (WIDTH // 2 - titulo.get_width() // 2, 120))

    recorde_texto = fonte_recorde.render("Maior recorde: " + str(maior_recorde) + " metros", True, (180, 180, 180))
    superficie.blit(recorde_texto, (WIDTH // 2 - recorde_texto.get_width() // 2, 210))

    rect_iniciar  = desenhar_botao(superficie, "Iniciar Partida", WIDTH // 2, 330, 280, 55, fonte_botao)
    rect_config   = desenhar_botao(superficie, "Configuracoes",   WIDTH // 2, 410, 280, 55, fonte_botao)
    rect_fechar   = desenhar_botao(superficie, "Fechar Jogo",     WIDTH // 2, 490, 280, 55, fonte_botao)

    return rect_iniciar, rect_config, rect_fechar


def desenhar_configuracoes(superficie):
    global vel_inicial_kmh, ambiente_escolhido

    superficie.fill((20, 20, 40))

    fonte_titulo = pygame.font.SysFont("Arial", 36, bold=True)
    fonte_label  = pygame.font.SysFont("Arial", 22, bold=True)
    fonte_opcao  = pygame.font.SysFont("Arial", 18)
    fonte_voltar = pygame.font.SysFont("Arial", 22, bold=True)

    titulo = fonte_titulo.render("Configuracoes", True, (255, 220, 0))
    superficie.blit(titulo, (WIDTH // 2 - titulo.get_width() // 2, 50))

    label_vel = fonte_label.render("Velocidade inicial:", True, (255, 255, 255))
    superficie.blit(label_vel, (WIDTH // 2 - label_vel.get_width() // 2, 120))

    mouse_x, mouse_y = pygame.mouse.get_pos()
    retangulos_vel = []
    total   = len(OPCOES_VELOCIDADE)
    espaco  = 100
    inicio_x = WIDTH // 2 - (total * espaco) // 2 + espaco // 2

    for i in range(total):
        kmh  = OPCOES_VELOCIDADE[i]
        cx   = inicio_x + i * espaco
        cy   = 190
        rect = pygame.Rect(cx - 38, cy - 25, 76, 50)

        if kmh == vel_inicial_kmh:
            cor_fundo = (100, 180, 100)
            cor_borda = (200, 255, 200)
        elif rect.collidepoint(mouse_x, mouse_y):
            cor_fundo = (80, 80, 160)
            cor_borda = (150, 150, 255)
        else:
            cor_fundo = (40, 40, 100)
            cor_borda = (100, 100, 200)

        pygame.draw.rect(superficie, cor_fundo, rect, border_radius=8)
        pygame.draw.rect(superficie, cor_borda, rect, 2, border_radius=8)
        texto = fonte_opcao.render(str(kmh) + " km/h", True, (255, 255, 255))
        superficie.blit(texto, (cx - texto.get_width() // 2, cy - texto.get_height() // 2))
        retangulos_vel.append((rect, kmh))

    label_amb = fonte_label.render("Ambiente:", True, (255, 255, 255))
    superficie.blit(label_amb, (WIDTH // 2 - label_amb.get_width() // 2, 270))

    retangulos_amb = []
    total_amb  = len(OPCOES_AMBIENTE)
    espaco_amb = 160
    inicio_amb = WIDTH // 2 - (total_amb * espaco_amb) // 2 + espaco_amb // 2

    for i in range(total_amb):
        nome = OPCOES_AMBIENTE[i]
        cx   = inicio_amb + i * espaco_amb
        cy   = 340
        rect = pygame.Rect(cx - 68, cy - 25, 136, 50)

        if nome == ambiente_escolhido:
            cor_fundo = (100, 180, 100)
            cor_borda = (200, 255, 200)
        elif rect.collidepoint(mouse_x, mouse_y):
            cor_fundo = (80, 80, 160)
            cor_borda = (150, 150, 255)
        else:
            if nome in CORES_AMBIENTE:
                r, g, b   = CORES_AMBIENTE[nome]
                cor_fundo = (r // 2, g // 2, b // 2)
            else:
                cor_fundo = (40, 40, 100)
            cor_borda = (100, 100, 200)

        pygame.draw.rect(superficie, cor_fundo, rect, border_radius=8)
        pygame.draw.rect(superficie, cor_borda, rect, 2, border_radius=8)
        texto = fonte_opcao.render(nome, True, (255, 255, 255))
        superficie.blit(texto, (cx - texto.get_width() // 2, cy - texto.get_height() // 2))
        retangulos_amb.append((rect, nome))

    rect_voltar = desenhar_botao(superficie, "Voltar ao Menu", WIDTH // 2, 460, 280, 55, fonte_voltar)

    return retangulos_vel, retangulos_amb, rect_voltar


jogo_rodando = True

while jogo_rodando:
    dt = clock.tick(FPS) / 1000.0

    if tela_atual == "menu":
        rect_iniciar, rect_config, rect_fechar = desenhar_menu(window)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                jogo_rodando = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if rect_iniciar.collidepoint(event.pos):
                        iniciar_partida()
                        tela_atual = "jogo"
                    if rect_config.collidepoint(event.pos):
                        tela_atual = "configuracoes"
                    if rect_fechar.collidepoint(event.pos):
                        jogo_rodando = False

    elif tela_atual == "configuracoes":
        retangulos_vel, retangulos_amb, rect_voltar = desenhar_configuracoes(window)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                jogo_rodando = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for rect, kmh in retangulos_vel:
                        if rect.collidepoint(event.pos):
                            vel_inicial_kmh = kmh
                    for rect, nome in retangulos_amb:
                        if rect.collidepoint(event.pos):
                            ambiente_escolhido = nome
                    if rect_voltar.collidepoint(event.pos):
                        tela_atual = "menu"

    elif tela_atual == "jogo":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                jogo_rodando = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_over:
                    iniciar_partida()

                if event.key == pygame.K_m and game_over:
                    tela_atual = "menu"

                if game_over == False:
                    if event.key == pygame.K_a:
                        carro.mudar_faixa(-1)
                    if event.key == pygame.K_d:
                        carro.mudar_faixa(+1)

        if game_over == False:
            carro.update()

            cam_x = cam_x + (carro.x - VIRT_W // 2 - cam_x) * 0.10
            cam_y = cam_y + (carro.y - VIRT_H // 2 - cam_y) * 0.10

            atualizar_obstaculos(obstaculos, dt)

            if carro.voltas > voltas_ant:
                voltas_ant = carro.voltas
                obstaculos = gerar_obstaculos(carro.pontos, voltas=carro.voltas)

            if verificar_colisao(carro.x, carro.y, carro.indice, carro.pontos, obstaculos):
                game_over = True
                if carro.pontuacao > maior_recorde:
                    maior_recorde = carro.pontuacao

        virtual.fill(CORES_AMBIENTE[ambiente_atual])
        desenhar_pista(virtual, segmentos, cam_x, cam_y)
        desenhar_obstaculos(virtual, carro.pontos, obstaculos, cam_x, cam_y)
        carro.desenhar(virtual, cam_x, cam_y)
        desenhar_hud(virtual, carro)

        if game_over:
            desenhar_game_over(virtual, carro.pontuacao, carro.voltas)

        pygame.transform.scale(virtual, (WIDTH, HEIGHT), window)
        pygame.display.update()

pygame.quit()
