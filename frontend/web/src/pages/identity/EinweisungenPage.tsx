import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2, Plus } from "lucide-react";
import { useMemo, useState } from "react";
import { useForm } from "react-hook-form";

import {
  einweisungAnlegenSchema,
  type EinweisungAnlegenRequest,
} from "@/adapters/api/schemas/identity";
import { ApiErrorAlert } from "@/components/ApiErrorAlert";
import { ConfirmDialog } from "@/components/katalog/ConfirmDialog";
import { EinweisungStatusBadge } from "@/components/identity/IdentityStatusBadge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useBenutzerQuery } from "@/hooks/identity/useBenutzer";
import {
  useCreateEinweisungMutation,
  useEinweisungenQuery,
  useWiderrufenEinweisungMutation,
} from "@/hooks/identity/useEinweisungen";
import { useCurrentUser } from "@/hooks/useAuth";
import { darfEinweisungSchreiben } from "@/lib/identityRoles";

export function EinweisungenPage() {
  const { data: user } = useCurrentUser();
  const schreiben = darfEinweisungSchreiben(user);
  const { data: benutzer = [] } = useBenutzerQuery();

  const [filterBenutzerId, setFilterBenutzerId] = useState("");
  const [filterVersionId, setFilterVersionId] = useState("");
  const [filterStatus, setFilterStatus] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [widerrufenId, setWiderrufenId] = useState<string | null>(null);

  const { data: einweisungen = [], isLoading, error } = useEinweisungenQuery(
    filterBenutzerId,
    filterVersionId || undefined,
  );

  const createMutation = useCreateEinweisungMutation(
    filterBenutzerId,
    filterVersionId || undefined,
  );
  const widerrufenMutation = useWiderrufenEinweisungMutation(
    filterBenutzerId,
    filterVersionId || undefined,
  );

  const form = useForm<EinweisungAnlegenRequest>({
    resolver: zodResolver(einweisungAnlegenSchema),
    defaultValues: { benutzer_id: "", version_id: "", bemerkung: "", gueltig_bis: "" },
  });

  const gefiltert = useMemo(() => {
    if (!filterStatus) return einweisungen;
    return einweisungen.filter((e) => e.status.toLowerCase() === filterStatus.toLowerCase());
  }, [einweisungen, filterStatus]);

  const onSubmit = form.handleSubmit(async (values) => {
    await createMutation.mutateAsync({
      benutzer_id: values.benutzer_id,
      version_id: values.version_id,
      bemerkung: values.bemerkung || undefined,
      gueltig_bis: values.gueltig_bis || undefined,
    });
    form.reset();
    setShowForm(false);
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold">Einweisungen</h2>
          <p className="text-sm text-muted-foreground">Historie und Verwaltung von Einweisungen.</p>
        </div>
        {schreiben && (
          <Button type="button" onClick={() => setShowForm((v) => !v)}>
            <Plus className="size-4" aria-hidden />
            Einweisung anlegen
          </Button>
        )}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Filter</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-3">
          <div className="space-y-2">
            <Label htmlFor="filter-benutzer">Benutzer</Label>
            <select
              id="filter-benutzer"
              className="flex h-9 w-full rounded-md border border-input bg-background px-3 text-sm"
              value={filterBenutzerId}
              onChange={(e) => setFilterBenutzerId(e.target.value)}
            >
              <option value="">— Benutzer wählen —</option>
              {benutzer.map((b) => (
                <option key={b.benutzer_id} value={b.benutzer_id}>
                  {b.anzeigename}
                </option>
              ))}
            </select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="filter-version">Version</Label>
            <Input
              id="filter-version"
              placeholder="Version-ID"
              value={filterVersionId}
              onChange={(e) => setFilterVersionId(e.target.value)}
              className="font-mono text-sm"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="filter-status">Status</Label>
            <select
              id="filter-status"
              className="flex h-9 w-full rounded-md border border-input bg-background px-3 text-sm"
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
            >
              <option value="">Alle</option>
              <option value="gueltig">Gültig</option>
              <option value="widerrufen">Widerrufen</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {schreiben && showForm && (
        <Card>
          <CardHeader>
            <CardTitle>Einweisung anlegen</CardTitle>
            <CardDescription>Neue Einweisung für einen Benutzer und eine Version.</CardDescription>
          </CardHeader>
          <CardContent>
            <form className="space-y-4" onSubmit={onSubmit} noValidate>
              <div className="space-y-2">
                <Label htmlFor="benutzer_id">Benutzer</Label>
                <select
                  id="benutzer_id"
                  className="flex h-9 w-full rounded-md border border-input bg-background px-3 text-sm"
                  value={form.watch("benutzer_id")}
                  onChange={(e) =>
                    form.setValue("benutzer_id", e.target.value, { shouldValidate: true })
                  }
                >
                  <option value="">— Benutzer wählen —</option>
                  {benutzer.map((b) => (
                    <option key={b.benutzer_id} value={b.benutzer_id}>
                      {b.anzeigename}
                    </option>
                  ))}
                </select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="version_id">Version-ID</Label>
                <Input id="version_id" className="font-mono" {...form.register("version_id")} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="gueltig_bis">Gültig bis (optional)</Label>
                <Input id="gueltig_bis" type="date" {...form.register("gueltig_bis")} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="bemerkung">Bemerkung</Label>
                <Input id="bemerkung" {...form.register("bemerkung")} />
              </div>
              <div className="flex gap-2">
                <Button type="submit" disabled={createMutation.isPending}>
                  {createMutation.isPending ? <Loader2 className="size-4 animate-spin" /> : "Anlegen"}
                </Button>
                <Button type="button" variant="outline" onClick={() => setShowForm(false)}>
                  Abbrechen
                </Button>
              </div>
              <ApiErrorAlert error={createMutation.error} />
            </form>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Historie</CardTitle>
        </CardHeader>
        <CardContent>
          {!filterBenutzerId && (
            <p className="text-sm text-muted-foreground">
              Bitte einen Benutzer im Filter auswählen.
            </p>
          )}
          {filterBenutzerId && isLoading && (
            <p className="text-sm text-muted-foreground">Wird geladen…</p>
          )}
          <ApiErrorAlert error={error} />
          {filterBenutzerId && !isLoading && !error && (
            <ul className="divide-y">
              {gefiltert.map((e) => (
                <li key={e.einweisung_id} className="flex items-center justify-between gap-4 py-3">
                  <div>
                    <p className="font-mono text-sm">{e.version_id}</p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(e.datum).toLocaleString("de-DE")}
                      {e.gueltig_bis ? ` · gültig bis ${e.gueltig_bis}` : ""}
                    </p>
                    {e.bemerkung && <p className="text-sm">{e.bemerkung}</p>}
                  </div>
                  <div className="flex items-center gap-2">
                    <EinweisungStatusBadge status={e.status} />
                    {schreiben && e.status.toLowerCase() === "gueltig" && (
                      <Button size="sm" variant="outline" onClick={() => setWiderrufenId(e.einweisung_id)}>
                        Widerrufen
                      </Button>
                    )}
                  </div>
                </li>
              ))}
              {gefiltert.length === 0 && (
                <li className="py-4 text-sm text-muted-foreground">Keine Einweisungen gefunden.</li>
              )}
            </ul>
          )}
        </CardContent>
      </Card>

      <ConfirmDialog
        open={Boolean(widerrufenId)}
        title="Einweisung widerrufen"
        description="Die Einweisung wird widerrufen und ist nicht mehr gültig."
        confirmLabel="Widerrufen"
        onConfirm={async () => {
          if (widerrufenId) {
            await widerrufenMutation.mutateAsync(widerrufenId);
          }
          setWiderrufenId(null);
        }}
        onCancel={() => setWiderrufenId(null)}
        pending={widerrufenMutation.isPending}
      />
      <ApiErrorAlert error={widerrufenMutation.error} />
    </div>
  );
}
