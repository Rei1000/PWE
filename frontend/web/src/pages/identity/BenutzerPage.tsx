import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2, Plus } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link } from "react-router-dom";

import { benutzerAnlegenSchema, type BenutzerAnlegenRequest } from "@/adapters/api/schemas/identity";
import { ApiErrorAlert } from "@/components/ApiErrorAlert";
import { BenutzerStatusBadge } from "@/components/identity/IdentityStatusBadge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useBenutzerQuery, useCreateBenutzerMutation } from "@/hooks/identity/useBenutzer";
import { useCurrentUser } from "@/hooks/useAuth";
import { ALLE_ROLLEN, istAdministrator } from "@/lib/identityRoles";
import { rolleLabel } from "@/lib/identityLabels";

export function BenutzerPage() {
  const { data: user } = useCurrentUser();
  const admin = istAdministrator(user);
  const { data: benutzer = [], isLoading, error } = useBenutzerQuery();
  const createMutation = useCreateBenutzerMutation();
  const [showForm, setShowForm] = useState(false);

  const form = useForm<BenutzerAnlegenRequest>({
    resolver: zodResolver(benutzerAnlegenSchema),
    defaultValues: {
      login: "",
      anzeigename: "",
      passwort: "",
      rollen: ["pruefer"],
    },
  });

  const selectedRollen = form.watch("rollen");

  const toggleRolle = (rolle: string) => {
    const current = form.getValues("rollen");
    if (current.includes(rolle)) {
      form.setValue(
        "rollen",
        current.filter((r) => r !== rolle),
        { shouldValidate: true },
      );
    } else {
      form.setValue("rollen", [...current, rolle], { shouldValidate: true });
    }
  };

  const onSubmit = form.handleSubmit(async (values) => {
    await createMutation.mutateAsync(values);
    form.reset({ login: "", anzeigename: "", passwort: "", rollen: ["pruefer"] });
    setShowForm(false);
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold">Benutzer</h2>
          <p className="text-sm text-muted-foreground">
            {admin ? "Anlegen und verwalten" : "Übersicht (nur Lesen)"}
          </p>
        </div>
        {admin && (
          <Button type="button" onClick={() => setShowForm((v) => !v)}>
            <Plus className="size-4" aria-hidden />
            Benutzer anlegen
          </Button>
        )}
      </div>

      {admin && showForm && (
        <Card>
          <CardHeader>
            <CardTitle>Neuer Benutzer</CardTitle>
            <CardDescription>Initialpasswort wird beim ersten Login geändert.</CardDescription>
          </CardHeader>
          <CardContent>
            <form className="space-y-4" onSubmit={onSubmit} noValidate>
              <div className="space-y-2">
                <Label htmlFor="login">Login</Label>
                <Input id="login" {...form.register("login")} />
                {form.formState.errors.login && (
                  <p className="text-sm text-destructive">{form.formState.errors.login.message}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="anzeigename">Anzeigename</Label>
                <Input id="anzeigename" {...form.register("anzeigename")} />
                {form.formState.errors.anzeigename && (
                  <p className="text-sm text-destructive">
                    {form.formState.errors.anzeigename.message}
                  </p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="passwort">Initialpasswort</Label>
                <Input id="passwort" type="password" {...form.register("passwort")} />
                {form.formState.errors.passwort && (
                  <p className="text-sm text-destructive">{form.formState.errors.passwort.message}</p>
                )}
              </div>
              <fieldset className="space-y-2">
                <legend className="text-sm font-medium">Rollen</legend>
                <div className="flex flex-wrap gap-3">
                  {ALLE_ROLLEN.map((rolle) => (
                    <label key={rolle} className="flex items-center gap-2 text-sm">
                      <input
                        type="checkbox"
                        checked={selectedRollen.includes(rolle)}
                        onChange={() => toggleRolle(rolle)}
                      />
                      {rolleLabel(rolle)}
                    </label>
                  ))}
                </div>
                {form.formState.errors.rollen && (
                  <p className="text-sm text-destructive">{form.formState.errors.rollen.message}</p>
                )}
              </fieldset>
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
          <CardTitle>Benutzerliste</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && <p className="text-sm text-muted-foreground">Wird geladen…</p>}
          <ApiErrorAlert error={error} />
          {!isLoading && !error && (
            <ul className="divide-y">
              {benutzer.map((b) => (
                <li key={b.benutzer_id} className="flex items-center justify-between gap-4 py-3">
                  <div>
                    <Link
                      to={`/verwaltung/benutzer/${b.benutzer_id}`}
                      className="font-medium hover:underline"
                    >
                      {b.anzeigename}
                    </Link>
                    <p className="text-xs text-muted-foreground">{b.login}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <BenutzerStatusBadge status={b.status} />
                    <span className="text-xs text-muted-foreground">
                      {b.rollen.map(rolleLabel).join(", ")}
                    </span>
                  </div>
                </li>
              ))}
              {benutzer.length === 0 && (
                <li className="py-4 text-sm text-muted-foreground">Keine Benutzer vorhanden.</li>
              )}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
