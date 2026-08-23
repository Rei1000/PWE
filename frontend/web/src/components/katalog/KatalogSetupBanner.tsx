export function KatalogSetupBanner() {
  return (
    <div
      className="rounded-md border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-sm"
      data-testid="katalog-setup-banner"
    >
      <p className="font-medium">Katalog-Setup / Laborbetrieb</p>
      <p className="mt-1 text-muted-foreground">
        Design-Time-Verwaltung — Anmeldung erforderlich; Rollen- und Qualifikationsregeln folgen in
        Gate 8.1b (ADR-0001 / ADR-0025).
      </p>
    </div>
  );
}
