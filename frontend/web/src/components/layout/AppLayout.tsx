import { useMutation } from "@tanstack/react-query";
import { Link, Outlet, useNavigate } from "react-router-dom";

import { logout } from "@/adapters/api/auth";
import { getApiBaseUrl } from "@/adapters/api/client";
import { Button } from "@/components/ui/button";
import { useCurrentUser, useInvalidateSession } from "@/hooks/useAuth";
import { darfIdentityLesen } from "@/lib/identityRoles";

export function AppLayout() {
  const { data: user } = useCurrentUser();
  const invalidate = useInvalidateSession();
  const navigate = useNavigate();
  const showVerwaltung = darfIdentityLesen(user);

  const logoutMutation = useMutation({
    mutationFn: logout,
    onSettled: () => {
      invalidate();
      navigate("/login", { replace: true });
    },
  });

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="mx-auto flex max-w-3xl items-center justify-between px-6 py-4">
          <div>
            <p className="text-lg font-semibold">PWE</p>
            <p className="text-xs text-muted-foreground">Prüf-Workflow-Engine — PC</p>
          </div>
          <nav className="flex items-center gap-4 text-sm">
            <Link to="/" className="text-muted-foreground hover:text-foreground">
              Start
            </Link>
            <Link to="/katalog" className="text-muted-foreground hover:text-foreground">
              Katalog (Setup)
            </Link>
            {showVerwaltung && (
              <Link to="/verwaltung" className="text-muted-foreground hover:text-foreground">
                Verwaltung
              </Link>
            )}
            <Link to="/health" className="text-muted-foreground hover:text-foreground">
              Health
            </Link>
            {user && (
              <>
                <span className="text-muted-foreground">{user.anzeigename}</span>
                {!user.passwortwechsel_erforderlich && (
                  <Link
                    to="/passwort-aendern"
                    className="text-muted-foreground hover:text-foreground"
                  >
                    Passwort ändern
                  </Link>
                )}
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => logoutMutation.mutate()}
                  disabled={logoutMutation.isPending}
                >
                  Abmelden
                </Button>
              </>
            )}
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
