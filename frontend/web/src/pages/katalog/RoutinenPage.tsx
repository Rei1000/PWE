import { Link } from "react-router-dom";
import { Loader2, Plus, Trash2 } from "lucide-react";
import { useState } from "react";

import { ApiErrorAlert } from "@/components/ApiErrorAlert";
import { ConfirmDialog } from "@/components/katalog/ConfirmDialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useDeleteRoutineMutation, useRoutinenQuery } from "@/hooks/katalog/useRoutinen";
import { katalogConflictMessage } from "@/lib/katalogErrors";

export function RoutinenPage() {
  const { data: routinen = [], isLoading, error } = useRoutinenQuery();
  const deleteMutation = useDeleteRoutineMutation();
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<unknown>(null);

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Routinen</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Geordnete Kommando-Folgen — keine Ausführung in diesem Bereich.
          </p>
        </div>
        <Button asChild>
          <Link to="/katalog/routinen/neu">
            <Plus className="size-4" aria-hidden />
            Routine anlegen
          </Link>
        </Button>
      </div>

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
          {!isLoading && routinen.length === 0 && (
            <p className="text-sm text-muted-foreground">Noch keine Routinen angelegt.</p>
          )}
          <ul className="divide-y">
            {routinen.map((item) => (
              <li key={item.routine_id} className="flex items-center justify-between gap-4 py-3">
                <div>
                  <p className="font-medium">{item.bezeichnung}</p>
                  <p className="text-xs text-muted-foreground">
                    {item.anzahl_aktionen} Aktion(en) ·{" "}
                    <span className="font-mono">{item.routine_id}</span>
                  </p>
                </div>
                <div className="flex gap-2">
                  <Button asChild size="sm" variant="outline">
                    <Link to={`/katalog/routinen/${item.routine_id}`}>Bearbeiten</Link>
                  </Button>
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    className="text-destructive"
                    onClick={() => {
                      setDeleteError(null);
                      setDeleteId(item.routine_id);
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
        title="Routine löschen?"
        description="Die Routine wird dauerhaft aus der Bibliothek entfernt."
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
