# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 2.x | Yes |
| 1.x | No |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it by:

1. **Do NOT** open a public issue
2. Email: matteohermesai@gmail.com
3. Include: description, steps to reproduce, impact, suggested fix

We will acknowledge within 48 hours and provide a fix within 7 days.

## Security Best Practices

- Never commit secrets or API keys to the repository
- Use environment variables for all sensitive configuration
- Keep dependencies updated
- Run `make lint` before committing
- All inputs are validated via Pydantic models
