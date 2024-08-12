import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
import pyaudio
import socket
import threading

# Funções para controlar o microfone e som do sistema
def toggle_microphone():
    global mic_active
    mic_active = not mic_active
    if mic_active:
        print("Microfone ligado")
    else:
        print("Microfone desligado")

def toggle_system_sound():
    global sound_active
    sound_active = not sound_active
    if sound_active:
        print("Som do sistema ligado")
    else:
        print("Som do sistema desligado")

# Função para servir o áudio via streaming
def stream_audio():
    global mic_active, sound_active

    # Configuração do PyAudio
    p = pyaudio.PyAudio()

    # Configurações de áudio
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100

    # Configurando a entrada de áudio
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    # Configuração do socket para streaming
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 12345))  # Escuta em todas as interfaces de rede na porta 12345
    server_socket.listen(1)
    print("Aguardando conexão para streaming de áudio...")
    
    conn, addr = server_socket.accept()
    print(f"Conectado a: {addr}")

    try:
        while True:
            if mic_active or sound_active:
                data = stream.read(CHUNK)
                conn.sendall(data)
    except KeyboardInterrupt:
        print("Encerrando streaming")
    finally:
        # Encerrar o streaming e liberar recursos
        stream.stop_stream()
        stream.close()
        p.terminate()
        conn.close()
        server_socket.close()

# Função principal para a interface gráfica
def main():
    global mic_active, sound_active
    mic_active = True  # O microfone começa ligado
    sound_active = True  # O som do sistema começa ligado

    # Iniciando o aplicativo PyQt
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle('Controle de Áudio e Streaming')

    # Layout
    layout = QVBoxLayout()

    # Rótulos de status
    mic_label = QLabel("Microfone: Ligado")
    sound_label = QLabel("Som do Sistema: Ligado")
    layout.addWidget(mic_label)
    layout.addWidget(sound_label)

    # Botões de controle
    mic_button = QPushButton("Ligar/Desligar Microfone")
    sound_button = QPushButton("Ligar/Desligar Som do Sistema")
    layout.addWidget(mic_button)
    layout.addWidget(sound_button)

    # Botão de sair
    exit_button = QPushButton("Sair")
    layout.addWidget(exit_button)

    # Funções dos botões
    def on_mic_button_clicked():
        toggle_microphone()
        mic_label.setText(f"Microfone: {'Ligado' if mic_active else 'Desligado'}")

    def on_sound_button_clicked():
        toggle_system_sound()
        sound_label.setText(f"Som do Sistema: {'Ligado' if sound_active else 'Desligado'}")

    def on_exit_button_clicked():
        print("Saindo da aplicação...")
        app.quit()  # Encerra a aplicação

    mic_button.clicked.connect(on_mic_button_clicked)
    sound_button.clicked.connect(on_sound_button_clicked)
    exit_button.clicked.connect(on_exit_button_clicked)

    # Aplicando o layout à janela
    window.setLayout(layout)
    window.show()

    # Iniciar o servidor de streaming em uma nova thread
    streaming_thread = threading.Thread(target=stream_audio, daemon=True)
    streaming_thread.start()

    # Executar o aplicativo
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
