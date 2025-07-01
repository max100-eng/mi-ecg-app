import matplotlib.pyplot as plt

def plot_ecg(señal, peaks, fs):
    plt.figure(figsize=(12,4))
    plt.plot(np.arange(len(señal))/fs, señal)
    plt.scatter(peaks/fs, señal[peaks], c='r')
    plt.xlabel("Tiempo (s)")
    plt.ylabel("Amplitud (mV)")
    return plt
