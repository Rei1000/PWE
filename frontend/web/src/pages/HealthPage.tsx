import { zodResolver } from "@hookform/resolvers/zod";
import { Activity, AlertCircle, CheckCircle2, Loader2, RefreshCw } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";

import {
  refreshIntervalSchema,
  type RefreshIntervalForm,
} from "@/forms/schemas";
import { getApiBaseUrl } from "@/adapters/api/client";
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
import { useHealthQuery } from "@/hooks/useHealthQuery";

export function HealthPage() {
  const [refetchIntervalMs, setRefetchIntervalMs] = useState<number | undefined>(undefined);

  const { data, error, isLoading, isFetching, refetch, isSuccess } = useHealthQuery(
    refetchIntervalMs,
  );

  const form = useForm<RefreshIntervalForm>({
    resolver: zodResolver(refreshIntervalSchema),
    defaultValues: { intervalSeconds: 30 },
  });

  const onApplyInterval = (values: RefreshIntervalForm) => {
    setRefetchIntervalMs(values.intervalSeconds * 1000);
  };

  const onClearInterval = () => {
    setRefetchIntervalMs(undefined);
    form.reset({ intervalSeconds: 30 });
  };

  return (
    <div className="mx-auto flex min-h-screen max-w-lg flex-col justify-center p-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="size-5" aria-hidden />
            PWE — API Health
          </CardTitle>
          <CardDescription>
            Proof of Wiring: Frontend-Adapter → Dev-Proxy → FastAPI. Keine Fachlogik.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <dl className="space-y-2 text-sm">
            <div className="flex justify-between gap-4">
              <dt className="text-muted-foreground">API-Basis</dt>
              <dd className="font-mono text-xs">{getApiBaseUrl()}</dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt className="text-muted-foreground">Status</dt>
              <dd className="flex items-center gap-2">
                {isLoading && (
                  <>
                    <Loader2 className="size-4 animate-spin" aria-hidden />
                    Verbinde…
                  </>
                )}
                {isSuccess && (
                  <>
                    <CheckCircle2 className="size-4 text-green-600" aria-hidden />
                    <span className="font-mono">{data.status}</span>
                  </>
                )}
                {error && (
                  <>
                    <AlertCircle className="size-4 text-destructive" aria-hidden />
                    <span className="text-destructive">Fehler</span>
                  </>
                )}
              </dd>
            </div>
          </dl>

          {error && (
            <p className="rounded-md border border-destructive/30 bg-destructive/5 p-3 text-sm text-destructive">
              {error instanceof Error ? error.message : "Unbekannter Fehler"}
            </p>
          )}

          <div className="flex gap-2">
            <Button type="button" onClick={() => refetch()} disabled={isFetching}>
              <RefreshCw className={isFetching ? "animate-spin" : ""} aria-hidden />
              Erneut prüfen
            </Button>
          </div>

          <form
            className="space-y-3 border-t pt-4"
            onSubmit={form.handleSubmit(onApplyInterval)}
            noValidate
          >
            <p className="text-sm text-muted-foreground">
              Auto-Refresh (Transport-Formular, React Hook Form + Zod — rein UI)
            </p>
            <div className="space-y-2">
              <Label htmlFor="intervalSeconds">Intervall (Sekunden, 5–120)</Label>
              <Input
                id="intervalSeconds"
                type="number"
                min={5}
                max={120}
                {...form.register("intervalSeconds")}
              />
              {form.formState.errors.intervalSeconds && (
                <p className="text-sm text-destructive">
                  {form.formState.errors.intervalSeconds.message}
                </p>
              )}
            </div>
            <div className="flex gap-2">
              <Button type="submit" variant="secondary" size="sm">
                Intervall anwenden
              </Button>
              <Button type="button" variant="ghost" size="sm" onClick={onClearInterval}>
                Intervall aus
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
