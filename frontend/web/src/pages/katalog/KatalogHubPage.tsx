import { Link } from "react-router-dom";
import { ArrowRight, Command, FileEdit, ListOrdered, FileText } from "lucide-react";

import { EntwurfOeffnenSection } from "@/components/katalog/EntwurfOeffnenSection";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const sections = [
  {
    title: "Externe Kommandos",
    description: "Zentrale Gerätekommandos für Automatisierung und Routinen.",
    to: "/katalog/kommandos",
    icon: Command,
  },
  {
    title: "Routinen",
    description: "Geordnete Kommando-Folgen für ProzedurSchritte.",
    to: "/katalog/routinen",
    icon: ListOrdered,
  },
  {
    title: "PrüfschrittVorlagen",
    description: "Bibliothek der Prüfschritt-Vorlagen (Bezeichnung, Beschreibung).",
    to: "/katalog/vorlagen",
    icon: FileText,
  },
  {
    title: "Produktdefinitions-Entwürfe",
    description: "Design-Time-Editor für Schritte, Sollvorgaben, Automatisierung und Veröffentlichung.",
    to: "/katalog/entwuerfe/neu",
    icon: FileEdit,
  },
] as const;

export function KatalogHubPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Katalog-Administration</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Bibliothek und Entwurfseditor für Design-Time-Konfiguration.
        </p>
      </div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {sections.map((section) => (
          <Card key={section.to}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <section.icon className="size-5" aria-hidden />
                {section.title}
              </CardTitle>
              <CardDescription>{section.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <Button asChild variant="secondary" size="sm">
                <Link to={section.to}>
                  Verwalten
                  <ArrowRight className="size-4" aria-hidden />
                </Link>
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
      <EntwurfOeffnenSection />
    </div>
  );
}
