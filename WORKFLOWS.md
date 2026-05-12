# Base Ephemeral Template Workflows

## 1) Generate Project
1. Select this template in ProjectMaker.
2. Provide required project settings.
3. Cookiecutter scaffolds backend, frontend, infra, and scripts.

## 2) Configure Environment
1. Set backend env vars in `BackEndApi/.envs/.local/`.
2. Set frontend env vars in `frontend/.env`.
3. Verify DB and API keys are present.

## 3) Local Development
1. Start backend (`BackEndApi`): install deps, migrate, runserver.
2. Start frontend (`frontend`): install deps, run Vite dev server.
3. Validate auth + main project routes load.

## 4) Backlog to Execution
1. Create/open backlog items in UI.
2. Send item to developer agent from backlog flow.
3. Frontend work must pass the built-in UI guardrails before completion:
   - `npm run lint:i18n` runs `eslint-plugin-i18next` to block untranslated JSX copy
   - `npm run lint:styles` runs `stylelint` to block raw color values in normal stylesheet files
   - `npm run ui:guardrails` runs those open-source linters plus the repo custom JSX/color audit
   - `npm run test:e2e:ci` runs the guardrails plus Playwright visual checks and screenshot capture
4. Dark-mode verification is part of the default E2E path. The visual guardrail spec writes light/dark screenshots that ProjectMaker can attach to execution results and now runs `@axe-core/playwright` accessibility checks on the same critical shells.
5. Treat large UI surfaces such as sections, panels, cards, tables, modals, and major form containers as theme-safe surfaces by default. Do not leave raw bright backgrounds on those surfaces in dark mode, even if a `dark:*` override exists. Use shared theme tokens/primitives or an explicit exception marker such as `data-theme-exception="inverted-surface"` for intentional inverted treatments.
6. When UI behavior changes, update generated repo docs in the same change:
   - `docs/UI_WORKFLOWS.md` for user flow/interaction changes
   - `docs/UI_DESIGN.md` for component/view design rules and states
7. Review generated code changes and approve/reject.

## 5) Deployment Lifecycle
1. Open deployments page and prepare discovery/config.
2. Run dockerize/deploy flow.
3. Use logs and status indicators for verification/recovery.

## 6) Operations
1. Use stop/restart/wake controls for runtime state.
2. Re-deploy when config or code changes require it.
3. Monitor budget/usage and notifications from dashboard.
