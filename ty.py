import time
import docx2txt # Usado para ler arquivos docx
import PyPDF2 # Usado para ler arquivos pdf
import os
import pygame # Usado para tocar música
from PyQt5 import QtWidgets, QtCore, QtGui
from gtts import gTTS # Usado para converter texto em fala

def read_file(file_path):
    try:
        if file_path.split(".")[-1] == 'txt':
            with open(file_path) as text_to_read:
                return text_to_read.read()
        elif file_path.split(".")[-1] == 'docx':
            return docx2txt.process(file_path)
        elif file_path.split(".")[-1] == 'pdf':
            pdfFileObj = open(file_path, 'rb') 
            pdfReader = PyPDF2.PdfFileReader(pdfFileObj) 
            pdf_text = ''
            for page_num in range(pdfReader.numPages):
                pageObj = pdfReader.getPage(page_num)
                pdf_text += pageObj.extractText()
            pdfFileObj.close() 
            return pdf_text
        else:
            print('Arquivo não suportado!')
            return None
    except IOError as e:
        print(f'Erro ao ler o arquivo: {str(e)}')
        return None

# Classe para criar um novo thread para a criação do arquivo de áudio
class AudioThread(QtCore.QThread):
    progress = QtCore.pyqtSignal(int)
    finished = QtCore.pyqtSignal()
    def __init__(self, text, filename):
        super(AudioThread, self).__init__()
        self.text = text
        self.filename = filename

    # Função que é executada quando o thread é iniciado
    def run(self):
        try:
            # Cria um objeto gTTS com o texto e a linguagem especificada
            tts = gTTS(text=self.text, lang='pt-br')
            # Emite um sinal de progresso para cada porcentagem de progresso
            for i in range(1, 101):
                self.progress.emit(i)
                time.sleep(0.01)
            # Salva o objeto gTTS como um arquivo mp3
            tts.save(self.filename)
            # Emite um sinal de que o thread terminou
            self.finished.emit()
        except Exception as e:
            print(f'Erro ao criar o arquivo de áudio: {str(e)}')

