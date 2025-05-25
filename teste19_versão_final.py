import sys # Adicione esta linha!
import pygame, random, time
from pygame.locals import *
import os

# --- VARIÁVEIS DE CONTROL DO JOGO ---
LARGURA_TELA = 400
ALTURA_TELA = 600
VELOCIDADE = 20
GRAVIDADE = 2.5
VELOCIDADE_JOGO = 15  # Velocidade de movimento dos tubos e moedas

LARGURA_CHAO = 2 * LARGURA_TELA
ALTURA_CHAO = 100

LARGURA_TUBO = 80
ALTURA_TUBO = 500

ESPACAMENTO_TUBO = 150  # Espaçamento entre o tubo superior e inferior

# --- ATIVE OU DESATIVE O MODO DEPURAR ---
DEBUG_MODE = True  # Defina como True para ver mensagens de depuração


def debug_print(message):
    """Função para imprimir mensagens de depuração se DEBUG_MODE estiver ativado."""
    if DEBUG_MODE:
        print(message)


# Dicionários para armazenar caminhos de recursos
PATHS_SONS = {
    'wing': 'assets/audio/wing.wav',
    'hit': 'assets/audio/hit.wav',
    'point': 'assets/audio/point.wav'
}

PATHS_SPRITES = {
    'bluebird_up': 'assets/sprites/bluebird-upflap.png',
    'bluebird_mid': 'assets/sprites/bluebird-midflap.png',
    'bluebird_down': 'assets/sprites/bluebird-downflap.png',
    'pipe': 'assets/sprites/pipe-green.png',
    'base': 'assets/sprites/base.png',
    'background': 'assets/sprites/background-day.png',
    'message': 'assets/sprites/message.png',
    'coin': 'assets/moeda certa.png',  # Caminho para a imagem da moeda
    'game_over_text': 'assets/sprites/gameover.png',
    'score_board': 'assets/sprites/placar.jpg',  # ESTE É O PLACAR COM "MEDAL" E "SCORE"
    'button_restart': 'assets/sprites/Screenshot_20250523-130903_Gallery.jpg',  # Botão de Play/Reiniciar
    'button_medal': 'assets/sprites/Screenshot_20250523_130855.jpg',  # Botão da Medalha (Pódio)
    'digit_0': 'assets/sprites/00.png',
    'digit_1': 'assets/sprites/1.png',
    'digit_2': 'assets/sprites/2.png',
    'digit_3': 'assets/sprites/3.png',
    'digit_4': 'assets/sprites/4.png',
    'digit_5': 'assets/sprites/5.png',
    'digit_6': 'assets/sprites/6.png',
    'digit_7': 'assets/sprites/7.png',
    'digit_8': 'assets/sprites/8.png',
    'digit_9': 'assets/sprites/9.png'
}


# --- FUNÇÃO PARA CARREGAR IMAGENS DE FORMA SEGURA ---
def carregar_imagem_com_verificacao(caminho, alpha=True, scale=None):
    """Carrega uma imagem, verifica sua existência e opcionalmente a escala e converte."""
    if not os.path.exists(caminho):
        debug_print(f"ERRO CRÍTICO: Imagem não encontrada no caminho: {caminho}")
        pygame.quit()
        sys.exit()
    try:
        img = pygame.image.load(caminho)
        if scale:
            img = pygame.transform.scale(img, scale)
        if alpha:
            return img.convert_alpha()  # Converte para pixel alpha, para transparência
        else:
            return img.convert()  # Converte para formato de pixel, para otimização
    except pygame.error as e:
        debug_print(f"ERRO AO CARREGAR/CONVERTER IMAGEM {caminho}: {e}")
        pygame.quit()
        sys.exit()


# --- FUNÇÃO PARA CARREGAR SONS DE FORMA SEGURA ---
def carregar_som_com_verificacao(caminho):
    """Carrega um arquivo de áudio, verificando sua existência."""
    if not os.path.exists(caminho):
        debug_print(f"ERRO CRÍTICO: Arquivo de áudio não encontrado no caminho: {caminho}")
        return None  # Retorna None se o arquivo não for encontrado
    try:
        return pygame.mixer.Sound(caminho)
    except pygame.error as e:
        debug_print(f"ERRO AO CARREGAR SOM {caminho}: {e}")
        return None


