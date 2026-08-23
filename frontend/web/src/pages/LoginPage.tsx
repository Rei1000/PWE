import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { useLocation, useNavigate } from "react-router-dom";
import { z } from "zod";

import { login } from "@/adapters/api/auth";
import { ApiErrorAlert } from "@/components/ApiErrorAlert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ME_QUERY_KEY } from "@/hooks/useAuth";

const schema = z.object({
  login: z.string().min(1, "Login erforderlich"),
  passwort: z.string().min(1, "Passwort erforderlich"),
});

type FormValues = z.infer<typeof schema>;

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const qc = useQueryClient();
  const from = (location.state as { from?: string } | null)?.from ?? "/";

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { login: "admin", passwort: "" },
  });

  const mutation = useMutation({
    mutationFn: (values: FormValues) => login(values.login, values.passwort),
    onSuccess: async (user) => {
      qc.setQueryData(ME_QUERY_KEY, user);
      navigate(from, { replace: true });
    },
  });

  return (
    <div className="mx-auto max-w-sm space-y-6 py-16">
      <div>
        <h1 className="text-xl font-semibold">Anmelden</h1>
        <p className="text-sm text-muted-foreground">PWE — Identity Foundation (Gate 8.1a)</p>
      </div>
      <form
        className="space-y-4"
        onSubmit={form.handleSubmit((v) => mutation.mutate(v))}
        noValidate
      >
        <div className="space-y-2">
          <Label htmlFor="login">Login</Label>
          <Input id="login" autoComplete="username" {...form.register("login")} />
        </div>
        <div className="space-y-2">
          <Label htmlFor="passwort">Passwort</Label>
          <Input
            id="passwort"
            type="password"
            autoComplete="current-password"
            {...form.register("passwort")}
          />
        </div>
        <ApiErrorAlert error={mutation.error} />
        <Button type="submit" disabled={mutation.isPending} className="w-full">
          {mutation.isPending ? "…" : "Anmelden"}
        </Button>
      </form>
    </div>
  );
}
