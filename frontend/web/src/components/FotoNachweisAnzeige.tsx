import { useEffect, useState } from "react";

import { fetchNachweisDatei } from "@/adapters/api/prueflaeufe";
import { ApiErrorAlert } from "@/components/ApiErrorAlert";
import { Loader2 } from "lucide-react";

type FotoNachweisAnzeigeProps = {
  prueflaufId: string;
  nachweisId: string;
  dateiname?: string | null;
};

/**
 * Inline-Anzeige eines Foto-Nachweises via kontextgebundenem Download (Gate 8.3b).
 */
export function FotoNachweisAnzeige({
  prueflaufId,
  nachweisId,
  dateiname,
}: FotoNachweisAnzeigeProps) {
  const [objectUrl, setObjectUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    let cancelled = false;
    let url: string | null = null;

    async function load() {
      setLoading(true);
      setError(null);
      setObjectUrl(null);
      try {
        const blob = await fetchNachweisDatei(prueflaufId, nachweisId);
        if (cancelled) return;
        const created = URL.createObjectURL(blob);
        if (cancelled) {
          URL.revokeObjectURL(created);
          return;
        }
        url = created;
        setObjectUrl(created);
      } catch (err) {
        if (!cancelled) {
          setError(err);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void load();

    return () => {
      cancelled = true;
      if (url) {
        URL.revokeObjectURL(url);
      }
    };
  }, [prueflaufId, nachweisId]);

  if (loading) {
    return (
      <p className="flex items-center gap-2 text-xs text-muted-foreground" data-testid="foto-anzeige-loading">
        <Loader2 className="size-3 animate-spin" aria-hidden />
        Foto wird geladen…
      </p>
    );
  }

  if (error) {
    return <ApiErrorAlert error={error} />;
  }

  if (!objectUrl) {
    return null;
  }

  const alt = dateiname ? `Foto-Nachweis ${dateiname}` : `Foto-Nachweis ${nachweisId.slice(0, 8)}`;

  return (
    <img
      src={objectUrl}
      alt={alt}
      className="max-h-48 max-w-full rounded border object-contain"
      data-testid="foto-nachweis-bild"
    />
  );
}
