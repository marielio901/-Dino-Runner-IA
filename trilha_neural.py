# trilha_neural.py
# Simulação de múltiplos dinos (5) treinando com base no histórico salvo e gerando novos dados sem dependências externas + painel tkinter

import pygame
import random
import os
import sqlite3
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

pygame.init()

LARGURA, ALTURA = 800, 400
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Dino Runner - Treinamento Neural")

PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)

CAM_DINO = os.path.join("sprites", "dino.png")
CAM_DINO_BAIXO = os.path.join("sprites", "dino_baixo.png")
CAM_CACTO = os.path.join("sprites", "cacto.png")
CAM_MISSIL = os.path.join("sprites", "missil.png")
CAM_CHAO = os.path.join("sprites", "chao.png")

fonte = pygame.font.Font(None, 26)

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
TREINO_ID = f"trilha_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

DINO_IMG = pygame.transform.scale(pygame.image.load(CAM_DINO).convert_alpha(), (70, 70))
DINO_BAIXO_IMG = pygame.transform.scale(pygame.image.load(CAM_DINO_BAIXO).convert_alpha(), (70, 50))
CACTO = pygame.transform.scale(pygame.image.load(CAM_CACTO).convert_alpha(), (50, 100))
MISSIL = pygame.transform.scale(pygame.image.load(CAM_MISSIL).convert_alpha(), (90, 60))
CHAO = pygame.transform.scale(pygame.image.load(CAM_CHAO).convert_alpha(), (800, 50))

clock = pygame.time.Clock()
FPS = 60

# Inicializa janela tkinter
root = tk.Tk()
root.title("Desempenho dos Dinos")
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
plt.subplots_adjust(hspace=0.5)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

label_info = tk.Label(root, text="Análise de desempenho", font=("Arial", 12, "bold"))
label_info.pack()

stat_frame = tk.Frame(root)
stat_frame.pack()

label_acertos = tk.Label(stat_frame, text="", font=("Courier", 10))
label_acertos.grid(row=0, column=0, padx=10)
label_erros = tk.Label(stat_frame, text="", font=("Courier", 10))
label_erros.grid(row=1, column=0, padx=10)
label_variacao = tk.Label(stat_frame, text="", font=("Courier", 10))
label_variacao.grid(row=2, column=0, padx=10)
label_aprendizado = tk.Label(stat_frame, text="", font=("Courier", 10))
label_aprendizado.grid(row=3, column=0, padx=10)

class DinoIA:
    def __init__(self, x):
        self.img = DINO_IMG
        self.baixo = False
        self.rect = self.img.get_rect(midbottom=(x, 350))
        self.x = x
        self.y = float(self.rect.y)
        self.gravidade = 0
        self.vivo = True
        self.pontos = 0
        self.acertos = 0
        self.erros = 0

    def atualizar_estado(self):
        if self.baixo:
            self.img = DINO_BAIXO_IMG
            self.rect.height = 50
            self.rect.bottom = 350
        else:
            self.img = DINO_IMG
            self.rect.height = 70
            self.rect.bottom = min(self.rect.bottom, 350)

        self.gravidade += 0.8
        self.y += self.gravidade
        self.rect.y = int(self.y)

        if self.rect.bottom > 350:
            self.rect.bottom = 350
            self.y = self.rect.y

    def desenhar(self):
        TELA.blit(self.img, self.rect)

def desenhar_chao():
    for x in range(0, LARGURA, CHAO.get_width()):
        TELA.blit(CHAO, (x, ALTURA - CHAO.get_height()))

def carregar_acao_treinada(distancia, altura, tipo, velocidade):
    cur.execute("SELECT acao FROM acoes WHERE tipo = ? ORDER BY ABS(distancia - ?) + ABS(altura - ?) + ABS(velocidade - ?) LIMIT 1", (tipo, distancia, altura, velocidade))
    resultado = cur.fetchone()
    if resultado:
        return resultado[0]
    return random.choice([0, 1, 2])

