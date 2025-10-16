import pygame
import serial 
import time

#A porta bluetooth, identificar nas configuracoes bluetooth do dispositivo
porta_bluetooth = 'COM7'
velocidade_serial = 9600

try:
    arduino = serial.Serial(porta_bluetooth, velocidade_serial, timeout=1)
    print(f"Conectado ao Arduino na porta {porta_bluetooth}")
    time.sleep(2)
except serial.SerialException as e:
    print(f"Erro ao conectar{e}")
    print("Verifique o numero da porta COM e se o carrinho esta ligado e pareado")
    exit()

#Inicializa o Pygame e o Joystick
pygame.init()
if pygame.joystick.get_count() == 0:
    print("Falta o joystick")
    exit()
joystick = pygame.joystick.Joystick(0)
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
