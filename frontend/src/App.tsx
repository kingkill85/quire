import { useState } from "react";
import { Downloads } from "./components/Downloads";
import { LoginForm } from "./components/LoginForm";
import { SearchBar } from "./components/SearchBar";
import { SearchResults } from "./components/SearchResults";
import {
  searchBooks,
  startDownload,
  type AuthState,
  type SearchResult,
} from "./lib/api";

function App() {
  const [auth, setAuth] = useState<AuthState | null>(null);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState<Set<string>>(new Set());
  const [error, setError] = useState<string | null>(null);

  const handleLogin = (authState: AuthState) => {
    setAuth(authState);
  };

  const handleLogout = () => {
    setAuth(null);
    setResults([]);
  };

  const handleSearch = async (query: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await searchBooks(query);
      setResults(data.results);
    } catch {
      setError("Search failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (result: SearchResult) => {
    if (!auth) return;
    setDownloading((prev) => new Set(prev).add(result.url));
    try {
      await startDownload(result, auth.accessToken);
    } catch {
      setError("Failed to start download.");
    }
  };

  if (!auth) {
    return <LoginForm onLogin={handleLogin} />;
  }

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100">
      <div className="max-w-3xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold">Quire</h1>
          <div className="flex items-center gap-3">
            <span className="text-neutral-400 text-sm">
              {auth.user.displayName || auth.user.email}
            </span>
            <button
              onClick={handleLogout}
              className="text-neutral-500 hover:text-neutral-300 text-sm transition-colors"
            >
              Sign out
            </button>
          </div>
        </div>

        <div className="space-y-6">
          <SearchBar onSearch={handleSearch} loading={loading} />

          {error && (
            <div className="bg-red-900/30 border border-red-800 rounded-lg p-3 text-red-300 text-sm">
              {error}
            </div>
          )}

          <Downloads />

          {results.length > 0 && (
            <div>
              <p className="text-neutral-400 text-sm mb-3">
                {results.length} result{results.length !== 1 ? "s" : ""}
              </p>
              <SearchResults
                results={results}
                onDownload={handleDownload}
                downloading={downloading}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
