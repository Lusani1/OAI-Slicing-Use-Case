
# OAI-Slicing-Use-Case

Practical OpenAirInterface 5G Core network slicing use case using a **shared control plane**, **multiple SMFs**, **multiple VPP-based UPFs**, and **UERANSIM-based gNB/UE emulation** for distributed service domains. The scenario demonstrates how a central 5G core can support multiple slices with slice-specific DNNs, subnets, and user-plane anchoring. 
## Architecture Overview

This repository implements a slicing scenario aligned to the attached architecture:
<img width="978" height="523" alt="Screenshot from 2026-03-11 11-51-36" src="https://github.com/user-attachments/assets/52815b8b-775a-4cad-b6c1-cc9a8c5ecb53" />



- A **shared control plane** hosted in a central data centre
- An **Education Slice** spanning two access domains
- A **Telemedicine Slice** spanning a separate access domain
- Dedicated **UPFs** and **DNNs** per traffic domain
- Slice-aware session handling using **S-NSSAI**, **SMF selection**, and **UPF/DNN mapping** 
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
- `oai-smf2`
  
The config for the shared control plane is `shared_control_functions.yaml`
  
### User plane
The deployment includes three VPP-based UPFs:

- `vpp-upf`
- `vpp-upf2`
- `vpp-upf3`

The configs for the user plane functions (edge nodes) are `upf1.yaml`, `upf2.yaml` and `upf3.yaml`.

### Access emulation
Three UERANSIM instances emulate geographically separated gNB/UE domains:

- `ueransim`
- `ueransim1`
- `ueransim2`
  
The configs for the gNB/UE stacks are `docker-compose-ueransim-vpp_slice1_1.yaml`, `docker-compose-ueransim-vpp_slice1_2.yaml`, and `docker-compose-ueransim-vpp_slice2.yaml`.

---

## Slice Design

## 1. Education Slice
This slice is configured with:

- `SST=1`
- `SD=000001`

It is handled by `oai-smf` and supports:

- DNN `default`
- DNN `oai.ipv4`
  
Associated UPFs:

- `vpp-upf` for `default`
- `vpp-upf2` for `oai.ipv4` 

Configured UE subnets:

- `13.1.1.0/26` for `default`
- `12.1.1.64/26` for `oai.ipv4` 

Mapped access domains:

- Slice 1 domain A via `ueransim`
- Slice 1 domain B via `ueransim1` 
---

## 2. Telemedicine Slice
This slice is configured with:

- `SST=1`
- `SD=000000`

It is handled by `oai-smf2` and supports:

- DNN `oai` 

Associated UPF:

- `vpp-upf3` 

Configured UE subnet:

- `14.1.1.128/25` 

Mapped access domain:

- Slice 2 via `ueransim2`
  
---

## Core Configuration Summary

The AMF is configured to support multiple slices under PLMN:

- `MCC=208`
- `MNC=95`
- `TAC=0xa000`

Supported slices include:

- `SST=1, SD=000000`
- `SST=1, SD=000001`
- one additional custom slice entry present in the config
  
AMF slice-aware operation is enabled with:

- `enable_nssf: no`
- `enable_smf_selection: yes`
  
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
- `SD=1` 

### `ueransim1`
Used for another Education Slice access domain:

- `NCI=0x000000012`
- `LINK_IP=192.168.70.142`
- `GTP_IP=192.168.74.142`
- `NUMBER_OF_UE=50`
- `APN=oai.ipv4`
- `SST=1`
- `SD=1` 

### `ueransim2`
Used for the Telemedicine Slice:

- `NCI=0x000000013`
- `LINK_IP=192.168.70.144`
- `GTP_IP=192.168.75.144`
- `NUMBER_OF_UE=1`
- `APN=oai`
- `SST=1`
- `SD=0` 

---

## Docker Networks

The deployment uses the following Docker networks:

- `demo-oai-public-net` → shared SBI/N2/control-plane network
- `oai-public-access` → access network for `vpp-upf`
- `oai-public-access2` → access network for `vpp-upf2`
- `oai-public-access3` → access network for `vpp-upf3`
- `oai-public-core` → N6/core-facing network for external DNs
  
---

## Repository Structure (For this use case)

```text
OAI-Slicing-Use-Case/
├── upf1.yaml
├── upf2.yaml
├── upf3.yaml
├── dn1.yaml
├── dn2.yaml
├── dn3.yaml
├──shared_control_functions.yaml
├── docker-compose-ueransim-vpp_slice1_1.yaml
├── docker-compose-ueransim-vpp_slice1_2.yaml
├── docker-compose-ueransim-vpp_slice2.yaml
├── conf/
│   ├── basic_vpp_nrf_config.yaml
│   ├── basic_vpp_nrf_config_slice1.yaml
│   └── basic_vpp_nrf_config_slice2.yaml
└── README.md
```
---

## File roles
- `docker-compose-basic-vpp-nrf.yaml`
  
Deploys the shared core, SMFs, UPFs, and external data networks. 

