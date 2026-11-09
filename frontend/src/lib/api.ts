/**
 * The only place in this application that talks to the API.
 *
 * Everything above this file deals in typed objects and thrown errors.
 * Nothing above it knows about status codes, headers, or the shape of an
 * error body - which is what makes the backend's error contract changeable
 * in one place rather than in every component that shows a message.
 */

const BASE = "/api/v1";

/** Where the token lives.
 *
 * localStorage, not a cookie, because this API authenticates with a bearer
 * header and has no CSRF protection - it does not need any, precisely
 * because the credential is not sent automatically by the browser. The
 * trade is that a cross-site scripting bug could read it, which is why the
 * application renders no user-supplied HTML anywhere.
 */
const TOKEN_KEY = "ecommerce.access_token";

export function getToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    // Private browsing and blocked site data both throw here. Being signed
    // out is a correct outcome; crashing is not.
    return null;
  }
}

export function setToken(token: string | null): void {
  try {
    if (token === null) localStorage.removeItem(TOKEN_KEY);
    else localStorage.setItem(TOKEN_KEY, token);
  } catch {
    /* see getToken */
  }
}

/**
 * An error the API returned, carrying the parts a component needs to react.
 *
 * `code` is the stable machine-readable name the backend sends beside the
 * message. Branching on it rather than on the wording means a reworded
 * message does not change behaviour.
 */
export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly fieldErrors: Record<string, string>;

  constructor(status: number, code: string, message: string, fieldErrors: Record<string, string> = {}) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.fieldErrors = fieldErrors;
  }

  /** The caller is not signed in, or their token expired. */
  get isAuth(): boolean {
    return this.status === 401;
  }

  /** The request was fine; the state of the data conflicts with it. */
  get isConflict(): boolean {
    return this.status === 409;
  }
}

type RequestOptions = {
  method?: string;
  body?: unknown;
  /** Sent on checkout so a retry cannot order twice. */
  idempotencyKey?: string;
  signal?: AbortSignal;
};

/** FastAPI's 422 body, which lists per-field problems. */
type ValidationDetail = { loc: (string | number)[]; msg: string }[];

function readFieldErrors(detail: unknown): Record<string, string> {
  if (!Array.isArray(detail)) return {};
  const out: Record<string, string> = {};
  for (const item of detail as ValidationDetail) {
    // loc is ["body", "field"] - the last string is the field name.
    const field = [...item.loc].reverse().find((part) => typeof part === "string" && part !== "body");
    if (typeof field === "string" && !out[field]) out[field] = item.msg;
  }
  return out;
}

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, idempotencyKey, signal } = options;

  const headers: Record<string, string> = {};
  if (body !== undefined) headers["Content-Type"] = "application/json";
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  if (idempotencyKey) headers["Idempotency-Key"] = idempotencyKey;

  let response: Response;
  try {
    response = await fetch(`${BASE}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
      signal,
    });
  } catch (cause) {
    if (cause instanceof DOMException && cause.name === "AbortError") throw cause;
    // The server was unreachable. Distinct from an error it sent, and the
    // only case where the advice is "check your connection".
    throw new ApiError(0, "network_error", "Cannot reach the server. Check your connection.");
  }

  if (response.status === 204) return undefined as T;

  const text = await response.text();
  const payload = text ? (JSON.parse(text) as unknown) : null;

  if (!response.ok) {
    const bodyObject = (payload ?? {}) as { detail?: unknown; code?: string };
    const code = bodyObject.code ?? "error";
    const fieldErrors = readFieldErrors(bodyObject.detail);
    const message =
      typeof bodyObject.detail === "string"
        ? bodyObject.detail
        : Object.values(fieldErrors)[0] ?? "Something went wrong.";
    throw new ApiError(response.status, code, message, fieldErrors);
  }

  return payload as T;
}

/** Reads a response header the API sets, for callers that care. */
export async function requestWithHeaders<T>(
  path: string,
  options: RequestOptions = {},
): Promise<{ data: T; headers: Headers }> {
  const { method = "GET", body, idempotencyKey } = options;
  const headers: Record<string, string> = {};
  if (body !== undefined) headers["Content-Type"] = "application/json";
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  if (idempotencyKey) headers["Idempotency-Key"] = idempotencyKey;

  const response = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  const text = await response.text();
  const payload = text ? (JSON.parse(text) as unknown) : null;

  if (!response.ok) {
    const bodyObject = (payload ?? {}) as { detail?: unknown; code?: string };
    const fieldErrors = readFieldErrors(bodyObject.detail);
    const message =
      typeof bodyObject.detail === "string"
        ? bodyObject.detail
        : Object.values(fieldErrors)[0] ?? "Something went wrong.";
    throw new ApiError(response.status, bodyObject.code ?? "error", message, fieldErrors);
  }

  return { data: payload as T, headers: response.headers };
}
