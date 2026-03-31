import type { SearchResult } from "../lib/api";

const SOURCE_LABELS: Record<string, string> = {
  openlibrary: "Open Library",
  libgen: "LibGen",
  annas_archive: "Anna's Archive",
  zlibrary: "Z-Library",
  gutenberg: "Gutenberg",
  standard_ebooks: "Standard Ebooks",
};

interface Props {
  results: SearchResult[];
  onDownload: (result: SearchResult) => void;
  downloading: Set<string>;
}

export function SearchResults({ results, onDownload, downloading }: Props) {
  if (results.length === 0) return null;

  return (
    <div className="space-y-3">
      {results.map((result, i) => (
        <div
          key={`${result.source}-${result.url}-${i}`}
          className="bg-neutral-900 border border-neutral-800 rounded-lg p-4 flex items-start gap-4"
        >
          {result.cover_url && (
            <img
              src={result.cover_url}
              alt=""
              className="w-12 h-16 object-cover rounded bg-neutral-800"
            />
          )}
          <div className="flex-1 min-w-0">
            <h3 className="text-neutral-100 font-medium truncate">{result.title}</h3>
            <p className="text-neutral-400 text-sm">{result.author}</p>
            <div className="flex gap-2 mt-1 text-xs text-neutral-500">
              <span className="bg-neutral-800 px-2 py-0.5 rounded">
                {SOURCE_LABELS[result.source] || result.source}
              </span>
              <span className="bg-neutral-800 px-2 py-0.5 rounded uppercase">
                {result.format}
              </span>
              {result.year && (
                <span className="bg-neutral-800 px-2 py-0.5 rounded">{result.year}</span>
              )}
              {result.size_bytes && (
                <span className="bg-neutral-800 px-2 py-0.5 rounded">
                  {(result.size_bytes / 1024 / 1024).toFixed(1)} MB
                </span>
              )}
            </div>
          </div>
          <button
            onClick={() => onDownload(result)}
            disabled={downloading.has(result.url) || result.format === "metadata-only"}
            className="bg-green-600 hover:bg-green-500 disabled:bg-neutral-700 disabled:text-neutral-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors shrink-0"
          >
            {downloading.has(result.url) ? "Sent" : "Download"}
          </button>
        </div>
      ))}
    </div>
  );
}
