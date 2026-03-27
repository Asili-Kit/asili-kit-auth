# Asili Kit Auth - Integration Roadmap

This roadmap defines the ordered steps required to make the auth module easy to integrate in external projects.

## Phase 1 - Safe Defaults and Runtime Consistency

Status: ✅ complete

1. Enforce secure configuration defaults.
- Fail fast if `SECRET_KEY` is unsafe outside debug.

2. Separate local convenience from production migrations.
- Keep runtime table creation optional using `AUTO_CREATE_TABLES`.
- Recommend Alembic as the production source of truth.

3. Ensure mobile logout matches backend contract.
- Send bearer token on logout requests.

## Phase 2 - Developer Integration Experience

Status: ✅ complete

1. Create a one-page Quickstart (10-15 minutes max).
- Backend install, env setup, migration, run command.
- Flutter module setup and minimal usage.

2. Publish a stable API contract section.
- Endpoint list, request/response examples, error codes.
- Token lifecycle and session rotation behavior.

3. Add environment strategy.
- `dev`, `staging`, `prod` base URL conventions.
- Avoid hard-coded API host in mobile code.

4. Add integration examples.
- One minimal host app integration flow.
- Startup auth check + guarded route + logout.

## Integration Acceptance Criteria

1. A developer can run backend + migrations in under 10 minutes.
2. A Flutter app can integrate login/register/logout in under 30 minutes.
3. API errors are predictable and documented.
4. Security-critical defaults are safe in non-debug mode.
5. Updating module versions is documented and low risk.
