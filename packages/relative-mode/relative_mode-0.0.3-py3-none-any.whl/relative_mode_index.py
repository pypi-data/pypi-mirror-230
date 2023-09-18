# %% packages

import librosa.display

print("Librosa:", librosa.__version__)
import matplotlib

print("Matplotlib:", matplotlib.__version__)
import numpy as np

print("Numpy:", np.__version__)
from matplotlib import pyplot as plt
#import IPython.display as ipd

import pandas as pd

print("Pandas:", pd.__version__)

print("------- packages loaded ---------------")

# %%

# Import functions
from src.relative_mode import Tonal_Fragment
from src.relative_mode import relative_mode
from src.relative_mode import RME_across_time

#from src.relative_mode_across_time import RME_across_time

print("------- functions loaded ---------------")

## get an example
filename = 'data/Bach_1_Gould_0_Major_bachGould1971.wav'
y, sr = librosa.load(filename)
# %%

print("------- relative mode estimation ---------------")
# %% wrapped into meta-function

#def relative_mode(y=y, sr=sr, winlen=3, hoplen=3, distance='cosine', profile='albrecht', chromatype='CENS'):
#    t = librosa.estimate_tuning(y=y, sr=sr)
#    y440 = librosa.effects.pitch_shift(y, sr=sr, n_steps=-t)
#    df = pd.DataFrame(columns=['filename', 'tonmaxmaj', 'tonmaxmin', 'tondeltamax', 'tondeltamaxMd', 'tondeltamaxSi'])
#
#    df_segments = pd.DataFrame(columns=['onset', 'tonmaxmaj', 'tonmaxmin', 'tonkey', 'tondeltamax'])
#    frames = librosa.util.frame(y440, frame_length=int(sr * winlen), hop_length=int(sr * hoplen))
#    N = int(frames.shape[1])
#    for ii in range(0, N):
#        ton = Tonal_Fragment(frames[:, ii], sr, distance=distance, profile=profile, chromatype=chromatype)
#        df_segments.loc[len(df_segments)] = [ii, ton.max_maj, ton.max_min, ton.key, ton.maj_min_delta_max]
#
#    df.loc[len(df)] = [filename, np.mean(df_segments['tonmaxmaj']), np.mean(df_segments['tonmaxmin']),
#                       np.mean(df_segments['tondeltamax']), np.median(df_segments['tondeltamax']),
#                       sum(np.sign(df_segments['tondeltamax']))]
#    return df, df_segments


# %%
x1, x2 = relative_mode(y=y, sr=sr, profile='simple')
print(x1.tondeltamax)
print(x2.tondeltamax)
# %%
print("------- relative mode estimation across time ---------------")

fig,x3 = RME_across_time(filename=filename, winlen=3, hoplen=3, cropfirst=0, croplast=0, chromatype='CENS', profile='albrecht',distance='cosine', plot=True)

#print(x3)
fig
plt.show()