# Classe para a janela principal da aplicação
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle('Leitor de texto')
        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.layout = QtWidgets.QVBoxLayout(self.centralwidget)

        # Botão para abrir o menu de opções
        self.b_button = QtWidgets.QPushButton('</>')  # Botão quadrado '</>'
        self.b_button.setFixedSize(30, 30)  # Tamanho do botão
        self.b_button.setStyleSheet("background-color: lightblue")  # Cor do botão
        self.layout.addWidget(self.b_button, alignment=QtCore.Qt.AlignLeft)  # Posição do botão

        # Label para mostrar mensagens ao usuário
        self.label = QtWidgets.QLabel('Selecione um arquivo para começar!\n(Insira apenas "docx", "pdf" e "txt")')
        self.label.setAlignment(QtCore.Qt.AlignCenter)  # Adicionado para centralizar o texto
        self.layout.addWidget(self.label)

        # Botão para abrir a janela de diálogo de entrada de texto
        self.text_button = QtWidgets.QPushButton('Digitar texto')  
        self.text_button.clicked.connect(self.input_text) # Conecta o botão a função input_text
        self.text_button.setStyleSheet("background-color: lightblue")
        self.layout.addWidget(self.text_button)

        # Botão para abrir a janela de diálogo de seleção de arquivo
        self.file_button = QtWidgets.QPushButton('Selecionar arquivo')
        self.file_button.clicked.connect(self.select_file) # Conecta o botão a função select_file
        self.file_button.setStyleSheet("background-color: lightblue")
        self.layout.addWidget(self.file_button)

        # Botão para iniciar a criação do arquivo de áudio
        self.read_button = QtWidgets.QPushButton('Criar áudio')
        self.read_button.clicked.connect(self.create_audio_file) # Conecta o botão a função create_audio_file
        self.read_button.setStyleSheet("background-color: lightblue")
        self.layout.addWidget(self.read_button)

        # Label para mostrar o tempo de leitura do arquivo de áudio
        self.time_label = QtWidgets.QLabel('')
        self.layout.addWidget(self.time_label)

        # Botão para iniciar ou pausar a reprodução do arquivo de áudio
        self.play_button = QtWidgets.QPushButton('Play')
        self.play_button.clicked.connect(self.play_pause_audio) # Conecta o botão a função play_pause_audio
        self.play_button.setStyleSheet("background-color: green")
        self.layout.addWidget(self.play_button)

        # Slider para controlar a velocidade de reprodução do arquivo de áudio
        self.speed_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal) # Adicionado um slider para controlar a velocidade
        self.speed_slider.setMinimum(50) # Velocidade mínima
        self.speed_slider.setMaximum(200) # Velocidade máxima
        self.speed_slider.setValue(100) # Velocidade inicial
        self.speed_slider.setTickPosition(QtWidgets.QSlider.TicksBelow) # Posição dos ticks
        self.speed_slider.setTickInterval(10) # Intervalo entre os ticks
        self.layout.addWidget(self.speed_slider)

        # Variáveis para armazenar o caminho do arquivo selecionado e do arquivo de áudio criado
        self.file_path = ''
        self.audio_file = ''

        pygame.mixer.init()  

        self.is_playing = False

    def select_file(self):
        # Função para selecionar o arquivo
        try:
            self.file_path, _ = QtWidgets.QFileDialog.getOpenFileName()
            if self.file_path:
                self.label.setText(f'Arquivo lido: {os.path.basename(self.file_path)}')
        except Exception as e:
            self.label.setText(f'Erro ao selecionar o arquivo: {str(e)}')

    def input_text(self):
        # Função para inserir o texto
        text, ok = QtWidgets.QInputDialog.getMultiLineText(self, 'Texto para arquivo', 'Digite o texto que deseja salvar no arquivo:')
        if ok:
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Salvar como", "", "Arquivos de Texto (*.txt)")
            if filename:
                try:
                    with open(filename, 'w', encoding='utf-8') as text_file:
                        text_file.write(text)
                    QtWidgets.QMessageBox.information(self, 'Sucesso', 'Arquivo TXT criado com sucesso!')
                except IOError as e:
                    self.label.setText(f'Erro ao criar o arquivo TXT: {str(e)}')
            else:
                self.label.setText('Por favor, escolha um local para salvar o arquivo!')

    def create_audio_file(self):
        # Função para criar o arquivo de áudio
        if self.file_path:
            try:
                filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Salvar como", "", "Arquivos de Áudio (*.mp3)")  # Alterado para .mp3
                if filename:
                    self.audio_file = filename
                    progress = QtWidgets.QProgressDialog("Criando arquivo de áudio...", "Cancelar", 0, 100, self)
                    progress.setWindowModality(QtCore.Qt.WindowModal)
                    progress.setStyleSheet("QProgressDialog {background-color: white;}")
                    progress.show()
                    txt = read_file(self.file_path)
                    if txt is not None:
                        self.thread = AudioThread(txt, filename)
                        self.thread.progress.connect(progress.setValue)
                        self.thread.finished.connect(progress.close)
                        self.thread.finished.connect(self.audio_created)
                        self.thread.start()
                    else:
                        self.label.setText('Por favor, escolha um arquivo suportado!')
                else:
                    self.label.setText('Por favor, escolha um local para salvar o arquivo!')
            except Exception as e:
                self.label.setText(f'Erro ao criar o arquivo de áudio: {str(e)}')
        else:
            self.label.setText('Por favor selecione um arquivo!')

    def audio_created(self):
        QtWidgets.QMessageBox.information(self, 'Sucesso', 'Arquivo de áudio criado com sucesso!')

    def play_pause_audio(self):
        # Função para tocar ou pausar o áudio
        if os.path.exists(self.audio_file):
            if not self.is_playing:
                pygame.mixer.music.load(self.audio_file)
                pygame.mixer.music.set_volume(self.speed_slider.value()/100)  # Adicionado para controlar a velocidade
                pygame.mixer.music.play()
                self.play_button.setText('Pause')
                self.play_button.setStyleSheet("background-color: red")
                self.is_playing = True
                start_time = time.time()
                while pygame.mixer.music.get_busy():  
                    current_time = time.time()
                    elapsed_time = int(current_time - start_time)
                    minutes, seconds = divmod(elapsed_time, 60)
                    self.time_label.setText(f'Tempo de leitura: {minutes} minutos {seconds} segundos')
                    QtWidgets.QApplication.processEvents()  
                    time.sleep(1)  
                self.play_button.setText('Play')
                self.play_button.setStyleSheet("background-color: green")
                self.is_playing = False
            else:
                pygame.mixer.music.pause()
                self.play_button.setText('Play')
                self.play_button.setStyleSheet("background-color: green")
                self.is_playing = False

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    app.setStyle('Fusion')  # Adicionado para corrigir o problema de cor do QProgressDialog
    window = MainWindow()
    window.setFixedSize(300, 280)  # Reduz a largura da interface gráfica
    window.show()
    app.exec_()
