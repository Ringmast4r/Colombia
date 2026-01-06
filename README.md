# Colombia OSINT - Gustavo Petro Infrastructure Analysis

<p align="center">
  <img src="Assets/Presidente_Gustavo_Petro_Urrego-1.jpg" alt="Gustavo Petro" width="400">
</p>

---

<p align="center">

![Visitors](https://api.visitorbadge.io/api/visitors?path=Ringmast4r%2FColombia&label=VISITORS&countColor=%23dc143c&style=for-the-badge)

![OFAC](https://img.shields.io/badge/OFAC-SANCTIONED-red?style=for-the-badge)
![Counter-Narcotics](https://img.shields.io/badge/COUNTER-NARCOTICS-blue?style=for-the-badge)
![OSINT](https://img.shields.io/badge/OPEN_SOURCE-INTELLIGENCE-black?style=for-the-badge)

![GitHub stars](https://img.shields.io/github/stars/Ringmast4r/Colombia?style=for-the-badge&logo=github&color=gold)
![GitHub forks](https://img.shields.io/github/forks/Ringmast4r/Colombia?style=for-the-badge&logo=github&color=blue)
![GitHub watchers](https://img.shields.io/github/watchers/Ringmast4r/Colombia?style=for-the-badge&logo=github&color=green)

![GitHub repo size](https://img.shields.io/github/repo-size/Ringmast4r/Colombia?style=for-the-badge&logo=github&color=purple)
![GitHub last commit](https://img.shields.io/github/last-commit/Ringmast4r/Colombia?style=for-the-badge&logo=github&color=orange)
![License](https://img.shields.io/badge/LICENSE-OSINT-green?style=for-the-badge)

</p>

---

## Target Overview

| Attribute | Detail |
|-----------|--------|
| **Subject** | Gustavo Francisco Petro Urrego |
| **Position** | 35th President of Colombia |
| **Status** | **US SANCTIONED** (OFAC SDN List - October 24, 2025) |
| **Background** | Former M-19 guerrilla member (joined age 17) |
| **Domain** | presidencia.gov.co |
| **Registered** | 1999-10-29 |

---

## Project Statistics

| Category | Count | Size |
|----------|-------|------|
| RAW DOWNLOADS | 455+ | 2.0 GB |
| KEY FINDINGS | 35 | 224 KB |
| HTML Maps | 24+ | 247 MB |
| Hashes/Credentials | 6 | 34 KB |
| Intel Reports | 5 | 24 KB |
| **TOTAL** | **544+** | **2.5 GB** |

---

## Critical Findings

### Critical Finding #1: Open ArcGIS Server

| Component | Detail |
|-----------|--------|
| URL | `https://ergit.presidencia.gov.co/server/rest/services` |
| Status | **PUBLICLY ACCESSIBLE - NO AUTHENTICATION** |
| Version | ArcGIS Enterprise 11.3.0 (Build 51575) |
| Services | 300+ across 26 folders |
| Data | Military maps, armed group territories, victim data |

### Critical Finding #2: Police AI Platform (AWS)

| Component | Detail |
|-----------|--------|
| URL | `https://ia.policia.gov.co` |
| AWS Account | 926162397524 |
| S3 Bucket | `pon-prod-ai-platform-926162397524.s3.amazonaws.com` |
| AI Backend | Amazon Bedrock (NADIA AI assistant) |
| Subdomains | 20+ discovered (app, nadia, aisearchengine, etc.) |

### Critical Finding #3: Intelligence Agencies

| Agency | Subdomains | Notable |
|--------|------------|---------|
| DNI (National Intelligence) | 15 | Codename servers: birmania, denver, kuwait |
| Fiscalia (Prosecutor) | 30+ | GIS app, payroll, recording systems |
| DIJIN (Criminal Investigation) | 5+ | Pandora case management |

---

## Infrastructure Enumerated

| Domain | Subdomains | Type |
|--------|------------|------|
| ejercito.mil.co | 147 | Army |
| armada.mil.co | 94 | Navy |
| fac.mil.co | 79 | Air Force |
| cgfm.mil.co | 41 | Joint Forces |
| policia.gov.co | 60+ | Police |
| ia.policia.gov.co | 20+ | Police AI |
| dni.gov.co | 15 | Intelligence |
| fiscalia.gov.co | 30+ | Prosecutor |
| mininterior.gov.co | 27 | Interior Ministry |
| colombiahumana.co | 54 | Political Party |
| pactohistorico.co | 12 | Political Party |
| **TOTAL** | **513+** | |

---

## ArcGIS Services Enumerated

| Folder | Services | Critical Data |
|--------|----------|---------------|
| Root | 33 | Military maps, judicial data |
| Hosted | 240+ | Armed groups, violence, coca |
| DDHH | 22 | Human rights, protection routes |
| UnidadCumplimiento | 8 | Compliance tracking |
| aicma | 4 | Landmine data |
| FondoPaz | 2 | Peace fund projects |
| **TOTAL** | **300+** | |

---

## Credentials Extracted

| Type | Count | Source |
|------|-------|--------|
| All Emails | 460+ | ArcGIS feature data |
| Gov Emails (.gov.co) | 113 | Government domains |
| Hashes/GUIDs | 103 | Service metadata |
| Usernames | 3 | Portal configs |
| AWS Account ID | 1 | S3 bucket naming |
| Session Cookies | 3 | Police AI platform |

---

## Intelligence Data Captured

### Military Intelligence
- CNR_SEP_2025_MIL1: September 2025 operational map (156 MB)
- CNR_julio_2025_MIL1: July 2025 operational map
- Mapa_AT_MIL1: AT zone military map
- Mapa_Caso_03_MIL1: Case 03 investigation map

### Armed Group Territories (87+ zones)
- ELN: 11 zones + critical zones (21 MB)
- Clan del Golfo (AGC): 22 zones (1.9 MB)
- Disidencias EMC: 22 zones + critical zones (97 MB)
- Segunda Marquetalia: 21 zones (Dec 2024)
- Disidencias EMBF: 11 zones

### Peace Process Data
- 163 MB signatory location data (Firmantes mayo 2025)
- 37.7 MB attack data (110 incidents H1 2025)
- AETCR camp locations (24 reintegration sites)
- 29 homicides, 9 disappearances, 68 threats

### Violence Statistics (2010-2025)
- Homicides, Femicides, Kidnappings
- Extortion, Human trafficking, Displacement
- Massacres, Threats, Sexual crimes
- Actions against police

---

## Subject Timeline

| Year | Event |
|------|-------|
| 1960 | Born April 19, Cienaga de Oro, Cordoba |
| 1977 | Joins M-19 guerrilla (age 17), pseudonym "Aureliano" |
| 1985 | M-19 Palace of Justice siege - 98+ killed |
| 1985 | Petro arrested for M-19 membership |
| 1990 | M-19 demobilizes, becomes political party |
| 2022 | Elected President of Colombia (first left-wing) |
| Sep 2025 | US visa revoked after pro-Palestinian UN speech |
| Oct 2025 | **SANCTIONED by US Treasury (OFAC SDN List)** |
| Jan 2026 | Maduro captured - Petro condemns US, deploys troops |

---

## Repository Structure

```
COLOMBIA/
|-- README.md                         <- This file
|-- INDEX.txt                         <- Master index
|-- GUSTAVO_PETRO_TIMELINE.txt        <- Full chronological dossier
|-- PRESIDENCIA_OSINT_REPORT.txt      <- Technical OSINT report
|-- SOURCES.txt                       <- News/research sources
|
|-- KEY FINDINGS/                     <- 35 intelligence files
|   |-- 01-09: Infrastructure, subdomains, IPs, ArcGIS, DNS
|   |-- 10-18: Domains, party sites, social media, tokens
|   |-- 19-27: Military intel, peace attacks, credentials
|   |-- 28-35: US crisis, Police AI, Intel agencies, wrap-up
|
|-- RAW DOWNLOADS/                    <- ArcGIS data (455+ files, 2.0 GB)
|   |-- CNR_*_MIL1_*                  <- Military map layers
|   |-- DDHH_*                        <- Human rights data
|   |-- ELN_*, ClanDelGolfo_*, EMC_*  <- Armed group territories
|   |-- Homicidios_*, Masacre_*       <- Violence statistics
|   |-- PoliceAI_*, DNI_*             <- Platform captures
|
|-- Credentials/                      <- Extracted credentials (40 KB)
|   |-- EMAILS.txt                    <- 460+ exposed emails
|   |-- GOV_EMAILS.txt                <- 113 government emails
|   |-- HASHES.txt                    <- 103 hashes/GUIDs
|   |-- USERNAMES.txt                 <- 3 usernames
|   |-- AWS_CREDENTIALS.txt           <- AWS Account ID, STS tokens
|   |-- SESSION_COOKIES.txt           <- Police AI session cookies
|
|-- HTML/                             <- Interactive maps (247 MB)
|   |-- index.html                    <- Overview
|   |-- armed_groups_map.html         <- Territory visualization
|   |-- attacks_on_signatories_map.html
|   |-- *.geojson                     <- Map data files
|
|-- intel/                            <- Intelligence reports (24 KB)
|   |-- PETRO_PROFILE.txt
|   |-- M19_CRIMES.txt
|   |-- US_SANCTIONS.txt
|   |-- MADURO_CONNECTION.txt
|   |-- DRUG_TRADE.txt
|
|-- sources/                          <- OSINT methodology (13 KB)
|   |-- OSINT_SOURCES.txt             <- Complete source documentation
|
|-- Assets/                           <- Graphics
|-- Snips/                            <- Screenshots
```

---

## Vulnerability Summary

| Severity | Count | Examples |
|----------|-------|----------|
| CRITICAL | 5 | ArcGIS no auth, military maps public, 240+ hosted services |
| HIGH | 6 | Armed group data, signatory locations, 460 emails |
| MEDIUM | 5 | Portal config, server version, AWS temp creds |
| **TOTAL** | **16** | |

---

## Sessions Conducted

| Session | Date | Focus | Output |
|---------|------|-------|--------|
| 1 | Jan 4 Evening | ArcGIS discovery | 1.18 GB |
| 2 | Jan 5 Morning | Crisis research, military | 0.2 GB |
| 3 | Jan 5 PM #1 | Police AI, intel agencies | 0.3 GB |
| 4 | Jan 5 PM #2 | Complete enumeration | 0.4 GB |

---

## Methodology

All intelligence gathered through legal OSINT techniques:
- Certificate Transparency (crt.sh) subdomain enumeration
- DNS reconnaissance (A, MX, TXT, NS records)
- WHOIS/ASN mapping
- Public ArcGIS REST API enumeration
- HTTP header analysis
- AWS infrastructure identification
- News aggregation & official statements

---

## Legal Notice

This repository contains **publicly available information** gathered through open source intelligence. No systems were compromised. Sources include:
- Public DNS records
- Certificate Transparency logs
- US Treasury/OFAC public designations
- Publicly accessible ArcGIS services (no authentication required)
- News media

---

*Last Updated: January 5, 2026*
