# Documentation App

## Project Structure

This project is structured into several key modules to ensure maintainability, clarity, and modularity. Below is an overview of each core file and its purpose:

---

### `app.py`

This file defines the **FastAPI application instance**. It sets up the main application entry point, configures all necessary routes, and integrates the lifespan functionality that orchestrates startup and shutdown events for the service.

---

### `auth.py`

This module provides a **single function for Bearer token validation**. Every incoming request to protected endpoints is checked to ensure that it includes a valid authorization token. This layer of authentication enhances the security of the application by preventing unauthorized access.

---

### `lifespan.py`

This module acts as the **central orchestration layer** of the application. It performs the following critical tasks during application startup:
- Loads credentials and configuration settings from the config file.
- Initializes and wires up the main submodules:
  - [SDP Module](/docs/sdp/README.md)
  - [CheckMK Module](/docs/checkmk/README.md)
- Launches background tasks for both modules to handle async operations.
- Sets up the required database tables.
- Refreshes the in-memory problem cache to ensure up-to-date tracking of issues.

Essentially, this file lays the foundation for the application's runtime behavior and background processing.

---

### `models.py`

Contains **Pydantic models** used for request parsing and response serialization. These models ensure that all incoming and outgoing JSON payloads conform to a defined schema, allowing structured and type-safe interactions across the application.

---

### `notification.py`

Handles the **construction and dispatching of service desk requests**. Specifically:
- Converts CheckMK problem data into a `CreationRequest` object.
- Sends the request to the [SDP Module](/docs/sdp/README.md) for further handling.
- Persists the request into the database, establishing a mapping between:
  - A CheckMK problem ID, and
  - The corresponding SDP request ID.

This mapping allows for consistent tracking and correlation of issues across systems.

---

### `routes.py`

Defines all **HTTP API endpoints** exposed for the SDP plugin via FastAPI. Each route is tied to a specific notification function for creating the request.

---

## Summary

This modular architecture supports scalability, simplifies debugging, and promotes separation of concerns. Each file is responsible for a distinct part of the system, contributing to a robust and well-organized application.
