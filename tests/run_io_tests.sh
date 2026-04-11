#!/bin/bash

OUTPUT_CSV="io_bound_results.csv"
CONNECTIONS=(20 50 100 200 300 400 500 600 700 800 1000 1250 1500 1750 2000 2500 3000 3500 4000 4500 5000)
SERVERS=("Sync:8001" "Async:8002")
DURATION="90s"
THREADS="2"
CPU_CORE="6"

echo "Server,Connections,RPS,Avg_Lat,p50,p99,Max_Lat,Stdev_Lat,Timeouts,ConnErrors,HTTPErrors" > $OUTPUT_CSV

echo "====================================================="
echo " Starting automated I/O-bound tests (Scenario A)"
echo "====================================================="

for conn in "${CONNECTIONS[@]}"; do
    for srv in "${SERVERS[@]}"; do
        name="${srv%%:*}"
        port="${srv##*:}"
        url="http://host.docker.internal:${port}/io-task"
        
        echo "[*] Testing: $name | Connections: $conn"

        result=$(docker run --rm --cpuset-cpus="$CPU_CORE" williamyeh/wrk -t$THREADS -c$conn -d$DURATION --latency --timeout 30s "$url")

        rps=$(echo "$result" | grep "Requests/sec:" | awk '{print $2}')

        p50=$(echo "$result" | grep "50%" | awk '{print $2}')
        p99=$(echo "$result" | grep "99%" | awk '{print $2}')

        lat_stats=$(echo "$result" | awk '/^\s*Latency/ {print; exit}')
        avg_lat=$(echo "$lat_stats" | awk '{print $2}')
        stdev_lat=$(echo "$lat_stats" | awk '{print $3}')
        max_lat=$(echo "$lat_stats" | awk '{print $4}')

        timeouts=$(echo "$result" | grep "Socket errors:" | grep -o 'timeout [0-9]*' | awk '{print $2}')
        if [ -z "$timeouts" ]; then timeouts=0; fi

        conn_errs=$(echo "$result" | grep "Socket errors:" | grep -o 'connect [0-9]*' | awk '{print $2}')
        if [ -z "$conn_errs" ]; then conn_errs=0; fi

        http_errs=$(echo "$result" | grep "Non-2xx or 3xx responses:" | awk '{print $5}')
        if [ -z "$http_errs" ]; then http_errs=0; fi

        echo "$name,$conn,$rps,$avg_lat,$p50,$p99,$max_lat,$stdev_lat,$timeouts,$conn_errs,$http_errs" >> $OUTPUT_CSV
        
        echo "    Result: RPS=$rps, Avg=$avg_lat, Max=$max_lat, p99=$p99, Err=$conn_errs"
        echo "    Waiting 5 seconds for network socket stabilization (cooldown)..."
        sleep 5
    done
done

echo "====================================================="
echo " Tests completed! Results saved to: $OUTPUT_CSV"
echo "====================================================="