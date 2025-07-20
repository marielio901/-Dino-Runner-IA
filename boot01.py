# boot01.py — IA simples baseada em histórico com análise de desempenho

import pygame
import random
import os
import sqlite3
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

pygame.init()

LARGURA, ALTURA = 800, 400
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Dino Runner IA")

PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)

# Caminhos
CAM_DINO = os.path.join("sprites", "dino.png")
CAM_DINO_BAIXO = os.path.join("sprites", "dino_baixo.png")
CAM_CACTO = os.path.join("sprites", "cacto.png")
CAM_MISSIL = os.path.join("sprites", "missil.png")
CAM_CHAO = os.path.join("sprites", "chao.png")

fonte = pygame.font.Font(None, 36)

# Banco de dados
con = sqlite3.connect("dados_treino.db")
cur = con.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS acoes (
    treino_id TEXT,
    timestamp TEXT,
    distancia REAL,
    altura REAL,
    tipo INTEGER,
    velocidade REAL,
    acao INTEGER
)
""")
con.commit()
TREINO_ID = f"boot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Sprites
DINO = pygame.transform.scale(pygame.image.load(CAM_DINO).convert_alpha(), (70, 70))
DINO_BAIXO = pygame.transform.scale(pygame.image.load(CAM_DINO_BAIXO).convert_alpha(), (70, 50))
CACTO = pygame.transform.scale(pygame.image.load(CAM_CACTO).convert_alpha(), (50, 100))
MISSIL = pygame.transform.scale(pygame.image.load(CAM_MISSIL).convert_alpha(), (90, 60))
CHAO = pygame.transform.scale(pygame.image.load(CAM_CHAO).convert_alpha(), (800, 50))

clock = pygame.time.Clock()
FPS = 60

# Tkinter
root = tk.Tk()
root.title("Desempenho IA")
fig, ax = plt.subplots(figsize=(6, 4))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

label_pontos = tk.Label(root, text="", font=("Courier", 12))
label_pontos.pack()


meta = 100
melhor_pontuacao = 0
historico_pontos = []


def desenhar_chao():
    for x in range(0, LARGURA, CHAO.get_width()):
        TELA.blit(CHAO, (x, ALTURA - CHAO.get_height()))


def registrar_acao(distancia, altura, tipo, velocidade, acao):
    timestamp = datetime.now().isoformat()
    cur.execute("INSERT INTO acoes VALUES (?, ?, ?, ?, ?, ?, ?)", (TREINO_ID, timestamp, distancia, altura, tipo, velocidade, acao))
    con.commit()


def obter_acao(distancia, altura, tipo, velocidade):
    d = round(distancia, 1)
    h = round(altura, 1)
    v = round(velocidade, 1)
    cur.execute("""
        SELECT acao, COUNT(*) as freq FROM acoes
        WHERE ABS(distancia - ?) < 0.1 AND ABS(altura - ?) < 0.1 AND tipo = ? AND ABS(velocidade - ?) < 0.1
        GROUP BY acao ORDER BY freq DESC LIMIT 1
    """, (d, h, tipo, v))
    row = cur.fetchone()
    if row:
        return int(row[0])
    if tipo == 0 and distancia < 0.2:
        return 0
    elif tipo == 1 and 0.1 < distancia < 0.3:
        return 1
    return 2


def atualizar_grafico():
    ax.clear()
    ax.plot(historico_pontos, marker='o', color='blue')
    ax.axhline(meta, color='green', linestyle='--', label=f"Meta: {meta}")
    ax.set_title("Progresso de Pontuação por Rodada")
    ax.set_xlabel("Rodada")
    ax.set_ylabel("Pontos")
    ax.legend()
    canvas.draw()
    label_pontos.config(text=f"Melhor: {melhor_pontuacao} | Rodadas: {len(historico_pontos)}")
    root.update()


while True:
    dino = DINO
    dino_rect = dino.get_rect(midbottom=(100, 350))
    dino_y = float(dino_rect.y)
    gravidade = 0
    abaixado = False
    tipo_obstaculo = "chao"
    obstaculo = CACTO.get_rect(midbottom=(900, 350))
    pontos = 0
    velocidade = 6

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                root.destroy()
                exit()

        distancia = (obstaculo.x - dino_rect.x) / 800
        altura = obstaculo.y / 400
        tipo = 1 if obstaculo.height < 100 else 0
        vel = min(20, abs(distancia) / 10.0) / 20

        acao = obter_acao(distancia, altura, tipo, vel)

        if acao == 0 and dino_rect.bottom == 350:
            gravidade = -18
        if acao == 1:
            abaixado = True
        else:
            abaixado = False

        registrar_acao(distancia, altura, tipo, vel, acao)

        if abaixado:
            dino = DINO_BAIXO
            dino_rect.height = 50
            dino_rect.bottom = 350
        else:
            dino = DINO
            dino_rect.height = 70
            dino_rect.bottom = min(dino_rect.bottom, 350)

        gravidade += 0.8
        dino_y += gravidade
        dino_rect.y = int(dino_y)

        if dino_rect.bottom > 350:
            dino_rect.bottom = 350
            dino_y = dino_rect.y

        obstaculo.x -= velocidade
        if obstaculo.right < 0:
            pontos += 1
            velocidade = 6 + pontos // 5
            tipo_obstaculo = random.choices(["chao", "voador"], weights=[0.6, 0.4])[0]
            if tipo_obstaculo == "chao":
                obstaculo = CACTO.get_rect(midbottom=(random.randint(800, 1000), 350))
            elif tipo_obstaculo == "voador":
                y_missil = random.randint(220, 240)
                obstaculo = MISSIL.get_rect(topleft=(random.randint(800, 1000), y_missil))

        if dino_rect.colliderect(obstaculo):
            historico_pontos.append(pontos)
            if pontos > melhor_pontuacao:
                melhor_pontuacao = pontos
            atualizar_grafico()
            break

        TELA.fill(BRANCO)
        desenhar_chao()
        TELA.blit(dino, dino_rect)
        if tipo_obstaculo == "chao":
            TELA.blit(CACTO, obstaculo)
        else:
            TELA.blit(MISSIL, obstaculo)
        texto = fonte.render(f"Pontos: {pontos}  Meta: {meta}", True, PRETO)
        TELA.blit(texto, (10, 10))
        pygame.display.update()
        clock.tick(FPS)