# --- INICIALIZAÇÃO DO PYGAME ---
pygame.init()

tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption('Flappy Bird')

# --- CARREGAMENTO GLOBAL DE TODOS OS RECURSOS APÓS A INICIALIZAÇÃO DO DISPLAY ---
# A fonte agora será usada para a pontuação em tempo real, e os dígitos para a tela final
fonte_score_ingame = pygame.font.Font(None, 48)

# Carregar imagens originais do pássaro para rotação
IMAGENS_PASSARO_ORIGINAIS = [
    carregar_imagem_com_verificacao(PATHS_SPRITES['bluebird_up']),
    carregar_imagem_com_verificacao(PATHS_SPRITES['bluebird_mid']),
    carregar_imagem_com_verificacao(PATHS_SPRITES['bluebird_down'])
]
IMAGEM_TUBO_ORIGINAL = carregar_imagem_com_verificacao(PATHS_SPRITES['pipe'], scale=(LARGURA_TUBO, ALTURA_TUBO))
IMAGEM_CHAO = carregar_imagem_com_verificacao(PATHS_SPRITES['base'], scale=(LARGURA_CHAO, ALTURA_CHAO))
FUNDO = carregar_imagem_com_verificacao(PATHS_SPRITES['background'], alpha=False, scale=(LARGURA_TELA, ALTURA_TELA))
IMAGEM_INICIO = carregar_imagem_com_verificacao(PATHS_SPRITES['message'])
IMAGEM_MOEDA = carregar_imagem_com_verificacao(PATHS_SPRITES['coin'])  # Carrega a imagem da moeda

# Novas imagens para a tela de Game Over
IMAGEM_GAMEOVER_TEXT = carregar_imagem_com_verificacao(PATHS_SPRITES['game_over_text'])
IMAGEM_SCORE_BOARD = carregar_imagem_com_verificacao(PATHS_SPRITES['score_board'],
                                                     scale=(226, 114))  # ESCALA DO PLACAR AJUSTADA NOVAMENTE!
IMAGEM_BUTTON_RESTART = carregar_imagem_com_verificacao(PATHS_SPRITES['button_restart'],
                                                        scale=(100, 50))  # ESCALA DO BOTÃO DE REINICIAR
IMAGEM_BUTTON_MEDAL = carregar_imagem_com_verificacao(PATHS_SPRITES['button_medal'],
                                                      scale=(100, 50))  # ESCALA DO BOTÃO DA MEDALHA

# Carregar imagens dos dígitos
IMAGENS_DIGITOS = {}
for i in range(10):
    # '00.png' para o 0, '1.png' para o 1, etc.
    if i == 0:
        IMAGENS_DIGITOS[str(i)] = carregar_imagem_com_verificacao(PATHS_SPRITES[f'digit_0'])
    else:
        IMAGENS_DIGITOS[str(i)] = carregar_imagem_com_verificacao(PATHS_SPRITES[f'digit_{i}'])

# Opcional: Escalonar os dígitos se eles forem muito grandes ou pequenos (descomentar e ajustar se necessário)
# Assumindo que as imagens dos dígitos já têm um tamanho consistente ou que o escalonamento abaixo é suficiente.
# Se precisar de ajuste de tamanho, faremos isso na função draw_score_digits.

SOM_ASA = carregar_som_com_verificacao(PATHS_SONS['wing'])
SOM_COLISAO = carregar_som_com_verificacao(PATHS_SONS['hit'])
SOM_PONTO = carregar_som_com_verificacao(PATHS_SONS['point'])

# Variáveis de Estado do Jogo (reiniciadas ao iniciar novo jogo)
pontuacao = 0
atingiu_pontuacao_para_modo_moeda = False
moedas_habilitadas = False
moedas_coletadas_nesta_fase = 0

