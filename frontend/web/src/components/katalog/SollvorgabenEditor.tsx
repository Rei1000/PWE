import { Plus, Trash2 } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  findDuplicateFeldnamen,
  rowsFromSollvorgaben,
  sollvorgabenFromRows,
  type SollvorgabeRow,
} from "@/lib/entwurfEditor";

type SollvorgabenEditorProps = {
  value: Record<string, unknown>;
  onChange: (next: Record<string, { min?: number; max?: number }>) => void;
  disabled?: boolean;
};

export function SollvorgabenEditor({ value, onChange, disabled = false }: SollvorgabenEditorProps) {
  const [rows, setRows] = useState<SollvorgabeRow[]>(() => rowsFromSollvorgaben(value));
  const [duplicateError, setDuplicateError] = useState<string | null>(null);

  const sync = (nextRows: SollvorgabeRow[]) => {
    setRows(nextRows);
    const duplicates = findDuplicateFeldnamen(nextRows);
    if (duplicates.length > 0) {
      setDuplicateError(`Doppelte Feldnamen: ${duplicates.join(", ")}`);
      return;
    }
    setDuplicateError(null);
    onChange(sollvorgabenFromRows(nextRows));
  };

  const updateRow = (index: number, patch: Partial<SollvorgabeRow>) => {
    const next = rows.map((row, i) => (i === index ? { ...row, ...patch } : row));
    sync(next);
  };

  const addRow = () => {
    sync([...rows, { feldname: "", min: "", max: "" }]);
  };

  const removeRow = (index: number) => {
    sync(rows.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-3" data-testid="sollvorgaben-editor">
      <div className="flex items-center justify-between gap-2">
        <Label>Sollvorgaben (optional)</Label>
        <Button type="button" size="sm" variant="outline" onClick={addRow} disabled={disabled}>
          <Plus className="size-4" aria-hidden />
          Zeile hinzufügen
        </Button>
      </div>
      {rows.length === 0 && (
        <p className="text-sm text-muted-foreground">Noch keine Sollvorgaben definiert.</p>
      )}
      {rows.map((row, index) => (
        <div key={index} className="grid gap-2 rounded-md border p-3 md:grid-cols-[1fr_1fr_1fr_auto]">
          <div className="space-y-1">
            <Label htmlFor={`feld-${index}`}>Feldname</Label>
            <Input
              id={`feld-${index}`}
              value={row.feldname}
              disabled={disabled}
              onChange={(event) => updateRow(index, { feldname: event.target.value })}
            />
          </div>
          <div className="space-y-1">
            <Label htmlFor={`min-${index}`}>Min (optional)</Label>
            <Input
              id={`min-${index}`}
              type="number"
              value={row.min}
              disabled={disabled}
              onChange={(event) => updateRow(index, { min: event.target.value })}
            />
          </div>
          <div className="space-y-1">
            <Label htmlFor={`max-${index}`}>Max (optional)</Label>
            <Input
              id={`max-${index}`}
              type="number"
              value={row.max}
              disabled={disabled}
              onChange={(event) => updateRow(index, { max: event.target.value })}
            />
          </div>
          <div className="flex items-end">
            <Button
              type="button"
              size="sm"
              variant="outline"
              className="text-destructive"
              disabled={disabled}
              onClick={() => removeRow(index)}
            >
              <Trash2 className="size-4" aria-hidden />
            </Button>
          </div>
        </div>
      ))}
      {duplicateError && <p className="text-sm text-destructive">{duplicateError}</p>}
    </div>
  );
}
