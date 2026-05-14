# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database (run once on first setup — also runs schema migrations safely)
python init_db.py

# Run the application
streamlit run app.py
```

The app runs on `http://localhost:8501` by default. There are no automated tests or linting configured.

## Entry Points

- **[pages/login.py](pages/login.py)** — The real user-facing entry point. `app.py` is a legacy shell that redirects to login; it is not the active UI.
- **[init_db.py](init_db.py)** — Creates all tables via `Base.metadata.create_all` AND runs `run_migrations()` (additive `ALTER TABLE` statements safe to re-run on existing DBs). Also seeds the `superadmin` account if missing.
- **[database.py](database.py)** — SQLAlchemy engine + `SessionLocal` factory (`sqlite:///./mrp.db`).

## Architecture

Strict three-layer pattern:

```
Pages (Streamlit UI) → Services (business logic) → Models (SQLAlchemy ORM) → SQLite DB
```

**Pages** ([pages/](pages/)) call `require_login()` / `require_cliente()` at the top, open `db = SessionLocal()`, call service functions, then close `db`. Never manage sessions inside services.

**Services** ([services/](services/)) receive `db: Session` and contain all business logic. They do not open or close sessions.

**Models** ([models/](models/)) are pure SQLAlchemy ORM with no logic.

## MRP Core Workflow

1. **Requirement** created at a work-site warehouse — `requirement_service.create_requirement()` immediately tries to reserve stock from the principal warehouse via `inventory_service.reserve_stock()`. Each `RequirementItem` gets status `reserved` or `pending`; the parent `Requirement` gets `fulfilled`, `partial`, or `pending`.
2. **Dispatch** created from a fulfilled/partial requirement — `dispatch_service.create_dispatch()` decrements `Inventory.stock` and `Inventory.reserved`, writes a `Movement(type="OUT")`.
3. **Receipt** confirms arrival at work site — increments the work-site `Inventory.stock`, writes a `Movement(type="IN")`.
4. When stock is added anywhere, `inventory_service` calls `reprocess_requirements()` to auto-satisfy `pending`/`partial` requirements.

**Stock invariant:** `available = stock - reserved`. `reserve_stock()` checks `stock - reserved >= requested_qty` before committing.

**`Inventory` model fields** ([models/inventory.py](models/inventory.py)): `stock` (total on hand) and `reserved` (held for pending requirements).

## Session & Authentication

**Session persistence** uses `st.query_params["token"]` (URL query parameter). Cookies via JS were abandoned because browsers block `document.cookie` from `data:` URL iframes. On F5/new tab, `init_session()` reads the token from the URL param and validates against the `user_sessions` DB table. `st.switch_page()` preserves `st.session_state` between pages without a full reload.

**Login security**: bcrypt (12 rounds) · 5 failed attempts locks account 15 min · sessions expire after 30 min inactivity (server-side check in `get_valid_session`).

## Role System

Two roles: `superadmin` and `cliente`. Stored in `User.role`, propagated to `UserSession.role`, available in `st.session_state.role` after login.

**Superadmin** (único, no eliminable):
- Login redirige a `pages/admin.py`
- No ve las páginas operacionales — `require_cliente()` lo redirige a `/admin`
- Acceso inicial: usuario `superadmin`, contraseña `Admin@12345`

**Cliente:**
- Login redirige a `pages/dashboard.py`
- Todos los datos se filtran por `Warehouse.owner_id == user_id`

**Guards** ([utils/auth.py](utils/auth.py)):
- `require_login()` — redirige al login si no hay sesión
- `require_cliente()` — además redirige al superadmin a `/admin` (salvo que esté impersonando)
- `require_superadmin()` — solo superadmin puede pasar

**Al agregar nuevas páginas operacionales**, usar `require_cliente()` y pasar `owner_id = get_current_user_id()` a todas las queries de `Warehouse`.

**Impersonación**: "Visualizar" en `pages/admin.py` establece `st.session_state["impersonating"] = True` y `impersonating_user_id`. `get_current_user_id()` devuelve `impersonating_user_id` cuando está activo, por lo que todos los filtros de datos son automáticamente correctos.

## Utils

- **[utils/navbar.py](utils/navbar.py)** — `render_navbar()` (suprime la nav nativa + animación fade-in) y `render_sidebar_menu()` (sidebar completo con `MutationObserver` JS que asigna `data-nav` a botones para inyección de iconos vía CSS).
- **[utils/theme.py](utils/theme.py)** — Dark/light mode CSS inyectado vía `st.markdown`.
- **[utils/session_manager.py](utils/session_manager.py)** — `init_session()` / `logout_session()`.

## Known Code Issues

- **[services/requirement_service.py](services/requirement_service.py)** contiene código muerto e inalcanzable después de la función `reprocess_requirements`: una segunda implementación parcial que comienza con `from models.requirement import Requirement` fuera de cualquier función o comentario. Es inofensiva pero debe eliminarse.
- **[app.py](app.py)** tiene un bloque grande de código comentado (legacy) seguido de código activo que renderiza una hero page — este código corre en el arranque pero los usuarios son inmediatamente redirigidos al login.

## Streamlit Configuration

[.streamlit/config.toml](.streamlit/config.toml) sets primary color `#2563eb`, hides the top toolbar, logger level `error`. Do not change `server.headless` or `browser.gatherUsageStats` without understanding the deployment context.
