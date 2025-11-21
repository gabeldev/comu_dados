import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.signal import butter, lfilter

class MultiplexadorAudio:
    def __init__(self, file1, file2, file3): # Construtor
        self.__fs = 44100    # Frequência de amostragem (Hz)
        self.__duration = 3  # Duração do sinal (segundos)
        self.__fc_A = 4000   # Portadora do sinal A
        self.__fc_B = 10000  # Portadora do sinal B
        self.__fc_C = 14000  # Portadora do sinal C
        
        # Carrega e processa os sinais
        self.sinais = self.carrega_e_trata_audios(file1, file2, file3)
        
    def filtro_passa_baixa(self, data, cutoff, order=5):
        """Filtra o áudio antes de modular para evitar sobreposição de espectro entre canais"""
        nyq = 0.5 * self.__fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        y = lfilter(b, a, data)
        return y

    def carrega_e_trata_audios(self, f1, f2, f3):
        sinais = []
        # Tamanho desejado em amostras
        n_samples = int(self.__fs * self.__duration)
        
        for f in [f1, f2, f3]:
            data, fs_read = sf.read(f)
            
            # Converter para Mono se for estéreo
            if data.ndim > 1:
                data = np.mean(data, axis=1)
            
            # Ajustar tamanho (cortar ou preencher com zero)
            if len(data) > n_samples:
                data = data[:n_samples]
            else:
                data = np.pad(data, (0, n_samples - len(data)), 'constant')
            
            # Filtrar banda base para não invadir o canal vizinho
            data_filtrada = self.filtro_passa_baixa(data, cutoff=1900) 
            
            # Normalizar
            data_filtrada = data_filtrada / np.max(np.abs(data_filtrada))
            sinais.append(data_filtrada)
            
        return sinais

    def plot_spectrum(self, signal, title, ax=None, color='blue'):
        """Função auxiliar para plotar espectro"""
        N = len(signal)
        yf = fft(signal)
        xf = fftfreq(N, 1 / self.__fs)[:N//2]
        magnitude = 2.0/N * np.abs(yf[0:N//2])
        
        if ax is None:
            plt.figure(figsize=(10, 4))
            plt.plot(xf, magnitude, color=color)
            plt.title(title)
            plt.grid()
            plt.xlabel("Frequência (Hz)")
            plt.ylabel("Magnitude")
            plt.show()
        else:
            ax.plot(xf, magnitude, color=color)
            ax.set_title(title)
            ax.grid(True)
            ax.set_xlim(0, 20000) # Focar na banda de interesse

    def executar(self):
        # Tempo vetor
        t = np.arange(int(self.__fs * self.__duration)) / self.__fs
        
        a, b, c = self.sinais[0], self.sinais[1], self.sinais[2]
        
        # Modulação AM-DSB-SC
        a_mod = a * np.cos(2 * np.pi * self.__fc_A * t)
        b_mod = b * np.cos(2 * np.pi * self.__fc_B * t)
        c_mod = c * np.cos(2 * np.pi * self.__fc_C * t)
        
        # a) Mostrar o espectro dos sinais modulados separadamente
        fig, axs = plt.subplots(3, 1, figsize=(10, 8), constrained_layout=True)
        self.plot_spectrum(a_mod, f"Sinal A Modulado (Portadora {self.__fc_A}Hz)", axs[0], 'r')
        self.plot_spectrum(b_mod, f"Sinal B Modulado (Portadora {self.__fc_B}Hz)", axs[1], 'g')
        self.plot_spectrum(c_mod, f"Sinal C Modulado (Portadora {self.__fc_C}Hz)", axs[2], 'b')
        plt.suptitle("Item A: Espectros Separados")
        plt.show()

        # Multiplexação
        muxed = a_mod + b_mod + c_mod
        muxed = muxed / np.max(np.abs(muxed)) # Normalizar final

        # b) Mostrar espectro do sinal multiplexado
        self.plot_spectrum(muxed, "Item B: Espectro do Sinal Multiplexado (A+B+C)", color='black')

        # c) Salvar arquivo
        sf.write("muxed_audio.wav", muxed, self.__fs)
        
        # Salvar bases para comparação posterior no demux
        sf.write("audio_A_base.wav", a, self.__fs)
        sf.write("audio_B_base.wav", b, self.__fs)
        sf.write("audio_C_base.wav", c, self.__fs)
        
        print("Multiplexação concluída. Arquivo 'muxed_audio.wav' gerado.")