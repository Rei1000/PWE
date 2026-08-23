import type { NachweisDetail } from "@/adapters/api/schemas/prueflaeufe";
import { FotoNachweisAnzeige } from "@/components/FotoNachweisAnzeige";

type SchrittNachweiseProps = {
  prueflaufId: string;
  nachweise: NachweisDetail[];
};

function formatNachweisKompakt(nachweis: NachweisDetail): string {
  if (nachweis.art === "messwert") {
    const parts = Object.entries(nachweis.payload).map(([key, value]) => `${key}=${String(value)}`);
    if (parts.length > 0) {
      return `Messwert: ${parts.join(", ")}`;
    }
  }
  if (nachweis.art === "komponentenerfassung") {
    const typ = nachweis.payload.komponenten_typ ?? nachweis.payload.typ;
    const sn = nachweis.payload.seriennummer;
    if (typ || sn) {
      return `Komponente: ${[typ, sn].filter(Boolean).join(" · ")}`;
    }
  }
  return nachweis.art.replace(/_/g, " ");
}

/**
 * Art-spezifische Nachweisdarstellung in der Schrittkarte (Gate 8.3b).
 */
export function SchrittNachweise({ prueflaufId, nachweise }: SchrittNachweiseProps) {
  if (nachweise.length === 0) {
    return null;
  }

  return (
    <div className="space-y-2" data-testid="schritt-nachweise">
      <p className="text-xs font-medium">Nachweise</p>
      <ul className="space-y-2">
        {nachweise.map((nachweis) => (
          <li key={nachweis.nachweis_id} className="rounded border p-2 space-y-1">
            {nachweis.art === "foto" ? (
              <FotoNachweisAnzeige
                prueflaufId={prueflaufId}
                nachweisId={nachweis.nachweis_id}
                dateiname={
                  typeof nachweis.payload.dateiname === "string"
                    ? nachweis.payload.dateiname
                    : null
                }
              />
            ) : (
              <p className="text-xs text-muted-foreground">
                {formatNachweisKompakt(nachweis)}
                {nachweis.ist_automatisch && " (automatisch)"}
              </p>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
