import numpy as np
import soundfile as sf
from multiplexador import MultiplexadorAudio
from demultiplexador import Demultiplexador

if __name__ == "__main__":
    fs = 44100
    t = np.linspace(0, 5, 5*fs)
    sf.write('input1.wav', 0.5*np.sin(2*np.pi*440*t), fs) # Lá
    sf.write('input2.wav', 0.5*np.sin(2*np.pi*880*t), fs) # Lá oitava acima
    sf.write('input3.wav', 0.5*np.random.randn(len(t)), fs) # Ruído branco

    print("Etapa 1: Multiplexação")
    mux = MultiplexadorAudio("input1.wav", "input2.wav", "input3.wav")
    mux.executar()
    
    print("\nEtapa 2: Demultiplexação")
    demux = Demultiplexador()
    
    demux.comparar_sinais_visual()