- `basic_vpp_nrf_config.yaml`
  
Shared AMF/NRF/UDM/UDR/AUSF configuration and AMF slice support. 

- `basic_vpp_nrf_config_slice1.yaml`
  
SMF configuration for the slice with SST=1, SD=000001. 

- `basic_vpp_nrf_config_slice2.yaml`
  
SMF configuration for the slice with SST=1, SD=000000. 
- `docker-compose-ueransim-vpp_slice1_1.yaml`
  
UERANSIM deployment for Education Slice domain A. 

- `docker-compose-ueransim-vpp_slice1_2.yaml`
  
UERANSIM deployment for Education Slice domain B. 

- `docker-compose-ueransim-vpp_slice2.yaml`
  
UERANSIM deployment for the Telemedicine Slice.

---

## Prerequisites
Before running the scenario, ensure the host has:
- Docker
- Docker Compose
- Linux with support for privileged containers
- Sufficient CPU and RAM for multiple CN containers and UERANSIM instances
- Proper routing / iptables support for container-based data networking
The compose files assume the referenced OAI and UERANSIM images are available locally or can be pulled successfully.

---

## Deployment
1. Start the shared core
```bash
docker compose -f docker-compose-basic-vpp-nrf.yaml up -d
```
2. Start Education Slice access domain A
```bash
docker compose -f docker-compose-ueransim-vpp_slice1_1.yaml up -d
```
3. Start Education Slice access domain B
```bash
docker compose -f docker-compose-ueransim-vpp_slice1_2.yaml up -d
```
4. Start Telemedicine Slice access domain
```bash
docker compose -f docker-compose-ueransim-vpp_slice2.yaml up -d
```
---
## Validation
Check running containers
```bash
docker ps
```
You should see containers such as:
- mysql
- oai-nrf
- oai-amf
- oai-ausf
- oai-udm
- oai-udr
- oai-smf
- oai-smf2
- vpp-upf
- vpp-upf2
- vpp-upf3
- ueransim
- ueransim1
- ueransim2

### Check UE tunnel establishment

The UERANSIM containers use a health check based on the presence of uesimtun0, which is a good first sign that registration and PDU session establishment succeeded. 

```bash
docker inspect --format='{{json .State.Health}}' ueransim | jq
docker inspect --format='{{json .State.Health}}' ueransim1 | jq
docker inspect --format='{{json .State.Health}}' ueransim2 | jq
```
### Check logs
```bash
docker logs oai-amf
docker logs oai-smf
docker logs oai-smf2
docker logs vpp-upf
docker logs vpp-upf2
docker logs vpp-upf3
docker logs ueransim
docker logs ueransim1
docker logs ueransim2
```
### Check UE addressing inside container
```bash
docker exec -it ueransim ip addr show uesimtun0
docker exec -it ueransim1 ip addr show uesimtun0
docker exec -it ueransim2 ip addr show uesimtun0
```
Expected UE IP pools include:
- 13.1.1.0/26
- 12.1.1.64/26
- 14.1.1.128/25

---

## How Traffic Is Steered
This use case demonstrates the following slice workflow:
1. UERANSIM gNBs connect to the shared AMF over N2
2. UEs register using the configured PLMN and requested S-NSSAI
3. The AMF performs slice-aware SMF selection
4. The appropriate SMF anchors the session to the correct UPF
5. User traffic is forwarded over N3 and broken out over N6 to the intended DN 

In this setup:
- SST=1, SD=000001 is handled by oai-smf
- SST=1, SD=000000 is handled by oai-smf2 

For the Education Slice:
- default traffic maps to vpp-upf
- oai.ipv4 traffic maps to vpp-upf2 

For the Telemedicine Slice:
- oai traffic maps to vpp-upf3 

---

## Use Case Interpretation
This repository can be used to demonstrate:
- shared-control-plane slicing
- distributed UPF anchoring
- multi-domain access under a common slice
- separation of service domains such as education and telemedicine
- practical OAI-based slice selection and traffic steering using Docker Compose

Although the architecture uses geographic labels such as Gauteng, Limpopo, Cape Town, and Northern Cape, the deployment itself is implemented as a lab/demo environment using Docker-based logical separation. 

---

## Limitations
This repository is intended for research, experimentation, and demonstration.
Current limitations include:
- static Docker networking
- emulated RAN/UE environment using UERANSIM
- minimal security hardening
- no orchestration layer such as Kubernetes or OSM
- no production-grade observability or resiliency framework

---

## Future Improvements
Possible next steps include:
- integrating NSSF-driven slice selection
- replacing UERANSIM with real OAI RAN components
- adding QoS differentiation and traffic policing
- collecting per-slice performance metrics
- deploying edge applications behind each DN
- integrating with orchestration platforms such as OpenStack, Kubernetes, or OSM

---

## Acknowledgement
This repository builds on OpenAirInterface 5G Core components, VPP-based UPF containers, and UERANSIM-based access emulation, adapted into a multi-slice demonstration environment for practical experimentation.
