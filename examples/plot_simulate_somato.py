"""
====================
Simulate somato data
====================

This example demonstrates how to simulate the source time
courses obtained during median nerve stimulation in the MNE
somatosensory dataset.
"""

# Authors: Mainak Jas <mainakjas@gmail.com>
#          Ryan Thorpe <ryan_thorpe@brown.edu>

###############################################################################
# First, we will import the packages and define the paths
import os.path as op
import numpy as np
import matplotlib.pyplot as plt

import mne
from mne.datasets import somato
from mne.minimum_norm import apply_inverse, make_inverse_operator

data_path = somato.data_path()
subject = '01'
task = 'somato'
raw_fname = op.join(data_path, 'sub-{}'.format(subject), 'meg',
                    'sub-{}_task-{}_meg.fif'.format(subject, task))
fwd_fname = op.join(data_path, 'derivatives', 'sub-{}'.format(subject),
                    'sub-{}_task-{}-fwd.fif'.format(subject, task))
subjects_dir = op.join(data_path, 'derivatives', 'freesurfer', 'subjects')

###############################################################################
# Then, we get the raw data and estimage the source time course

raw = mne.io.read_raw_fif(raw_fname, preload=True)
raw.filter(1, 40)

events = mne.find_events(raw, stim_channel='STI 014')
event_id, tmin, tmax = 1, -.2, .15
baseline = None
epochs = mne.Epochs(raw, events, event_id, tmin, tmax, baseline=baseline,
                    reject=dict(grad=4000e-13, eog=350e-6), preload=True)
evoked = epochs.average()

fwd = mne.read_forward_solution(fwd_fname)
cov = mne.compute_covariance(epochs)
inv = make_inverse_operator(epochs.info, fwd, cov)

method = "MNE"
snr = 3.
lambda2 = 1. / snr ** 2
stc = apply_inverse(evoked, inv, lambda2, method=method, pick_ori="normal",
                    return_residual=False, verbose=True)

pick_vertex = np.argmax(np.linalg.norm(stc.data, axis=1))

plt.figure()
plt.plot(1e3 * stc.times, stc.data[pick_vertex, :].T * 1e9, 'ro-')
plt.xlabel('time (ms)')
plt.ylabel('%s value (nAM)' % method)
plt.xlim((0, 150))
plt.axhline(0)
plt.show()

###############################################################################
# Now, let us try to simulate the same with MNE-neuron

import os.path as op

import hnn_core
from hnn_core import simulate_dipole, read_params, Network

hnn_core_root = op.dirname(hnn_core.__file__)

params_fname = op.join(hnn_core_root, 'param', 'N20.json')
params = read_params(params_fname)

net = Network(params)
dpl = simulate_dipole(net, n_trials=1)

import matplotlib.pyplot as plt
fig, axes = plt.subplots(2, 1, sharex=True, figsize=(6, 6))
dpl[0].plot(ax=axes[0], show=False)
net.plot_input(ax=axes[1])
net.spikes.plot()