dinos = [DinoIA(100 + i * 100) for i in range(5)]
tipo_obstaculo = "chao"
obstaculo = CACTO.get_rect(midbottom=(900, 350))
velocidade = 6
historico = [[] for _ in range(5)]

obstaculos_passados = 0

def atualizar_graficos():
    ax1.clear()
    ax2.clear()

    acertos = [d.acertos for d in dinos]
    erros = [d.erros for d in dinos]
    barras = np.arange(len(dinos))

    ax1.bar(barras, acertos, color='green')
    ax1.set_title("Acertos")
    ax1.set_xticks(barras)
    ax1.set_xticklabels([f"D{i+1}" for i in barras])

    ax2.bar(barras, erros, color='red')
    ax2.set_title("Erros")
    ax2.set_xticks(barras)
    ax2.set_xticklabels([f"D{i+1}" for i in barras])

    media_acertos = np.mean(acertos)
    media_erros = np.mean(erros)
    variacao = np.std(np.array(acertos) - np.array(erros))
    crescimento = np.mean([np.mean(h[-10:]) if len(h) >= 10 else 0 for h in historico])

    label_acertos.config(text=f"Média de Acertos: {media_acertos:.2f}")
    label_erros.config(text=f"Média de Erros: {media_erros:.2f}")
    label_variacao.config(text=f"Variação Acerto/Erro: {variacao:.2f}")
    label_aprendizado.config(text=f"Crescimento Médio (10 últimas): {crescimento:.2f}")

    canvas.draw()
    root.update()

while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            root.destroy()
            exit()

    for idx, dino in enumerate(dinos):
        if not dino.vivo:
            continue

        distancia = (obstaculo.x - dino.rect.x) / 800
        altura = obstaculo.y / 400
        tipo = 1 if obstaculo.height < 100 else 0
        vel = min(20, abs(distancia) / 10.0) / 20

        acao = carregar_acao_treinada(distancia, altura, tipo, vel)

        if acao == 0 and dino.rect.bottom == 350:
            dino.gravidade = -18 + random.uniform(-1, 1)
        if acao == 1:
            dino.baixo = True
        else:
            dino.baixo = False

        cur.execute("INSERT INTO acoes VALUES (?, ?, ?, ?, ?, ?, ?)", (TREINO_ID, datetime.now().isoformat(), distancia, altura, tipo, vel, acao))
        con.commit()
        dino.atualizar_estado()
        if dino.rect.colliderect(obstaculo):
            dino.vivo = False
            dino.erros += 1
            historico[idx].append(dino.pontos)
        else:
            dino.acertos += 1

    if all(not d.vivo for d in dinos):
        dinos = [DinoIA(100 + i * 100) for i in range(5)]
        obstaculo = CACTO.get_rect(midbottom=(900, 350))
        velocidade = 6
        continue

    obstaculo.x -= velocidade
    if obstaculo.right < 0:
        for d in dinos:
            if d.vivo:
                d.pontos += 1
        velocidade += 1
        obstaculos_passados += 1
        tipo_obstaculo = random.choices(["chao", "voador"], weights=[0.6, 0.4])[0]
        if tipo_obstaculo == "chao":
            obstaculo = CACTO.get_rect(midbottom=(random.randint(800, 1000), 350))
        else:
            y_missil = random.randint(220, 240)
            obstaculo = MISSIL.get_rect(topleft=(random.randint(800, 1000), y_missil))

    TELA.fill(BRANCO)
    desenhar_chao()
    for dino in dinos:
        if dino.vivo:
            dino.desenhar()
    if tipo_obstaculo == "chao":
        TELA.blit(CACTO, obstaculo)
    else:
        TELA.blit(MISSIL, obstaculo)
    texto = fonte.render(f"Vel: {velocidade}", True, PRETO)
    TELA.blit(texto, (10, 10))
    pygame.display.update()
    clock.tick(FPS)
    atualizar_graficos()
