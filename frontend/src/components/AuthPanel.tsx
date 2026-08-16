import { useState } from "react";

import { supabase } from "../lib/supabase";

type AuthPanelProps = {
  onSignedIn: () => void;
};

function formatAuthError(message: string): string {
  const lower = message.toLowerCase();
  if (
    lower.includes("password should contain") ||
    lower.includes("at least one character")
  ) {
    return "Use a stronger password: include uppercase and lowercase letters, a number, and a symbol.";
  }
  if (lower.includes("invalid login credentials")) {
    return "Email or password is incorrect.";
  }
  if (lower.includes("user already registered")) {
    return "An account with this email already exists. Sign in instead.";
  }
  return message;
}

function isUnconfirmedError(message: string): boolean {
  const lower = message.toLowerCase();
  return (
    lower.includes("email not confirmed") ||
    lower.includes("email_not_confirmed") ||
    lower.includes("confirm your email")
  );
}

export function AuthPanel({ onSignedIn }: AuthPanelProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [needsConfirmation, setNeedsConfirmation] = useState(false);
  const [busy, setBusy] = useState(false);

  async function submit() {
    if (!supabase) {
      return;
    }
    setBusy(true);
    setError("");
    if (mode === "signup") {
      setSuccess("");
    }
    const action =
      mode === "signin"
        ? supabase.auth.signInWithPassword({ email, password })
        : supabase.auth.signUp({
            email,
            password,
            options: {
              emailRedirectTo: `${window.location.origin}/`,
            },
          });
    const { data, error: authError } = await action;
    setBusy(false);
    if (authError) {
      if (mode === "signin" && isUnconfirmedError(authError.message)) {
        setNeedsConfirmation(true);
        setError("");
        return;
      }
      if (mode === "signin" && needsConfirmation) {
        setError("");
        return;
      }
      setError(formatAuthError(authError.message));
      return;
    }
    if (mode === "signup" && !data.session) {
      setNeedsConfirmation(true);
      setSuccess("Account created.");
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
        <h1 className="text-2xl font-semibold">
          {mode === "signin" ? "Sign in" : "Create account"}
        </h1>
        <p className="mt-2 text-sm text-slate-400">
          Sign in to upload documents and ask questions.
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
            minLength={8}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100"
          />
        </label>
        {mode === "signup" && (
          <p className="mt-2 text-xs leading-5 text-slate-400">
            Include uppercase, lowercase, a number, and a symbol.
          </p>
        )}
        {success && <p className="mt-3 text-sm text-emerald-400">{success}</p>}
        {mode === "signin" && needsConfirmation && (
          <p className="mt-3 text-sm text-cyan-300">
            Confirm your email, then sign in. Check your inbox for the link.
          </p>
        )}
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
          onClick={() => {
            setMode(mode === "signin" ? "signup" : "signin");
            setError("");
            if (mode === "signin") {
              setSuccess("");
            }
          }}
        >
          {mode === "signin"
            ? "Need an account? Sign up"
            : "Have an account? Sign in"}
        </button>
      </form>
    </main>
  );
}
