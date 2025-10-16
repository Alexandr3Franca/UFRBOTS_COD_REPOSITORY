# --- Importação das Bibliotecas Necessárias ---
from ultralytics import YOLO  # A biblioteca principal para rodar o modelo de IA.
import cv2                    # OpenCV, para captura de câmera, desenho de formas e exibição de vídeo.
import numpy as np            # Numpy, para operações numéricas (usado pelo YOLO e OpenCV).
import math                   # Biblioteca de matemática, para cálculos trigonométricos e geométricos.
import serial                 # PySerial, para a comunicação via porta serial com o Arduino/Bluetooth.
import time                   # Biblioteca de tempo, para adicionar pequenas pausas (delays).

# --- Definição da Classe Principal do Projeto ---
# Usar uma classe ajuda a organizar o código, mantendo variáveis e funções relacionadas juntas.
class PoseEstimation:
    # --- Método Construtor (__init__) ---
    # Este método é executado automaticamente uma única vez quando criamos um objeto da classe.
    # É usado para configurar tudo o que o programa precisa para começar.
    def __init__(self, video_name):
        # Carrega o modelo de estimativa de pose pré-treinado do YOLO.
        # Este arquivo (.pt) deve estar na mesma pasta do script.
        self.model = YOLO("yolo11n-pose.pt")
        
        # O caminho do vídeo não é usado se a webcam estiver ativa, mas é parte da estrutura.
        self.video_path = video_name
        
        # Fator de escala para redimensionar a janela de exibição no final. 0.5 = 50% do tamanho original.
        self.scale = 1.0
        
        # --- Configuração da Conexão com o Arduino ---
        self.arduino = None  # Inicia a variável do Arduino como nula.
        porta_bluetooth = 'COM7'  # IMPORTANTE: Verifique no seu PC e altere esta porta COM se necessário.
        
        # O bloco 'try...except' tenta se conectar ao Arduino.
        # Se a conexão falhar (carrinho desligado, porta errada), ele avisa o erro mas não trava o programa.
        try:
            self.arduino = serial.Serial(porta_bluetooth, 9600, timeout=1)
            print(f"Conectado ao Arduino na porta {porta_bluetooth}")
            time.sleep(2)  # Uma pequena pausa para estabilizar a conexão serial.
        except serial.SerialException as e:
            print(f"Erro ao conectar ao Arduino: {e}")
            print("O programa continuará em modo de teste visual.")
        
        # Esta variável armazena o último comando enviado.
        # Usamos isso para evitar enviar o mesmo comando repetidamente e sobrecarregar o Bluetooth.
        self.ultimo_comando = ""

    # --- Método Principal de Análise e Controle ---
    # Contém o loop principal que roda continuamente para processar o vídeo.
    def analyze_pose_and_control(self):
        # Cria uma janela com um nome específico. O WINDOW_NORMAL permite redimensioná-la.
        cv2.namedWindow("Controle com YOLO", cv2.WINDOW_NORMAL)
        # Inicia a captura de vídeo da webcam padrão (índice 0).
        cam = cv2.VideoCapture(0)
        
        # Loop principal: continua rodando enquanto a câmera estiver aberta.
        while cam.isOpened():
            # Lê um único frame (uma imagem) da câmera. 'ret' é um booleano (True se a leitura foi bem-sucedida).
            ret, frame = cam.read()
            if not ret:  # Se não conseguir ler o frame, encerra o loop.
                break
            
            # Inverte o frame horizontalmente para criar um "efeito espelho", que é mais intuitivo.
            frame = cv2.flip(frame, 1)
            # Obtém as dimensões do frame (altura, largura) para cálculos de posicionamento.
            height, width, _ = frame.shape
            
            # --- Definições Geométricas do Joystick Virtual ---
            center_x, center_y = width // 2, height // 2  # Ponto central da tela.
            outer_radius = 200  # Raio do círculo externo (a área total do joystick).
            inner_radius = 60   # Raio do círculo interno (a "zona morta" no centro).

            # --- Desenho do Joystick na Tela (Feedback Visual) ---
            # Desenha o círculo externo em verde.
            cv2.circle(frame, (center_x, center_y), outer_radius, (0, 255, 0), 2)
            # Desenha a zona morta em vermelho.
            cv2.circle(frame, (center_x, center_y), inner_radius, (0, 0, 255), 2)
            
            # Calcula os pontos para desenhar as linhas de divisão diagonais (formato de "X").
            offset = int(outer_radius / math.sqrt(2))
            # Desenha as duas linhas diagonais em branco para delimitar visualmente os quadrantes.
            cv2.line(frame, (center_x - offset, center_y - offset), 
                             (center_x + offset, center_y + offset), (255, 255, 255), 1)
            cv2.line(frame, (center_x - offset, center_y + offset), 
                             (center_x + offset, center_y - offset), (255, 255, 255), 1)

            # --- Executa a Detecção de Pose do YOLO no Frame Atual ---
            results = self.model(frame, verbose=False) # verbose=False para não poluir o terminal com logs do YOLO.
            
            # Inicia as variáveis de controle com valores padrão de "parado".
            direcao = 'S'
            velocidade = 0

            # O 'try...except IndexError' evita que o programa quebre se o YOLO não detectar nenhuma pessoa no frame.
            try:
                # Extrai as coordenadas (x, y) dos 17 pontos-chave da primeira pessoa detectada.
                keypoints = results[0].keypoints.xy.cpu().numpy()[0]
                
                # --- Ponto de Controle ---
                # Selecionamos o pulso direito (índice 10) como nosso cursor.
                # Para usar o pulso esquerdo, o índice seria 9.
                # Tudo está invertido
                pulso_x, pulso_y = keypoints[9]

                # --- Lógica de Controle do Joystick em Anel ---
                # Calcula a distância do pulso ao centro usando o Teorema de Pitágoras.
                distance_from_center = math.sqrt((pulso_x - center_x)**2 + (pulso_y - center_y)**2)
                
                # A lógica de controle só é ativada se o pulso estiver dentro do anel (entre o raio interno e externo).
                if inner_radius < distance_from_center <= outer_radius:
                    # Desenha um ponto verde no pulso para mostrar que o controle está ativo.
                    cv2.circle(frame, (int(pulso_x), int(pulso_y)), 10, (0, 255, 0), -1)

                    # --- LÓGICA DE CONTROLE POR ÂNGULO (MAIS ROBUSTA) ---
                    # Calcula a posição do pulso em relação ao centro.
                    delta_x = pulso_x - center_x
                    delta_y = pulso_y - center_y
                    
                    # Calcula o ângulo em graus. Usamos atan2 para obter o quadrante correto.
                    # Multiplicamos delta_y por -1 porque no OpenCV o eixo Y cresce para baixo.
                    angle = math.degrees(math.atan2(-delta_y, delta_x))

                    # Define as zonas de comando (cones) baseadas no ângulo calculado.
                    if -45 <= angle < 45:
                        direcao = 'R'  # Direita
                    elif 45 <= angle < 135:
                        direcao = 'F'  # Frente
                    elif angle >= 135 or angle < -135:
                        direcao = 'L'  # Esquerda
                    elif -135 <= angle < -45:
                        direcao = 'B'  # Trás
                    
                    # Calcula a velocidade (0-9) de forma proporcional à distância do pulso ao centro do anel.
                    velocidade = int( (distance_from_center - inner_radius) / (outer_radius - inner_radius) * 9 )
                
                # Garante que, por algum erro de cálculo, a velocidade nunca passe de 9.
                velocidade = min(velocidade, 9)

                # --- Desenho do Esqueleto Completo (Feedback Visual) ---
                color = (255, 255, 0) # Cor ciano para o esqueleto.
                # Lista de pares de índices de keypoints que devem ser conectados por uma linha.
                connections = [
                    (6, 4), (4, 2), (2, 0), (0, 1), (1, 3), (10, 8), (8, 6), (6, 5),
                    (5, 7), (7, 9), (6, 12), (11, 5), (11, 12), (11, 13), (13, 15),
                    (12, 14), (14, 16)
                ]
                # Itera sobre as conexões e desenha cada linha do esqueleto.
                for start_idx, end_idx in connections:
                    # Verifica se os pontos-chave são válidos (detectados) antes de desenhar.
                    if np.all(keypoints[start_idx] > 0) and np.all(keypoints[end_idx] > 0):
                        cv2.line(frame, tuple(keypoints[start_idx].astype(int)), tuple(keypoints[end_idx].astype(int)), color, 2)

            except IndexError:
                # Se nenhuma pessoa for detectada, o código dentro do 'try' falha e vem para cá.
                # 'pass' significa que ele simplesmente ignora o erro e continua para o próximo frame.
                pass 
            
            # --- Envio do Comando para o Arduino ---
            # Formata a direção e a velocidade em uma única string (ex: "F7", "S0").
            comando_final = f"{direcao}{velocidade}"
            # Envia o comando apenas se a conexão com o Arduino existir e se o comando for novo.
            if self.arduino and self.arduino.is_open and comando_final != self.ultimo_comando:
                self.arduino.write((comando_final + "\n").encode()) # Envia o comando pela porta serial.
                print(f"Comando enviado: {comando_final}")
                self.ultimo_comando = comando_final # Atualiza o último comando enviado.

            # --- Exibição do Frame ---
            # Redimensiona a janela de acordo com o fator de escala definido no construtor.
            window_width = int(width * self.scale)
            window_height = int(height * self.scale)
            cv2.resizeWindow("Controle com YOLO", window_width, window_height)
            # Mostra o frame final (com todos os desenhos) na janela.
            cv2.imshow("Controle com YOLO", frame)

            # Espera por 1 milissegundo. Se a tecla 'q' for pressionada, encerra o loop.
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # --- Finalização do Programa ---
        # Este código é executado quando o loop 'while' termina.
        # Envia um último comando de parada para garantir que o carrinho não continue andando.
        if self.arduino and self.arduino.is_open:
            self.arduino.write(b'S0\n')
            self.arduino.close() # Fecha a conexão serial de forma segura.
        
        cam.release() # Libera o dispositivo da câmera para que outros programas possam usá-la.
        cv2.destroyAllWindows() # Fecha todas as janelas do OpenCV.

# --- Função para Executar o Programa ---
def run_control():
    # Cria uma instância (objeto) da nossa classe PoseEstimation.
    pe = PoseEstimation('video.mp4')
    # Chama o método principal para iniciar a detecção e o controle.
    pe.analyze_pose_and_control()

# --- Ponto de Entrada do Script ---
# A condição __name__ == '__main__' garante que o código abaixo só será executado
# quando você rodar este arquivo diretamente (e não quando ele for importado por outro script).
if __name__ == '__main__':
    run_control()   
