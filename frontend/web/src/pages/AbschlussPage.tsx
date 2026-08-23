import { useMutation } from "@tanstack/react-query";
import { Download, ExternalLink, FileCheck, Loader2 } from "lucide-react";
import { useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";

import { fetchProtokollPdf, type AbschlussResponse } from "@/adapters/api";
import { ApiErrorAlert } from "@/components/ApiErrorAlert";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  downloadProtokollPdfBlob,
  openProtokollPdfInViewer,
} from "@/lib/protokollPdfAktion";

type AbschlussLocationState = {
  abschluss?: AbschlussResponse;
};

export function AbschlussPage() {
  const { prueflaufId = "" } = useParams();
  const location = useLocation();
  const abschluss = (location.state as AbschlussLocationState | null)?.abschluss;
  const [popupHinweis, setPopupHinweis] = useState<string | null>(null);

  const downloadMutation = useMutation({
    mutationFn: () => fetchProtokollPdf(prueflaufId),
    onSuccess: (blob) => {
      setPopupHinweis(null);
      downloadProtokollPdfBlob(blob, `protokoll-${prueflaufId.slice(0, 8)}.pdf`);
    },
  });

  const openMutation = useMutation({
    mutationFn: () => fetchProtokollPdf(prueflaufId),
    onSuccess: (blob) => {
      const result = openProtokollPdfInViewer(blob);
      if (!result.ok) {
        setPopupHinweis(
          "Das Popup wurde blockiert. Bitte Popups erlauben oder „Protokoll-PDF herunterladen“ nutzen und die Datei lokal öffnen.",
        );
        return;
      }
      setPopupHinweis(null);
    },
  });

  const busy = downloadMutation.isPending || openMutation.isPending;
  const aktionError = openMutation.error ?? downloadMutation.error;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileCheck className="size-5" aria-hidden />
          Prüflauf abgeschlossen
        </CardTitle>
        <CardDescription>
          Ergebnis vom Backend — UI trifft keine Gültigkeitsentscheidung.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {!abschluss ? (
          <p className="text-sm text-muted-foreground">
            Keine Abschlussdaten in der Navigation. Bitte Prüflauf über die Durchführungsseite
            abschließen.
          </p>
        ) : (
          <dl className="space-y-2 text-sm">
            <div className="flex justify-between gap-4">
              <dt className="text-muted-foreground">Status</dt>
              <dd className="font-mono">{abschluss.status}</dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt className="text-muted-foreground">Gültig</dt>
              <dd>{abschluss.ist_gueltig ? "Ja" : "Nein"}</dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt className="text-muted-foreground">Snapshot</dt>
              <dd className="font-mono text-xs">{abschluss.snapshot_id}</dd>
            </div>
          </dl>
        )}

        <div className="flex flex-wrap gap-2">
          <Button
            type="button"
            onClick={() => {
              setPopupHinweis(null);
              openMutation.reset();
              downloadMutation.reset();
              openMutation.mutate();
            }}
            disabled={busy || !prueflaufId}
            aria-busy={openMutation.isPending}
          >
            {openMutation.isPending ? (
              <Loader2 className="animate-spin" aria-hidden />
            ) : (
              <ExternalLink aria-hidden />
            )}
            Anzeigen & Drucken
          </Button>
          <Button
            type="button"
            variant="secondary"
            onClick={() => {
              setPopupHinweis(null);
              openMutation.reset();
              downloadMutation.reset();
              downloadMutation.mutate();
            }}
            disabled={busy || !prueflaufId}
            aria-busy={downloadMutation.isPending}
          >
            {downloadMutation.isPending ? (
              <Loader2 className="animate-spin" aria-hidden />
            ) : (
              <Download aria-hidden />
            )}
            Protokoll-PDF herunterladen
          </Button>
        </div>

        {popupHinweis && (
          <p className="text-sm text-destructive" role="alert">
            {popupHinweis}
          </p>
        )}
        <ApiErrorAlert error={aktionError} />

        <Link to="/" className="inline-block text-sm underline">
          Neuer Prüflauf
        </Link>
      </CardContent>
    </Card>
  );
}
