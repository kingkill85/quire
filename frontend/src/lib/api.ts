export interface SearchResult {
  source: string;
  title: string;
  author: string;
  url: string;
  format: string;
  size_bytes: number | null;
  language: string | null;
  year: number | null;
  isbn: string | null;
  cover_url: string | null;
  extra: Record<string, unknown>;
  size_display: string;
}

export interface DownloadItem {
  id: string;
  source: string;
  url: string;
  title: string;
  author: string;
  status: "queued" | "downloading" | "uploading" | "complete" | "error" | "cancelled";
  progress: number;
  error: string | null;
  verso_book_id: string | null;
  created_at: string;
}

export interface AuthState {
  accessToken: string;
  refreshToken: string;
  user: { email: string; displayName: string; role: string };
}

export async function loginToVerso(
  email: string,
  password: string,
): Promise<AuthState> {
  const resp = await fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!resp.ok) throw new Error("Login failed");
  return resp.json();
}

export async function searchBooks(
  query: string,
  sources?: string,
): Promise<{ results: SearchResult[]; errors: unknown[] }> {
  const params = new URLSearchParams({ q: query });
  if (sources) params.set("sources", sources);
  const resp = await fetch(`/api/search?${params}`);
  if (!resp.ok) throw new Error("Search failed");
  return resp.json();
}

export async function startDownload(
  result: SearchResult,
  token: string,
): Promise<DownloadItem> {
  const resp = await fetch("/api/download", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      source: result.source,
      url: result.url,
      title: result.title,
      author: result.author,
    }),
  });
  if (!resp.ok) throw new Error("Download failed");
  const data = await resp.json();
  return data.item;
}

export async function getDownloads(): Promise<DownloadItem[]> {
  const resp = await fetch("/api/downloads");
  if (!resp.ok) throw new Error("Failed to fetch downloads");
  const data = await resp.json();
  return data.items;
}
