import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, Loader2 } from "lucide-react";
import { useForm } from "react-hook-form";
import { Link, useNavigate, useParams } from "react-router-dom";

import {
  beurteileSchritt,
  erfasseKomponente,
  erfasseNachweis,
  schliessePrueflaufAb,
} from "@/adapters/api";
import { ApiErrorAlert } from "@/components/ApiErrorAlert";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { komponenteFormSchema, nachweisFormSchema, type KomponenteForm, type NachweisForm } from "@/forms/schemas";
import { usePrueflaufDetail } from "@/hooks/usePrueflaufDetail";
import { prueflaufQueryKey } from "@/lib/queryClient";

export function PrueflaufPage() {
  const { prueflaufId = "" } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { data, isLoading, error } = usePrueflaufDetail(prueflaufId);

  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: prueflaufQueryKey(prueflaufId) });

  const komponenteMutation = useMutation({
    mutationFn: (values: KomponenteForm) => erfasseKomponente(prueflaufId, values),
    onSuccess: invalidate,
  });

  const nachweisMutation = useMutation({
    mutationFn: ({ schrittId, messwert }: { schrittId: string; messwert: number }) =>
      erfasseNachweis(prueflaufId, schrittId, {
        art: "messwert",
        payload: { spannung: messwert },
        ist_automatisch: false,
      }),
    onSuccess: invalidate,
  });

  const beurteilungMutation = useMutation({
    mutationFn: (schrittId: string) => beurteileSchritt(prueflaufId, schrittId),
    onSuccess: invalidate,
  });

  const abschlussMutation = useMutation({
    mutationFn: () => schliessePrueflaufAb(prueflaufId),
    onSuccess: (result) => {
      navigate(`/prueflaeufe/${prueflaufId}/abschluss`, { state: { abschluss: result } });
    },
  });

  const komponenteForm = useForm<KomponenteForm>({
    resolver: zodResolver(komponenteFormSchema),
    defaultValues: { komponenten_typ: "mainboard", seriennummer: "MB-8" },
  });

  const nachweisForm = useForm<NachweisForm>({
    resolver: zodResolver(nachweisFormSchema),
    defaultValues: { messwert: 230 },
  });

  if (isLoading) {
    return (
      <p className="flex items-center gap-2 text-muted-foreground">
        <Loader2 className="size-4 animate-spin" aria-hidden />
        Prüflauf wird geladen…
      </p>
    );
  }

  if (error || !data) {
    return (
      <div className="space-y-4">
        <ApiErrorAlert error={error ?? new Error("Prüflauf nicht gefunden")} />
        <Link to="/" className="text-sm underline">
          Zurück zum Start
        </Link>
      </div>
    );
  }

  const fehlendeKomponenten = data.fehlende_komponenten;
  const istAbgeschlossen = data.ist_abgeschlossen;

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Prüflauf {data.prueflauf_id.slice(0, 8)}…</CardTitle>
          <CardDescription>
            {data.produktkodierung} · {data.pruefobjekt_kennung} · Status:{" "}
            <span className="font-mono">{data.status}</span>
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {data.kann_komponente_erfassen && (
            <form
              className="space-y-3 rounded-lg border p-4"
              onSubmit={komponenteForm.handleSubmit((values) => komponenteMutation.mutate(values))}
            >
              <p className="text-sm font-medium">Istbestückung erfassen</p>
              <p className="text-xs text-muted-foreground">
                Fehlend: {fehlendeKomponenten.join(", ")}
              </p>
              <div className="grid gap-3 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="komponenten_typ">Komponenten-Typ</Label>
                  <Input id="komponenten_typ" {...komponenteForm.register("komponenten_typ")} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="seriennummer">Seriennummer</Label>
                  <Input id="seriennummer" {...komponenteForm.register("seriennummer")} />
                </div>
              </div>
              <Button type="submit" size="sm" disabled={komponenteMutation.isPending}>
                Komponente erfassen
              </Button>
              <ApiErrorAlert error={komponenteMutation.error} />
            </form>
          )}

          <div className="space-y-4">
            <p className="text-sm font-medium">Prüfschritte</p>
            {data.schritte.map((schritt) => (
              <div key={schritt.schritt_id} className="rounded-lg border p-4 space-y-3">
                <div className="flex items-center justify-between gap-2">
                  <p className="font-medium">
                    {schritt.schritt_id}{" "}
                    {schritt.ist_pflicht && (
                      <span className="text-xs text-muted-foreground">(Pflicht)</span>
                    )}
                  </p>
                  {schritt.beurteilung && (
                    <span className="flex items-center gap-1 text-sm text-green-700">
                      <CheckCircle2 className="size-4" aria-hidden />
                      {schritt.beurteilung.ergebnis}
                    </span>
                  )}
                </div>
                <p className="text-xs text-muted-foreground font-mono">
                  Soll: {JSON.stringify(schritt.sollvorgaben)}
                </p>
                {schritt.nachweise.length > 0 && (
                  <p className="text-xs">
                    Nachweise:{" "}
                    {schritt.nachweise.map((n) => JSON.stringify(n.payload)).join("; ")}
                  </p>
                )}

                {!istAbgeschlossen &&
                  (schritt.kann_nachweis_erfassen || schritt.kann_beurteilt_werden) && (
                  <div className="space-y-2 border-t pt-3">
                    {schritt.kann_nachweis_erfassen && (
                      <form
                        className="flex flex-wrap items-end gap-2"
                        onSubmit={nachweisForm.handleSubmit((values) =>
                          nachweisMutation.mutate({
                            schrittId: schritt.schritt_id,
                            messwert: values.messwert,
                          }),
                        )}
                      >
                        <div className="space-y-1">
                          <Label htmlFor={`messwert-${schritt.schritt_id}`}>Messwert Spannung</Label>
                          <Input
                            id={`messwert-${schritt.schritt_id}`}
                            type="number"
                            className="w-32"
                            {...nachweisForm.register("messwert")}
                          />
                        </div>
                        <Button type="submit" size="sm" disabled={nachweisMutation.isPending}>
                          Nachweis erfassen
                        </Button>
                      </form>
                    )}
                    {schritt.kann_beurteilt_werden && (
                      <Button
                        type="button"
                        size="sm"
                        variant="secondary"
                        disabled={beurteilungMutation.isPending}
                        onClick={() => beurteilungMutation.mutate(schritt.schritt_id)}
                      >
                        Beurteilung auslösen
                      </Button>
                    )}
                    <ApiErrorAlert error={nachweisMutation.error ?? beurteilungMutation.error} />
                  </div>
                )}
              </div>
            ))}
          </div>

          {data.kann_abgeschlossen_werden && (
            <Button
              type="button"
              onClick={() => abschlussMutation.mutate()}
              disabled={abschlussMutation.isPending}
            >
              Prüflauf abschließen
            </Button>
          )}

          {istAbgeschlossen && (
            <Link to={`/prueflaeufe/${prueflaufId}/abschluss`}>
              <Button type="button" variant="secondary">
                Zum Abschluss
              </Button>
            </Link>
          )}

          <ApiErrorAlert error={abschlussMutation.error} />
        </CardContent>
      </Card>
    </div>
  );
}
