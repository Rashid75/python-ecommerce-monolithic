# Postman collection

Two files, both importable as they are:

| File | What it is |
|---|---|
| `python-ecommerce.postman_collection.json` | 34 requests, one per endpoint |
| `python-ecommerce.postman_environment.json` | 10 variables, no values for the secret ones |

Coverage was checked against the application's own OpenAPI schema rather than
written from memory — every endpoint the API serves has a request, and every
request matches an endpoint.

## Setting up

1. Start the API. Either in Docker:

   ```bash
   docker compose up -d api
   ```

   or on the host:

   ```bash
   uv run uvicorn app.main:app --port 8000
   ```

2. Import both files into Postman and select the **Python Ecommerce - local**
   environment.

3. Set `user_password` in the environment. It ships empty on purpose — see
   *Secrets* below.

4. Run **Auth → Register**, then **Auth → Sign in**.

Sign in stores the token in `access_token`, and the collection sends it on
every request through collection-level bearer auth. Public endpoints
(health, catalogue reads, the webhook) override that to no auth rather than
sending a header that means nothing.

## Variables you fill in yourself

`product_id`, `category_id`, `address_id` and `order_id` start empty and
nothing populates them. Create the thing, copy the `id` from the response
into the environment, and the requests that need it will work.

This is deliberate. The collection has no test scripts, so there is nothing
writing to those variables behind your back — which also means nothing to
read when a request fails for reasons you did not expect.

## Admin-only requests

These need `role = admin`:

- create, update and delete products
- create, update and delete categories
- adjust stock
- request a refund

Registration always creates a customer — the role is never taken from the
request body, because a field a client can send is a field an attacker can
set. Promote an account directly in the database:

```bash
PW=$(grep '^APP_DB_PASSWORD=' .env | cut -d= -f2-) && docker compose exec -e PGPASSWORD="$PW" db psql -U ecommerce -d python-ecommerce-monolithic-db -c "UPDATE users SET role = 'admin' WHERE email = 'postman@example.com';"
```

`PGPASSWORD` is not optional. `docker-compose.yml` initialises PostgreSQL
with `--auth-local=scram-sha-256`, so even a connection over the container's
own socket must present a password — `psql -U ecommerce` alone prompts and
then fails under `-T`.

Then sign in again. The role is read from the database on every request, but
you still need a token for that account.

A customer calling an admin endpoint gets **403**, not 404: the endpoint is
not a secret, the permission is.

## The webhook

`Payments → Webhook` returns **400** until `X-Signature` holds an HMAC-SHA256
of the exact request body, hex-encoded, keyed with
`APP_PAYMENT_WEBHOOK_SECRET` from `.env`.

That is the whole point of it — without the signature check the endpoint
would be a public "mark this order paid" button. There is no script here to
compute one, so:

```bash
python -c "import hmac,hashlib,os,sys; body=open(sys.argv[1],'rb').read(); print(hmac.new(os.environ['SECRET'].encode(), body, hashlib.sha256).hexdigest())" body.json
```

with `SECRET` set to the value in `.env`. Put the result in the
`webhook_signature` variable.

**Do not reformat the body.** The signature covers the exact bytes, so
changing one space invalidates it. The body in the request is on a single
line for that reason.

You also need a real payment reference. The API deliberately does not expose
the provider's reference, so read it from the database after starting a
payment:

```bash
PW=$(grep '^APP_DB_PASSWORD=' .env | cut -d= -f2-) && docker compose exec -e PGPASSWORD="$PW" db psql -U ecommerce -d python-ecommerce-monolithic-db -c "SELECT id, order_id, reference, status FROM payments ORDER BY id DESC LIMIT 5;"
```

Event types that do something: `payment.succeeded`, `payment.failed`,
`refund.succeeded`. Anything else is recorded and ignored.

Responses, all 200 except the last two:

| `status` | Meaning |
|---|---|
| `applied` | the event changed something |
| `duplicate` | this event id was seen before |
| `ignored` | the move is not legal from the payment's current state, or the type is not acted on |
| 400 | bad signature |
| 404 | no payment with that reference |

A `payment.failed` arriving after `payment.succeeded` is `ignored`, not an
error. Providers retry and reorder; an old delivery must not un-pay an order.

## A suggested run order

1. **Auth** → Register → Sign in
2. **Catalogue** → Create product *(admin)* — copy `id` into `product_id`
3. **Cart** → Add item → Get my cart — note `total`
4. **Addresses** → Add address — copy `id` into `address_id`
5. **Orders** → Checkout — set `expected_total` to the cart's `total`
6. **Payments** → Start a payment — then read the reference from the database
7. **Payments** → Webhook with `payment.succeeded`
8. **Orders** → Get one order — it is now `paid`

Step 5 is where most first attempts fail: `expected_total` must equal the
total the server computes from live prices, or checkout returns **409** with
the new total. That is the control that stops a customer being charged an
amount they were never shown, and it fires exactly as often as it should.

## Secrets

`user_password`, `access_token` and `webhook_signature` are typed as secret
and committed empty. Nothing credential-shaped is in this repository, and an
environment you have to fill in yourself is the intended friction.

If you export your own environment after filling it in, **do not commit it**.
`.gitignore` does not currently cover exported Postman environments, so that
is on you rather than on the tooling.

## What this collection does not do

- **No test scripts.** There are no assertions anywhere.
- **One script, on Sign in**, which asserts nothing — it copies the token
  into the environment so the other 33 requests work without pasting it by
  hand. Postman only offers the `test` event for post-response hooks, which
  is why it lives there despite not being a test.
- **No chaining.** Nothing extracts an id from one response into the next
  request.
- **Not synced to a Postman workspace.** These are files in the repository,
  reviewable in a diff. Publishing them to a workspace or a public docs page
  is a separate decision about audience.
