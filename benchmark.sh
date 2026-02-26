#!/bin/bash

# ==========================================
# TEST CONFIGURATION
# ==========================================
URL="http://host.docker.internal:8002/cpu-task"  # Endpoint to test
THREADS=2                                        # Number of wrk threads
CONNECTIONS=1000                                 # Number of concurrent connections
DURATION="30s"                                   # Duration of a single test run
WARMUP_DURATION="15s"                            # Duration of the warm-up phase
TIMEOUT="10s"                                    # Duration of the timeout
RUNS=5                                           # Number of test runs
COOLDOWN=60                                      # Cooldown time between runs in seconds
CPUSET="6"                                       # CPU cores assigned to the wrk generator
# ==========================================

echo "======================================================"
echo "  Starting automated repeatability benchmark"
echo "Target: $URL"
echo "Parameters: $RUNS runs of $DURATION, cooldown: $COOLDOWN s"
echo "======================================================"

# 1. Warm-up
echo "[1/4] Starting warm-up phase ($WARMUP_DURATION)..."
docker run --cpuset-cpus="6" williamyeh/wrk -t2 -c100 -d3s --latency --timeout $TIMEOUT "http://host.docker.internal:8001/cpu-task"
echo "  Warm-up complete. Cooling down CPU for $COOLDOWN seconds..."
sleep $COOLDOWN

# Arrays to store results
declare -a req_sec_arr
declare -a lat_99_arr

echo ""
echo "[2/4] Starting main test loop..."

# 2. Test Loop
for (( i=1; i<=$RUNS; i++ ))
do
    echo "------------------------------------------------------"
    echo "▶  RUN $i of $RUNS (Testing in progress...)"
    
    # Run wrk and capture the entire output
    output=$(docker run --rm --cpuset-cpus="$CPUSET" williamyeh/wrk -t$THREADS -c$CONNECTIONS -d$DURATION --latency --timeout $TIMEOUT "$URL")

    # Extract metrics using grep and awk
    req_sec=$(echo "$output" | grep "Requests/sec:" | awk '{print $2}')
    lat_99=$(echo "$output" | grep "99%" | awk '{print $2}')

    echo "  Results for run $i:"
    echo "   - Throughput: $req_sec req/sec"
    echo "   - Latency (99%): $lat_99"

    # Store results in arrays
    req_sec_arr+=($req_sec)
    lat_99_arr+=($lat_99)

    # Cooldown (skip after the last run)
    if [ $i -lt $RUNS ]; then
        echo "  Cooling down CPU for $COOLDOWN seconds..."
        sleep $COOLDOWN
    fi
done

echo ""
echo "[3/4] Collecting statistical data..."
echo "Collected Requests/sec values: ${req_sec_arr[@]}"

# 3. Statistical calculations using AWK
echo ""
echo "======================================================"
echo "  STATISTICAL SUMMARY (Throughput)"
echo "======================================================"

# Pass the results array to awk to calculate mean, standard deviation, and CV
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
    
    printf "Mean:                          %.2f req/sec\n", mean;
    printf "Standard Deviation (StDev):    %.2f req/sec\n", stdev;
    printf "Coefficient of Variation (CV): %.2f%%\n\n", cv;

    print "ENVIRONMENT VERDICT:"
    if (cv < 5.0) {
        print "  EXCELLENT STABILITY (CV < 5%).";
        print "The environment is \"sterile\". Results are suitable for academic research.";
    } else if (cv < 10.0) {
        print "  ACCEPTABLE STABILITY (5% < CV < 10%).";
        print "Results are valid, but there is slight system noise in the background.";
    } else {
        print "  POOR STABILITY (CV > 10%).";
        print "Significant system noise or thermal throttling detected. Increase cooldown time or close background apps.";
    }
}' <(printf "%s\n" "${req_sec_arr[@]}")

echo "======================================================"