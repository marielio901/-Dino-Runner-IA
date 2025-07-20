# boot02.py — IA treinada baseada em aprendizado histórico aprimorado

import pygame
import random
import os
import sqlite3
from datetime import datetime
import numpy as np
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

pygame.init()

LARGURA, ALTURA = 800, 400
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Dino Runner - Boot 02 IA Aprimorada")

PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)

CAM_DINO = os.path.join("sprites", "dino.png")
CAM_DINO_BAIXO = os.path.join("sprites", "dino_baixo.png")
CAM_CACTO = os.path.join("sprites", "cacto.png")
CAM_MISSIL = os.path.join("sprites", "missil.png")
CAM_CHAO = os.path.join("sprites", "chao.png")

fonte = pygame.font.Font(None, 36)

con = sqlite3.connect("dados_treino.db")
cur = con.cursor()
TREINO_ID = f"boot2_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

DINO = pygame.transform.scale(pygame.image.load(CAM_DINO).convert_alpha(), (70, 70))
DINO_BAIXO = pygame.transform.scale(pygame.image.load(CAM_DINO_BAIXO).convert_alpha(), (70, 50))
CACTO = pygame.transform.scale(pygame.image.load(CAM_CACTO).convert_alpha(), (50, 100))
MISSIL = pygame.transform.scale(pygame.image.load(CAM_MISSIL).convert_alpha(), (90, 60))
CHAO = pygame.transform.scale(pygame.image.load(CAM_CHAO).convert_alpha(), (800, 50))

clock = pygame.time.Clock()
FPS = 60

# Tkinter UI para performance
root = tk.Tk()
root.title("Boot 02 - Análise de Desempenho")
fig, ax = plt.subplots()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()
label = tk.Label(root, text="Rodadas e Pontos", font=("Courier", 12))
label.pack()

resultados = []
meta = 100


def desenhar_chao():
    for x in range(0, LARGURA, CHAO.get_width()):
        TELA.blit(CHAO, (x, ALTURA - CHAO.get_height()))


def registrar_acao(dist, alt, tipo, vel, acao):
    cur.execute("INSERT INTO acoes VALUES (?, ?, ?, ?, ?, ?, ?)",
                (TREINO_ID, datetime.now().isoformat(), dist, alt, tipo, vel, acao))
    con.commit()


def obter_melhor_acao(distancia, altura, tipo, velocidade):
    cur.execute("""
        SELECT acao FROM acoes
        WHERE tipo = ?
        ORDER BY ABS(distancia - ?) + ABS(altura - ?) + ABS(velocidade - ?) ASC
        LIMIT 5
    """, (tipo, distancia, altura, velocidade))
    rows = cur.fetchall()
    if rows:
        acoes = [r[0] for r in rows]
        return max(set(acoes), key=acoes.count)
    return random.choice([0, 1, 2])


def atualizar_grafico():
    ax.clear()
    ax.plot(resultados, label="Pontos")
    ax.axhline(meta, color='red', linestyle='--', label="Meta")
    ax.set_title("Desempenho por Rodada")
    ax.set_xlabel("Rodadas")
    ax.set_ylabel("Pontos")
    ax.legend()
    canvas.draw()
    root.update()

# Loop de treino
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

        acao = obter_melhor_acao(distancia, altura, tipo, vel)

        if acao == 0 and dino_rect.bottom == 350:
            gravidade = -18
        abaixado = acao == 1

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
            else:
                y_missil = random.randint(220, 240)
                obstaculo = MISSIL.get_rect(topleft=(random.randint(800, 1000), y_missil))

        if dino_rect.colliderect(obstaculo):
            resultados.append(pontos)
            atualizar_grafico()
            break

        TELA.fill(BRANCO)
        desenhar_chao()
        TELA.blit(dino, dino_rect)
        if tipo_obstaculo == "chao":
            TELA.blit(CACTO, obstaculo)
        else:
            TELA.blit(MISSIL, obstaculo)
        texto = fonte.render(f"Pontos: {pontos}", True, PRETO)
        TELA.blit(texto, (10, 10))
        pygame.display.update()
        clock.tick(FPS)
