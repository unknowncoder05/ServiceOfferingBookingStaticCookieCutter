# {{ cookiecutter.project_name }} — Frontend

React 19 + TypeScript frontend for **{{ cookiecutter.project_name }}**.

## Tech Stack

- **React 19** with TypeScript
- **Redux Toolkit** — global state management
- **React Router 7** — client-side routing
- **Tailwind CSS** — utility-first styling
- **Axios** — HTTP client with JWT interceptors
- **i18next** — EN/ES translations
- **WebSocket** — real-time updates via Django Channels
- **Tiptap** — rich text editor (available, import as needed)
- **React Flow** — node graph UI (available, import as needed)

## Existing Pages & Routes

All routes are registered in `src/App.tsx`.

| Route | Component | Auth required |
|---|---|---|
| `/login` | `AuthPage` | No |
| `/signup` | `AuthPage` | No |
| `/verify` | `VerifyAccount` | No |
| `/verify-login` | `VerifyLogin` | No |
| `/dashboard` | `Dashboard` | Yes |
| `/items` | `ItemsPage` | Yes |
| `/items/:id` | `ItemsPage` | Yes |
| `/settings` | `SettingsPage` | Yes |
| `/server-down` | `ServerDown` | No |
| `/start-server` | `ServerStartPage` | No |

## Existing Redux Slices

| Slice | File | Purpose |
|---|---|---|
| `auth` | `store/authSlice.ts` | User auth state, login/signup/logout thunks |

## Project Structure

```
src/
├── App.tsx                 # Router setup and auth guard
├── components/             # Reusable UI components
│   ├── LoginForm.tsx
│   ├── SignUpForm.tsx
│   ├── VerifyAccount.tsx
│   └── VerifyLogin.tsx
├── pages/                  # One file per route
│   ├── AuthPage.tsx
│   ├── Dashboard.tsx
│   ├── ItemsPage.tsx
│   ├── SettingsPage.tsx
│   ├── ServerDown.tsx
│   └── ServerStartPage.tsx
├── store/                  # Redux store
│   ├── index.ts            # Store configuration
│   ├── hooks.ts            # useAppDispatch / useAppSelector
│   └── authSlice.ts        # Auth state
├── services/               # API and external services
│   ├── api.ts              # Axios instance + JWT interceptors
│   └── BackendManager.ts   # Backend health polling
├── context/
│   └── ThemeContext.tsx     # Dark mode toggle
├── config/
│   └── environment.ts      # Typed env vars (REACT_APP_*)
├── types/                  # Shared TypeScript types
│   └── auth.ts
└── i18n/                   # Translation files (EN / ES)
```

## Getting Started

```bash
npm install
cp .env.example .env      # set REACT_APP_API_URL
npm start                 # → http://localhost:3000
```

Build for production:

```bash
npm run build
```

## Environment Variables

Declared in `.env` (local) and `projectmaker.yml` (deployed). Accessed via `src/config/environment.ts`.

| Variable | Description |
|---|---|
| `REACT_APP_API_URL` | Backend API base URL (e.g. `http://localhost:8000/api/v1`) |
| `REACT_APP_API_GATEWAY_START_ENDPOINT` | Backend wake-up URL (optional, for sleep-mode backends) |
| `REACT_APP_KEEP_ALIVE_INTERVAL` | Keep-alive polling interval in ms |
| `REACT_APP_STARTUP_TIMEOUT` | Backend startup timeout in ms |

## Authentication Flow

1. User submits email + password on `/login` → receives JWT access + refresh tokens
2. Tokens stored in `localStorage`; Axios interceptor attaches `Authorization: Bearer <token>` to every request
3. On 401, the interceptor refreshes the token and retries automatically
4. `/verify` and `/verify-login` handle account verification codes
5. Redux `auth` slice holds `isAuthenticated`, `user`, `isLoading`

## Adding a New Page

1. Create `src/pages/MyPage.tsx`
2. Add route in `src/App.tsx` (wrap in auth guard if needed)
3. Add Redux slice in `src/store/mySlice.ts` if global state is needed
4. Add navigation link in `Dashboard.tsx` or relevant layout

## Running Tests

```bash
npm test
```
