import { ArrowDown, ArrowUp, Copy, Pencil, Plus, Trash2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

import type { ProzedurSchrittEntwurfResponse } from "@/adapters/api/schemas/katalog";
import { ApiErrorAlert } from "@/components/ApiErrorAlert";
import { ConfirmDialog } from "@/components/katalog/ConfirmDialog";
import { EntwurfSchrittAutomatisierung } from "@/components/katalog/EntwurfSchrittAutomatisierung";
import { SollvorgabenEditor } from "@/components/katalog/SollvorgabenEditor";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useVorlagenQuery } from "@/hooks/katalog/useVorlagen";
import {
  useEntwurf,
  useEntwurfVeroeffentlichenMutation,
  useSchrittAktualisierenMutation,
  useSchrittAnlegenMutation,
  useSchrittLoeschenMutation,
  useSchritteReihenfolgeMutation,
} from "@/hooks/katalog/useEntwurf";
import { findDuplicateFeldnamen, moveSchrittIds, rowsFromSollvorgaben, sollvorgabenFromRows, suggestSchrittId } from "@/lib/entwurfEditor";
import { rememberEntwurfRecent } from "@/lib/entwurfRecents";

type EditorMode = "create" | "edit";

export function EntwurfEditorPage() {
  const { produktdefinitionId = "" } = useParams();
  const { data: entwurf, isLoading, error, refetch } = useEntwurf(produktdefinitionId);
  const { data: vorlagen = [] } = useVorlagenQuery();

  const [selectedSchrittId, setSelectedSchrittId] = useState<string | null>(null);
  const [mode, setMode] = useState<EditorMode | null>(null);
  const [deleteSchrittId, setDeleteSchrittId] = useState<string | null>(null);
  const [publishOpen, setPublishOpen] = useState(false);
  const [publishedVersionId, setPublishedVersionId] = useState<string | null>(null);

  const [schrittIdInput, setSchrittIdInput] = useState(() => suggestSchrittId());
  const [vorlageId, setVorlageId] = useState("");
  const [istPflicht, setIstPflicht] = useState(true);
  const [sollvorgaben, setSollvorgaben] = useState<Record<string, { min?: number; max?: number }>>({});
  const [formError, setFormError] = useState<string | null>(null);

  const schrittAnlegenMutation = useSchrittAnlegenMutation(produktdefinitionId);
  const schrittLoeschenMutation = useSchrittLoeschenMutation(produktdefinitionId);
  const reorderMutation = useSchritteReihenfolgeMutation(produktdefinitionId);
  const publishMutation = useEntwurfVeroeffentlichenMutation(produktdefinitionId);
  const updateMutation = useSchrittAktualisierenMutation(
    produktdefinitionId,
    selectedSchrittId ?? "",
  );

  const vorlageLabelMap = useMemo(
    () => new Map(vorlagen.map((v) => [v.vorlage_id, v.bezeichnung])),
    [vorlagen],
  );

  const schritte = useMemo(
    () => [...(entwurf?.prozedur_schritte ?? [])].sort((a, b) => a.reihenfolge - b.reihenfolge),
    [entwurf?.prozedur_schritte],
  );

  const selectedSchritt: ProzedurSchrittEntwurfResponse | null =
    schritte.find((s) => s.schritt_id === selectedSchrittId) ?? null;

  useEffect(() => {
    if (entwurf) {
      rememberEntwurfRecent({
        produktdefinition_id: entwurf.produktdefinition_id,
        produktkodierung: entwurf.produktkodierung,
      });
    }
  }, [entwurf]);

  const resetCreateForm = () => {
    setSchrittIdInput(suggestSchrittId());
    setVorlageId(vorlagen[0]?.vorlage_id ?? "");
    setIstPflicht(true);
    setSollvorgaben({});
    setFormError(null);
  };

  const loadEditForm = (schritt: ProzedurSchrittEntwurfResponse) => {
    setVorlageId(schritt.vorlage_id);
    setIstPflicht(schritt.ist_pflicht);
    setSollvorgaben(sollvorgabenFromRows(rowsFromSollvorgaben(schritt.sollvorgaben)));
    setFormError(null);
  };

  const startCreate = () => {
    setMode("create");
    setSelectedSchrittId(null);
    resetCreateForm();
  };

  const startEdit = (schritt: ProzedurSchrittEntwurfResponse) => {
    setMode("edit");
    setSelectedSchrittId(schritt.schritt_id);
    loadEditForm(schritt);
  };

  const submitSchritt = async () => {
    setFormError(null);
    const duplicates = findDuplicateFeldnamen(rowsFromSollvorgaben(sollvorgaben));
    if (duplicates.length > 0) {
      setFormError(`Doppelte Feldnamen: ${duplicates.join(", ")}`);
      return;
    }
    if (!vorlageId) {
      setFormError("Bitte eine Vorlage wählen.");
      return;
    }

    if (mode === "create") {
      if (!schrittIdInput.trim()) {
        setFormError("Schritt-ID ist erforderlich.");
        return;
      }
      await schrittAnlegenMutation.mutateAsync({
        schritt_id: schrittIdInput.trim(),
        vorlage_id: vorlageId,
        ist_pflicht: istPflicht,
        sollvorgaben,
      });
      setMode(null);
      setSelectedSchrittId(schrittIdInput.trim());
      return;
    }

    if (mode === "edit" && selectedSchrittId) {
      await updateMutation.mutateAsync({
        vorlage_id: vorlageId,
        ist_pflicht: istPflicht,
        sollvorgaben,
      });
    }
  };

  const moveSchritt = async (index: number, direction: -1 | 1) => {
    const ids = schritte.map((s) => s.schritt_id);
    const next = moveSchrittIds(ids, index, direction);
    if (next === ids) return;
    await reorderMutation.mutateAsync({ schritt_ids: next });
  };

  const copyId = async () => {
    if (!entwurf) return;
    await navigator.clipboard.writeText(entwurf.produktdefinition_id);
  };

  const automationLabel = (schritt: ProzedurSchrittEntwurfResponse) => {
    if (schritt.kommando_id) return `Kommando: ${schritt.kommando_id}`;
    if (schritt.routine_id) return `Routine: ${schritt.routine_id}`;
    return "Keine";
  };

  if (isLoading) {
    return <p className="text-sm text-muted-foreground">Entwurf wird geladen…</p>;
  }

  if (error || !entwurf) {
    return (
      <div className="space-y-4">
        <ApiErrorAlert error={error} />
        <Button type="button" variant="outline" onClick={() => void refetch()}>
          Erneut laden
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Entwurfseditor</h1>
          <p className="mt-1 text-sm text-muted-foreground">Design-Time — keine Run-Time-Ausführung.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button type="button" onClick={startCreate}>
            <Plus className="size-4" aria-hidden />
            Schritt hinzufügen
          </Button>
          <Button type="button" variant="secondary" onClick={() => setPublishOpen(true)}>
            Veröffentlichen
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Entwurf</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 text-sm md:grid-cols-2">
          <div>
            <p className="text-muted-foreground">Produktkodierung (read-only)</p>
            <p className="font-medium">{entwurf.produktkodierung}</p>
          </div>
          <div>
            <p className="text-muted-foreground">Produktdefinitions-ID (read-only)</p>
            <div className="flex items-center gap-2">
              <p className="font-mono text-xs">{entwurf.produktdefinition_id}</p>
              <Button type="button" size="sm" variant="outline" onClick={() => void copyId()}>
                <Copy className="size-4" aria-hidden />
              </Button>
            </div>
          </div>
          {entwurf.sollbestueckung.length > 0 && (
            <div className="md:col-span-2">
              <p className="text-muted-foreground">Sollbestückung (read-only)</p>
              <p>{entwurf.sollbestueckung.join(", ")}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {publishedVersionId && (
        <div className="rounded-md border border-green-600/30 bg-green-600/10 p-4 text-sm" role="status">
          Veröffentlicht — neue Version: <span className="font-mono">{publishedVersionId}</span>
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>ProzedurSchritte</CardTitle>
        </CardHeader>
        <CardContent>
          {schritte.length === 0 ? (
            <p className="text-sm text-muted-foreground">Noch keine Schritte — bitte einen Schritt hinzufügen.</p>
          ) : (
            <ul className="divide-y">
              {schritte.map((schritt, index) => (
                <li key={schritt.schritt_id} className="flex flex-wrap items-center justify-between gap-3 py-3">
                  <div>
                    <p className="font-medium">
                      {schritt.reihenfolge}. {vorlageLabelMap.get(schritt.vorlage_id) ?? schritt.vorlage_id}
                    </p>
                    <p className="font-mono text-xs text-muted-foreground">{schritt.schritt_id}</p>
                    <p className="text-xs text-muted-foreground">
                      {schritt.ist_pflicht ? "Pflicht" : "Optional"} · {automationLabel(schritt)}
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <Button type="button" size="sm" variant="outline" onClick={() => startEdit(schritt)}>
                      <Pencil className="size-4" aria-hidden />
                      Bearbeiten
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="outline"
                      disabled={index === 0 || reorderMutation.isPending}
                      onClick={() => void moveSchritt(index, -1)}
                    >
                      <ArrowUp className="size-4" aria-hidden />
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="outline"
                      disabled={index === schritte.length - 1 || reorderMutation.isPending}
                      onClick={() => void moveSchritt(index, 1)}
                    >
                      <ArrowDown className="size-4" aria-hidden />
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="outline"
                      className="text-destructive"
                      onClick={() => setDeleteSchrittId(schritt.schritt_id)}
                    >
                      <Trash2 className="size-4" aria-hidden />
                    </Button>
                  </div>
                </li>
              ))}
            </ul>
          )}
          <ApiErrorAlert error={reorderMutation.error} />
        </CardContent>
      </Card>

      {mode && (
        <Card>
          <CardHeader>
            <CardTitle>{mode === "create" ? "Schritt anlegen" : "Schritt bearbeiten"}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {mode === "create" && (
              <div className="space-y-2">
                <Label htmlFor="schritt-id">Schritt-ID</Label>
                <Input
                  id="schritt-id"
                  value={schrittIdInput}
                  onChange={(event) => setSchrittIdInput(event.target.value)}
                />
              </div>
            )}
            {mode === "edit" && selectedSchritt && (
              <p className="text-sm text-muted-foreground">
                Schritt-ID (nicht änderbar): <span className="font-mono">{selectedSchritt.schritt_id}</span>
              </p>
            )}
            <div className="space-y-2">
              <Label htmlFor="vorlage-id">Vorlage</Label>
              <select
                id="vorlage-id"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={vorlageId}
                onChange={(event) => setVorlageId(event.target.value)}
              >
                <option value="">— auswählen —</option>
                {vorlagen.map((v) => (
                  <option key={v.vorlage_id} value={v.vorlage_id}>
                    {v.bezeichnung}
                  </option>
                ))}
                {vorlageId && !vorlagen.some((v) => v.vorlage_id === vorlageId) && (
                  <option value={vorlageId}>Unbekannte Vorlage ({vorlageId})</option>
                )}
              </select>
              <Link to="/katalog/vorlagen" className="text-xs text-muted-foreground underline">
                Vorlagen verwalten
              </Link>
            </div>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={istPflicht}
                onChange={(event) => setIstPflicht(event.target.checked)}
              />
              Pflichtschritt
            </label>
            <SollvorgabenEditor
              key={mode === "edit" ? selectedSchrittId ?? "edit" : "create"}
              value={sollvorgaben}
              onChange={setSollvorgaben}
            />
            {formError && <p className="text-sm text-destructive">{formError}</p>}
            <div className="flex gap-2">
              <Button
                type="button"
                disabled={schrittAnlegenMutation.isPending || updateMutation.isPending}
                onClick={() => void submitSchritt()}
              >
                Speichern
              </Button>
              <Button type="button" variant="outline" onClick={() => setMode(null)}>
                Abbrechen
              </Button>
            </div>
            <ApiErrorAlert error={schrittAnlegenMutation.error ?? updateMutation.error} />
          </CardContent>
        </Card>
      )}

      {mode === "edit" && selectedSchritt && (
        <EntwurfSchrittAutomatisierung produktdefinitionId={produktdefinitionId} schritt={selectedSchritt} />
      )}

      <ConfirmDialog
        open={deleteSchrittId !== null}
        title="Schritt löschen?"
        description="Der Schritt wird dauerhaft aus dem Entwurf entfernt."
        onCancel={() => setDeleteSchrittId(null)}
        onConfirm={async () => {
          if (!deleteSchrittId) return;
          await schrittLoeschenMutation.mutateAsync(deleteSchrittId);
          if (selectedSchrittId === deleteSchrittId) {
            setSelectedSchrittId(null);
            setMode(null);
          }
          setDeleteSchrittId(null);
        }}
        pending={schrittLoeschenMutation.isPending}
      />

      <ConfirmDialog
        open={publishOpen}
        title="Entwurf veröffentlichen?"
        description="Es wird eine neue unveränderliche Produktdefinitionsversion erzeugt. Der Entwurf bleibt weiterhin bearbeitbar."
        confirmLabel="Veröffentlichen"
        onCancel={() => setPublishOpen(false)}
        onConfirm={async () => {
          const version = await publishMutation.mutateAsync();
          setPublishedVersionId(version.version_id);
          setPublishOpen(false);
        }}
        pending={publishMutation.isPending}
      />
      <ApiErrorAlert error={publishMutation.error} />
    </div>
  );
}
