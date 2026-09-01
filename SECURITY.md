# Security

## Reporting a vulnerability

Please do **not** open a public issue for security vulnerabilities. Report privately by email to the maintainers (address TBD) or via GitHub's private vulnerability reporting once the repository is public.

Include:

- The affected version(s).
- A description of the vulnerability and its impact.
- Reproduction steps or a proof of concept.
- Any proposed fix, if you have one.

You will receive an acknowledgement within 48 hours. We follow responsible disclosure: coordinate with us before publicizing.

## Design guarantees

- **No untrusted execution.** Installer definitions are product-owned and reviewed. ForgeStack never executes arbitrary installer URLs from untrusted manifests.
- **Approval required.** No external tool is installed silently. Commands and sources are displayed before sensitive installers run.
- **No silent privilege escalation.** If elevated access is needed it is never done without explicit user consent.
- **No secrets in config.** Provider tokens never belong in repository config; upstream auth flows are preferred.
- **No destructive writes.** Config is backed up or diffed before modification. No auto-push, no auto-commit by default.
- **No DB manipulation.** ForgeStack avoids direct AGTX database access and interacts through supported interfaces.

## Scope

ForgeStack is macOS-first, Linux best-effort. Windows is not currently supported or tested.