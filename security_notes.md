# Production Security Notes

This document provides a more detailed overview of security considerations when moving this application toward a production environment. The default configuration is designed for ease of development and is **not secure for production use**.

### 1. API Authentication

- **Current State**: The API uses a single, static bearer token (`API_STATIC_TOKEN`) shared by all clients.
- **Risk**: High. If this token is compromised, any party can access the API. There is no per-user authentication or authorization.
- **Action Plan**:
    - **Replace static tokens with a standard OAuth 2.0 flow**. The "Client Credentials" flow is suitable for machine-to-machine communication. For user-facing applications, an "Authorization Code" flow is required.
    - Use a library like `Authlib` or `FastAPI-Users` to implement the chosen OAuth 2.0 flow.
    - Implement token introspection or JWT validation to verify tokens on each request.
    - If integrating with a Learning Management System (LMS), use the **LTI 1.3** standard, which provides a secure, OAuth2-based launch flow.

### 2. Secrets Management

- **Current State**: Secrets (`NEO4J_PASSWORD`, `API_STATIC_TOKEN`) are stored in a plain-text `.env` file.
- **Risk**: High. Storing secrets in code or in plain-text files on disk is a major security risk. These files can be accidentally committed to version control or exposed if the server's file system is compromised.
- **Action Plan**:
    - **Use a dedicated secrets management service**. Examples include:
        - AWS Secrets Manager
        - Google Secret Manager
        - HashiCorp Vault
        - Azure Key Vault
    - The application should fetch secrets from the secrets manager at startup. **Do not** store secrets in environment variables in your production environment's host configuration (e.g., in Docker Compose files). Instead, use the integration tools provided by your cloud or container orchestrator to securely inject them.

### 3. Neo4j Aura Credentials

- **Current State**: A long-lived database password is stored in the `.env` file.
- **Risk**: Medium to High. If this password leaks, your database is compromised.
- **Action Plan**:
    - **Regularly rotate your Neo4j Aura password**. This can be done from the Aura console. Treat database credentials as sensitive secrets and follow the secrets management plan above.
    - **Implement the principle of least privilege**. Create a read-only database user for the API if it only needs to read from the graph. The current implementation uses the default admin user, which has full permissions. Create a new user with `ROLE reader` and use its credentials for the API service.

### 4. Network Security

- **Current State**: The application runs over HTTP by default.
- **Risk**: High. All traffic, including the bearer token and student data, is sent in plain text.
- **Action Plan**:
    - **Enforce HTTPS**. Deploy the application behind a reverse proxy (like Nginx, Traefik, or a cloud load balancer) that handles TLS/SSL termination.
    - Configure the reverse proxy to only accept connections on port 443 (HTTPS) and redirect any HTTP traffic to HTTPS.

### 5. Input Validation and Secure Dependencies

- **Current State**: Good. FastAPI with Pydantic provides strong, automatic validation of incoming request bodies, which is a great defense against many injection-style attacks.
- **Action Plan**:
    - **Keep dependencies up to date**. Regularly run a security scanner on your dependencies (like `pip-audit` or `Snyk`) to check for known vulnerabilities and update packages accordingly.
    - `pip-audit`
    - `safety check`
    - `snyk test --file=requirements.txt`
