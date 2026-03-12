# THREAT MODEL: Utilities4Iran

**Status:** ACTIVE (v0.1.0 Baseline)
**Environment:** Hostile / Heavily Monitored

## 1. The Adversary
Code deployed in this repository operates on the Iranian internet. The adversary is the state-operated telecommunications infrastructure. You must assume every packet, DNS request, and connection attempt is hostilely monitored and aggressively filtered.

**Adversary Capabilities:**
* **Deep Packet Inspection (DPI):** Active sniffing for VPN signatures, proxy protocols, and non-standard TLS traffic.
* **DNS Hijacking & Spoofing:** Redirection of legitimate traffic to state-controlled sinkholes.
* **SNI Filtering:** Dropping connections based on Server Name Indication before a TLS handshake completes.
* **Bandwidth Throttling & Connection Dropping:** Intentional degradation of unclassified encrypted traffic to force users onto plaintext channels.
* **Active Probing:** Replaying intercepted traffic to identify and block proxy endpoints.

## 2. The User
The end-user is operating under extreme physical and digital threat. 
* **Zero Trace:** A crashed application that leaves a plaintext log, an unencrypted SQLite database, or an orphaned `.env` file is a physical liability for the user. 
* **Resource Constrained:** Intermittent power, heavily throttled bandwidth, and outdated hardware are the norm.

## 3. Engineering Mandates (Non-Negotiable)

If your code violates these principles, your Pull Request will be rejected.

1.  **Stateless Execution:** Do not write credentials, API keys, or user metadata to local disk storage. Use environment variables exclusively.
2.  **No Telemetry:** Do not include analytics, crash reporters (e.g., Sentry), or external tracking scripts. 
3.  **Fail-Safe Design:** If the application loses connection or hits an API rate limit, it must fail silently or display a generic error. It must never dump stack traces or routing information to the UI or standard output.
4.  **Encrypted Transit Only:** Plaintext HTTP is explicitly forbidden. All connections must be over TLS 1.3 or routed through circumvention protocols.
5.  **Obfuscation over Efficiency:** If an operational requirement demands hiding traffic patterns, operational security overrides latency optimizations.