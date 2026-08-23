import { cn } from "@/lib/utils";

const STATUS_STYLES: Record<string, string> = {
  neu: "bg-amber-100 text-amber-900 border-amber-200",
  aktiv: "bg-emerald-100 text-emerald-900 border-emerald-200",
  gesperrt: "bg-red-100 text-red-900 border-red-200",
  archiviert: "bg-muted text-muted-foreground border-border",
};

const STATUS_LABELS: Record<string, string> = {
  neu: "Neu",
  aktiv: "Aktiv",
  gesperrt: "Gesperrt",
  archiviert: "Archiviert",
};

type BenutzerStatusBadgeProps = {
  status: string;
  className?: string;
};

export function BenutzerStatusBadge({ status, className }: BenutzerStatusBadgeProps) {
  const normalized = status.toLowerCase();
  return (
    <span
      className={cn(
        "inline-flex rounded-full border px-2 py-0.5 text-xs font-medium",
        STATUS_STYLES[normalized] ?? "bg-muted text-muted-foreground",
        className,
      )}
    >
      {STATUS_LABELS[normalized] ?? status}
    </span>
  );
}

export function ProfilStatusBadge({ aktiv }: { aktiv: boolean }) {
  return (
    <span
      className={cn(
        "inline-flex rounded-full border px-2 py-0.5 text-xs font-medium",
        aktiv
          ? "bg-emerald-100 text-emerald-900 border-emerald-200"
          : "bg-muted text-muted-foreground border-border",
      )}
    >
      {aktiv ? "Aktiv" : "Inaktiv"}
    </span>
  );
}

export function EinweisungStatusBadge({ status }: { status: string }) {
  const normalized = status.toLowerCase();
  const isGueltig = normalized === "gueltig";
  return (
    <span
      className={cn(
        "inline-flex rounded-full border px-2 py-0.5 text-xs font-medium",
        isGueltig
          ? "bg-emerald-100 text-emerald-900 border-emerald-200"
          : "bg-muted text-muted-foreground border-border",
      )}
    >
      {isGueltig ? "Gültig" : normalized === "widerrufen" ? "Widerrufen" : status}
    </span>
  );
}
