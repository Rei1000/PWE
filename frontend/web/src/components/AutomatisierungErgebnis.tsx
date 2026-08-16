import { AlertTriangle, CheckCircle2 } from "lucide-react";

import type { AutomatisierungAusfuehrenResponse } from "@/adapters/api/schemas/prueflaeufe";

const FEHLERART_TEXT: Record<
  NonNullable<AutomatisierungAusfuehrenResponse["fehlerart"]>,
  string
> = {
  keine_geraeteantwort: "Keine Geräteantwort",
  geraetefehlschlag: "Das Gerät meldet einen Fehler",
  ungueltige_antwort: "Die Geräteantwort konnte nicht ausgewertet werden",
};

type AutomatisierungErgebnisProps = {
  ergebnis: AutomatisierungAusfuehrenResponse;
};

/**
 * Präsentation des ADR-0016-Ergebnisobjekts.
 * HTTP 200 / `fehlgeschlagen` — kein ApiError.
 */
export function AutomatisierungErgebnis({ ergebnis }: AutomatisierungErgebnisProps) {
  const fehlgeschlagen = ergebnis.fehlgeschlagen;

  return (
    <div
      className={
        fehlgeschlagen
          ? "space-y-2 rounded-md border border-amber-600/40 bg-amber-50 p-3 text-sm text-amber-950"
          : "space-y-2 rounded-md border border-green-700/30 bg-green-50 p-3 text-sm text-green-950"
      }
      role="status"
      data-testid="automatisierung-ergebnis"
    >
      <div className="flex items-start gap-2">
        {fehlgeschlagen ? (
          <AlertTriangle className="mt-0.5 size-4 shrink-0" aria-hidden />
        ) : (
          <CheckCircle2 className="mt-0.5 size-4 shrink-0" aria-hidden />
        )}
        <div className="space-y-1">
          <p className="font-medium">
            {fehlgeschlagen
              ? "Automatisierung fehlgeschlagen"
              : "Automatisierung erfolgreich"}
          </p>
          <p>
            {ergebnis.ausgefuehrte_aktionen}{" "}
            {ergebnis.ausgefuehrte_aktionen === 1 ? "Aktion" : "Aktionen"} ausgeführt
            {fehlgeschlagen && ergebnis.abgebrochen_bei_aktion_position != null
              ? ` · Abbruch bei Position ${ergebnis.abgebrochen_bei_aktion_position}`
              : ""}
          </p>
          {fehlgeschlagen && ergebnis.fehlerart && (
            <p>{FEHLERART_TEXT[ergebnis.fehlerart]}</p>
          )}
          {fehlgeschlagen && (
            <p className="text-xs opacity-90">
              Die Ausführung hat begonnen; bereits erzeugte Nachweise bleiben gespeichert.
              Ein erneuter Start erzeugt eine neue Nachweis-Welle.
            </p>
          )}
          {ergebnis.nachweise.length > 0 && (
            <p className="text-xs">
              Neue Nachweise ({ergebnis.nachweise.length}):{" "}
              {ergebnis.nachweise.map((n) => n.art).join(", ")}
            </p>
          )}
          <p className="font-mono text-[11px] opacity-70">
            Ausführung {ergebnis.ausfuehrung_id}
          </p>
        </div>
      </div>
    </div>
  );
}
