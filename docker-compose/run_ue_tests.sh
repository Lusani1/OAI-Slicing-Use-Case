#!/bin/bash
set -e

# === Configuration ===
UEs=("ueransim" "ueransim1")
UE_IPs=("12.1.1.2" "12.1.1.66")
DNs=("oai-ext-dn" "oai-ext-dn2")
DN_IPs=("192.168.73.135" "192.168.73.139")
PORTS=("5201" "5202")
DURATION=60   # seconds per test
RESULTS_DIR="results_parallel"

mkdir -p $RESULTS_DIR

echo "🧹 Cleaning old iperf3 servers..."
for DN in "${DNs[@]}"; do
  docker exec -i $DN pkill -f iperf3 || true
done

echo "🚀 Starting new iperf3 servers..."
docker exec -d ${DNs[0]} iperf3 -s -p ${PORTS[0]} -i 1
docker exec -d ${DNs[1]} iperf3 -s -p ${PORTS[1]} -i 1

sleep 2

echo "▶️ Running parallel tests..."
for i in "${!UEs[@]}"; do
  UE=${UEs[$i]}
  UE_IP=${UE_IPs[$i]}
  DN_IP=${DN_IPs[$i]}
  PORT=${PORTS[$i]}

  # UDP test
  docker exec -i $UE iperf3 -c $DN_IP -p $PORT -B $UE_IP -u -b 5M -t $DURATION \
    2>&1 | ts '[%Y-%m-%d %H:%M:%S]' > $RESULTS_DIR/${UE}_udp.log &

  # TCP test
  docker exec -i $UE iperf3 -c $DN_IP -p $PORT -B $UE_IP -t $DURATION \
    2>&1 | ts '[%Y-%m-%d %H:%M:%S]' > $RESULTS_DIR/${UE}_tcp.log &
done

wait
echo "✅ All tests completed. Results saved in $RESULTS_DIR/"
