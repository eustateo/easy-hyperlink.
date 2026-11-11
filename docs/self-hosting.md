# Self-hosting Easy Hyperlink

## Public route

The public app is https://oscareustate.com/easy-hyperlink, and the portfolio project page is https://oscareustate.com/projects/easy-hyperlink.

Traffic follows the existing Cloudflare Tunnel → nginx on loopback port 8080 → portfolio Next.js on loopback port 3000 → Easy Hyperlink on the internal Docker address `172.23.0.2:8000`. No DNS change, inbound router rule, SSH tunnel, or SSH configuration change is required.

The portfolio's `next.config.ts` rewrites `/easy-hyperlink` to `http://172.23.0.2:8000/easy-hyperlink/`, and `/easy-hyperlink/:path+` to the corresponding backend path. The first rewrite deliberately adds the slash only at the backend because Next.js removes trailing slashes publicly. Browser API and JavaScript URLs are absolute paths under `/easy-hyperlink`, so either public URL works.

## Runtime isolation

`compose.production.yaml` runs a non-root container with a read-only filesystem, all Linux capabilities dropped, no privilege escalation, default seccomp/AppArmor, resource limits, and a private internal Docker network. It publishes no host ports. The host proxy reaches the fixed private address on the internal Docker network. There are no host directory mounts, SSH key mounts, Docker socket mounts, privileged mode, or host networking. The service restarts automatically and has a healthcheck. The source and container contain no SSH client credentials.

The subnet was checked against existing Docker networks before being reserved; do not change it without updating the portfolio rewrite and checking for conflicts. The application does not need outbound internet access. An internal Docker network blocks ordinary external routing. This is not a VM boundary; the host kernel and Docker daemon remain part of the trusted computing base. Internal networks alone do not prove all host services are unreachable.

## Configuration

Server source: `/home/oscareustate/apps/easy-hyperlink`.

Create `.env.production` with mode `0600`, using `.env.example` as a guide. Generate a secret on the server, not in the repository. Do not print or commit the resulting environment file.

`TRUST_CLOUDFLARE=true` must only be used with this private proxy chain. Cloudflare supplies `CF-Visitor` with the original scheme. nginx currently overwrites `X-Forwarded-Proto` with the local HTTP scheme, so the app explicitly derives HTTPS from `CF-Visitor` instead. Uvicorn's generic proxy-header trust is disabled. Next.js supplies the original host in `X-Forwarded-Host`; the app restores and validates it before redirecting. All app and API routes redirect HTTP to HTTPS and reject unexpected hosts.

HSTS lasts one hour for the current hostname. It intentionally does not cover all subdomains or request browser preloading. Django's corresponding two optional warnings remain visible in the security review.

## Deploy an update

Review and commit the intended source, scan dependencies, and run tests. Transfer an archive of that exact commit, excluding secrets. Preserve `.env.production` and backups; never archive or overwrite unrelated applications.

From the server source directory:

```sh
docker compose --env-file .env.production -f compose.production.yaml build web
docker compose --env-file .env.production -f compose.production.yaml up -d --wait
docker compose --env-file .env.production -f compose.production.yaml ps
```

There are no migrations, user accounts, admin site, or stored links. The Docker image installs dependencies from `uv.lock` with `--frozen`.

Check the public app, its JavaScript, a valid API POST, invalid schemes, HTTP redirect, sensitive-file 404s, container health and isolation. Recheck the portfolio homepage and project page.

For rollback, retain the previous image tag and source archive before rebuilding; restore the matching source/configuration and recreate this service using that image. The portfolio proxy and project entry are a separate small commit in its deployed repository. Keep its previous `.next` build until the new portfolio passes the live checks. Do not deploy the unfinished local portfolio tree as part of this app update.

## Initial release record

The initial app runtime is source revision `24db2fb6d31044f2490f65e1228dc74d26db36cc`, image `easy-hyperlink:24db2fb`. `.env.production` also selects `RELEASE_TAG=24db2fb`. The matching portfolio revision is `7407fde0537b14ec82294b744c19dc26bbb937c5`.

The portfolio's previous `.next`, `node_modules`, source archive, and revision record are retained in `/home/oscareustate/apps/easy-hyperlink-portfolio-backup-20261111`. The live portfolio remained on its existing source/deploy mechanism; the user's unfinished local portfolio edits were not deployed.

The final app does not publish port 8140 or any other host port. A Docker internal-only network does not provide the originally attempted loopback port mapping, so the host proxy uses the verified private container address instead. Its subnet and fixed address are explicit in Compose.

## Guide and icon update — 11 November 2026

Runtime revision `ae973f08d0e51ca59426e15e8305153005774899`, image `easy-hyperlink:ae973f0`, adds the SVG tab/brand icon, three-step guide, before/after email example, and app paste guidance. The image carries the source revision as an OCI label. The previous `24db2fb` image is retained for rollback. The production environment selects the new release tag; its secret was preserved.

The container remains healthy with no published ports or host mounts, and a read-only, non-root runtime. All eight integration tests passed. The public page, icon SVG route/MIME type, CSP image policy, example JavaScript, and API fragment preservation were checked over HTTPS. Browser visual/clipboard inspection remained unavailable because the browser access host was unavailable. Compatibility guidance links to official editor documentation and does not claim every browser/app combination was tested.
