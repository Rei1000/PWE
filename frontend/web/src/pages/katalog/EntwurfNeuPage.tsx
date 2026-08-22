import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { z } from "zod";

import { ApiErrorAlert } from "@/components/ApiErrorAlert";
import { EntwurfOeffnenSection } from "@/components/katalog/EntwurfOeffnenSection";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useEntwurfAnlegenMutation } from "@/hooks/katalog/useEntwurf";
import { rememberEntwurfRecent } from "@/lib/entwurfRecents";

const formSchema = z.object({
  produktkodierung: z.string().min(1, "Produktkodierung ist erforderlich"),
});

type FormValues = z.infer<typeof formSchema>;

export function EntwurfNeuPage() {
  const navigate = useNavigate();
  const createMutation = useEntwurfAnlegenMutation();
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: { produktkodierung: "" },
  });

  const onSubmit = form.handleSubmit(async (values) => {
    const entwurf = await createMutation.mutateAsync({
      produktkodierung: values.produktkodierung,
      prozedur_schritte: [],
      sollbestueckung: [],
    });
    rememberEntwurfRecent({
      produktdefinition_id: entwurf.produktdefinition_id,
      produktkodierung: entwurf.produktkodierung,
    });
    navigate(`/katalog/entwuerfe/${entwurf.produktdefinition_id}`);
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Produktdefinitions-Entwürfe</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Design-Time-Editor — Entwürfe werden per ID geöffnet, nicht über eine globale Liste.
        </p>
      </div>

      <EntwurfOeffnenSection />

      <Card>
        <CardHeader>
          <CardTitle>Neuen Entwurf anlegen</CardTitle>
        </CardHeader>
        <CardContent>
          <form className="space-y-4" onSubmit={onSubmit} noValidate>
            <div className="space-y-2">
              <Label htmlFor="produktkodierung">Produktkodierung</Label>
              <Input id="produktkodierung" {...form.register("produktkodierung")} />
              {form.formState.errors.produktkodierung && (
                <p className="text-sm text-destructive">{form.formState.errors.produktkodierung.message}</p>
              )}
            </div>
            <Button type="submit" disabled={createMutation.isPending}>
              {createMutation.isPending ? "Wird angelegt…" : "Entwurf anlegen"}
            </Button>
            <ApiErrorAlert error={createMutation.error} />
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
