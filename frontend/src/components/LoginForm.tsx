import { useState } from "react";
import { loginToVerso, type AuthState } from "../lib/api";

interface Props {
  onLogin: (auth: AuthState) => void;
}

export function LoginForm({ onLogin }: Props) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const auth = await loginToVerso(email, password);
      onLogin(auth);
    } catch {
      setError("Login failed. Check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 flex items-center justify-center">
      <div className="w-full max-w-sm">
        <h1 className="text-3xl font-bold mb-2 text-center">Quire</h1>
        <p className="text-neutral-400 text-sm text-center mb-8">
          Sign in with your Verso account
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email"
            required
            className="w-full bg-neutral-900 border border-neutral-700 rounded-lg px-4 py-3 text-neutral-100 placeholder-neutral-500 focus:outline-none focus:border-blue-500 transition-colors"
          />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            required
            className="w-full bg-neutral-900 border border-neutral-700 rounded-lg px-4 py-3 text-neutral-100 placeholder-neutral-500 focus:outline-none focus:border-blue-500 transition-colors"
          />

          {error && (
            <div className="bg-red-900/30 border border-red-800 rounded-lg p-3 text-red-300 text-sm">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-500 disabled:bg-neutral-700 text-white py-3 rounded-lg font-medium transition-colors"
          >
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>
      </div>
    </div>
  );
}
