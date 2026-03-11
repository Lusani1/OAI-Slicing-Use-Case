# OAI-Slicing-Use-Case

Practical OpenAirInterface 5G Core network slicing use case using a **shared control plane**, **multiple SMFs**, **multiple VPP-based UPFs**, and **UERANSIM-based gNB/UE emulation** for distributed service domains. The scenario demonstrates how a central 5G core can support multiple slices with slice-specific DNNs, subnets, and user-plane anchoring. :contentReference[oaicite:0]{index=0} :contentReference[oaicite:1]{index=1}

## Architecture Overview

This repository implements a slicing scenario aligned to the attached architecture:

- A **shared control plane** hosted in a central data centre
- An **Education Slice** spanning two access domains
- A **Telemedicine Slice** spanning a separate access domain
- Dedicated **UPFs** and **DNNs** per traffic domain
- Slice-aware session handling using **S-NSSAI**, **SMF selection**, and **UPF/DNN mapping** :contentReference[oaicite:2]{index=2} :contentReference[oaicite:3]{index=3} :contentReference[oaicite:4]{index=4}

---

## Implemented Network Functions

### Shared control plane
The shared core includes:

- `mysql`
- `oai-nrf`
- `oai-amf`
- `oai-ausf`
- `oai-udm`
- `oai-udr`
- `oai-smf`
- `oai-smf2` :contentReference[oaicite:5]{index=5} :contentReference[oaicite:6]{index=6}

### User plane
The deployment includes three VPP-based UPFs:

- `vpp-upf`
- `vpp-upf2`
- `vpp-upf3` :contentReference[oaicite:7]{index=7} :contentReference[oaicite:8]{index=8}

### Access emulation
Three UERANSIM instances emulate geographically separated gNB/UE domains:

- `ueransim`
- `ueransim1`
- `ueransim2` :contentReference[oaicite:9]{index=9} :contentReference[oaicite:10]{index=10} :contentReference[oaicite:11]{index=11}

---

## Slice Design

## 1. Education Slice
This slice is configured with:

- `SST=1`
- `SD=000001`

It is handled by `oai-smf` and supports:

- DNN `default`
- DNN `oai.ipv4` :contentReference[oaicite:12]{index=12} :contentReference[oaicite:13]{index=13}

Associated UPFs:

- `vpp-upf` for `default`
- `vpp-upf2` for `oai.ipv4` :contentReference[oaicite:14]{index=14}

Configured UE subnets:

- `13.1.1.0/26` for `default`
- `12.1.1.64/26` for `oai.ipv4` :contentReference[oaicite:15]{index=15}

Mapped access domains:

- Slice 1 domain A via `ueransim`
- Slice 1 domain B via `ueransim1` :contentReference[oaicite:16]{index=16} :contentReference[oaicite:17]{index=17}

---

## 2. Telemedicine Slice
This slice is configured with:

- `SST=1`
- `SD=000000`

It is handled by `oai-smf2` and supports:

- DNN `oai` :contentReference[oaicite:18]{index=18} :contentReference[oaicite:19]{index=19}

Associated UPF:

- `vpp-upf3` :contentReference[oaicite:20]{index=20}

Configured UE subnet:

- `14.1.1.128/25` :contentReference[oaicite:21]{index=21}

Mapped access domain:

- Slice 2 via `ueransim2` :contentReference[oaicite:22]{index=22}

---

## Core Configuration Summary

The AMF is configured to support multiple slices under PLMN:

- `MCC=208`
- `MNC=95`
- `TAC=0xa000`

Supported slices include:

- `SST=1, SD=000000`
- `SST=1, SD=000001`
- one additional custom slice entry present in the config :contentReference[oaicite:23]{index=23}

AMF slice-aware operation is enabled with:

- `enable_nssf: no`
- `enable_smf_selection: yes` :contentReference[oaicite:24]{index=24}

---

## UERANSIM Profiles

### `ueransim`
Used for one Education Slice access domain:

- `NCI=0x000000010`
- `LINK_IP=192.168.70.141`
- `GTP_IP=192.168.72.141`
- `NUMBER_OF_UE=1`
- `APN=default`
- `SST=1`
- `SD=1` :contentReference[oaicite:25]{index=25}

### `ueransim1`
Used for another Education Slice access domain:

- `NCI=0x000000012`
- `LINK_IP=192.168.70.142`
- `GTP_IP=192.168.74.142`
- `NUMBER_OF_UE=50`
- `APN=oai.ipv4`
- `SST=1`
- `SD=1` :contentReference[oaicite:26]{index=26}

### `ueransim2`
Used for the Telemedicine Slice:

- `NCI=0x000000013`
- `LINK_IP=192.168.70.144`
- `GTP_IP=192.168.75.144`
- `NUMBER_OF_UE=1`
- `APN=oai`
- `SST=1`
- `SD=0` :contentReference[oaicite:27]{index=27}

---

## Docker Networks

The deployment uses the following Docker networks:

- `demo-oai-public-net` → shared SBI/N2/control-plane network
- `oai-public-access` → access network for `vpp-upf`
- `oai-public-access2` → access network for `vpp-upf2`
- `oai-public-access3` → access network for `vpp-upf3`
- `oai-public-core` → N6/core-facing network for external DNs :contentReference[oaicite:28]{index=28} :contentReference[oaicite:29]{index=29} :contentReference[oaicite:30]{index=30} :contentReference[oaicite:31]{index=31}

---

## Repository Structure

```text
OAI-Slicing-Use-Case/
├── docker-compose-basic-vpp-nrf.yaml
├── docker-compose-ueransim-vpp_slice1_1.yaml
├── docker-compose-ueransim-vpp_slice1_2.yaml
├── docker-compose-ueransim-vpp_slice2.yaml
├── conf/
│   ├── basic_vpp_nrf_config.yaml
│   ├── basic_vpp_nrf_config_slice1.yaml
│   └── basic_vpp_nrf_config_slice2.yaml
└── README.md
