import { useMemo, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";

import { ApiErrorAlert } from "@/components/ApiErrorAlert";
import { ConfirmDialog } from "@/components/katalog/ConfirmDialog";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { useKommandosQuery } from "@/hooks/katalog/useKommandos";
import { useRoutinenQuery } from "@/hooks/katalog/useRoutinen";
import { useAutomatisierungZuweisenMutation } from "@/hooks/katalog/useEntwurf";
import type { ProzedurSchrittEntwurfResponse } from "@/adapters/api/schemas/katalog";
import { katalogEntwurfKey } from "@/lib/katalogQueryKeys";

type EntwurfSchrittAutomatisierungProps = {
  produktdefinitionId: string;
  schritt: ProzedurSchrittEntwurfResponse;
};

type PendingAssign = { type: "kommando" | "routine"; id: string };

export function EntwurfSchrittAutomatisierung({
  produktdefinitionId,
  schritt,
}: EntwurfSchrittAutomatisierungProps) {
  const { data: kommandos = [] } = useKommandosQuery();
  const { data: routinen = [] } = useRoutinenQuery();
  const queryClient = useQueryClient();
  const mutation = useAutomatisierungZuweisenMutation(produktdefinitionId, schritt.schritt_id);
  const [selectedKommandoId, setSelectedKommandoId] = useState("");
  const [selectedRoutineId, setSelectedRoutineId] = useState("");
  const [pendingAssign, setPendingAssign] = useState<PendingAssign | null>(null);
  const [switchError, setSwitchError] = useState<unknown>(null);

  const kommandoLabel = useMemo(() => {
    if (!schritt.kommando_id) return null;
    return kommandos.find((k) => k.kommando_id === schritt.kommando_id)?.bezeichnung ?? schritt.kommando_id;
  }, [kommandos, schritt.kommando_id]);

  const routineLabel = useMemo(() => {
    if (!schritt.routine_id) return null;
    return routinen.find((r) => r.routine_id === schritt.routine_id)?.bezeichnung ?? schritt.routine_id;
  }, [routinen, schritt.routine_id]);

  const hasAutomation = Boolean(schritt.kommando_id || schritt.routine_id);

  const removeAutomation = async () => {
    setSwitchError(null);
    await mutation.mutateAsync({ kommando_id: null, routine_id: null });
    setSelectedKommandoId("");
    setSelectedRoutineId("");
  };

  const assignKommando = async (kommandoId: string) => {
    setSwitchError(null);
    await mutation.mutateAsync({ kommando_id: kommandoId });
    setSelectedKommandoId("");
  };

  const assignRoutine = async (routineId: string) => {
    setSwitchError(null);
    await mutation.mutateAsync({ routine_id: routineId });
    setSelectedRoutineId("");
  };

  const requestAssign = (next: PendingAssign) => {
    if (hasAutomation) {
      setPendingAssign(next);
      return;
    }
    void (next.type === "kommando" ? assignKommando(next.id) : assignRoutine(next.id));
  };

  const confirmSwitch = async () => {
    if (!pendingAssign) return;
    setSwitchError(null);
    try {
      await mutation.mutateAsync({ kommando_id: null, routine_id: null });
    } catch (error) {
      setSwitchError(error);
      setPendingAssign(null);
      return;
    }
    try {
      if (pendingAssign.type === "kommando") {
        await assignKommando(pendingAssign.id);
      } else {
        await assignRoutine(pendingAssign.id);
      }
    } catch (error) {
      setSwitchError(error);
      await queryClient.invalidateQueries({ queryKey: katalogEntwurfKey(produktdefinitionId) });
    } finally {
      setPendingAssign(null);
    }
  };

  return (
    <div className="space-y-4 rounded-md border p-4" data-testid="entwurf-schritt-automatisierung">
      <div>
        <h3 className="text-sm font-medium">Automatisierung</h3>
        <p className="text-xs text-muted-foreground">
          Kommando oder Routine — Wechsel erfordert zuerst das Entfernen der bestehenden Zuweisung.
        </p>
      </div>

      <div className="text-sm">
        {hasAutomation ? (
          <p>
            Aktuell:{" "}
            {schritt.kommando_id ? (
              <span>Kommando „{kommandoLabel}“</span>
            ) : (
              <span>Routine „{routineLabel}“</span>
            )}
          </p>
        ) : (
          <p className="text-muted-foreground">Keine Automatisierung zugewiesen.</p>
        )}
      </div>

      {hasAutomation && (
        <Button
          type="button"
          size="sm"
          variant="outline"
          disabled={mutation.isPending}
          onClick={() => void removeAutomation()}
        >
          Automatisierung entfernen
        </Button>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="kommando-select">Externes Kommando</Label>
          <div className="flex gap-2">
            <select
              id="kommando-select"
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={selectedKommandoId}
              disabled={mutation.isPending}
              onChange={(event) => setSelectedKommandoId(event.target.value)}
            >
              <option value="">— auswählen —</option>
              {kommandos.map((item) => (
                <option key={item.kommando_id} value={item.kommando_id}>
                  {item.bezeichnung}
                </option>
              ))}
            </select>
            <Button
              type="button"
              size="sm"
              disabled={!selectedKommandoId || mutation.isPending}
              data-testid="assign-kommando"
              onClick={() => requestAssign({ type: "kommando", id: selectedKommandoId })}
            >
              Zuweisen
            </Button>
          </div>
        </div>
        <div className="space-y-2">
          <Label htmlFor="routine-select">Routine</Label>
          <div className="flex gap-2">
            <select
              id="routine-select"
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={selectedRoutineId}
              disabled={mutation.isPending}
              onChange={(event) => setSelectedRoutineId(event.target.value)}
            >
              <option value="">— auswählen —</option>
              {routinen.map((item) => (
                <option key={item.routine_id} value={item.routine_id}>
                  {item.bezeichnung}
                </option>
              ))}
            </select>
            <Button
              type="button"
              size="sm"
              disabled={!selectedRoutineId || mutation.isPending}
              data-testid="assign-routine"
              onClick={() => requestAssign({ type: "routine", id: selectedRoutineId })}
            >
              Zuweisen
            </Button>
          </div>
        </div>
      </div>

      <ApiErrorAlert error={mutation.error} />
      <ApiErrorAlert error={switchError} />

      <ConfirmDialog
        open={pendingAssign !== null}
        title="Automatisierung wechseln?"
        description="Die bestehende Automatisierung wird zuerst entfernt und anschließend die neue zugewiesen."
        confirmLabel="Wechseln"
        onCancel={() => setPendingAssign(null)}
        onConfirm={() => void confirmSwitch()}
        pending={mutation.isPending}
      />
    </div>
  );
}
