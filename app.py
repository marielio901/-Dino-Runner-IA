import pygame
import random
import os

pygame.init()

# Tela
LARGURA, ALTURA = 800, 400
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Dino Runner")

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERMELHO = (200, 0, 0)

# Fonte
fonte = pygame.font.Font(None, 36)

# Caminhos
CAM_MUSICA = os.path.join("som", "The Final Countdown (2023).mp3")
CAM_SOM_PULO = os.path.join("som", "pulo.mp3")
CAM_SOM_GRITO = os.path.join("som", "grito.mp3")
CAM_DINO = os.path.join("sprites", "dino.png")
CAM_DINO_BAIXO = os.path.join("sprites", "dino_baixo.png")
CAM_CACTO = os.path.join("sprites", "cacto.png")
CAM_MISSIL = os.path.join("sprites", "missil.png")
CAM_CHAO = os.path.join("sprites", "chao.png")

# Sprites
dino_img = pygame.transform.scale(pygame.image.load(CAM_DINO).convert_alpha(), (70, 70))
dino_baixo_img = pygame.transform.scale(pygame.image.load(CAM_DINO_BAIXO).convert_alpha(), (70, 50))
cacto_img = pygame.transform.scale(pygame.image.load(CAM_CACTO).convert_alpha(), (50, 100))
missil_img = pygame.transform.scale(pygame.image.load(CAM_MISSIL).convert_alpha(), (90, 60))
chao_tile = pygame.image.load(CAM_CHAO).convert_alpha()

# Ajuste da altura do tile
chao_tile = pygame.transform.scale(chao_tile, (chao_tile.get_width(), 50))

# Sons
som_pulo = pygame.mixer.Sound(CAM_SOM_PULO)
som_pulo.set_volume(0.5)
som_grito = pygame.mixer.Sound(CAM_SOM_GRITO)
som_grito.set_volume(0.5)

# Telas
def tela_inicio(fundo_statico):
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE:
                return
        TELA.blit(fundo_statico, (0, 0))
        texto = fonte.render("Pressione ESPAÇO para começar", True, PRETO)
        TELA.blit(texto, (LARGURA // 2 - texto.get_width() // 2, ALTURA // 2 - 20))
        pygame.display.update()

def tela_game_over(fundo_statico):
    pygame.mixer.music.stop()
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE:
                return
        TELA.blit(fundo_statico, (0, 0))
        texto1 = fonte.render("VOCÊ PERDEU!", True, VERMELHO)
        texto2 = fonte.render("Pressione ESPAÇO para recomeçar", True, PRETO)
        TELA.blit(texto1, (LARGURA // 2 - texto1.get_width() // 2, ALTURA // 2 - 40))
        TELA.blit(texto2, (LARGURA // 2 - texto2.get_width() // 2, ALTURA // 2 + 10))
        pygame.display.update()

# Jogo
def desenhar_chao():
    for x in range(0, LARGURA, chao_tile.get_width()):
        TELA.blit(chao_tile, (x, ALTURA - chao_tile.get_height()))

def jogar():
    pygame.mixer.music.load(CAM_MUSICA)
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)

    clock = pygame.time.Clock()
    FPS = 60

    dino_surface = dino_img
    dino_rect = dino_surface.get_rect(midbottom=(100, 350))
    dino_y = float(dino_rect.y)
    gravidade = 0
    abaixado = False

    tipo_obstaculo = "chao"
    obstaculo = cacto_img.get_rect(midbottom=(900, 350))

    pontos = 0
    velocidade = 6

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP and dino_rect.bottom == 350:
                    gravidade = -18
                    som_pulo.play()
                if evento.key == pygame.K_DOWN:
                    abaixado = True
            if evento.type == pygame.KEYUP:
                if evento.key == pygame.K_DOWN:
                    abaixado = False

        # Dino
        if abaixado:
            dino_surface = dino_baixo_img
            dino_rect.height = 50
            dino_rect.bottom = 350
        else:
            dino_surface = dino_img
            dino_rect.height = 70
            dino_rect.bottom = min(dino_rect.bottom, 350)

        gravidade += 0.8
        dino_y += gravidade
        dino_rect.y = int(dino_y)

        if dino_rect.bottom > 350:
            dino_rect.bottom = 350
            dino_y = dino_rect.y

        # Obstáculo
        if tipo_obstaculo in ["chao", "voador"]:
            obstaculo.x -= velocidade
            if obstaculo.right < 0:
                pontos += 1
                velocidade = 6 + pontos // 5
                tipo_obstaculo = random.choices(["chao", "voador"], weights=[0.6, 0.4])[0]
                if tipo_obstaculo == "chao":
                    obstaculo = cacto_img.get_rect(midbottom=(random.randint(800, 1000), 350))
                elif tipo_obstaculo == "voador":
                    y_missil = random.randint(220, 240)  # posição ajustada para mais alto
                    obstaculo = missil_img.get_rect(topleft=(random.randint(800, 1000), y_missil))

        # Colisão
        colisao = False
        if tipo_obstaculo in ["chao", "voador"] and dino_rect.colliderect(obstaculo):
            som_grito.play()
            colisao = True

        # Desenha cenário
        TELA.fill(BRANCO)
        desenhar_chao()
        TELA.blit(dino_surface, dino_rect)

        if tipo_obstaculo == "chao":
            TELA.blit(cacto_img, obstaculo)
        elif tipo_obstaculo == "voador":
            TELA.blit(missil_img, obstaculo)

        texto = fonte.render(f"Pontos: {pontos}  Vel: {velocidade}", True, PRETO)
        TELA.blit(texto, (10, 10))

        pygame.display.update()
        clock.tick(FPS)

        if colisao:
            fundo = TELA.copy()
            return fundo

# === Execução principal ===
while True:
    fundo_inicial = pygame.Surface((LARGURA, ALTURA))
    fundo_inicial.fill(BRANCO)
    desenhar_chao()
    fundo_inicial.blit(chao_tile, (0, ALTURA - chao_tile.get_height()))
    tela_inicio(fundo_inicial)
    fundo_colisao = jogar()
    tela_game_over(fundo_colisao)
