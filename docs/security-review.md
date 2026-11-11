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

Runtime inspection confirmed UID 10001, an empty effective capability mask, `NoNewPrivs: 1`, and seccomp filtering enabled. No host mounts, SSH key directory, or Docker socket were present, and the application files were not writable. Socket checks from inside the container could not reach host bridge SSH, the host Tailscale SSH address, or an internet HTTPS test address. These are targeted connectivity checks, not proof against every possible exploit.

The new application uses a non-root, read-only container with no host mounts, SSH keys, Docker socket, host networking, or Linux capabilities. It has `no-new-privileges`, CPU/memory/process limits, an internal network, and no published host ports. It uses the host's default Docker seccomp/AppArmor protections.

The container still shares the host kernel. Keep Docker, Linux, and base images patched; container isolation is a risk reduction, not an absolute security boundary.

## Findings on the existing portfolio

The original production dependency audit found three affected packages: Next.js (critical advisories), sharp (high), and source-map-js (high). Some advisories concern features the portfolio may not use; a dependency advisory alone does not establish exploitability or prior compromise. The publication change updates Next.js to 16.4.6 and compatible dependencies. A fresh `npm audit --omit=dev` on the staged Linux installation found zero production vulnerabilities. The full development installation still reports moderate advisories in lint/build tooling; those tools are not used to serve requests and are not an all-dependencies clean bill of health.

## Homelab SSH findings

Read-only inspection found `PermitRootLogin no`, `PasswordAuthentication no`, `KbdInteractiveAuthentication no`, `PubkeyAuthentication yes`, and `MaxAuthTries 3` in the readable server configuration. The SSH directory is mode 0700 and authorized_keys is mode 0600. UFW is active and fail2ban is running. Tailscale Serve has no configured public service. The existing Cloudflare tunnel publishes HTTP services and has no SSH route.

The administrator supplied `sudo ufw status verbose` output during this review. UFW is active with default deny incoming, allow outgoing, and deny routed. SSH port 22 is allowed on `tailscale0` for IPv4 and IPv6, with no public-interface SSH allow rule shown. Although sshd listens on all interfaces, these UFW rules restrict ordinary inbound SSH to the Tailscale interface. Root/password/keyboard-interactive login are disabled in the readable configuration, and our successful connection used key authentication.

**Remaining scope limits:** UFW also has broad allow-all rules on `tailscale0`. Devices permitted by tailnet ACLs can therefore reach other host listeners as well as SSH; review those ACLs and narrow this rule to intended services when convenient. A limited external TCP connectivity probe of the homelab’s observed public IPv4 endpoint found ports 22 (SSH), 2375 (unencrypted Docker API), 8000, and 8140 unreachable by timeout. This is one point-in-time IPv4 check, not a scan of every address or protocol. The effective privileged sshd configuration, current router forwarding table, and tailnet ACLs were not verified. A firewall snapshot and dependency scans cannot establish that compromise has never occurred. Docker-published ports require their own review because Docker networking may bypass ordinary UFW forwarding rules; the new app publishes no host ports.

No SSH, firewall, router, tailnet policy, existing tunnel, or authentication setting was changed. This deployment adds no SSH route or public application listener.

## Deployment checklist notes

Django deliberately leaves HSTS subdomain coverage and browser preloading disabled. Those two optional deployment-check warnings remain because this app does not establish HTTPS readiness for every other subdomain. The short HSTS policy covers only the current hostname.

## Live verification

- App source revision: `24db2fb6d31044f2490f65e1228dc74d26db36cc`; image tag `easy-hyperlink:24db2fb`, image ID `sha256:04b8069fc1c80abe8674246ea8466d3e727f0a72bd2be7d9ad56d3e013ec8515`.
- Portfolio revision: `7407fde0537b14ec82294b744c19dc26bbb937c5`; clean deployed Git worktree, Next.js 16.4.6, sharp 0.35.5, source-map-js 1.2.2. Lint, TypeScript, and production build passed; the staged Linux production dependency audit reported zero known vulnerabilities.
- The final container is healthy, UID 10001, read-only, with `cap_drop: ALL`, `no-new-privileges`, zero host mounts, zero published host ports, and an internal Docker network. Restart policy is `unless-stopped`.
- Public homepage, projects index, project detail, app page, and JavaScript returned HTTP 200. A valid API POST returned the normalized link. Unsupported schemes and embedded credentials returned 422. A 17 KiB body returned 413. HTTP redirected to the public HTTPS address. CSP, nosniff, no-store, and short HSTS headers were present.
- Public `.env`, `.git/config`, admin, and API documentation paths returned 404. The staged complete proxy path also rejected an unexpected forwarded host with HTTP 400.
- All eight application integration tests and JavaScript syntax validation passed. Credential-pattern scanning found no private-key blocks, GitHub token patterns, or AWS access-key patterns in the project source. This pattern check is not an exhaustive secret detector.
- Browser UI/clipboard testing was unavailable because the computer-use browser host was unavailable. HTTP/API, routing, headers, and JavaScript syntax were verified; actual rich-text clipboard behavior remains browser-dependent.
- The previous portfolio build and dependencies were retained at `/home/oscareustate/apps/easy-hyperlink-portfolio-backup-20261111` for rollback. Other hosted services and SSH/firewall/tunnel configurations were preserved.

No operating-system/container-image CVE inventory or authenticated penetration test was performed. Keep the base image, Linux, Docker, dependencies, and Tailscale clients updated.
