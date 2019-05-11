import numpy as np
from port_audio_record import BeagleFirmware
import matplotlib.pyplot as plt

beags = BeagleFirmware(5000)

fake_data = np.random.randn(100000, 3).astype(np.float32)

p_atfc = []
for i in range(int(fake_data.shape[0] / beags.buffer_size)):
    starti = beags.buffer_size * i
    endi = beags.buffer_size * (i + 1)
    buf_out = fake_data[starti: endi, :]
    proc_out = beags.process(buf_out)
    beags.dump(proc_out)
    p_atfc.append(np.concatenate(proc_out))

p_atfc = np.concatenate(p_atfc)
p_atfc = p_atfc[2:, :]


# process all the data at once
num_i = int(np.ceil(fake_data.shape[0] / beags.num_step))
win_i = np.arange(num_i) * beags.num_step

cont_process = []
for i in win_i:
    if i + beags.winwidth > fake_data.shape[0]:
        break
    d_in = fake_data[i: i + beags.winwidth, :]
    cont_process.append(beags.twidle @ d_in)
cont_process = np.array(cont_process)

buff_diff = np.abs(cont_process[: p_atfc.shape[0], :] - p_atfc)
