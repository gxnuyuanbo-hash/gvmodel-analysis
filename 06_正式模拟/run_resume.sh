#!/bin/sh
# Resume the full queue after an interruption: fit only reps without pop_<rep>.csv (avoids ~5,000 Rscript start-ups that
# fit_cell.R would skip anyway), then Chen matching per cell, as in run_queue.sh full. Log: logs/queue_full.txt
cd "$(dirname "$0")"; export LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8
echo "resume $(date)" >> logs/queue_full.txt
while read s c n; do i=0; while [ $i -lt $n ]; do f=$(printf "out/%s/c%02d/pop_%04d.csv" $s $c $i); [ -f "$f" ] || echo "$s $c $i"; i=$((i+1)); done; done < logs/tasks_full.txt |
  xargs -P 2 -L 1 sh -c 'Rscript fit_cell.R $0 $1 $2 > /dev/null 2>&1 || echo "FAILED $0 $1 $2"' >> logs/queue_full.txt
while read s c n; do [ "$s" != "sbc" ] && python3 -I chen_apply.py $s $c; done < logs/tasks_full.txt
echo "done $(date)" >> logs/queue_full.txt
