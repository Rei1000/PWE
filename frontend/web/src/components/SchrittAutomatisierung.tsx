import { Loader2, Play } from "lucide-react";

import { ApiErrorAlert } from "@/components/ApiErrorAlert";
import { AutomatisierungErgebnis } from "@/components/AutomatisierungErgebnis";
import { Button } from "@/components/ui/button";
import { useAutomatisierungAusfuehren } from "@/hooks/useAutomatisierungAusfuehren";

type SchrittAutomatisierungProps = {
  prueflaufId: string;
  schrittId: string;
  hatAutomatisierung: boolean;
  kannAusfuehren: boolean;
  bezeichnung?: string | null;
};

/**
 * Inline-Automatisierung in der Schrittkarte (Gate 6.3b).
 * Sichtbarkeit/Aktivierung ausschließlich über Backend-Read-Model-Flags.
 */
export function SchrittAutomatisierung({
  prueflaufId,
  schrittId,
  hatAutomatisierung,
  kannAusfuehren,
  bezeichnung,
}: SchrittAutomatisierungProps) {
  const mutation = useAutomatisierungAusfuehren(prueflaufId, schrittId);

  if (!hatAutomatisierung) {
    return null;
  }

  const pending = mutation.isPending;
  const disabled = !kannAusfuehren || pending;

  return (
    <div className="space-y-2 border-t pt-3" data-testid="schritt-automatisierung">
      {bezeichnung && (
        <p className="text-xs text-muted-foreground">Automatisierung: {bezeichnung}</p>
      )}
      <div className="flex flex-wrap items-center gap-2">
        <Button
          type="button"
          size="sm"
          disabled={disabled}
          aria-busy={pending}
          onClick={() => {
            if (pending) return;
            mutation.reset();
            mutation.mutate();
          }}
        >
          {pending ? (
            <Loader2 className="size-4 animate-spin" aria-hidden />
          ) : (
            <Play className="size-4" aria-hidden />
          )}
          {pending ? "Automatisierung läuft…" : "Automatisierung ausführen"}
        </Button>
      </div>
      <p className="text-xs text-muted-foreground">
        Jeder Start erzeugt eine neue Nachweis-Welle. Bei unklarem Verbindungsabbruch
        nicht blind erneut starten.
      </p>
      {mutation.isSuccess && mutation.data && (
        <AutomatisierungErgebnis ergebnis={mutation.data} />
      )}
      <ApiErrorAlert error={mutation.error} />
    </div>
  );
}
