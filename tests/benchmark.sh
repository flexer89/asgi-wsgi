#!/bin/bash

# ==========================================
THREADS=2                                        # Number of wrk threads
CONNECTIONS=50                                   # Number of concurrent connections
DURATION="60s"                                   # Duration of a single test run
WARMUP_DURATION="15s"                            # Duration of the warm-up phase
TIMEOUT="10s"                                    # Duration of the timeout
RUNS=10                                          # Number of test runs
COOLDOWN=60                                      # Cooldown time between runs in seconds
CPUSET="6"                                       # CPU cores assigned to the wrk generator
LOG_FILE="benchmark_$(date +%Y%m%d_%H%M%S).log"  # Log file name with timestamp
URL="http://host.docker.internal:8001/io-task"
# ==========================================

exec > >(tee -i "$LOG_FILE") 2>&1

echo "======================================================"
echo "  Starting automated repeatability benchmark"
echo "Parameters: $RUNS runs of $DURATION, cooldown: $COOLDOWN s"
echo "Log file: $LOG_FILE"
echo "======================================================"

echo "[1/4] Starting warm-up phase ($WARMUP_DURATION)..."
docker run --cpuset-cpus="6" williamyeh/wrk -t$THREADS -c$CONNECTIONS -d$WARMUP_DURATION --latency --timeout $TIMEOUT $URL
echo "  Warm-up complete. Cooling down CPU for $COOLDOWN seconds..."
sleep $COOLDOWN

declare -a req_sec_arr
declare -a lat_99_arr

echo ""
echo "[2/4] Starting main test loop..."

for (( i=1; i<=$RUNS; i++ ))
do
    echo "------------------------------------------------------"
    echo "▶  RUN $i of $RUNS (Testing in progress...)"
    
    output=$(docker run --rm --cpuset-cpus="$CPUSET" williamyeh/wrk -t$THREADS -c$CONNECTIONS -d$DURATION --latency --timeout $TIMEOUT $URL)

    req_sec=$(echo "$output" | grep "Requests/sec:" | awk '{print $2}')
    lat_99=$(echo "$output" | grep "99%" | awk '{print $2}')

    echo "  Results for run $i:"
    echo "   - Throughput: $req_sec req/sec"
    echo "   - Latency (99%): $lat_99"

    req_sec_arr+=($req_sec)
    lat_99_arr+=($lat_99)

    if [ $i -lt $RUNS ]; then
        echo "  Cooling down CPU for $COOLDOWN seconds..."
        sleep $COOLDOWN
    fi
done

echo ""
echo "[3/4] Collecting statistical data..."
echo "Collected Requests/sec values: ${req_sec_arr[@]}"

echo ""
echo "======================================================"
echo "  STATISTICAL SUMMARY (Throughput)"
echo "======================================================"

awk -v runs="$RUNS" '
BEGIN {
    sum = 0;
    sum_sq = 0;
}
{
    sum += $1;
    val[NR] = $1;
}
END {
    # Calculate Mean
    mean = sum / runs;
    
    # Calculate Variance and Standard Deviation
    for (i=1; i<=runs; i++) {
        sum_sq += (val[i] - mean)^2;
    }
    variance = sum_sq / runs;
    stdev = sqrt(variance);
    
    # Calculate Coefficient of Variation (CV)
    cv = (stdev / mean) * 100;
    
    printf "Mean:                            %.2f req/sec\n", mean;
    printf "Standard Deviation (StDev):    %.2f req/sec\n", stdev;
    printf "Coefficient of Variation (CV): %.2f%%\n\n", cv;

    print "ENVIRONMENT VERDICT:"
    if (cv < 5.0) {
        print "  EXCELLENT STABILITY (CV < 5%).";
        print "The environment is \"sterile\". Results are suitable.";
    } else if (cv < 10.0) {
        print "  ACCEPTABLE STABILITY (5% < CV < 10%).";
        print "Results are valid, but there is slight system noise in the background.";
    } else {
        print "  POOR STABILITY (CV > 10%).";
        print "Significant system noise. Increase cooldown time or close background apps.";
    }
}' <(printf "%s\n" "${req_sec_arr[@]}")

echo "======================================================"