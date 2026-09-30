# Security

Architecture files can contain confidential client, site, access, and building information.

## Agent safety model
- Skills request only the access needed for the task.
- Bulk CAD/BIM transforms follow inventory → dry run → sample → validate → full run → audit.
- Never embed credentials, private client data, or proprietary model files in this repository.
- Treat third-party MCP servers, plugins, scripts, and downloaded references as untrusted until reviewed.
- Global installers must not use sudo, modify unrelated configuration, or overwrite existing user content without backup.

Report exploitable security issues through GitHub security advisories where available.
