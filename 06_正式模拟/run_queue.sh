#!/bin/sh
# Run the formal simulation queue: generate data, fit 2 datasets at a time, then Chen matching per cell.
# Usage: sh run_queue.sh pilot   -> reps 0-2 of every cell (timing check; these are also the first formal replications)
#        sh run_queue.sh full    -> all reps, in the order key cell, SBC, other s1 cells, s3
# Existing outputs are skipped, so the queue can be stopped and restarted. Log: logs/queue_<mode>.txt
cd "$(dirname "$0")"; export LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8
MODE=${1:-pilot}
python3 -I - "$MODE" > logs/tasks_$MODE.txt <<'PY'
import json, sys
cells = json.load(open('cells.json')); mode = sys.argv[1]
order = sorted(cells, key=lambda c: (0 if c['study'] == 's1' and c['key'] else 1 if c['study'] == 'sbc' else 2 if c['study'] == 's1' else 3, c['cell']))
for c in order:
    n = 3 if mode == 'pilot' else c['reps']
    print(c['study'], c['cell'], n)
PY
while read s c n; do python3 -I sim_gen.py $s $c 0 $n; done < logs/tasks_$MODE.txt
while read s c n; do i=0; while [ $i -lt $n ]; do echo "$s $c $i"; i=$((i+1)); done; done < logs/tasks_$MODE.txt |
  xargs -P 2 -L 1 sh -c 'Rscript fit_cell.R $0 $1 $2 > /dev/null 2>&1 || echo "FAILED $0 $1 $2"' >> logs/queue_$MODE.txt
while read s c n; do [ "$s" != "sbc" ] && python3 -I chen_apply.py $s $c; done < logs/tasks_$MODE.txt
echo "done $(date)" >> logs/queue_$MODE.txt
