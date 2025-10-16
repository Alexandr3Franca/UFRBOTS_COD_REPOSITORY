from ultralytics import YOLO
import cv2
import matplotlib.pyplot as plt
import numpy as np
import time

# Carregando o modelo

def compute_angle(start, middle, end):
    vector1 = middle - start
    vector2 = end - middle
    dot_product = np.dot(vector1, vector2)
    magnitude_v1 = np.linalg.norm(vector1)
    magnitude_v2 = np.linalg.norm(vector2)
    cos_angle = dot_product / (magnitude_v1*magnitude_v2)
    angle_rad = np.arccos(np.clip(cos_angle, -1.0, 1.0))
    angle_deg = np.degrees(angle_rad)
    return angle_deg

class PoseEstimation:
    def __init__(self, video_name):
        self.model = YOLO("yolo11n-pose.pt") #carrega o modelo
        self.active_keypoints = range(17) #[11,13,15]
        self.video_path = video_name
        self.scale = 1.0
        current_fps = 24
        desired_fps = 10
        self.skip_factor = current_fps // desired_fps

    def analyze_pose(self, show_angle=False):
        frame_count = 0
        frame_leg_only = 200
        color = (255,255,0)

        window_name = "KeyPoints on Video"

        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cam = cv2.VideoCapture(0)
        while cam.isOpened():
            ret, frame = cam.read()
            if not ret:
                break
            #frame_count +=1
            #if frame_count % self.skip_factor != 0:
            #    continue
            height, width, _ = frame.shape
            window_width = int(frame.shape[1] * self.scale)
            window_height = int(frame.shape[1] * self.scale)
            cv2.resizeWindow(window_name, window_width, window_height)

            results = self.model(frame)
            keypoints = results[0].keypoints.xy.cpu().numpy()[0]

            #for i in range(len(self.active_keypoints)-1):
            cv2.line(frame, tuple(keypoints[self.active_keypoints[6]].astype(int)),
                            tuple(keypoints[self.active_keypoints[4]].astype(int)), color, 2)
            
            cv2.line(frame, tuple(keypoints[self.active_keypoints[4]].astype(int)),
                            tuple(keypoints[self.active_keypoints[2]].astype(int)), color, 2)
            cv2.line(frame, tuple(keypoints[self.active_keypoints[2]].astype(int)),
                            tuple(keypoints[self.active_keypoints[0]].astype(int)), color, 2)
            cv2.line(frame, tuple(keypoints[self.active_keypoints[0]].astype(int)),
                            tuple(keypoints[self.active_keypoints[1]].astype(int)), color, 2)
            cv2.line(frame, tuple(keypoints[self.active_keypoints[1]].astype(int)),
                            tuple(keypoints[self.active_keypoints[3]].astype(int)), color, 2)
            
            cv2.line(frame, tuple(keypoints[self.active_keypoints[10]].astype(int)),
                            tuple(keypoints[self.active_keypoints[8]].astype(int)), color, 2)
            cv2.line(frame, tuple(keypoints[self.active_keypoints[8]].astype(int)),
                            tuple(keypoints[self.active_keypoints[6]].astype(int)), color, 2)
            cv2.line(frame, tuple(keypoints[self.active_keypoints[6]].astype(int)),
                            tuple(keypoints[self.active_keypoints[5]].astype(int)), color, 2)
            cv2.line(frame, tuple(keypoints[self.active_keypoints[5]].astype(int)),
                            tuple(keypoints[self.active_keypoints[7]].astype(int)), color, 2)
            cv2.line(frame, tuple(keypoints[self.active_keypoints[7]].astype(int)),
                            tuple(keypoints[self.active_keypoints[9]].astype(int)), color, 2)
            cv2.line(frame, tuple(keypoints[self.active_keypoints[6]].astype(int)),
                            tuple(keypoints[self.active_keypoints[12]].astype(int)), color, 2)
            cv2.line(frame, tuple(keypoints[self.active_keypoints[11]].astype(int)),
                            tuple(keypoints[self.active_keypoints[5]].astype(int)), color, 2)
            cv2.line(frame, tuple(keypoints[self.active_keypoints[11]].astype(int)),
                            tuple(keypoints[self.active_keypoints[12]].astype(int)), color, 2)
            cv2.line(frame, tuple(keypoints[self.active_keypoints[11]].astype(int)),
                            tuple(keypoints[self.active_keypoints[13]].astype(int)), color, 2)
            cv2.line(frame, tuple(keypoints[self.active_keypoints[13]].astype(int)),
                            tuple(keypoints[self.active_keypoints[15]].astype(int)), color, 2)
            cv2.line(frame, tuple(keypoints[self.active_keypoints[12]].astype(int)),
                            tuple(keypoints[self.active_keypoints[14]].astype(int)), color, 2)
            cv2.line(frame, tuple(keypoints[self.active_keypoints[14]].astype(int)),
                            tuple(keypoints[self.active_keypoints[16]].astype(int)), color, 2)
            # draw joy
            center_x = 150
            center_y = 150
            radius = 150
            cv2.circle(frame, (center_x, center_y), radius, color,2)
            ##########


            #self.draw_joy(frame)
            frame = cv2.flip(frame, 1)
            cv2.imshow(window_name, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cam.release()
        cv2.destroyAllWindows()

def run_analyze_pose(show_angle):
    pe = PoseEstimation('bmu.mp4')
    pe.analyze_pose(show_angle=show_angle)

if __name__ == '__main__':
    run_analyze_pose(show_angle=True)
#Inicializa o Pygame e o Joystick
pygame.init()
joystick = analyse_pose
joystick.init()
print(f"Joystick'{joystick.get_name()}' inicializado ")

#Para nao enviar comandos repetidos
ultimo_comando =""

try:
    while True:
        pygame.event.pump() #Atualiza estado

        #le os eixos
        eixo_y = joystick.get_axis(1)
        eixo_x = joystick.get_axis(0)

        # Logica para comandos
        # 1. Define a direcao com base no eixo
        if eixo_y < -0.5:
            direcao = 'F' # Frente
        elif eixo_y > 0.5:
            direcao = 'B' # Tras
        elif eixo_x < -0.5:
            direcao = 'L' # Esquerda
        elif eixo_x > 0.5:
            direcao = 'R' # Direita
        else:
            direcao = 'S' # Parado 

        #  Define a velocidade com base na inclinacao do eixo
        if direcao in ['F', 'B']:
            velocidade = int(abs(eixo_y) * 9)
        elif direcao in ['L', 'R']:
            velocidade = int(abs(eixo_x) * 9)
        else:
            velocidade = 0
        velocidade = min(velocidade, 9) # Garante que o valor nunca passe de 9

        # Monta o comando final
        comando_final = f"{direcao}{velocidade}"

        #Envia o comando para o carrinho (apenas se for diferente do anterior)
        if comando_final != ultimo_comando:
            arduino.write((comando_final + "\n").encode()) # Envia os dados pela porta serial Bluetooth
            print(f"Comando enviado: {comando_final}")
            ultimo_comando = comando_final

        time.sleep(0.05) # Pausa de 50ms para nao sobrecarregar

except KeyboardInterrupt:
    print("\nPrograma encerrado pelo usuario.")
finally:
    # Garante que o carro pare quando o programa for fechado
    print("Enviando comando de parada final...")
    arduino.write(b'S0')
    arduino.close()
    print("Conexao encerrada.")    
