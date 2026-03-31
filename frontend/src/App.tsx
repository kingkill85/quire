import { useEffect, useState } from "react";

function App() {
  const [health, setHealth] = useState<string>("checking...");

  useEffect(() => {
    fetch("/api/health")
      .then((r) => r.json())
      .then((d) => setHealth(d.status))
      .catch(() => setHealth("error"));
  }, []);

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">Quire</h1>
        <p className="text-neutral-400">
          Backend: <span className="text-green-400">{health}</span>
        </p>
      </div>
    </div>
  );
}

export default App;
