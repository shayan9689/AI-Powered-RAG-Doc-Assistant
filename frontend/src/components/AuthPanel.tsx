import { useState } from "react";

import { supabase } from "../lib/supabase";

type AuthPanelProps = {
  onSignedIn: () => void;
};

export function AuthPanel({ onSignedIn }: AuthPanelProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit() {
    if (!supabase) {
      return;
    }
    setBusy(true);
    setError("");
    const action =
      mode === "signin"
        ? supabase.auth.signInWithPassword({ email, password })
        : supabase.auth.signUp({ email, password });
    const { data, error: authError } = await action;
    setBusy(false);
    if (authError) {
      setError(authError.message);
      return;
    }
    if (mode === "signup" && !data.session) {
      setError(
        "Account created. Disable Confirm email in Supabase Auth, then sign in.",
      );
      setMode("signin");
      return;
    }
    onSignedIn();
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-950 px-6 text-slate-100">
      <form
        className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-8"
        onSubmit={(event) => {
          event.preventDefault();
          void submit();
        }}
      >
        <h1 className="text-2xl font-semibold">Sign in</h1>
        <p className="mt-2 text-sm text-slate-400">
          Use the same email you will confirm in Supabase Auth.
        </p>
        <label className="mt-6 block text-sm text-slate-300">
          Email
          <input
            type="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100"
          />
        </label>
        <label className="mt-4 block text-sm text-slate-300">
          Password
          <input
            type="password"
            required
            minLength={6}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100"
          />
        </label>
        {error && <p className="mt-3 text-sm text-rose-400">{error}</p>}
        <button
          type="submit"
          disabled={busy}
          className="mt-6 w-full rounded-lg bg-cyan-600 py-2 font-medium text-white disabled:opacity-50"
        >
          {mode === "signin" ? "Sign in" : "Create account"}
        </button>
        <button
          type="button"
          className="mt-3 w-full text-sm text-cyan-400"
          onClick={() => setMode(mode === "signin" ? "signup" : "signin")}
        >
          {mode === "signin"
            ? "Need an account? Sign up"
            : "Have an account? Sign in"}
        </button>
      </form>
    </main>
  );
}
