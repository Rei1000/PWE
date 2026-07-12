import { Link, Outlet } from "react-router-dom";

import { getApiBaseUrl } from "@/adapters/api/client";

export function AppLayout() {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="mx-auto flex max-w-3xl items-center justify-between px-6 py-4">
          <div>
            <p className="text-lg font-semibold">PWE</p>
            <p className="text-xs text-muted-foreground">Prüf-Workflow-Engine — PC</p>
          </div>
          <nav className="flex gap-4 text-sm">
            <Link to="/" className="text-muted-foreground hover:text-foreground">
              Start
            </Link>
            <Link to="/health" className="text-muted-foreground hover:text-foreground">
              Health
            </Link>
          </nav>
        </div>
        <p className="mx-auto max-w-3xl px-6 pb-2 text-xs font-mono text-muted-foreground">
          API: {getApiBaseUrl()}
        </p>
      </header>
      <main className="mx-auto max-w-3xl px-6 py-8">
        <Outlet />
      </main>
    </div>
  );
}
