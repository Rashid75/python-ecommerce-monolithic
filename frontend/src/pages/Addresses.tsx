import { useState, type FormEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { MapPin, Pencil, Plus, Star, Trash2, X } from "lucide-react";
import { ApiError, request } from "@/lib/api";
import type { Address, AddressInput } from "@/lib/types";
import { Button } from "@/components/ui/Button";
import { Field } from "@/components/ui/Field";
import { Card } from "@/components/ui/Card";
import { Skeleton } from "@/components/ui/Skeleton";
import { EmptyState } from "@/components/EmptyState";
import { ErrorState } from "@/components/ErrorState";
import { useToast } from "@/hooks/toastContext";

const BLANK: AddressInput = {
  label: "",
  recipient_name: "",
  phone: "",
  line1: "",
  line2: "",
  city: "",
  region: "",
  postal_code: "",
  country: "BH",
  is_default: false,
};

/** Turns empty strings into nulls, which is what the API's optional fields expect. */
function clean(input: AddressInput): AddressInput {
  const optional = (value: string | null | undefined) => (value?.trim() ? value.trim() : null);
  return {
    label: optional(input.label),
    recipient_name: input.recipient_name.trim(),
    phone: input.phone.trim(),
    line1: input.line1.trim(),
    line2: optional(input.line2),
    city: input.city.trim(),
    region: optional(input.region),
    postal_code: optional(input.postal_code),
    country: input.country.trim().toUpperCase(),
    is_default: input.is_default,
  };
}

function AddressForm({
  initial,
  busy,
  error,
  onSubmit,
  onCancel,
}: {
  initial: AddressInput;
  busy: boolean;
  error: ApiError | null;
  onSubmit: (value: AddressInput) => void;
  onCancel: () => void;
}) {
  const [form, setForm] = useState<AddressInput>(initial);
  const set = (key: keyof AddressInput) => (event: { target: { value: string } }) =>
    setForm((current) => ({ ...current, [key]: event.target.value }));

  function submit(event: FormEvent) {
    event.preventDefault();
    onSubmit(clean(form));
  }

  return (
    <Card className="p-5">
      <form onSubmit={submit} className="space-y-4" noValidate>
        <div className="grid gap-4 sm:grid-cols-2">
          <Field
            label="Label"
            value={form.label ?? ""}
            onChange={set("label")}
            hint="Yours to choose — Home, Office."
            error={error?.fieldErrors.label}
          />
          <Field
            label="Recipient name"
            required
            value={form.recipient_name}
            onChange={set("recipient_name")}
            hint="Who receives the parcel."
            error={error?.fieldErrors.recipient_name}
          />
          <Field
            label="Phone"
            required
            value={form.phone}
            onChange={set("phone")}
            error={error?.fieldErrors.phone}
          />
          <Field
            label="Country"
            required
            maxLength={2}
            value={form.country}
            onChange={set("country")}
            hint="Two letters, e.g. BH, AE, SA."
            error={error?.fieldErrors.country}
            className="uppercase"
          />
          <Field
            label="Address line 1"
            required
            value={form.line1}
            onChange={set("line1")}
            error={error?.fieldErrors.line1}
            className="sm:col-span-2"
          />
          <Field
            label="Address line 2"
            value={form.line2 ?? ""}
            onChange={set("line2")}
            error={error?.fieldErrors.line2}
            className="sm:col-span-2"
          />
          <Field
            label="City"
            required
            value={form.city}
            onChange={set("city")}
            error={error?.fieldErrors.city}
          />
          <Field
            label="Region"
            value={form.region ?? ""}
            onChange={set("region")}
            hint="Province, emirate or governorate. Optional."
            error={error?.fieldErrors.region}
          />
          <Field
            label="Postal code"
            value={form.postal_code ?? ""}
            onChange={set("postal_code")}
            hint="Optional — not every address uses one."
            error={error?.fieldErrors.postal_code}
          />
        </div>

        <label className="flex items-center gap-2 text-sm text-body">
          <input
            type="checkbox"
            checked={form.is_default ?? false}
            onChange={(event) => setForm((current) => ({ ...current, is_default: event.target.checked }))}
            className="size-4 rounded accent-[oklch(0.54_0.21_275)]"
          />
          Use this as my default address
        </label>

        {error && Object.keys(error.fieldErrors).length === 0 && (
          <p role="alert" className="rounded-[--radius-control] bg-critical-50 px-3 py-2 text-sm font-medium text-critical-700 dark:bg-critical-700/15 dark:text-critical-500">
            {error.message}
          </p>
        )}

        <div className="flex gap-2">
          <Button type="submit" loading={busy}>
            Save address
          </Button>
          <Button type="button" variant="ghost" onClick={onCancel}>
            Cancel
          </Button>
        </div>
      </form>
    </Card>
  );
}

export function Addresses() {
  const toast = useToast();
  const queryClient = useQueryClient();
  const [editing, setEditing] = useState<Address | "new" | null>(null);

  const addresses = useQuery({
    queryKey: ["addresses"],
    queryFn: () => request<Address[]>("/addresses"),
  });

  const done = (message: string) => {
    queryClient.invalidateQueries({ queryKey: ["addresses"] });
    setEditing(null);
    toast.show("success", message);
  };

  const create = useMutation({
    mutationFn: (body: AddressInput) => request<Address>("/addresses", { method: "POST", body }),
    onSuccess: () => done("Address added"),
  });

  const update = useMutation({
    mutationFn: ({ id, body }: { id: number; body: AddressInput }) =>
      request<Address>(`/addresses/${id}`, { method: "PATCH", body }),
    onSuccess: () => done("Address updated"),
  });

  const remove = useMutation({
    mutationFn: (id: number) => request(`/addresses/${id}`, { method: "DELETE" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["addresses"] });
      toast.show("info", "Address deleted");
    },
    onError: (error: unknown) =>
      toast.show("error", error instanceof ApiError ? error.message : "Could not delete that"),
  });

  if (addresses.isError) return <ErrorState error={addresses.error} onRetry={() => addresses.refetch()} />;

  const mutationError =
    (create.error instanceof ApiError ? create.error : null) ??
    (update.error instanceof ApiError ? update.error : null);

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">Addresses</h1>
          <p className="mt-1 text-sm text-muted">Where your orders can be delivered.</p>
        </div>
        {editing === null && (
          <Button icon={<Plus aria-hidden className="size-4" />} onClick={() => setEditing("new")}>
            Add address
          </Button>
        )}
      </div>

      {editing !== null && (
        <AddressForm
          initial={
            editing === "new"
              ? BLANK
              : {
                  label: editing.label ?? "",
                  recipient_name: editing.recipient_name,
                  phone: editing.phone,
                  line1: editing.line1,
                  line2: editing.line2 ?? "",
                  city: editing.city,
                  region: editing.region ?? "",
                  postal_code: editing.postal_code ?? "",
                  country: editing.country,
                  is_default: editing.is_default,
                }
          }
          busy={create.isPending || update.isPending}
          error={mutationError}
          onCancel={() => setEditing(null)}
          onSubmit={(body) =>
            editing === "new" ? create.mutate(body) : update.mutate({ id: editing.id, body })
          }
        />
      )}

      {addresses.isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2">
          {Array.from({ length: 2 }, (_, index) => (
            <Skeleton key={index} className="h-40" />
          ))}
        </div>
      ) : addresses.data!.length === 0 && editing === null ? (
        <EmptyState
          icon={<MapPin aria-hidden className="size-5" />}
          title="No addresses yet"
          description="You need one before you can check out. It takes about thirty seconds."
          action={<Button onClick={() => setEditing("new")}>Add an address</Button>}
        />
      ) : (
        <ul className="grid gap-4 sm:grid-cols-2">
          {addresses.data!.map((address) => (
            <li key={address.id}>
              <Card className="flex h-full flex-col p-5">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <p className="flex items-center gap-2 font-medium text-heading">
                      {address.recipient_name}
                      {address.is_default && (
                        <span className="inline-flex items-center gap-1 rounded-full bg-brand-50 px-2 py-0.5 text-xs font-medium text-brand-700 dark:bg-brand-700/20 dark:text-brand-300">
                          <Star aria-hidden className="size-3" />
                          Default
                        </span>
                      )}
                    </p>
                    {address.label && <p className="mt-0.5 text-xs text-muted">{address.label}</p>}
                  </div>
                  <div className="flex shrink-0 gap-1">
                    <button
                      onClick={() => setEditing(address)}
                      aria-label={`Edit address for ${address.recipient_name}`}
                      className="inline-flex size-8 items-center justify-center rounded-[--radius-control] text-muted transition-colors hover:bg-ink-100 hover:text-heading dark:hover:bg-surface-raised"
                    >
                      <Pencil aria-hidden className="size-4" />
                    </button>
                    <button
                      onClick={() => remove.mutate(address.id)}
                      aria-label={`Delete address for ${address.recipient_name}`}
                      className="inline-flex size-8 items-center justify-center rounded-[--radius-control] text-muted transition-colors hover:bg-critical-50 hover:text-critical-600 dark:hover:bg-critical-700/15"
                    >
                      <Trash2 aria-hidden className="size-4" />
                    </button>
                  </div>
                </div>

                <address className="mt-3 flex-1 text-sm not-italic text-body">
                  <p>{address.line1}</p>
                  {address.line2 && <p>{address.line2}</p>}
                  <p>
                    {address.city}
                    {address.region && `, ${address.region}`}
                    {address.postal_code && ` ${address.postal_code}`}
                  </p>
                  <p>{address.country}</p>
                  <p className="tabular mt-1 text-muted">{address.phone}</p>
                </address>
              </Card>
            </li>
          ))}
        </ul>
      )}

      {editing !== null && (
        <button
          onClick={() => setEditing(null)}
          className="sr-only focus:not-sr-only focus:inline-flex focus:items-center focus:gap-1"
        >
          <X aria-hidden className="size-4" />
          Close the address form
        </button>
      )}
    </div>
  );
}
