import { Loader2 } from "lucide-react";
import { useState } from "react";
import { Link, useParams } from "react-router-dom";

import { ApiErrorAlert } from "@/components/ApiErrorAlert";
import { ConfirmDialog } from "@/components/katalog/ConfirmDialog";
import { BenutzerStatusBadge } from "@/components/identity/IdentityStatusBadge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  useAktivierenBenutzerMutation,
  useArchivierenBenutzerMutation,
  useBenutzerDetailQuery,
  useEntsperrenBenutzerMutation,
  useResetBenutzerPasswortMutation,
  useSetBenutzerRollenMutation,
  useSperrenBenutzerMutation,
  useWiederherstellenBenutzerMutation,
} from "@/hooks/identity/useBenutzer";
import {
  useAssignProfilMutation,
  useBenutzerProfileIdsQuery,
  useProfileQuery,
  useRemoveProfilMutation,
} from "@/hooks/identity/useProfile";
import { useCurrentUser } from "@/hooks/useAuth";
import { rolleLabel } from "@/lib/identityLabels";
import {
  ALLE_ROLLEN,
  darfProfilZuordnung,
  istAdministrator,
} from "@/lib/identityRoles";

type ConfirmAction = "sperren" | "archivieren" | "passwort-reset" | null;

export function BenutzerDetailPage() {
  const { benutzerId = "" } = useParams();
  const { data: currentUser } = useCurrentUser();
  const admin = istAdministrator(currentUser);
  const darfProfile = darfProfilZuordnung(currentUser);

  const { data: benutzer, isLoading, error } = useBenutzerDetailQuery(benutzerId);
  const { data: alleProfile = [] } = useProfileQuery();
  const { data: zugewieseneIds = [] } = useBenutzerProfileIdsQuery(benutzerId);

  const aktivierenMutation = useAktivierenBenutzerMutation(benutzerId);
  const sperrenMutation = useSperrenBenutzerMutation(benutzerId);
  const entsperrenMutation = useEntsperrenBenutzerMutation(benutzerId);
  const archivierenMutation = useArchivierenBenutzerMutation(benutzerId);
  const wiederherstellenMutation = useWiederherstellenBenutzerMutation(benutzerId);
  const rollenMutation = useSetBenutzerRollenMutation(benutzerId);
  const passwortMutation = useResetBenutzerPasswortMutation(benutzerId);
  const assignMutation = useAssignProfilMutation(benutzerId);
  const removeMutation = useRemoveProfilMutation(benutzerId);

  const [confirmAction, setConfirmAction] = useState<ConfirmAction>(null);
  const [neuesPasswort, setNeuesPasswort] = useState("");
  const [rollenDraft, setRollenDraft] = useState<string[] | null>(null);
  const [profilZuweisen, setProfilZuweisen] = useState("");

  const archiviert = benutzer?.status === "archiviert";
  const bearbeitbar = admin && !archiviert;

  const toggleRolle = (rolle: string) => {
    const base = rollenDraft ?? benutzer?.rollen ?? [];
    if (base.includes(rolle)) {
      setRollenDraft(base.filter((r) => r !== rolle));
    } else {
      setRollenDraft([...base, rolle]);
    }
  };

  const speichereRollen = async () => {
    if (!rollenDraft?.length) return;
    await rollenMutation.mutateAsync(rollenDraft);
    setRollenDraft(null);
  };

  const zugewieseneProfile = alleProfile.filter((p) => zugewieseneIds.includes(p.profil_id));
  const verfuegbareProfile = alleProfile.filter(
    (p) => p.aktiv && !zugewieseneIds.includes(p.profil_id),
  );

  const handleConfirm = async () => {
    if (confirmAction === "sperren") {
      await sperrenMutation.mutateAsync();
    } else if (confirmAction === "archivieren") {
      await archivierenMutation.mutateAsync();
    } else if (confirmAction === "passwort-reset") {
      await passwortMutation.mutateAsync(neuesPasswort);
      setNeuesPasswort("");
    }
    setConfirmAction(null);
  };

  if (isLoading) {
    return <p className="text-sm text-muted-foreground">Wird geladen…</p>;
  }

  if (error || !benutzer) {
    return <ApiErrorAlert error={error ?? new Error("Benutzer nicht gefunden")} />;
  }

  const aktuelleRollen = rollenDraft ?? benutzer.rollen;

  return (
    <div className="space-y-6">
      <div>
        <Link to="/verwaltung/benutzer" className="text-sm text-muted-foreground hover:underline">
          ← Zurück zur Liste
        </Link>
        <div className="mt-2 flex flex-wrap items-center gap-3">
          <h2 className="text-xl font-semibold">{benutzer.anzeigename}</h2>
          <BenutzerStatusBadge status={benutzer.status} />
          {benutzer.passwortwechsel_erforderlich && (
            <span className="text-xs text-amber-700">Passwortwechsel ausstehend</span>
          )}
        </div>
        <p className="text-sm text-muted-foreground">{benutzer.login}</p>
      </div>

      {bearbeitbar && (
        <Card>
          <CardHeader>
            <CardTitle>Status</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-2">
            {benutzer.status === "neu" && (
              <Button
                size="sm"
                onClick={() => aktivierenMutation.mutate()}
                disabled={aktivierenMutation.isPending}
              >
                Aktivieren
              </Button>
            )}
            {benutzer.status === "aktiv" && (
              <Button size="sm" variant="outline" onClick={() => setConfirmAction("sperren")}>
                Sperren
              </Button>
            )}
            {benutzer.status === "gesperrt" && (
              <Button
                size="sm"
                onClick={() => entsperrenMutation.mutate()}
                disabled={entsperrenMutation.isPending}
              >
                Entsperren
              </Button>
            )}
            {benutzer.status !== "archiviert" && (
              <Button size="sm" variant="outline" onClick={() => setConfirmAction("archivieren")}>
                Archivieren
              </Button>
            )}
            <ApiErrorAlert
              error={
                aktivierenMutation.error ??
                sperrenMutation.error ??
                entsperrenMutation.error ??
                archivierenMutation.error
              }
            />
          </CardContent>
        </Card>
      )}

      {admin && benutzer.status === "archiviert" && (
        <Card>
          <CardHeader>
            <CardTitle>Wiederherstellen</CardTitle>
          </CardHeader>
          <CardContent>
            <Button
              size="sm"
              onClick={() => wiederherstellenMutation.mutate()}
              disabled={wiederherstellenMutation.isPending}
            >
              Wiederherstellen
            </Button>
            <ApiErrorAlert error={wiederherstellenMutation.error} />
          </CardContent>
        </Card>
      )}

      {bearbeitbar && (
        <Card>
          <CardHeader>
            <CardTitle>Rollen</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-3">
              {ALLE_ROLLEN.map((rolle) => (
                <label key={rolle} className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={aktuelleRollen.includes(rolle)}
                    onChange={() => toggleRolle(rolle)}
                  />
                  {rolleLabel(rolle)}
                </label>
              ))}
            </div>
            <Button
              size="sm"
              onClick={speichereRollen}
              disabled={!rollenDraft || rollenMutation.isPending}
            >
              {rollenMutation.isPending ? <Loader2 className="size-4 animate-spin" /> : "Rollen speichern"}
            </Button>
            <ApiErrorAlert error={rollenMutation.error} />
          </CardContent>
        </Card>
      )}

      {!bearbeitbar && (
        <Card>
          <CardHeader>
            <CardTitle>Rollen</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm">{benutzer.rollen.map(rolleLabel).join(", ")}</p>
          </CardContent>
        </Card>
      )}

      {bearbeitbar && (
        <Card>
          <CardHeader>
            <CardTitle>Passwort</CardTitle>
            <CardDescription>Setzt ein neues Passwort und erzwingt Passwortwechsel beim Login.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="space-y-2">
              <Label htmlFor="reset-passwort">Neues Passwort</Label>
              <Input
                id="reset-passwort"
                type="password"
                value={neuesPasswort}
                onChange={(e) => setNeuesPasswort(e.target.value)}
              />
            </div>
            <Button
              size="sm"
              variant="outline"
              disabled={!neuesPasswort}
              onClick={() => setConfirmAction("passwort-reset")}
            >
              Passwort zurücksetzen
            </Button>
          </CardContent>
        </Card>
      )}

      {darfProfile && !archiviert && (
        <Card>
          <CardHeader>
            <CardTitle>Berechtigungsprofile</CardTitle>
            <CardDescription>
              Zugewiesene Profile in dieser Sitzung. Bereits bestehende Zuordnungen ohne Read-API
              werden nach Zuweisung oder Entfernung aktualisiert.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {zugewieseneProfile.length === 0 ? (
              <p className="text-sm text-muted-foreground">Keine Profile zugewiesen.</p>
            ) : (
              <ul className="divide-y">
                {zugewieseneProfile.map((p) => (
                  <li key={p.profil_id} className="flex items-center justify-between py-2">
                    <div>
                      <p className="font-medium">{p.bezeichnung}</p>
                      <p className="text-xs text-muted-foreground font-mono">{p.profil_id}</p>
                    </div>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => removeMutation.mutate(p.profil_id)}
                      disabled={removeMutation.isPending}
                    >
                      Entfernen
                    </Button>
                  </li>
                ))}
              </ul>
            )}
            <div className="flex flex-wrap items-end gap-2">
              <div className="space-y-1">
                <Label htmlFor="profil-zuweisen">Profil zuweisen</Label>
                <select
                  id="profil-zuweisen"
                  className="flex h-9 w-full min-w-[200px] rounded-md border border-input bg-background px-3 text-sm"
                  value={profilZuweisen}
                  onChange={(e) => setProfilZuweisen(e.target.value)}
                >
                  <option value="">— Profil wählen —</option>
                  {verfuegbareProfile.map((p) => (
                    <option key={p.profil_id} value={p.profil_id}>
                      {p.bezeichnung}
                    </option>
                  ))}
                </select>
              </div>
              <Button
                size="sm"
                disabled={!profilZuweisen || assignMutation.isPending}
                onClick={async () => {
                  await assignMutation.mutateAsync(profilZuweisen);
                  setProfilZuweisen("");
                }}
              >
                Zuweisen
              </Button>
            </div>
            <ApiErrorAlert error={assignMutation.error ?? removeMutation.error} />
          </CardContent>
        </Card>
      )}

      <ConfirmDialog
        open={confirmAction === "sperren"}
        title="Benutzer sperren"
        description={`„${benutzer.anzeigename}" wird gesperrt und kann sich nicht mehr anmelden.`}
        confirmLabel="Sperren"
        onConfirm={handleConfirm}
        onCancel={() => setConfirmAction(null)}
        pending={sperrenMutation.isPending}
      />
      <ConfirmDialog
        open={confirmAction === "archivieren"}
        title="Benutzer archivieren"
        description={`„${benutzer.anzeigename}" wird archiviert und ist nicht mehr bearbeitbar.`}
        confirmLabel="Archivieren"
        onConfirm={handleConfirm}
        onCancel={() => setConfirmAction(null)}
        pending={archivierenMutation.isPending}
      />
      <ConfirmDialog
        open={confirmAction === "passwort-reset"}
        title="Passwort zurücksetzen"
        description={`Das Passwort für „${benutzer.anzeigename}" wird ersetzt. Der Benutzer muss beim nächsten Login ein neues Passwort setzen.`}
        confirmLabel="Zurücksetzen"
        onConfirm={handleConfirm}
        onCancel={() => setConfirmAction(null)}
        pending={passwortMutation.isPending}
      />
    </div>
  );
}
