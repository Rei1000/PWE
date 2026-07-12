import { AlertCircle } from "lucide-react";

import { ApiError } from "@/adapters/api/client";

type ApiErrorAlertProps = {
  error: unknown;
};

export function ApiErrorAlert({ error }: ApiErrorAlertProps) {
  if (!error) return null;

  const message = error instanceof Error ? error.message : "Unbekannter Fehler";
  const code = error instanceof ApiError ? error.code : undefined;

  return (
    <div
      className="flex gap-2 rounded-md border border-destructive/30 bg-destructive/5 p-3 text-sm text-destructive"
      role="alert"
    >
      <AlertCircle className="mt-0.5 size-4 shrink-0" aria-hidden />
      <div>
        <p>{message}</p>
        {code && <p className="mt-1 font-mono text-xs opacity-80">code: {code}</p>}
      </div>
    </div>
  );
}
