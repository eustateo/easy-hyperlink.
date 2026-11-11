# Self-hosting Easy Hyperlink

## Public route

The public app is https://oscareustate.com/easy-hyperlink, and the portfolio project page is https://oscareustate.com/projects/easy-hyperlink.

Traffic follows the existing Cloudflare Tunnel → nginx on loopback port 8080 → portfolio Next.js on loopback port 3000 → Easy Hyperlink on loopback port 8140. No DNS change, inbound router rule, SSH tunnel, or SSH configuration change is required.

The portfolio's `next.config.ts` rewrites `/easy-hyperlink` to `http://127.0.0.1:8140/easy-hyperlink/`, and `/easy-hyperlink/:path+` to the corresponding backend path. The first rewrite deliberately adds the slash only at the backend because Next.js removes trailing slashes publicly. Browser API and JavaScript URLs are absolute paths under `/easy-hyperlink`, so either public URL works.

## Runtime isolation

`compose.production.yaml` runs a non-root container with a read-only filesystem, all Linux capabilities dropped, no privilege escalation, default seccomp/AppArmor, resource limits, and a private internal Docker network. The only published port binds to `127.0.0.1`. There are no host directory mounts, SSH key mounts, Docker socket mounts, privileged mode, or host networking. The service restarts automatically and has a healthcheck. The source and container contain no SSH client credentials.

The application does not need outbound internet access. An internal Docker network blocks ordinary external routing. This is not a VM boundary; the host kernel and Docker daemon remain part of the trusted computing base. Internal networks alone do not prove all host services are unreachable.

## Configuration

Server source: `/home/oscareustate/apps/easy-hyperlink`.

Create `.env.production` with mode `0600`, using `.env.example` as a guide. Generate a secret on the server, not in the repository. Do not print or commit the resulting environment file.

`TRUST_CLOUDFLARE=true` must only be used with this loopback-only proxy chain. Cloudflare supplies `CF-Visitor` with the original scheme. nginx currently overwrites `X-Forwarded-Proto` with the local HTTP scheme, so the app explicitly derives HTTPS from `CF-Visitor` instead. Uvicorn's generic proxy-header trust is disabled. All app and API routes redirect HTTP to HTTPS and reject unexpected hosts.

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
