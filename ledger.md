# Project Context Ledger: AUI (AOS Unified UI Control System)

## 2026-07-13: Initial Synthesis and E2E Implementation
- **Author**: Antigravity (AI Architect)
- **Goal**: Synthesize `browser-use`, `desktop-vision-operator`, and `etw-shadow-dom`.
- **Decision Rationale**: Multiverse Planner selected an async daemon using Win32 API window enums, a shared file IPC protocol with `filelock`, and Playwright hook interception.
- **Fundamental Truths**:
  - Standard Windows COM `UIAutomation` can fail or return empty trees in headless or Session 0 terminal contexts.
  - Native Win32 `EnumWindows` and `EnumChildWindows` APIs via `ctypes` reliably bypass these COM service limitations, extracting window titles, class names, and boundaries.
- **Dead-Ends**:
  - Playwright's native `FileChooser` handler blocks indefinitely on custom desktop-native dialog hooks.
  - FastAPI-based HTTP APIs introduce port collision risks and process lifecycle tracking complexity compared to atomic file locks.

## 2026-07-13: Enterprise-Ready Upgrade
- **Author**: Antigravity (AI Architect)
- **Goal**: Apply ruff checks, OpenTelemetry instrumentation, Docker Compose integration, and PolyForm licensing.
- **Fundamental Truths**:
  - Running GUI/PyAutoGUI/browser-use E2E tests inside Docker requires Xvfb virtual display framing. Setting up Xvfb screen parameters inside the Docker entrypoint guarantees test execution.
  - Active OTLP trace exporters block or timeout in local testing when no collector is running. Telemetry initialization must gracefully fallback to a silent provider unless explicit endpoints are passed.
