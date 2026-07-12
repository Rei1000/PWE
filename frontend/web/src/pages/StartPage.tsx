import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { Database, Play } from "lucide-react";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";

import { DEMO_KATALOG_ENTWURF, seedDemoKatalog, startPrueflauf } from "@/adapters/api";
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
import { startPrueflaufFormSchema, type StartPrueflaufForm } from "@/forms/schemas";

export function StartPage() {
  const navigate = useNavigate();

  const seedMutation = useMutation({
    mutationFn: () => seedDemoKatalog(DEMO_KATALOG_ENTWURF),
  });

  const form = useForm<StartPrueflaufForm>({
    resolver: zodResolver(startPrueflaufFormSchema),
    defaultValues: {
      produktkodierung: DEMO_KATALOG_ENTWURF.produktkodierung,
      pruefobjekt_kennung: "GER-800",
      pruefer_id: "pruefer-1",
    },
  });

  const startMutation = useMutation({
    mutationFn: (values: StartPrueflaufForm) => startPrueflauf(values),
    onSuccess: (data) => {
      navigate(`/prueflaeufe/${data.prueflauf_id}`);
    },
  });

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Prüflauf starten</CardTitle>
          <CardDescription>
            Gate 6.2 Happy Path — Katalog-Seed über API, dann Prüflauf anlegen. Keine Fachlogik
            in der UI.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-3">
            <p className="text-sm text-muted-foreground">
              Schritt 1: Demo-Katalog anlegen und veröffentlichen (
              <span className="font-mono">{DEMO_KATALOG_ENTWURF.produktkodierung}</span>)
            </p>
            <Button
              type="button"
              variant="secondary"
              onClick={() => seedMutation.mutate()}
              disabled={seedMutation.isPending}
            >
              <Database aria-hidden />
              {seedMutation.isPending ? "Seed läuft…" : "Katalog seeden"}
            </Button>
            {seedMutation.isSuccess && (
              <p className="text-sm text-green-700">
                Version {seedMutation.data.version_id} veröffentlicht.
              </p>
            )}
            <ApiErrorAlert error={seedMutation.error} />
          </div>

          <form
            className="space-y-4 border-t pt-4"
            onSubmit={form.handleSubmit((values) => startMutation.mutate(values))}
            noValidate
          >
            <p className="text-sm text-muted-foreground">Schritt 2: Prüflauf starten</p>
            <div className="space-y-2">
              <Label htmlFor="produktkodierung">Produktkodierung</Label>
              <Input id="produktkodierung" {...form.register("produktkodierung")} />
              {form.formState.errors.produktkodierung && (
                <p className="text-sm text-destructive">
                  {form.formState.errors.produktkodierung.message}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="pruefobjekt_kennung">Prüfobjekt-Kennung</Label>
              <Input id="pruefobjekt_kennung" {...form.register("pruefobjekt_kennung")} />
              {form.formState.errors.pruefobjekt_kennung && (
                <p className="text-sm text-destructive">
                  {form.formState.errors.pruefobjekt_kennung.message}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="pruefer_id">Prüfer-ID</Label>
              <Input id="pruefer_id" {...form.register("pruefer_id")} />
              {form.formState.errors.pruefer_id && (
                <p className="text-sm text-destructive">{form.formState.errors.pruefer_id.message}</p>
              )}
            </div>
            <Button type="submit" disabled={startMutation.isPending}>
              <Play aria-hidden />
              {startMutation.isPending ? "Starte…" : "Prüflauf starten"}
            </Button>
            <ApiErrorAlert error={startMutation.error} />
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
