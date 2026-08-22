import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Loader2, Pencil, Plus, Trash2 } from "lucide-react";

import { kommandoCreateRequestSchema, type KommandoCreateRequest } from "@/adapters/api/schemas/bibliothek";
import { getKommando } from "@/adapters/api/bibliothek";
import { ApiErrorAlert } from "@/components/ApiErrorAlert";
import { ConfirmDialog } from "@/components/katalog/ConfirmDialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  useCreateKommandoMutation,
  useDeleteKommandoMutation,
  useKommandosQuery,
  useUpdateKommandoMutation,
} from "@/hooks/katalog/useKommandos";
import { katalogConflictMessage } from "@/lib/katalogErrors";

type FormValues = KommandoCreateRequest;

export function KommandosPage() {
  const { data: kommandos = [], isLoading, error } = useKommandosQuery();
  const createMutation = useCreateKommandoMutation();
  const deleteMutation = useDeleteKommandoMutation();
  const [editingId, setEditingId] = useState<string | null>(null);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<unknown>(null);

  const updateMutation = useUpdateKommandoMutation(editingId ?? "");

  const form = useForm<FormValues>({
    resolver: zodResolver(kommandoCreateRequestSchema),
    defaultValues: { bezeichnung: "", kommandocode: "" },
  });

  const resetForm = () => {
    setEditingId(null);
    form.reset({ bezeichnung: "", kommandocode: "" });
    createMutation.reset();
    updateMutation.reset();
  };

  const startEdit = async (item: { kommando_id: string; bezeichnung: string }) => {
    setEditingId(item.kommando_id);
    const detail = await getKommando(item.kommando_id);
    form.reset({ bezeichnung: detail.bezeichnung, kommandocode: detail.kommandocode });
  };

  const onSubmit = form.handleSubmit(async (values) => {
    if (editingId) {
      await updateMutation.mutateAsync(values);
    } else {
      await createMutation.mutateAsync(values);
    }
    resetForm();
  });

  const activeMutation = editingId ? updateMutation : createMutation;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Externe Kommandos</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Design-Time — keine Kommandoausführung in diesem Bereich.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{editingId ? "Kommando bearbeiten" : "Kommando anlegen"}</CardTitle>
          <CardDescription>Bezeichnung und Kommandocode für die Bibliothek.</CardDescription>
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
              <Label htmlFor="kommandocode">Kommandocode</Label>
              <Input id="kommandocode" {...form.register("kommandocode")} className="font-mono" />
              {form.formState.errors.kommandocode && (
                <p className="text-sm text-destructive">{form.formState.errors.kommandocode.message}</p>
              )}
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

      <Card>
        <CardHeader>
          <CardTitle>Bibliothek</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && (
            <p className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="size-4 animate-spin" aria-hidden />
              Lädt…
            </p>
          )}
          <ApiErrorAlert error={error} />
          {!isLoading && kommandos.length === 0 && (
            <p className="text-sm text-muted-foreground">Noch keine Kommandos angelegt.</p>
          )}
          <ul className="divide-y">
            {kommandos.map((item) => (
              <li key={item.kommando_id} className="flex items-center justify-between gap-4 py-3">
                <div>
                  <p className="font-medium">{item.bezeichnung}</p>
                  <p className="font-mono text-xs text-muted-foreground">{item.kommando_id}</p>
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
                      setDeleteId(item.kommando_id);
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
        title="Kommando löschen?"
        description="Das Kommando wird dauerhaft aus der Bibliothek entfernt."
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
