import subprocess
import json
import time
import re
import pandas as pd
import matplotlib.pyplot as plt

# --------------------------
# CONFIG
# --------------------------
tests = [
    {"client": "12.1.1.2", "server": "192.168.73.135", "label": "Limpopo→DN"},
    {"client": "12.1.1.66", "server": "192.168.73.139", "label": "CapeTown→DN2"},
]

duration = 20  # seconds per test
parallel_streams = [1, 5, 10]  # single + multi-session
protocols = ["tcp", "udp"]

results = []

# --------------------------
# FUNCTIONS
# --------------------------
def run_iperf(client_ip, server_ip, protocol, parallel, label):
    cmd = [
        "iperf3", "-c", server_ip, "-t", str(duration), "-J"
    ]
    if protocol == "udp":
        cmd += ["-u", "-b", "100M"]  # UDP target bitrate
    if parallel > 1:
        cmd += ["-P", str(parallel)]
    
    print(f"Running {protocol.upper()} test: {label}, streams={parallel}")
    output = subprocess.run(cmd, capture_output=True, text=True)

    # --------------------------
    # Handle errors
    # --------------------------
    if output.returncode != 0:
        print(f"❌ iperf3 failed for {label} ({protocol}, {parallel} streams):\n{output.stderr}")
        return
    
    # --------------------------
    # JSON Parsing
    # --------------------------
    if output.stdout.strip().startswith("{"):
        try:
            data = json.loads(output.stdout)

            throughput = None
            jitter = None
            loss = None

            if protocol == "tcp":
                if "sum_received" in data["end"]:
                    throughput = data["end"]["sum_received"]["bits_per_second"] / 1e6
                elif "sum_sent" in data["end"]:
                    throughput = data["end"]["sum_sent"]["bits_per_second"] / 1e6
                elif "sum" in data["end"]:
                    throughput = data["end"]["sum"]["bits_per_second"] / 1e6

            elif protocol == "udp":
                if "sum_received" in data["end"]:
                    throughput = data["end"]["sum_received"]["bits_per_second"] / 1e6
                    jitter = data["end"]["sum_received"].get("jitter_ms", None)
                    loss = data["end"]["sum_received"].get("lost_percent", None)
                elif "sum" in data["end"]:
                    throughput = data["end"]["sum"]["bits_per_second"] / 1e6
                    jitter = data["end"]["sum"].get("jitter_ms", None)
                    loss = data["end"]["sum"].get("lost_percent", None)

            results.append({
                "label": label,
                "protocol": protocol,
                "parallel": parallel,
                "throughput_Mbps": throughput,
                "jitter_ms": jitter,
                "loss_percent": loss
            })
            return
        except Exception as e:
            print(f"⚠️ JSON parsing failed: {e}")

    # --------------------------
    # Fallback: Text Parsing
    # --------------------------
    print(f"⚠️ No JSON output. Trying text parsing...\n{output.stdout}")

    throughput = None
    jitter = None
    loss = None

    for line in output.stdout.splitlines():
        # TCP: look for "Mbits/sec"
        if "Mbits/sec" in line and throughput is None:
            match = re.search(r"(\d+\.?\d*)\s+Mbits/sec", line)
            if match:
                throughput = float(match.group(1))

        # UDP: jitter and loss
        if "ms" in line and "%" in line:
            match = re.search(
                r"(\d+\.?\d*)\s+Mbits/sec\s+(\d+\.?\d*)\s+ms\s+(\d+)/(\d+).*?(\d+\.?\d*)%",
                line
            )
            if match:
                throughput = float(match.group(1))
                jitter = float(match.group(2))
                loss = float(match.group(5))

    results.append({
        "label": label,
        "protocol": protocol,
        "parallel": parallel,
        "throughput_Mbps": throughput,
        "jitter_ms": jitter,
        "loss_percent": loss
    })


# --------------------------
# RUN TESTS
# --------------------------
for t in tests:
    for proto in protocols:
        for p in parallel_streams:
            run_iperf(t["client"], t["server"], proto, p, t["label"])
            time.sleep(5)

# --------------------------
# SAVE & PLOT
# --------------------------
df = pd.DataFrame(results)
df.to_csv("iperf_results.csv", index=False)

# Throughput Graphs
for proto in protocols:
    subset = df[df.protocol == proto]
    if subset.empty:
        continue
    plt.figure()
    for label in subset.label.unique():
        d = subset[subset.label == label]
        plt.plot(d.parallel, d.throughput_Mbps, marker="o", label=label)
    plt.title(f"{proto.upper()} Throughput vs Parallel Streams")
    plt.xlabel("Parallel Streams")
    plt.ylabel("Throughput (Mbps)")
    plt.legend()
    plt.grid()
    plt.savefig(f"{proto}_throughput.png")

# UDP Jitter & Loss Graphs
udp = df[df.protocol == "udp"]
if not udp.empty:
    plt.figure()
    for label in udp.label.unique():
        d = udp[udp.label == label]
        plt.plot(d.parallel, d.jitter_ms, marker="x", label=label)
    plt.title("UDP Jitter vs Parallel Streams")
    plt.xlabel("Parallel Streams")
    plt.ylabel("Jitter (ms)")
    plt.legend()
    plt.grid()
    plt.savefig("udp_jitter.png")
    
    plt.figure()
    for label in udp.label.unique():
        d = udp[udp.label == label]
        plt.plot(d.parallel, d.loss_percent, marker="s", label=label)
    plt.title("UDP Packet Loss vs Parallel Streams")
    plt.xlabel("Parallel Streams")
    plt.ylabel("Loss (%)")
    plt.legend()
    plt.grid()
    plt.savefig("udp_loss.png")

print("✅ Tests complete. Results saved to iperf_results.csv and graphs generated.")
