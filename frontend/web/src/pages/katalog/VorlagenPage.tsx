import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Trash2 } from "lucide-react";

import { vorlageCreateRequestSchema, type VorlageCreateRequest } from "@/adapters/api/schemas/bibliothek";
import { getVorlage } from "@/adapters/api/bibliothek";
import { ApiErrorAlert } from "@/components/ApiErrorAlert";
import { ConfirmDialog } from "@/components/katalog/ConfirmDialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  useCreateVorlageMutation,
  useDeleteVorlageMutation,
  useUpdateVorlageMutation,
  useVorlagenQuery,
} from "@/hooks/katalog/useVorlagen";
import { katalogConflictMessage } from "@/lib/katalogErrors";

type FormValues = VorlageCreateRequest;

export function VorlagenPage() {
  const { data: vorlagen = [], isLoading, error } = useVorlagenQuery();
  const createMutation = useCreateVorlageMutation();
  const deleteMutation = useDeleteVorlageMutation();
  const [editingId, setEditingId] = useState<string | null>(null);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<unknown>(null);

  const updateMutation = useUpdateVorlageMutation(editingId ?? "");

  const form = useForm<FormValues>({
    resolver: zodResolver(vorlageCreateRequestSchema),
    defaultValues: { bezeichnung: "", beschreibung: "" },
  });

  const resetForm = () => {
    setEditingId(null);
    form.reset({ bezeichnung: "", beschreibung: "" });
    createMutation.reset();
    updateMutation.reset();
  };

  const startEdit = async (item: { vorlage_id: string }) => {
    setEditingId(item.vorlage_id);
    const detail = await getVorlage(item.vorlage_id);
    form.reset({
      bezeichnung: detail.bezeichnung,
      beschreibung: detail.beschreibung ?? "",
    });
  };

  const onSubmit = form.handleSubmit(async (values) => {
    const payload = {
      bezeichnung: values.bezeichnung,
      beschreibung: values.beschreibung?.trim() ? values.beschreibung : null,
    };
    if (editingId) {
      await updateMutation.mutateAsync(payload);
    } else {
      await createMutation.mutateAsync(payload);
    }
    resetForm();
  });

  const activeMutation = editingId ? updateMutation : createMutation;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">PrüfschrittVorlagen</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Minimalfelder V1 — keine Eingabefelder, keine Sollvorgaben in der Vorlage.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{editingId ? "Vorlage bearbeiten" : "Vorlage anlegen"}</CardTitle>
        </CardHeader>
        <CardContent>
          <form className="space-y-4" onSubmit={onSubmit} noValidate>
            <div className="space-y-2">
              <Label htmlFor="bezeichnung">Bezeichnung</Label>
              <Input id="bezeichnung" {...form.register("bezeichnung")} />
              {form.formState.errors.bezeichnung && (
                <p className="text-sm text-destructive">{form.formState.errors.bezeichnung.message}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="beschreibung">Beschreibung (optional)</Label>
              <textarea
                id="beschreibung"
                className="flex min-h-20 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                {...form.register("beschreibung")}
              />
            </div>
            <div className="flex gap-2">
              <Button type="submit" disabled={activeMutation.isPending}>
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

      <Card>
        <CardHeader>
          <CardTitle>Bibliothek</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && <p className="text-sm text-muted-foreground">Lädt…</p>}
          <ApiErrorAlert error={error} />
          <ul className="divide-y">
            {vorlagen.map((item) => (
              <li key={item.vorlage_id} className="flex items-center justify-between gap-4 py-3">
                <div>
                  <p className="font-medium">{item.bezeichnung}</p>
                  <p className="font-mono text-xs text-muted-foreground">{item.vorlage_id}</p>
                </div>
                <div className="flex gap-2">
                  <Button type="button" size="sm" variant="outline" onClick={() => void startEdit(item)}>
                    Bearbeiten
                  </Button>
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    className="text-destructive"
                    onClick={() => {
                      setDeleteError(null);
                      setDeleteId(item.vorlage_id);
                    }}
                  >
                    <Trash2 className="size-4" aria-hidden />
                    Löschen
                  </Button>
                </div>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      <ConfirmDialog
        open={deleteId !== null}
        title="Vorlage löschen?"
        description="Die Vorlage wird dauerhaft aus der Bibliothek entfernt."
        onCancel={() => {
          setDeleteId(null);
          setDeleteError(null);
        }}
        onConfirm={async () => {
          if (!deleteId) return;
          try {
            await deleteMutation.mutateAsync(deleteId);
            setDeleteId(null);
            setDeleteError(null);
          } catch (err) {
            setDeleteError(err);
          }
        }}
        pending={deleteMutation.isPending}
      />
      {deleteError !== null ? (
        <div role="alert" className="text-sm text-destructive">
          {katalogConflictMessage(deleteError) ?? (deleteError instanceof Error ? deleteError.message : "Fehler")}
        </div>
      ) : null}
    </div>
  );
}
