import { AlertCircle } from "lucide-react";

import { katalogErrorMessage } from "@/lib/katalogErrors";
import { prueflaufErrorMessage } from "@/lib/prueflaufErrors";

type ApiErrorAlertProps = {
  error: unknown;
};

export function ApiErrorAlert({ error }: ApiErrorAlertProps) {
  if (!error) return null;

  const message =
    prueflaufErrorMessage(error) ??
    katalogErrorMessage(error);

  return (
    <div
      className="flex gap-2 rounded-md border border-destructive/30 bg-destructive/5 p-3 text-sm text-destructive"
      role="alert"
    >
      <AlertCircle className="mt-0.5 size-4 shrink-0" aria-hidden />
      <div>
        <p>{message}</p>
      </div>
    </div>
  );
}
