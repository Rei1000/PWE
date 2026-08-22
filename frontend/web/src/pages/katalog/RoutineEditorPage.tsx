import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowDown, ArrowUp, Loader2, Plus, Trash2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { Link, useNavigate, useParams } from "react-router-dom";
import { z } from "zod";

import { ApiErrorAlert } from "@/components/ApiErrorAlert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useKommandosQuery } from "@/hooks/katalog/useKommandos";
import {
  useCreateRoutineMutation,
  useRoutineQuery,
  useUpdateRoutineMutation,
} from "@/hooks/katalog/useRoutinen";

const routineFormSchema = z.object({
  bezeichnung: z.string().min(1),
});

type RoutineFormValues = z.infer<typeof routineFormSchema>;

export function RoutineEditorPage() {
  const { routineId } = useParams();
  const isNew = routineId === undefined;
  const navigate = useNavigate();
  const { data: kommandos = [] } = useKommandosQuery();
  const { data: routine, isLoading: routineLoading, error: routineError } = useRoutineQuery(
    isNew ? undefined : routineId,
  );
  const createMutation = useCreateRoutineMutation();
  const updateMutation = useUpdateRoutineMutation(routineId ?? "");
  const [kommandoIds, setKommandoIds] = useState<string[]>([]);
  const [selectedKommandoId, setSelectedKommandoId] = useState("");

  const kommandoLabelMap = useMemo(
    () => new Map(kommandos.map((k) => [k.kommando_id, k.bezeichnung])),
    [kommandos],
  );

  const form = useForm<RoutineFormValues>({
    resolver: zodResolver(routineFormSchema),
    defaultValues: { bezeichnung: "" },
  });

  useEffect(() => {
    if (routine) {
      form.reset({ bezeichnung: routine.bezeichnung });
      setKommandoIds(routine.aktionen.sort((a, b) => a.position - b.position).map((a) => a.kommando_id));
    }
  }, [routine, form]);

  const move = (index: number, direction: -1 | 1) => {
    const next = [...kommandoIds];
    const target = index + direction;
    if (target < 0 || target >= next.length) return;
    const tmp = next[index];
    next[index] = next[target]!;
    next[target] = tmp!;
    setKommandoIds(next);
  };

  const addKommando = () => {
    if (!selectedKommandoId) return;
    setKommandoIds((prev) => [...prev, selectedKommandoId]);
    setSelectedKommandoId("");
  };

  const removeAt = (index: number) => {
    setKommandoIds((prev) => prev.filter((_, i) => i !== index));
  };

  const onSubmit = form.handleSubmit(async (values) => {
    const payload = { bezeichnung: values.bezeichnung, kommando_ids: kommandoIds };
    if (isNew) {
      const created = await createMutation.mutateAsync(payload);
      navigate(`/katalog/routinen/${created.routine_id}`);
    } else {
      await updateMutation.mutateAsync(payload);
      navigate("/katalog/routinen");
    }
  });

  const activeMutation = isNew ? createMutation : updateMutation;

  if (!isNew && routineLoading) {
    return (
      <p className="flex items-center gap-2 text-muted-foreground">
        <Loader2 className="size-4 animate-spin" aria-hidden />
        Routine wird geladen…
      </p>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">{isNew ? "Routine anlegen" : "Routine bearbeiten"}</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Kommandos in Ausführungsreihenfolge — Hoch/Runter zum Sortieren.
        </p>
      </div>

      <ApiErrorAlert error={routineError} />

      <form className="space-y-6" onSubmit={onSubmit} noValidate>
        <Card>
          <CardHeader>
            <CardTitle>Stammdaten</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="bezeichnung">Bezeichnung</Label>
              <Input id="bezeichnung" {...form.register("bezeichnung")} />
              {form.formState.errors.bezeichnung && (
                <p className="text-sm text-destructive">{form.formState.errors.bezeichnung.message}</p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Kommando-Aktionen</CardTitle>
            <CardDescription>Reihenfolge entspricht der Ausführung bei Automatisierung.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-2">
              <select
                className="h-9 rounded-md border border-input bg-background px-3 text-sm"
                value={selectedKommandoId}
                onChange={(e) => setSelectedKommandoId(e.target.value)}
                aria-label="Kommando auswählen"
              >
                <option value="">Kommando wählen…</option>
                {kommandos.map((k) => (
                  <option key={k.kommando_id} value={k.kommando_id}>
                    {k.bezeichnung}
                  </option>
                ))}
              </select>
              <Button type="button" variant="secondary" onClick={addKommando} disabled={!selectedKommandoId}>
                <Plus className="size-4" aria-hidden />
                Hinzufügen
              </Button>
            </div>

            {kommandoIds.length === 0 && (
              <p className="text-sm text-muted-foreground">Noch keine Kommandos in der Routine.</p>
            )}

            <ol className="space-y-2" data-testid="routine-aktionen-liste">
              {kommandoIds.map((id, index) => (
                <li
                  key={`${id}-${index}`}
                  className="flex items-center justify-between gap-2 rounded-md border px-3 py-2"
                >
                  <div>
                    <span className="text-xs text-muted-foreground">#{index + 1}</span>{" "}
                    <span className="font-medium">{kommandoLabelMap.get(id) ?? `Unbekannt (${id})`}</span>
                  </div>
                  <div className="flex gap-1">
                    <Button
                      type="button"
                      size="sm"
                      variant="outline"
                      aria-label="Nach oben"
                      disabled={index === 0}
                      onClick={() => move(index, -1)}
                    >
                      <ArrowUp className="size-4" aria-hidden />
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="outline"
                      aria-label="Nach unten"
                      disabled={index === kommandoIds.length - 1}
                      onClick={() => move(index, 1)}
                    >
                      <ArrowDown className="size-4" aria-hidden />
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="outline"
                      className="text-destructive"
                      aria-label="Entfernen"
                      onClick={() => removeAt(index)}
                    >
                      <Trash2 className="size-4" aria-hidden />
                    </Button>
                  </div>
                </li>
              ))}
            </ol>
          </CardContent>
        </Card>

        <div className="flex gap-2">
          <Button type="submit" disabled={activeMutation.isPending}>
            {activeMutation.isPending ? "Speichert…" : "Speichern"}
          </Button>
          <Button type="button" variant="outline" asChild>
            <Link to="/katalog/routinen">Abbrechen</Link>
          </Button>
        </div>
        <ApiErrorAlert error={activeMutation.error} />
      </form>
    </div>
  );
}
