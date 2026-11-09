/**
 * The API's response shapes, mirrored.
 *
 * Money is `string` everywhere, never `number`. The backend sends NUMERIC
 * as a decimal string precisely so no rounding happens in transit, and
 * parsing it into a JavaScript float here would undo that - 19.99 is not
 * representable in binary floating point, and totals built from floats
 * drift. These strings are formatted for display and sent back verbatim;
 * they are never added up in this application.
 */

export type Money = string;

export type User = {
  id: number;
  email: string;
  is_active: boolean;
  role: "customer" | "admin";
  created_at: string;
};

export type Product = {
  id: number;
  sku: string;
  name: string;
  description: string | null;
  price: Money;
  is_active: boolean;
  stock_quantity: number;
  category_id: number | null;
  created_at: string;
  updated_at: string;
};

export type Page<T> = {
  items: T[];
  total: number;
  limit: number;
  offset: number;
};

export type Category = {
  id: number;
  name: string;
  created_at: string;
  updated_at: string;
};

/** Why a cart line cannot be bought right now, or null if it can. */
export type LineIssue = "unavailable" | "insufficient_stock" | null;

export type CartItem = {
  product_id: number;
  sku: string;
  name: string;
  quantity: number;
  unit_price: Money;
  line_total: Money;
  is_active: boolean;
  available_stock: number;
  issue: LineIssue;
};

export type Cart = {
  items: CartItem[];
  total_items: number;
  total: Money;
  has_issues: boolean;
};

export type Address = {
  id: number;
  label: string | null;
  recipient_name: string;
  phone: string;
  line1: string;
  line2: string | null;
  city: string;
  region: string | null;
  postal_code: string | null;
  country: string;
  is_default: boolean;
  created_at: string;
  updated_at: string;
};

export type AddressInput = {
  label?: string | null;
  recipient_name: string;
  phone: string;
  line1: string;
  line2?: string | null;
  city: string;
  region?: string | null;
  postal_code?: string | null;
  country: string;
  is_default?: boolean;
};

/** The shipping address as an order keeps it: a copy, frozen at checkout. */
export type ShippingAddress = {
  recipient_name: string;
  phone: string;
  line1: string;
  line2: string | null;
  city: string;
  region: string | null;
  postal_code: string | null;
  country: string;
};

export type OrderStatus = "pending" | "paid" | "shipped" | "delivered" | "cancelled";

export type OrderItem = {
  product_id: number;
  sku: string;
  name: string;
  unit_price: Money;
  quantity: number;
  line_total: Money;
};

export type Order = {
  id: number;
  status: OrderStatus;
  total_amount: Money;
  shipping: ShippingAddress;
  items: OrderItem[];
  created_at: string;
  updated_at: string;
};

export type PaymentStatus = "pending" | "succeeded" | "failed" | "refunded";

export type Payment = {
  id: number;
  order_id: number;
  amount: Money;
  currency: string;
  status: PaymentStatus;
  created_at: string;
};

export type PaymentStarted = Payment & { instructions: string };
