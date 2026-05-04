# UI Workflows

This file tracks the implemented user-facing workflows for the Base Ephemeral template.

## Flow: Public Landing To Authentication
- Status: implemented
- Last updated: 2026-05-03
- Entry points: `/`, `/login`, `/signup`
- Steps:
  1. Anonymous users land on `HomePage`.
  2. Top-right actions route to `/login` or `/signup`.
  3. `AuthPage` swaps between `LoginForm` and `SignUpForm` based on pathname.
  4. Successful auth redirects to the guarded destination or `/dashboard`.
- Empty/loading/error states:
  - Initial app bootstrap shows a full-screen spinner while auth state resolves.
  - Auth forms own their validation and API errors.
- Dependencies:
  - `frontend/src/pages/HomePage.tsx`
  - `frontend/src/pages/AuthPage.tsx`
  - `frontend/src/components/LoginForm.tsx`
  - `frontend/src/components/SignUpForm.tsx`
- Notes:
  - The landing page is marketing-style and should stay lightweight.
  - Auth route switching is path-driven, not modal-driven.

## Flow: OTP Verification
- Status: implemented
- Last updated: 2026-05-03
- Entry points: `/verify`, `/verify-login`
- Steps:
  1. User reaches the verification page after signup or login initiation.
  2. `VerifyAccount` or `VerifyLogin` collects the OTP token.
  3. On success, auth state updates and protected navigation can continue.
- Empty/loading/error states:
  - Submit/loading state is handled inside the verification components.
  - Invalid code stays inline on the same page.
- Dependencies:
  - `frontend/src/components/VerifyAccount.tsx`
  - `frontend/src/components/VerifyLogin.tsx`
- Notes:
  - Keep verification as a dedicated step, not an inline drawer or modal.

## Flow: Authenticated Dashboard Entry
- Status: implemented
- Last updated: 2026-05-03
- Entry points: `/dashboard`
- Steps:
  1. `PrivateRoute` blocks unauthenticated access.
  2. Authenticated users see `Dashboard` with welcome copy and feature cards.
  3. Primary CTAs route to `/items` and `/settings`.
- Empty/loading/error states:
  - If auth is still resolving, the app-level loading screen remains visible.
- Dependencies:
  - `frontend/src/App.tsx`
  - `frontend/src/pages/Dashboard.tsx`
  - `frontend/src/components/shared/Navbar.tsx`
  - `frontend/src/components/shared/Breadcrumbs.tsx`
- Notes:
  - Dashboard is a launch surface, not a dense analytics console.

## Flow: Item Management
- Status: implemented
- Last updated: 2026-05-03
- Entry points: `/items`, `/items/:id`
- Steps:
  1. `/items` defaults to list mode and fetches all items.
  2. Header CTA switches the page into create mode.
  3. Clicking an item card routes to `/items/:id` and loads item detail.
  4. Detail mode exposes edit and back actions.
  5. Edit/create both use the same `ItemForm`.
  6. Archive, activate, and delete actions run from the list card actions.
- Empty/loading/error states:
  - Initial list load uses skeleton cards.
  - Empty list uses `EmptyState`.
  - Missing item detail shows a centered fallback card with back action.
  - API errors render inline and auto-clear in list mode.
- Dependencies:
  - `frontend/src/pages/ItemsPage.tsx`
  - `frontend/src/components/items/ItemList.tsx`
  - `frontend/src/components/items/ItemCard.tsx`
  - `frontend/src/components/items/ItemForm.tsx`
- Notes:
  - Create and edit stay in-page rather than opening route-level modals.
  - Detail/edit/list are all part of one route family and should remain consistent.

## Flow: Settings And GitHub Connection
- Status: implemented
- Last updated: 2026-05-03
- Entry points: `/settings`
- Steps:
  1. User opens settings from dashboard or navbar.
  2. Profile summary renders first.
  3. GitHub connection section starts OAuth via backend-generated auth URL.
  4. Callback returns to `/settings` with query params.
  5. Stored state token is verified before token exchange.
  6. User can disconnect GitHub from the same page.
- Empty/loading/error states:
  - Connect/disconnect actions use button-level loading states.
  - OAuth or API failures show toast feedback.
- Dependencies:
  - `frontend/src/pages/SettingsPage.tsx`
  - `frontend/src/services/api.ts`
- Notes:
  - OAuth callback cleanup happens inside the page and should remain idempotent.

## Flow: Theme And Language Switching
- Status: implemented
- Last updated: 2026-05-03
- Entry points: home page header, navbar/top bar controls
- Steps:
  1. User toggles dark/light theme with icon button.
  2. Theme state updates via `ThemeContext` and `ThemeInitializer`.
  3. User changes language via the compact EN/ES menu.
  4. Selection persists in local storage.
- Empty/loading/error states:
  - No separate loading state; changes are immediate client-side.
- Dependencies:
  - `frontend/src/context/ThemeContext.tsx`
  - `frontend/src/components/shared/ThemeInitializer.tsx`
  - `frontend/src/components/layout/TopBar.tsx`
  - `frontend/src/components/shared/Navbar.tsx`
- Notes:
  - Theme and language controls are global utilities and must stay visually lightweight.

## Flow: Command Palette Access
- Status: implemented
- Last updated: 2026-05-03
- Entry points: global app shell
- Steps:
  1. `CommandPalette` mounts once at app level.
  2. User opens it with its registered shortcut/mechanism.
  3. Palette provides fast navigation/command access across the app shell.
- Empty/loading/error states:
  - Palette stays hidden until invoked.
- Dependencies:
  - `frontend/src/components/shared/CommandPalette.tsx`
  - `frontend/src/App.tsx`
- Notes:
  - Keep it globally mounted so route changes do not reset command state unnecessarily.

## Flow: Backend Unavailable Recovery
- Status: implemented
- Last updated: 2026-05-03
- Entry points: app bootstrap, `/start-server`, `/server-down`
- Steps:
  1. App bootstrap checks backend health when API gateway startup is configured.
  2. If the backend is sleeping/unhealthy, routing is forced to `/start-server`.
  3. Explicit server failures can render `ServerDown`.
  4. Recovery actions return to `/` or retry bootstrap.
- Empty/loading/error states:
  - Bootstrap spinner appears before health status is known.
  - `ServerStartPage` and `ServerDown` are dedicated operational states.
- Dependencies:
  - `frontend/src/App.tsx`
  - `frontend/src/pages/ServerStartPage.tsx`
  - `frontend/src/pages/ServerDown.tsx`
  - `frontend/src/services/BackendManager.ts`
- Notes:
  - These states are part of the product workflow and must not be treated as generic 404/500 pages.

## Flow: Unknown Route Handling
- Status: implemented
- Last updated: 2026-05-03
- Entry points: any unmatched route
- Steps:
  1. Router falls through to `NotFoundPage`.
  2. User receives a centered 404 message and a single return-home CTA.
- Empty/loading/error states:
  - No alternate states.
- Dependencies:
  - `frontend/src/pages/NotFoundPage.tsx`
- Notes:
  - Keep the 404 action simple and deterministic.
