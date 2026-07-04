import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt

def modificar_decay_ir(ir, factor_decay, fs_ir):
    duracion_real = len(ir) / fs_ir
    decay_seg = duracion_real * factor_decay
    t = np.arange(len(ir)) / fs_ir

    if factor_decay <= 1:
        if factor_decay == 1:
            return ir.copy()
        envolvente = np.exp(- (5.0 / decay_seg) * t).reshape(-1, 1)
        return ir * envolvente
    else:
        muestras_ataque = int(0.060 * fs_ir)
        ataque = ir[:muestras_ataque].copy()
        cola = ir[muestras_ataque:].copy()
        
        muestras_cola = len(cola)
        muestras_cola_nuevas = int(muestras_cola * factor_decay)
        
        ind = np.linspace(0, muestras_cola - 1, muestras_cola)
        ind_nuevos = np.linspace(0, muestras_cola - 1, muestras_cola_nuevas)
        
        n_canales_ir = ir.shape[1]
        cola_estirada = np.zeros((muestras_cola_nuevas, n_canales_ir))
        
        for canal in range(n_canales_ir):
            cola_estirada[:, canal] = np.interp(ind_nuevos, ind, cola[:, canal])
        
        muestras_fade = int(0.040 * fs_ir)
        if muestras_fade < muestras_cola_nuevas:
            rampa_subida = np.linspace(0.0, 1.0, muestras_fade).reshape(-1, 1)
            cola_estirada[:muestras_fade] *= rampa_subida
        
        return np.vstack([ataque, cola_estirada])

def procesar_convolucion_completa(dry, ir, factor_decay, fs_ir, fs_audio, ms_predelay, freq_hpf, freq_lpf):
    ir_modificada = modificar_decay_ir(ir, factor_decay, fs_ir)
    
    canales_wet = []
    n_canales = min(dry.shape[1], ir_modificada.shape[1])
    for c in range(n_canales):
        canal_conv = fftconvolve(dry[:, c], ir_modificada[:, c], mode='full')
        canales_wet.append(canal_conv)
    audio_wet = np.stack(canales_wet, axis=-1)

    muestras_delay = int((ms_predelay * fs_audio) / 1000)
    if muestras_delay > 0:
        silencio = np.zeros((muestras_delay, n_canales))
        audio_wet = np.vstack([silencio, audio_wet])

    nyquist = fs_audio / 2.0
    if freq_hpf > 20:
        sos_hp = butter(2, freq_hpf / nyquist, btype='highpass', output='sos')
        for c in range(n_canales):
            audio_wet[:, c] = sosfilt(sos_hp, audio_wet[:, c])

    if freq_lpf < 20000:
        sos_lp = butter(2, freq_lpf / nyquist, btype='lowpass', output='sos')
        for c in range(n_canales):
            audio_wet[:, c] = sosfilt(sos_lp, audio_wet[:, c])

    pad_len = len(audio_wet) - len(dry)
    dry_padded = np.pad(dry, ((0, pad_len), (0, 0)), mode='constant')[:len(audio_wet), :n_canales]

    rms_dry = np.sqrt(np.mean(dry_padded**2))
    rms_wet = np.sqrt(np.mean(audio_wet**2))
    
    if rms_wet > 0 and rms_dry > 0:
        audio_wet = audio_wet * (rms_dry / rms_wet) * 0.4

    return dry_padded, audio_wet