grupo_moedas = pygame.sprite.Group()  # Grupo para gerenciar as moedas

# Variáveis de recorde
HIGH_SCORE_FILE = "highscore.txt"
high_score = 0

# --- ESTADOS DO JOGO ---
GAME_STATE_START = 0
GAME_STATE_PLAYING = 1
GAME_STATE_GAME_OVER = 2
game_state = GAME_STATE_START  # Define o estado inicial do jogo


# --- FUNÇÕES DE SALVAR/CARREGAR RECORDE ---
def load_high_score():
    """Carrega o recorde de um arquivo."""
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE, 'r') as f:
                return int(f.read().strip())
        except ValueError:
            debug_print(f"AVISO: highscore.txt contém valor inválido. Resetando para 0.")
            return 0
        except Exception as e:
            debug_print(f"ERRO ao carregar highscore: {e}")
            return 0
    return 0


def save_high_score(score):
    """Salva o recorde em um arquivo."""
    try:
        with open(HIGH_SCORE_FILE, 'w') as f:
            f.write(str(int(score)))
    except Exception as e:
        debug_print(f"ERRO ao salvar highscore: {e}")


# Carrega o recorde ao iniciar o programa
high_score = load_high_score()


# --- CLASSES COM MÉTODO 'update()' E ATRIBUTO 'rect' ---
class Passaro(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.imagens_originais = IMAGENS_PASSARO_ORIGINAIS
        self.velocidade = VELOCIDADE
        self.imagem_atual_index = 0
        self.image_original = self.imagens_originais[self.imagem_atual_index]
        self.image = pygame.transform.scale(self.image_original, (self.image_original.get_width() * 1.5,
                                                                  self.image_original.get_height() * 1.5))
        self.rect = self.image.get_rect()
        self.rect.center = (LARGURA_TELA / 6, ALTURA_TELA / 2)
        self.mascara = pygame.mask.from_surface(self.image)
        self.angulo_rotacao = 0
        self.tempo_animacao = 0

    def update(self):
        self.velocidade += GRAVIDADE
        self.rect.y += self.velocidade

        self.tempo_animacao += 1
        if self.tempo_animacao > 5:
            self.tempo_animacao = 0
            self.imagem_atual_index = (self.imagem_atual_index + 1) % 3
            self.image_original = self.imagens_originais[self.imagem_atual_index]

        if self.velocidade < 0:
            self.angulo_rotacao = 25
        else:
            self.angulo_rotacao = max(-90, self.velocidade * -3)

        scaled_image = pygame.transform.scale(self.image_original, (self.image_original.get_width() * 1.5,
                                                                    self.image_original.get_height() * 1.5))
        self.image = pygame.transform.rotate(scaled_image, self.angulo_rotacao)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.mascara = pygame.mask.from_surface(self.image)

    def impulsionar(self):
        self.velocidade = -VELOCIDADE
        self.angulo_rotacao = 25

    def iniciar(self):
        self.tempo_animacao += 1
        if self.tempo_animacao > 5:
            self.tempo_animacao = 0
            self.imagem_atual_index = (self.imagem_atual_index + 1) % 3
            self.image_original = self.imagens_originais[self.imagem_atual_index]
            self.image = pygame.transform.scale(self.image_original, (self.image_original.get_width() * 1.5,
                                                                      self.image_original.get_height() * 1.5))
        self.image = pygame.transform.rotate(self.image, 0)


class Tubo(pygame.sprite.Sprite):
    def __init__(self, invertido, pos_x, tamanho_y, tubo_id, is_transicao=False):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGEM_TUBO_ORIGINAL.copy()
        self.rect = self.image.get_rect()
        self.rect.x = pos_x
        self.passou = False
        self.id = tubo_id
        self.is_transicao = is_transicao
        self.invertido = invertido

        if invertido:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottom = tamanho_y
        else:
            self.rect.top = ALTURA_TELA - tamanho_y

        self.mascara = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x -= VELOCIDADE_JOGO


class Chao(pygame.sprite.Sprite):
    def __init__(self, pos_x):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGEM_CHAO
        self.mascara = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect[0] = pos_x
        self.rect[1] = ALTURA_TELA - ALTURA_CHAO

    def update(self):
        self.rect[0] -= VELOCIDADE_JOGO


# Funções Auxiliares
def esta_fora_da_tela(sprite):
    """Verifica se um sprite saiu completamente da tela pelo lado esquerdo."""
    return sprite.rect[0] < -(sprite.rect.width)


def obter_tubos(pos_x, tubo_id, is_transicao=False):
    """Retorna um par de tubos (superior e inferior) com base na posição e ID."""
    tamanho_buraco = ESPACAMENTO_TUBO

    if is_transicao:
        tamanho_inferior = (ALTURA_TELA - ALTURA_CHAO - tamanho_buraco) / 2
        tubo = Tubo(False, pos_x, tamanho_inferior, tubo_id, is_transicao=is_transicao)
        tubo_invertido = Tubo(True, pos_x, ALTURA_TELA - tamanho_inferior - tamanho_buraco, tubo_id,
                              is_transicao=is_transicao)
    else:
        tamanho = random.randint(100, 300)
        tubo = Tubo(False, pos_x, tamanho, tubo_id, is_transicao=False)
        tubo_invertido = Tubo(True, pos_x, ALTURA_TELA - tamanho - ESPACAMENTO_TUBO, tubo_id, is_transicao=False)

    return tubo, tubo_invertido


def criar_moeda(pos_x):
    """Cria e adiciona uma sprite de moeda ao grupo de moedas."""
    global grupo_moedas, IMAGEM_MOEDA

    moeda_sprite = pygame.sprite.Sprite()
    moeda_sprite.image = pygame.transform.scale(IMAGEM_MOEDA, (50, 50))
    moeda_sprite.rect = moeda_sprite.image.get_rect(center=(pos_x + LARGURA_TUBO // 2, ALTURA_TELA // 2))

    moeda_sprite.update = lambda: setattr(moeda_sprite.rect, 'x', moeda_sprite.rect.x - VELOCIDADE_JOGO)

    grupo_moedas.add(moeda_sprite)
    debug_print(
        f"MOEDA: Moeda criada em X={moeda_sprite.rect.centerx}. Grupo moedas contém: {len(grupo_moedas.sprites())} moedas.")


def reset_game():
    """Reinicia todas as variáveis e sprites para um novo jogo."""
    global pontuacao, atingiu_pontuacao_para_modo_moeda, moedas_habilitadas, moedas_coletadas_nesta_fase, \
        grupo_passaro, grupo_chao, grupo_tubos, grupo_moedas, contador_tubos_gerados, game_state, passaro

    pontuacao = 0
    atingiu_pontuacao_para_modo_moeda = False
    moedas_habilitadas = False
    moedas_coletadas_nesta_fase = 0

    grupo_passaro.empty()
    # Recria a instância do pássaro para garantir que esteja em seu estado inicial
    passaro = Passaro()
    grupo_passaro.add(passaro)

    grupo_chao.empty()
    for i in range(2):
        chao = Chao(LARGURA_CHAO * i)
        grupo_chao.add(chao)

    grupo_tubos.empty()
    grupo_moedas.empty()

    # Gera tubos para a tela de início novamente
    for i in range(2):
        tubos = obter_tubos(LARGURA_TELA * i + 800, -1)
        grupo_tubos.add(tubos[0], tubos[1])

    contador_tubos_gerados = 0
    game_state = GAME_STATE_START  # Volta para a tela de início


def draw_score_digits(score_value, x_pos, y_pos, digit_scale_factor=1.0, alignment='right'):
    """Desenha a pontuação usando as imagens dos dígitos."""
    score_str = str(int(score_value))

    # Pega as dimensões do primeiro dígito para estimar o tamanho
    base_digit_width = IMAGENS_DIGITOS['0'].get_width()
    base_digit_height = IMAGENS_DIGITOS['0'].get_height()

    digit_width = int(base_digit_width * digit_scale_factor)
    digit_height = int(base_digit_height * digit_scale_factor)

    total_width = len(score_str) * digit_width
    current_x = x_pos

    if alignment == 'right':
        current_x = x_pos - total_width
    elif alignment == 'center':
        current_x = x_pos - (total_width / 2)

    for digit_char in score_str:
        digit_image = IMAGENS_DIGITOS[digit_char]

        # Redimensiona o dígito para o tamanho desejado (digit_width, digit_height)
        scaled_digit = pygame.transform.scale(digit_image, (digit_width, digit_height))
        tela.blit(scaled_digit, (current_x, y_pos))
        current_x += digit_width  # Move para a próxima posição do dígito


# --- CRIAÇÃO DE GRUPOS E SPRITES INICIAIS ---
grupo_passaro = pygame.sprite.Group()
passaro = Passaro()
grupo_passaro.add(passaro)

grupo_chao = pygame.sprite.Group()
for i in range(2):
    chao = Chao(LARGURA_CHAO * i)
    grupo_chao.add(chao)

grupo_tubos = pygame.sprite.Group()
# Inicializa os tubos para a tela de início.
for i in range(2):
    tubos = obter_tubos(LARGURA_TELA * i + 800, -1)
    grupo_tubos.add(tubos[0], tubos[1])

contador_tubos_gerados = 0
debug_print(f"INICIALIZAÇÃO: Jogo pronto para iniciar. Pontuação inicial: {pontuacao}")

relogio = pygame.time.Clock()

# --- LOOP PRINCIPAL DO JOGO ---
while True:
    for evento in pygame.event.get():
        if evento.type == QUIT:
            pygame.quit()
            sys.exit()
        if evento.type == KEYDOWN:
            if evento.key == K_SPACE or evento.key == K_UP:
                if game_state == GAME_STATE_START:
                    passaro.impulsionar()
                    if SOM_ASA: SOM_ASA.play()
                    game_state = GAME_STATE_PLAYING
                elif game_state == GAME_STATE_PLAYING:
                    passaro.impulsionar()
                    if SOM_ASA: SOM_ASA.play()
        if evento.type == MOUSEBUTTONDOWN:
            if game_state == GAME_STATE_GAME_OVER:
                mouse_pos = pygame.mouse.get_pos()

                # Posicionamento dos elementos na tela de Game Over para cálculo do clique
                # Textura Game Over
                gameover_text_rect = IMAGEM_GAMEOVER_TEXT.get_rect(center=(LARGURA_TELA / 2, ALTURA_TELA / 2 - 100))

                # Placar (Score Board)
                score_board_rect = IMAGEM_SCORE_BOARD.get_rect(center=(LARGURA_TELA / 2, ALTURA_TELA / 2 + 20))

                # Botões (ajustado para serem relativos ao placar e ao centro da tela)
                button_spacing_x = 60  # Espaçamento horizontal entre os centros dos botões
                button_y_pos = score_board_rect.bottom + 30  # Posição Y dos botões abaixo do placar

                restart_button_rect = IMAGEM_BUTTON_RESTART.get_rect(
                    center=(LARGURA_TELA / 2 - button_spacing_x, button_y_pos))
                medal_button_rect = IMAGEM_BUTTON_MEDAL.get_rect(
                    center=(LARGURA_TELA / 2 + button_spacing_x, button_y_pos))

                if restart_button_rect.collidepoint(mouse_pos):
                    debug_print("CLICOU NO BOTÃO DE REINICIAR!")
                    reset_game()

    tela.blit(FUNDO, (0, 0))  # Desenha o fundo

    if game_state == GAME_STATE_START:
        tela.blit(IMAGEM_INICIO,
                  (LARGURA_TELA / 2 - IMAGEM_INICIO.get_width() / 2, ALTURA_TELA / 2 - IMAGEM_INICIO.get_height() / 2))

        if esta_fora_da_tela(grupo_chao.sprites()[0]):
            grupo_chao.remove(grupo_chao.sprites()[0])
            novo_chao = Chao(LARGURA_CHAO - 20)
            grupo_chao.add(novo_chao)

        passaro.iniciar()  # Anima o pássaro sem gravidade pesada na tela de início
        grupo_chao.update()  # Move o chão

        grupo_passaro.draw(tela)
        grupo_chao.draw(tela)

        # Pontuação em tempo real na tela de início (igual ao jogo, opcional para tela inicial)
        texto_pontuacao_ingame = fonte_score_ingame.render(str(int(pontuacao)), True, (255, 255, 255))
        retangulo_pontuacao_ingame = texto_pontuacao_ingame.get_rect(center=(LARGURA_TELA // 2, 50))
        tela.blit(texto_pontuacao_ingame, retangulo_pontuacao_ingame)


    elif game_state == GAME_STATE_PLAYING:
        debug_print(f"\n--- FRAME INÍCIO ---")
        debug_print(
            f"ESTADO ATUAL: Pontuação: {pontuacao}, Atingiu pontuação para moeda: {atingiu_pontuacao_para_modo_moeda}, Moedas Habilitadas: {moedas_habilitadas}")

        if esta_fora_da_tela(grupo_chao.sprites()[0]):
            grupo_chao.remove(grupo_chao.sprites()[0])
            novo_chao = Chao(LARGURA_CHAO - 20)
            grupo_chao.add(novo_chao)

        # Lógica de geração de tubos ou moedas
        if not moedas_habilitadas:
            if grupo_tubos.sprites() and esta_fora_da_tela(grupo_tubos.sprites()[0]):
                debug_print(f"GERAÇÃO TUBO: Tubo {grupo_tubos.sprites()[0].id} saindo da tela. Removendo.")
                grupo_tubos.remove(grupo_tubos.sprites()[0])
                grupo_tubos.remove(grupo_tubos.sprites()[0])  # Remove o par

                if pontuacao >= 9.0 and not atingiu_pontuacao_para_modo_moeda:
                    debug_print(
                        "GERAÇÃO TUBO: Condição de pontuação (>= 9.0) ATINGIDA! Gerando CANO DE TRANSIÇÃO PARA MODO MOEDA (ID 9998).")
                    tubos_transicao_modo_moeda = obter_tubos(LARGURA_TELA * 1.5, 9998, is_transicao=True)
                    grupo_tubos.add(tubos_transicao_modo_moeda[0], tubos_transicao_modo_moeda[1])
                    atingiu_pontuacao_para_modo_moeda = True
                else:
                    tubos = obter_tubos(LARGURA_TELA * 2, contador_tubos_gerados)
                    grupo_tubos.add(tubos[0], tubos[1])
                    debug_print(f"GERAÇÃO TUBO: Gerado NOVO Tubo ID: {contador_tubos_gerados} (Tubo normal).")
                    contador_tubos_gerados += 1
                    debug_print(f"GERAÇÃO TUBO: Novo contador_tubos_gerados: {contador_tubos_gerados}")
        else:  # Modo Moeda ativado
            debug_print(f"MODO MOEDA: Ativo. Moedas coletadas: {moedas_coletadas_nesta_fase}")

            if moedas_coletadas_nesta_fase >= 10:
                debug_print("MODO MOEDA: 10 moedas coletadas. Transição de volta ao modo canos normal.")
                moedas_habilitadas = False
                atingiu_pontuacao_para_modo_moeda = False
                moedas_coletadas_nesta_fase = 0
                grupo_moedas.empty()
                grupo_tubos.empty()
                contador_tubos_gerados = 0

                tubos_iniciais_normal = obter_tubos(LARGURA_TELA * 1.5, contador_tubos_gerados)
                grupo_tubos.add(tubos_iniciais_normal[0], tubos_iniciais_normal[1])
                contador_tubos_gerados += 1
                debug_print(
                    f"ESTADO PÓS-TRANSIÇÃO: Retornou ao modo tubos. Gerado tubo inicial ID: {contador_tubos_gerados - 1}")
            else:
                if grupo_moedas.sprites() and esta_fora_da_tela(grupo_moedas.sprites()[0]):
                    grupo_moedas.remove(grupo_moedas.sprites()[0])
                    debug_print(f"MODO MOEDA: Moeda removida da tela. Moedas restantes: {len(grupo_moedas.sprites())}")

                if not grupo_moedas.sprites() or grupo_moedas.sprites()[-1].rect.x < LARGURA_TELA - (
                        LARGURA_TUBO + ESPACAMENTO_TUBO + 100):
                    criar_moeda(LARGURA_TELA * 2)
                    debug_print("MODO MOEDA: Nova moeda gerada.")

        # Lógica de somar pontos por passar tubos (apenas para tubos normais)
        if not moedas_habilitadas:
            for tubo in grupo_tubos:
                if not tubo.is_transicao:
                    if tubo.rect.right < passaro.rect.left and not tubo.passou and not tubo.invertido:
                        tubo.passou = True
                        pontuacao += 1.0
                        if SOM_PONTO: SOM_PONTO.play()
                        debug_print(f"PONTUAÇÃO: Pássaro passou por tubo {tubo.id}. Pontuação atual: {pontuacao}")

        grupo_passaro.update()
        grupo_chao.update()
        grupo_tubos.update()
        grupo_moedas.update()

        grupo_passaro.draw(tela)
        grupo_tubos.draw(tela)
        grupo_moedas.draw(tela)
        grupo_chao.draw(tela)

        # Pontuação em tempo real no canto superior
        texto_pontuacao_ingame = fonte_score_ingame.render(str(int(pontuacao)), True, (255, 255, 255))
        retangulo_pontuacao_ingame = texto_pontuacao_ingame.get_rect(center=(LARGURA_TELA // 2, 50))
        tela.blit(texto_pontuacao_ingame, retangulo_pontuacao_ingame)

        # --- DETECÇÃO DE COLISÃO ---
        colisao_tubo = pygame.sprite.groupcollide(grupo_passaro, grupo_tubos, False, False, pygame.sprite.collide_mask)

        if colisao_tubo:
            debug_print("COLISÃO GERAL: Pássaro colidiu com algum(ns) tubo(s).")
            tubo_colidido_alvo = None

            for passaro_sprite_key, tubos_colididos_list in colisao_tubo.items():
                for tubo_sprite in tubos_colididos_list:
                    if tubo_sprite.is_transicao:
                        tubo_colidido_alvo = tubo_sprite
                        debug_print(f"COLISÃO ESPECÍFICA: Priorizando Cano de Transição (ID real: {tubo_sprite.id}).")
                        break
                if tubo_colidido_alvo:
                    break

            if not tubo_colidido_alvo and colisao_tubo:
                for p_list in colisao_tubo.values():
                    if p_list:
                        tubo_colidido_alvo = p_list[0]
                        debug_print(
                            f"COLISÃO ESPECÍFICA: Nenhum cano de transição, usando o primeiro tubo colidido. ID: {tubo_colidido_alvo.id}")
                        break

            if tubo_colidido_alvo:
                if tubo_colidido_alvo.is_transicao and tubo_colidido_alvo.id == 9998:
                    if not moedas_habilitadas:
                        moedas_habilitadas = True
                        debug_print("AÇÃO: CANO DE TRANSIÇÃO (ID 9998) ACIONADO! MODO MOEDA ATIVADO.")
                        grupo_tubos.empty()
                        criar_moeda(passaro.rect.x + 200)
                else:
                    debug_print(f"AÇÃO: COLISÃO COM TUBO ID {tubo_colidido_alvo.id} (NÃO É DE TRANSIÇÃO)! GAME OVER.")
                    if SOM_COLISAO: SOM_COLISAO.play()
                    game_state = GAME_STATE_GAME_OVER
                    if pontuacao > high_score:
                        high_score = pontuacao
                        save_high_score(high_score)
                        debug_print(f"NOVO RECORDE: {high_score}")

        # Coleta de moedas
        moedas_coletadas_sprites = pygame.sprite.groupcollide(grupo_passaro, grupo_moedas, False, True,
                                                              pygame.sprite.collide_mask)
        if moedas_coletadas_sprites:
            for passaro_colidido, lista_moedas in moedas_coletadas_sprites.items():
                for moeda_sprite in lista_moedas:
                    pontuacao += 10
                    moedas_coletadas_nesta_fase += 1
                    if SOM_PONTO: SOM_PONTO.play()
                    debug_print(
                        f"MOEDA: MOEDA COLETADA! Total nesta fase: {moedas_coletadas_nesta_fase}. Pontuação: {pontuacao}")

        # Colisão com o chão
        if pygame.sprite.groupcollide(grupo_passaro, grupo_chao, False, False, pygame.sprite.collide_mask):
            debug_print("AÇÃO: COLISÃO COM O CHÃO! GAME OVER.")
            if SOM_COLISAO: SOM_COLISAO.play()
            game_state = GAME_STATE_GAME_OVER
            if pontuacao > high_score:
                high_score = pontuacao
                save_high_score(high_score)
                debug_print(f"NOVO RECORDE: {high_score}")
        debug_print(f"--- FRAME FIM ---")

    elif game_state == GAME_STATE_GAME_OVER:
        # Desenha o fundo e o chão parado
        tela.blit(FUNDO, (0, 0))
        grupo_chao.draw(tela)  # Desenha o chão na posição final
        grupo_tubos.draw(tela)  # Desenha os tubos na posição final (se houver)
        grupo_passaro.draw(tela)  # Desenha o pássaro na posição final (colidido)

        # Desenha o texto "Game Over"
        gameover_text_rect = IMAGEM_GAMEOVER_TEXT.get_rect(center=(LARGURA_TELA / 2, ALTURA_TELA / 2 - 100))
        tela.blit(IMAGEM_GAMEOVER_TEXT, gameover_text_rect)

        # Desenha o placar (score board)
        score_board_rect = IMAGEM_SCORE_BOARD.get_rect(center=(LARGURA_TELA / 2, ALTURA_TELA / 2 + 20))
        tela.blit(IMAGEM_SCORE_BOARD, score_board_rect)

        # Desenha a pontuação atual no placar (SCORE)
        digit_scale_factor = 0.8

        # AJUSTADO: Coordenadas relativas ao centro do placar (score_board_rect.centerx, score_board_rect.centery)
        score_x_offset_relative = 60
        score_y_offset_relative = -15

        best_x_offset_relative = 60
        best_y_offset_relative = 20

        draw_score_digits(pontuacao, score_board_rect.centerx + score_x_offset_relative,
                          score_board_rect.centery + score_y_offset_relative, digit_scale_factor, alignment='right')
        draw_score_digits(high_score, score_board_rect.centerx + best_x_offset_relative,
                          score_board_rect.centery + best_y_offset_relative, digit_scale_factor, alignment='right')

        # Desenha os botões ABAIXO do placar
        button_spacing_x = 60  # Espaçamento horizontal entre os centros dos botões
        button_y_pos = score_board_rect.bottom + 30  # Posição Y dos botões abaixo do placar

        restart_button_rect = IMAGEM_BUTTON_RESTART.get_rect(center=(LARGURA_TELA / 2 - button_spacing_x, button_y_pos))
        medal_button_rect = IMAGEM_BUTTON_MEDAL.get_rect(center=(LARGURA_TELA / 2 + button_spacing_x, button_y_pos))

        tela.blit(IMAGEM_BUTTON_RESTART, restart_button_rect)
        tela.blit(IMAGEM_BUTTON_MEDAL, medal_button_rect)

    pygame.display.update()
    relogio.tick(15)  # Mantenha 15 FPS para o jogo base, pode aumentar para 30 ou 60 para maior fluidez