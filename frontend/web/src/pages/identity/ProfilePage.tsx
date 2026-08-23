import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2, Pencil, Plus } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { profilAnlegenSchema } from "@/adapters/api/schemas/identity";
import { ApiErrorAlert } from "@/components/ApiErrorAlert";
import { ConfirmDialog } from "@/components/katalog/ConfirmDialog";
import { ProfilStatusBadge } from "@/components/identity/IdentityStatusBadge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  useAktivierenProfilMutation,
  useCreateProfilMutation,
  useDeaktivierenProfilMutation,
  useProfileQuery,
  useUpdateProfilMutation,
} from "@/hooks/identity/useProfile";
import { useCurrentUser } from "@/hooks/useAuth";
import { darfProfileSchreiben } from "@/lib/identityRoles";

const profilFormSchema = profilAnlegenSchema.extend({
  produktIdsRaw: z.string().optional(),
});

type ProfilFormValues = z.infer<typeof profilFormSchema>;

function parseProduktIds(raw: string): string[] {
  return raw
    .split(/[\n,]/)
    .map((s) => s.trim())
    .filter(Boolean);
}

function ProfilAktivierenButton({ profilId }: { profilId: string }) {
  const mutation = useAktivierenProfilMutation(profilId);
  return (
    <Button
      size="sm"
      variant="outline"
      onClick={() => mutation.mutate()}
      disabled={mutation.isPending}
    >
      Aktivieren
    </Button>
  );
}

export function ProfilePage() {
  const { data: user } = useCurrentUser();
  const schreiben = darfProfileSchreiben(user);
  const { data: profile = [], isLoading, error } = useProfileQuery();
  const createMutation = useCreateProfilMutation();
  const [editingId, setEditingId] = useState<string | null>(null);
  const [deaktivierenId, setDeaktivierenId] = useState<string | null>(null);

  const updateMutation = useUpdateProfilMutation(editingId ?? "");
  const deaktivierenMutation = useDeaktivierenProfilMutation(deaktivierenId ?? "");

  const form = useForm<ProfilFormValues>({
    resolver: zodResolver(profilFormSchema),
    defaultValues: { bezeichnung: "", beschreibung: "", produktIdsRaw: "" },
  });

  const resetForm = () => {
    setEditingId(null);
    form.reset({ bezeichnung: "", beschreibung: "", produktIdsRaw: "" });
  };

  const startEdit = (profil: (typeof profile)[0]) => {
    setEditingId(profil.profil_id);
    form.reset({
      bezeichnung: profil.bezeichnung,
      beschreibung: profil.beschreibung ?? "",
      produktIdsRaw: profil.produktdefinition_ids.join("\n"),
    });
  };

  const onSubmit = form.handleSubmit(async (values) => {
    const body = {
      bezeichnung: values.bezeichnung,
      beschreibung: values.beschreibung || undefined,
      produktdefinition_ids: parseProduktIds(values.produktIdsRaw ?? ""),
    };
    if (editingId) {
      await updateMutation.mutateAsync(body);
    } else {
      await createMutation.mutateAsync(body);
    }
    resetForm();
  });

  const activeMutation = editingId ? updateMutation : createMutation;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold">Berechtigungsprofile</h2>
        <p className="text-sm text-muted-foreground">
          {schreiben ? "Anlegen und bearbeiten" : "Übersicht (nur Lesen)"}
        </p>
      </div>

      {schreiben && (
        <Card>
          <CardHeader>
            <CardTitle>{editingId ? "Profil bearbeiten" : "Profil anlegen"}</CardTitle>
            <CardDescription>
              Profile werden deaktiviert statt gelöscht. Produktdefinition-IDs je Zeile oder
              kommagetrennt.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form className="space-y-4" onSubmit={onSubmit} noValidate>
              <div className="space-y-2">
                <Label htmlFor="bezeichnung">Bezeichnung</Label>
                <Input id="bezeichnung" {...form.register("bezeichnung")} />
                {form.formState.errors.bezeichnung && (
                  <p className="text-sm text-destructive">
                    {form.formState.errors.bezeichnung.message}
                  </p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="beschreibung">Beschreibung</Label>
                <Input id="beschreibung" {...form.register("beschreibung")} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="produktIdsRaw">Produktdefinitionen</Label>
                <textarea
                  id="produktIdsRaw"
                  className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm font-mono"
                  {...form.register("produktIdsRaw")}
                />
              </div>
              <div className="flex gap-2">
                <Button type="submit" disabled={activeMutation.isPending}>
                  {activeMutation.isPending ? (
                    <Loader2 className="size-4 animate-spin" aria-hidden />
                  ) : editingId ? (
                    <Pencil className="size-4" aria-hidden />
                  ) : (
                    <Plus className="size-4" aria-hidden />
                  )}
                  {editingId ? "Speichern" : "Anlegen"}
                </Button>
                {editingId && (
                  <Button type="button" variant="outline" onClick={resetForm}>
                    Abbrechen
                  </Button>
                )}
              </div>
              <ApiErrorAlert error={activeMutation.error} />
            </form>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Profiliste</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && <p className="text-sm text-muted-foreground">Wird geladen…</p>}
          <ApiErrorAlert error={error} />
          {!isLoading && !error && (
            <ul className="divide-y">
              {profile.map((p) => (
                <li key={p.profil_id} className="flex items-center justify-between gap-4 py-3">
                  <div>
                    <p className="font-medium">{p.bezeichnung}</p>
                    {p.beschreibung && (
                      <p className="text-sm text-muted-foreground">{p.beschreibung}</p>
                    )}
                    <p className="text-xs font-mono text-muted-foreground">{p.profil_id}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <ProfilStatusBadge aktiv={p.aktiv} />
                    {schreiben && (
                      <>
                        <Button size="sm" variant="ghost" onClick={() => startEdit(p)}>
                          Bearbeiten
                        </Button>
                        {p.aktiv ? (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => setDeaktivierenId(p.profil_id)}
                          >
                            Deaktivieren
                          </Button>
                        ) : (
                          <ProfilAktivierenButton profilId={p.profil_id} />
                        )}
                      </>
                    )}
                  </div>
                </li>
              ))}
              {profile.length === 0 && (
                <li className="py-4 text-sm text-muted-foreground">Keine Profile vorhanden.</li>
              )}
            </ul>
          )}
        </CardContent>
      </Card>

      <ConfirmDialog
        open={Boolean(deaktivierenId)}
        title="Profil deaktivieren"
        description="Das Profil wird deaktiviert und kann nicht mehr zugewiesen werden. Es wird nicht gelöscht."
        confirmLabel="Deaktivieren"
        onConfirm={async () => {
          await deaktivierenMutation.mutateAsync();
          setDeaktivierenId(null);
        }}
        onCancel={() => setDeaktivierenId(null)}
        pending={deaktivierenMutation.isPending}
      />
    </div>
  );
}
