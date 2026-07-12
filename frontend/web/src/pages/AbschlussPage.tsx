import { useMutation } from "@tanstack/react-query";
import { Download, FileCheck, Loader2 } from "lucide-react";
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

type AbschlussLocationState = {
  abschluss?: AbschlussResponse;
};

export function AbschlussPage() {
  const { prueflaufId = "" } = useParams();
  const location = useLocation();
  const abschluss = (location.state as AbschlussLocationState | null)?.abschluss;

  const pdfMutation = useMutation({
    mutationFn: () => fetchProtokollPdf(prueflaufId),
    onSuccess: (blob) => {
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `protokoll-${prueflaufId.slice(0, 8)}.pdf`;
      anchor.click();
      URL.revokeObjectURL(url);
    },
  });

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

        <Button
          type="button"
          onClick={() => pdfMutation.mutate()}
          disabled={pdfMutation.isPending || !prueflaufId}
        >
          {pdfMutation.isPending ? (
            <Loader2 className="animate-spin" aria-hidden />
          ) : (
            <Download aria-hidden />
          )}
          Protokoll-PDF herunterladen
        </Button>
        <ApiErrorAlert error={pdfMutation.error} />

        <Link to="/" className="inline-block text-sm underline">
          Neuer Prüflauf
        </Link>
      </CardContent>
    </Card>
  );
}
