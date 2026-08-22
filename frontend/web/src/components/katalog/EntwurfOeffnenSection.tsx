import { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { loadEntwurfRecents } from "@/lib/entwurfRecents";

export function EntwurfOeffnenSection() {
  const navigate = useNavigate();
  const [entwurfId, setEntwurfId] = useState("");
  const recents = useMemo(() => loadEntwurfRecents(), []);

  const openEntwurf = () => {
    const trimmed = entwurfId.trim();
    if (!trimmed) return;
    navigate(`/katalog/entwuerfe/${trimmed}`);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Entwurf öffnen</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex flex-col gap-2 sm:flex-row">
          <div className="grow space-y-2">
            <Label htmlFor="entwurf-id">Produktdefinitions-ID</Label>
            <Input
              id="entwurf-id"
              value={entwurfId}
              onChange={(event) => setEntwurfId(event.target.value)}
              placeholder="z. B. pd-…"
            />
          </div>
          <div className="flex items-end">
            <Button type="button" onClick={openEntwurf} disabled={!entwurfId.trim()}>
              Öffnen
            </Button>
          </div>
        </div>
        {recents.length > 0 && (
          <div className="space-y-2">
            <p className="text-sm font-medium">Zuletzt bearbeitet</p>
            <ul className="space-y-2">
              {recents.map((item) => (
                <li key={item.produktdefinition_id}>
                  <Link
                    to={`/katalog/entwuerfe/${item.produktdefinition_id}`}
                    className="block rounded-md border px-3 py-2 text-sm hover:bg-accent"
                  >
                    <span className="font-medium">{item.produktkodierung}</span>
                    <span className="mt-1 block font-mono text-xs text-muted-foreground">
                      {item.produktdefinition_id}
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
