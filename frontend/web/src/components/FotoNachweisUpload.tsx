import { useEffect, useRef, useState } from "react";
import { Loader2, Upload } from "lucide-react";

import { ApiErrorAlert } from "@/components/ApiErrorAlert";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { useFotoNachweisErfassen } from "@/hooks/useFotoNachweisErfassen";
import { validateFotoDatei } from "@/lib/fotoKonstanten";

type FotoNachweisUploadProps = {
  prueflaufId: string;
  schrittId: string;
};

/**
 * Foto-Upload mit lokaler Vorschau und explizitem Submit (Gate 8.3b).
 */
export function FotoNachweisUpload({ prueflaufId, schrittId }: FotoNachweisUploadProps) {
  const mutation = useFotoNachweisErfassen(prueflaufId, schrittId);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [clientError, setClientError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  function clearSelection() {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setPreviewUrl(null);
    setSelectedFile(null);
    setClientError(null);
    if (inputRef.current) {
      inputRef.current.value = "";
    }
  }

  function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
    }
    setClientError(null);
    mutation.reset();

    if (!file) {
      setSelectedFile(null);
      return;
    }

    const validationError = validateFotoDatei(file);
    if (validationError) {
      setClientError(validationError);
      setSelectedFile(null);
      event.target.value = "";
      return;
    }

    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
  }

  function handleUpload() {
    if (!selectedFile || mutation.isPending) return;
    mutation.mutate(selectedFile, {
      onSuccess: () => {
        clearSelection();
      },
    });
  }

  const pending = mutation.isPending;

  return (
    <div className="space-y-2" data-testid="foto-nachweis-upload">
      <div className="space-y-1">
        <Label htmlFor={`foto-${schrittId}`}>Foto-Nachweis</Label>
        <input
          ref={inputRef}
          id={`foto-${schrittId}`}
          type="file"
          accept="image/jpeg,image/png"
          className="block w-full text-sm file:mr-3 file:rounded-md file:border file:border-input file:bg-background file:px-3 file:py-1 file:text-sm"
          onChange={handleFileChange}
          disabled={pending}
        />
        <p className="text-xs text-muted-foreground">JPEG oder PNG, max. 5 MiB</p>
      </div>

      {previewUrl && (
        <img
          src={previewUrl}
          alt="Vorschau"
          className="max-h-32 max-w-full rounded border object-contain"
          data-testid="foto-upload-vorschau"
        />
      )}

      <Button
        type="button"
        size="sm"
        variant="secondary"
        disabled={!selectedFile || pending}
        aria-busy={pending}
        onClick={handleUpload}
      >
        {pending ? (
          <Loader2 className="size-4 animate-spin" aria-hidden />
        ) : (
          <Upload className="size-4" aria-hidden />
        )}
        {pending ? "Foto wird hochgeladen…" : "Foto hochladen"}
      </Button>

      {clientError && (
        <p className="text-sm text-destructive" role="alert">
          {clientError}
        </p>
      )}
      <ApiErrorAlert error={mutation.error} />
    </div>
  );
}
