# Quick sanity check of generated datasets: shape, missing rate, accuracy, no-answer rate, careless count.
import json, glob, sys, numpy as np
for f in sorted(glob.glob(sys.argv[1] if len(sys.argv) > 1 else 'data/*/*/sim_*.json')):
    d = json.load(open(f)); t = json.load(open(f.replace('sim_', 'truth_'))); y = np.array(d['yk']); n = np.array(d['nsol']); o = y >= 0
    cor = np.array([[1 <= y[i, j] <= n[j] for j in range(y.shape[1])] for i in range(len(y))])
    print(f, y.shape, 'miss %.3f acc %.3f noans %.3f careless %d sigma %.2f' % ((~o).mean(), cor[o].mean(), (y[o] == 0).mean(), sum(t['careless']), t['sigma']))
