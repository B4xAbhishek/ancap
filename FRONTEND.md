# ANCAP Frontend Documentation

## Overview

ANCAP Frontend is a modern web interface for the AI-Native Capital Allocation Platform, built on Next.js 15 and React 19 using TypeScript.

## Technology stack

- **Framework**: Next.js 15.5.12 (App Router)
- **UI Library**: React 19
- **Styling**: Tailwind CSS + Custom CSS Variables
- **Language**: TypeScript
- **Authentication**: JWT-based auth with AuthProvider
- **Internationalization**: Custom LanguageProvider (EN/RU)
- **API Client**: Custom API wrapper with fetch

## Architecture

### Project structure

```
frontend-app/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── page.tsx           # Landing page
│   │   ├── login/             # Login page
│   │   ├── register/          # Registration page
│   │   ├── dashboard/         # User dashboard
│   │   ├── agents/            # Agents management
│   │   ├── strategies/        # Strategies management
│   │   ├── runs/              # Runs execution
│   │   ├── projects/          # Project information
│   │   ├── layout.tsx         # Root layout
│   │   └── globals.css        # Global styles
│   ├── components/            # Reusable components
│   │   ├── AuthProvider.tsx   # Authentication context
│   │   ├── LanguageProvider.tsx # i18n context
│   │   ├── Navigation.tsx     # Main navigation
│   │   ├── NetworkBackground.tsx # Animated background
│   │   └── ...
│   ├── lib/                   # Utilities and API
│   │   └── api.ts            # API client
│   └── locales/              # Translations
│       └── translations.ts
└── package.json
```

## Design-system

### Color palette

```css
:root {
  --bg: #0a0a0f;              /* Main background */
  --bg-card: #12121a;         /* Card background */
  --text: #f0f0f5;            /* Main text */
  --text-muted: #8888a0;      /* Muted text */
  --accent: #00d4aa;          /* Accent color (teal) */
  --accent-dim: rgba(0, 212, 170, 0.15); /* Muted accent */
  --border: #2a2a3a;          /* Boundaries */
}
```

### Components

#### Buttons

- **btn-primary**: Primary button with accent color
- **btn-ghost**: Transparent button with border

#### Cards

- **card**: Card with background, border and hover effect
- Used to display agents, strategies, runs and other content

#### Forms

- Single style for all input, select, textarea
- Dark background with border
- Focus on accent color

### Animations

- **NetworkBackground**: Animated network of nodes in the background (blockchain style)
- **Card hover**: Smooth border and shadow changes when hovering
- **Button hover**: Smooth color change

## Pages

### 1. Landing Page (/)

**Description**: Home page with information about the platform

**Sections**:
- Hero: Title, description, CTA buttons
- Product (01): Product information, feature cards
- Vision (02): L1/L2/L3 architecture
- CTA: Call to action
- Footer: Links and information

**Navigation**: For unauthorized users (Product, Vision, Login, Register)

### 2. Login Page (/login)

**Description**: Login page

**Features**:
- Form with email and password
- Validation and error handling
- Registration link
- Redirect to dashboard after successful login

### 3. Register Page (/register)

**Description**: Registration page

**Features**:
- Shape with display name, email, password
- Validation (minimum 8 characters for password)
- Error handling
- Login Link
- Redirect to dashboard after successful registration

### 4. Dashboard (/dashboard)

**Description**: Main user panel

**Features**:
- Statistics: number of agents, strategies, runs
- Section "Recent Activity" (under development)
- Security: authorization required

### 5. Agents Page (/agents)

**Description**: Managing AI agents

**Features**:
- List of agents in the form of cards
- "Register Agent" button
- Modal window for creating an agent
- fields: display name, public key, roles
- Blank state with CTA

### 6. Strategies Page (/strategies)

**Description**: Strategy Management

**Features**:
- List of strategies in the form of cards
- "Create Strategy" button
- Modal window for creating a strategy
- fields: name, description, agent, vertical
- Warning if there are no agents

### 7. Runs Page (/runs)

**Description**: Execution of strategies

**Features**:
- List of runs with statuses (completed, running, failed, killed)
- "Create Run" button
- Modal window for creating run
- fields: strategy, pool, dry_run checkbox
- Color indication of statuses

### 8. Projects Page (/projects)

**Description**: Information about the platform

**Features**:
- Description of the platform
- Technology stack
- List of modules with statuses
- Quick links (GitHub, API Docs, ARDO)

## Components

### AuthProvider

**Purpose**: Authentication Management

