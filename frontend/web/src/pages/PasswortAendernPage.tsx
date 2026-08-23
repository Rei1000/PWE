import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";

import { changePassword } from "@/adapters/api/auth";
import { passwortAendernSchema, type PasswortAendernRequest } from "@/adapters/api/schemas/identity";
import { ApiErrorAlert } from "@/components/ApiErrorAlert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useCurrentUser, useInvalidateSession } from "@/hooks/useAuth";

type PasswortAendernPageProps = {
  erzwungen?: boolean;
};

export function PasswortAendernPage({ erzwungen = false }: PasswortAendernPageProps) {
  const navigate = useNavigate();
  const invalidate = useInvalidateSession();
  const { data: user } = useCurrentUser();
  const forceChange = erzwungen || user?.passwortwechsel_erforderlich;

  const form = useForm<PasswortAendernRequest>({
    resolver: zodResolver(passwortAendernSchema),
    defaultValues: { altes_passwort: "", neues_passwort: "" },
  });

  const mutation = useMutation({
    mutationFn: (values: PasswortAendernRequest) =>
      changePassword(values.altes_passwort, values.neues_passwort),
    onSuccess: () => {
      invalidate();
      navigate("/login", {
        replace: true,
        state: { message: "Passwort geändert. Bitte erneut anmelden." },
      });
    },
  });

  return (
    <div className="mx-auto max-w-sm space-y-6 py-16">
      <div>
        <h1 className="text-xl font-semibold">
          {forceChange ? "Passwort ändern erforderlich" : "Passwort ändern"}
        </h1>
        <p className="text-sm text-muted-foreground">
          {forceChange
            ? "Vor der weiteren Nutzung muss ein neues Passwort gesetzt werden."
            : "Nach der Änderung werden Sie abgemeldet und müssen sich erneut anmelden."}
        </p>
      </div>
      <form
        className="space-y-4"
        onSubmit={form.handleSubmit((v) => mutation.mutate(v))}
        noValidate
      >
        <div className="space-y-2">
          <Label htmlFor="altes_passwort">Aktuelles Passwort</Label>
          <Input
            id="altes_passwort"
            type="password"
            autoComplete="current-password"
            {...form.register("altes_passwort")}
          />
          {form.formState.errors.altes_passwort && (
            <p className="text-sm text-destructive">{form.formState.errors.altes_passwort.message}</p>
          )}
        </div>
        <div className="space-y-2">
          <Label htmlFor="neues_passwort">Neues Passwort</Label>
          <Input
            id="neues_passwort"
            type="password"
            autoComplete="new-password"
            {...form.register("neues_passwort")}
          />
          {form.formState.errors.neues_passwort && (
            <p className="text-sm text-destructive">{form.formState.errors.neues_passwort.message}</p>
          )}
        </div>
        <ApiErrorAlert error={mutation.error} />
        <div className="flex gap-2">
          <Button type="submit" disabled={mutation.isPending} className="flex-1">
            {mutation.isPending ? "…" : "Passwort speichern"}
          </Button>
          {!forceChange && (
            <Button type="button" variant="outline" onClick={() => navigate(-1)}>
              Abbrechen
            </Button>
          )}
        </div>
      </form>
    </div>
  );
}
