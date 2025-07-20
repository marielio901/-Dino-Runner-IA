🦖 Dino IA Runner
Este é um projeto onde um dinossauro aprende a jogar sozinho, baseado em ações humanas gravadas. A IA treina com os dados, aprende com os próprios erros e melhora a cada rodada.

🎮 Como funciona
Você joga no app.py, e o jogo grava suas decisões (pular, abaixar ou continuar) junto com os dados do obstáculo.

No trilha_neural.py, 5 dinos treinam ao mesmo tempo, tomando decisões com base no histórico. Eles aprendem e mostram os resultados em tempo real com gráficos.

O boot01.py e boot02.py são versões da IA jogando sozinha. O segundo é mais esperto, treinado com base nos dados acumulados.

📊 Painel de desempenho
Durante o treino, o trilha_neural.py abre uma janela com:

Gráfico de acertos e erros

Média de desempenho

Crescimento de aprendizagem

Ranking dos dinos

Tudo atualizado em tempo real.
