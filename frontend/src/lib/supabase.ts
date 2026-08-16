import { createClient } from "@supabase/supabase-js";

function projectUrl(raw: string): string {
  let url = raw.trim().replace(/\/+$/, "");
  for (const suffix of ["/rest/v1", "/auth/v1", "/storage/v1"]) {
    if (url.endsWith(suffix)) {
      url = url.slice(0, -suffix.length).replace(/\/+$/, "");
    }
  }
  return url;
}

const url = projectUrl(import.meta.env.VITE_SUPABASE_URL ?? "");
const anonKey = import.meta.env.VITE_SUPABASE_ANON_KEY ?? "";

export const isSupabaseConfigured = Boolean(url && anonKey);

export const supabase = isSupabaseConfigured
  ? createClient(url, anonKey)
  : null;
