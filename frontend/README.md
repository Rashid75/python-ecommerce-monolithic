# Northline — storefront

A React storefront for the Python Ecommerce API in this repository.

| | |
|---|---|
| React 19 + TypeScript | strict mode, no `any` |
| Vite 7 | dev server with an API proxy, production build |
| Tailwind CSS 4 | CSS-first config, no `tailwind.config.js` |
| TanStack Query 5 | server state, caching, refetching |
| React Router 7 | routing and route guards |

## Running it

The API has to be up first — the storefront is a client, not a mock.

```bash
docker compose up -d api        # from the repository root
cd frontend
npm install
npm run dev
```

Then open http://localhost:5173.

Vite proxies `/api` and `/health` to `http://127.0.0.1:8000`, so the browser
sees one origin and no CORS configuration is needed for local work. That
also imitates the production arrangement — Nginx in front of both — rather
than working around it.

```bash
npm run build     # tsc -b && vite build
npm run lint      # eslint
```

## What it covers

Every customer-facing endpoint the API exposes:

| Area | |
|---|---|
| Catalogue | list with search, category filter, in-stock filter, pagination; product detail |
| Account | register, sign in, sign out, protected routes |
| Cart | add, change quantity, remove, empty, per-line availability warnings |
| Addresses | list, create, edit, delete, default handling |
| Checkout | address selection, server-computed total, **price-change confirmation** |
| Orders | list, detail with the frozen prices, cancellation |
| Payments | start a payment, see attempts and their status |

Admin endpoints — creating products and categories, adjusting stock,
requesting refunds — are **not** built. They need a different interface for a
different person, and bolting an admin area onto a storefront is how both
end up mediocre.

## Decisions worth knowing

**Money is a string, never a number.** The API sends `NUMERIC` as a decimal
string so nothing rounds in transit. Parsing it into a JavaScript float would
undo that — `19.99` is not representable in binary floating point. These
strings are formatted for display and sent back verbatim; this application
never does arithmetic on them. The server owns every total.

**The price-change flow is the point of the checkout page.** The cart stores
no price, so its total is today's. Checkout sends that total back as
`expected_total`; if it has moved the API answers **409** and the page shows
the new amount with a button naming it, charging nothing. The refusal is the
control working, not a failure, and the page is written to read that way.

**One idempotency key per checkout attempt**, generated once with
`useMemo` and reused on retry, so a timeout and a second press return the
first order instead of placing a second.

**`dark:` is bound to a class, not the OS.** Tailwind v4 defaults the
variant to `prefers-color-scheme`; this app lets the customer override the
OS, so `index.css` declares
`@custom-variant dark (&:where(.dark, .dark *))`. Without it every `dark:`
utility silently follows the OS instead.

**Design tokens, not ad-hoc colours.** Every colour, radius and shadow is
defined once in `src/index.css` under `@theme`, with semantic surface tokens
(`bg-surface`, `text-body`, `border-line`) layered on top. Dark mode is a
change to one block rather than a `dark:` variant on every element.

**Accessibility is built in, not retrofitted.** A skip link, labels tied to
every input, `aria-describedby` on errors, `aria-live` on toasts, a visible
focus ring for keyboard users only, and `aria-label` on every icon-only
control.

**Errors show the API's own message.** The backend was built so that no
internal exception text ever leaves it, which means repeating its message
tells the customer something true instead of a generic apology.

## Structure

```
src/
├── components/
│   ├── ui/            Button, Field, Badge, Card, Skeleton
│   ├── Layout.tsx     header, nav, cart badge, theme toggle
│   ├── ProductThumb   deterministic tile standing in for a photo
│   ├── EmptyState     what a page shows when there is nothing
│   └── ErrorState     what a page shows when a request failed
├── hooks/
│   ├── authContext    the context and useAuth
│   ├── useAuth.tsx    AuthProvider
│   ├── toastContext   the context and useToast
│   └── useToast.tsx   ToastProvider
├── lib/
│   ├── api.ts         the only code that calls the API
│   ├── types.ts       the API's response shapes
│   ├── format.ts      money and dates
│   └── cn.ts          class merging
└── pages/             one file per route
```

The hooks are split from their providers deliberately: a module exporting
both a component and a plain function cannot be hot-reloaded reliably,
because React Refresh cannot tell which exports are components.

## Known gaps

- **No tests.** Consistent with the rest of this repository, where test
  infrastructure was deferred.
- **No admin interface**, as above.
- **The token is in `localStorage`.** That is the right place for a bearer
  credential this API expects in a header — it is not sent automatically, so
  there is no CSRF surface — but a cross-site scripting bug could read it.
  The application renders no user-supplied HTML anywhere, which is what
  keeps that true.
- **Order history has no pagination**, because the API has none yet.
- **The product tiles are placeholders.** The API stores no images.