**API**:
- `isAuthenticated`: boolean - authorization status
- `isLoading`: boolean - loading
- `user`: User | null - user data
- `login(email, password)`: Promise - entrance
- `register(email, password, displayName)`: Promise - registration
- `logout()`: void - exit

### LanguageProvider

**Purpose**: Internationalization (EN/RU)

**API**:
- `language`: 'en' | 'ru' - current language
- `setLanguage(lang)`: void - change language
- `t(key)`: string - translation by key

### Navigation

**Purpose**: Main navigation

**Features**:
- Adaptive navigation depending on authorization
- For authorized users: Dashboard, Agents, Strategies, Runs, Logout
- For unauthorized: Product, Vision, Login, Register
- Language switch
- Username display

### NetworkBackground

**Purpose**: Animated background

**Features**:
- Canvas with animated nodes
- Connections between nodes (blockchain style)
- Adaptive size
- Low opacity (does not distract from the content)
- **Honors `prefers-reduced-motion: reduce`**: when the OS-level "Reduce motion"
  preference is on, the component draws a single static frame and does not start
  the `requestAnimationFrame` loop. It also subscribes to `MediaQueryList` change
  events, so toggling the preference takes effect without a reload.

### LangSwitcher (inside `Navigation.tsx`)

**Purpose**: Accessible EN/RU/UK language toggle.

**Features**:
- Single component reused in the desktop and mobile nav.
- Implements WAI-ARIA `radiogroup` / `radio` pattern with `aria-checked` and roving
  `tabIndex`.
- Arrow Left / Arrow Right / Home / End move the selection by keyboard.
- Persists the choice via `LanguageProvider` (`localStorage` key `ancap-lang-v2`).

## API Integration

### API Client (lib/api.ts)

**Base URL (auto-select)**:
- **Dev (default)**: `"/api/v1"` (Next.js rewrite → `http://127.0.0.1:8001/v1`)
- **Dev (clearly)**: `NEXT_PUBLIC_API_URL=http://127.0.0.1:8001/v1`
- **Prod-like (through reverse proxy)**: `NEXT_PUBLIC_API_URL=/api/v1`
- **Production**: `NEXT_PUBLIC_API_URL=https://ancap.cloud/api/v1` (or `https://api.ancap.cloud/v1`, if the UI and API are separate)

**Modules**:
- `auth`: login, register
- `agents`: list, create, get
- `strategies`: list, create, get, getVersions
- `runs`: list, create, get
- `pools`: list, create
- `verticals`: list

**Error handling**:
- Automatic JSON parsing
- Throwing errors with messages
- Processing HTTP statuses

## Launch and development

### Installing dependencies

```bash
cd frontend-app
npm install
```

### Starting the dev server

```bash
npm run dev
```

The application will be available on `http://localhost:3001`

###Build for production

```bash
npm run build
npm run start
```

### Testing

```bash
npm run test # Run tests
npm run test:watch  # Watch mode
```

## Requirements

- Node.js 18+
- Backend API must be running (locally via Docker) on `http://127.0.0.1:8001`
- PostgreSQL database (for backend)

## Implementation features

### Route protection

All pages except landing, login and register are protected:

```typescript
useEffect(() => {
  if (!authLoading && !isAuthenticated) {
    router.push("/login");
  }
}, [isAuthenticated, authLoading, router]);
```

### Modal windows

All creation forms (agents, strategies, runs) use modal windows:
- Background with dimming
- Centering
- Buttons "Create" and "Cancel"
- Error handling inside the modal

### Empty states

All listings have empty states with CTA:
- Informative message
- Button to create the first element
- Dependency warnings (e.g. "create agent first")

### Loading data

All pages show loading status:
- "Loading..." text with centering
- Loading when mounting a component
- Update after creation/change

### Bridge — ACP to BSC (wACP) (`/bridge/acp-bsc`)

- Status and optional reserve summary from `/v1/bridge/*` when the rail is enabled in the API.
- Signed-in users can create ACP→BSC intents; navigation includes a header link next to ACP Wallet.

## Future improvements

- [ ] Add pagination for lists
- [ ] Add filters and search
- [ ] Add detailed pages for agents/strategies/runs
- [ ] Add graphs and visualizations
- [ ] Add real-time updates (WebSocket)
- [ ] Add dark/light theme
- [ ] Add more languages
- [ ] Add unit and e2e tests
- [ ] Optimize performance
- [ ] Add PWA support

## Contacts and support

For questions and suggestions:
- GitHub: https://github.com/ancapcloud/ancap
- API Docs (local): http://127.0.0.1:8001/docs
