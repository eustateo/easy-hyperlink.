# Security review — 11 November 2026

Scope: Easy Hyperlink source, Python dependencies, deployment configuration, the serving portfolio's production dependencies, and read-only homelab SSH/network checks. This is a targeted review, not a penetration test or a guarantee against compromise.

## Application controls

- Django production mode requires a random secret and explicit hosts; debug is disabled in deployment.
- The page and API share the public HTTPS origin. Both reject unexpected Host headers and redirect HTTP to HTTPS.
- Only HTTP/HTTPS URLs are accepted, with no embedded credentials. Names, URLs, and request bodies have size limits. No destination URLs are fetched, so submitting an address does not make the server contact it.
- User names become DOM `textContent`, not HTML. Clipboard HTML comes from that DOM anchor. JavaScript is served as a separate same-origin file; CSP disallows inline scripts.
- The service has no login, admin endpoint, saved links, database writes, file upload, shell command, SSH operation, or Docker operation.
- Known Python dependency scan: `pip-audit` found no known vulnerabilities in the 17 third-party packages checked. The local project is reviewed as source and is not a PyPI advisory entry. Results are time-specific.
- Eight ASGI integration tests cover the composed production app, prefix routing, valid links, invalid schemes, embedded credentials, untrusted markup as JSON, malformed input, chunked request limits, hostile hosts, HTTPS redirect, and sensitive-path 404s.

## Runtime controls

The new application uses a non-root, read-only container with no host mounts, SSH keys, Docker socket, host networking, or Linux capabilities. It has `no-new-privileges`, CPU/memory/process limits, an internal network, and no published host ports. It uses the host's default Docker seccomp/AppArmor protections.

The container still shares the host kernel. Keep Docker, Linux, and base images patched; container isolation is a risk reduction, not an absolute security boundary.

## Findings on the existing portfolio

The original production dependency audit found three affected packages: Next.js (critical advisories), sharp (high), and source-map-js (high). Some advisories concern features the portfolio may not use; a dependency advisory alone does not establish exploitability or prior compromise. The publication change updates Next.js and compatible dependencies and requires a fresh production audit before rollout.

## Homelab SSH findings

Read-only inspection found `PermitRootLogin no`, `PasswordAuthentication no`, `KbdInteractiveAuthentication no`, `PubkeyAuthentication yes`, and `MaxAuthTries 3` in the readable server configuration. The SSH directory is mode 0700 and authorized_keys is mode 0600. UFW is active and fail2ban is running. Tailscale Serve has no configured public service. The existing Cloudflare tunnel publishes HTTP services and has no SSH route.

The administrator supplied `sudo ufw status verbose` output during this review. UFW is active with default deny incoming, allow outgoing, and deny routed. SSH port 22 is allowed on `tailscale0` for IPv4 and IPv6, with no public-interface SSH allow rule shown. Although sshd listens on all interfaces, these UFW rules restrict ordinary inbound SSH to the Tailscale interface. Root/password/keyboard-interactive login are disabled in the readable configuration, and our successful connection used key authentication.

**Remaining scope limits:** UFW also has broad allow-all rules on `tailscale0`. Devices permitted by tailnet ACLs can therefore reach other host listeners as well as SSH; review those ACLs and narrow this rule to intended services when convenient. The effective privileged sshd configuration, current router forwarding table, tailnet ACLs, and an independent external origin-port probe were not verified. A firewall snapshot and dependency scans cannot establish that compromise has never occurred. Docker-published ports require their own review because Docker networking may bypass ordinary UFW forwarding rules; the new app publishes no host ports.

No SSH, firewall, router, tailnet policy, existing tunnel, or authentication setting was changed. This deployment adds no SSH route or public application listener.

## Deployment checklist notes

Django deliberately leaves HSTS subdomain coverage and browser preloading disabled. Those two optional deployment-check warnings remain because this app does not establish HTTPS readiness for every other subdomain. The short HSTS policy covers only the current hostname.

## Live verification

Record deployment image/configuration, public route tests, isolation checks, and the final portfolio dependency audit here after rollout.
