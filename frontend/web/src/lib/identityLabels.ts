export const ROLLE_LABELS: Record<string, string> = {
  administrator: "Administrator",
  qm: "QM",
  abteilungsleiter: "Abteilungsleiter",
  pruefer: "Prüfer",
};

export function rolleLabel(rolle: string): string {
  return ROLLE_LABELS[rolle] ?? rolle;
}
