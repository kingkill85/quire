import { useEffect, useState } from "react";
import { getDownloads, type DownloadItem } from "../lib/api";

const STATUS_COLORS: Record<string, string> = {
  queued: "text-neutral-400",
  downloading: "text-blue-400",
  uploading: "text-yellow-400",
  complete: "text-green-400",
  error: "text-red-400",
  cancelled: "text-neutral-500",
};

export function Downloads() {
  const [items, setItems] = useState<DownloadItem[]>([]);

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const data = await getDownloads();
        setItems(data);
      } catch {
        // ignore polling errors
      }
    }, 2000);

    getDownloads().then(setItems).catch(() => {});
    return () => clearInterval(interval);
  }, []);

  if (items.length === 0) return null;

  return (
    <div className="space-y-2">
      <h2 className="text-neutral-300 font-medium text-sm uppercase tracking-wide">
        Downloads
      </h2>
      {items.map((item) => (
        <div
          key={item.id}
          className="bg-neutral-900 border border-neutral-800 rounded-lg p-3 flex items-center gap-3"
        >
          <div className="flex-1 min-w-0">
            <p className="text-neutral-100 text-sm truncate">{item.title}</p>
            <p className="text-neutral-500 text-xs">{item.author}</p>
          </div>
          <span className={`text-xs font-medium ${STATUS_COLORS[item.status] || ""}`}>
            {item.status}
            {item.status === "downloading" && ` ${item.progress.toFixed(0)}%`}
          </span>
          {item.error && (
            <span className="text-red-400 text-xs truncate max-w-48" title={item.error}>
              {item.error}
            </span>
          )}
        </div>
      ))}
    </div>
  );
}
