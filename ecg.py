# Copyright (c) 2017, MD2K Center of Excellence
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from typing import List
import numpy as np
import scipy.signal as signal
import datetime
from scipy.stats import iqr
import numpy as np
from scipy.stats import iqr
from scipy import interpolate, signal
import matplotlib.pyplot as plt
from matplotlib import style
import matplotlib.patches as mpatches
from collections import OrderedDict

def frequencyDomain(tmStamps,RRints, lf_bw = 0.11, hf_bw = 0.1):
    
    #Remove ectopic beats
    #RR intervals differing by more than 20% from the one proceeding it are removed
    NNs = []
    tss = []
    for c, rr in enumerate(RRints):        
        if abs(rr - RRints[c-1]) <= 0.20 * RRints[c-1]:
            NNs.append(rr)
            tss.append(tmStamps[c])
            
            
    frequency_range = np.linspace(0.001, 1, 10000)
    NNs = np.array(NNs)
    NNs = NNs - np.mean(NNs)
    result = signal.lombscargle(tss, NNs, frequency_range)
        
    #Pwelch w/ zero pad     
    fxx = frequency_range 
    pxx = result 
    
    vlf= (0.003, 0.04)
    lf = (0.04, 0.15)
    hf = (0.15, 0.4)
    
    plot_labels = ['VLF', 'LF', 'HF']
        
    df = fxx[1] - fxx[0]
    vlf_power = np.trapz(pxx[np.logical_and(fxx >= vlf[0], fxx < vlf[1])], dx = df)      
    lf_power = np.trapz(pxx[np.logical_and(fxx >= lf[0], fxx < lf[1])], dx = df)            
    hf_power = np.trapz(pxx[np.logical_and(fxx >= hf[0], fxx < hf[1])], dx = df)             
    totalPower = vlf_power + lf_power + hf_power
    
    #Normalize and take log
    vlf_NU_log = np.log((vlf_power / (totalPower - vlf_power)) + 1)
    lf_NU_log = np.log((lf_power / (totalPower - vlf_power)) + 1)
    hf_NU_log = np.log((hf_power / (totalPower - vlf_power)) + 1)
    lfhfRation_log = np.log((lf_power / hf_power) + 1)   
    
    freqDomainFeats = {'VLF_Power': vlf_NU_log, 'LF_Power': lf_NU_log,
                       'HF_Power': hf_NU_log, 'LF/HF': lfhfRation_log}
                       
    return freqDomainFeats



def ecg_feature_computation(b,a):
    return [np.var(a),iqr(a),np.mean(a),np.median(a),np.percentile(a,80),np.percentile(a,20),60000/np.median(a)]+list(frequencyDomain(b,a).values())



