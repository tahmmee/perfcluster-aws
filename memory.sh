for i in $(ps aux | grep beam.smp | awk '{print $(2)}'); do if [ -f /proc/$i/status ]; then cat /proc/$i/status | grep VmSize | awk '{print $(NF-1)}'; fi done | awk '{s+=$1} END {print s}'
