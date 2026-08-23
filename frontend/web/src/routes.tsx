import { Navigate } from "react-router-dom";

import { AppLayout } from "@/components/layout/AppLayout";
import { KatalogLayout } from "@/components/layout/KatalogLayout";
import { VerwaltungLayout } from "@/components/layout/VerwaltungLayout";
import { RequireAuth, RequireIdentityAccess, RequireNoForceChange } from "@/hooks/useAuth";
import { AbschlussPage } from "@/pages/AbschlussPage";
import { HealthPage } from "@/pages/HealthPage";
import { LoginPage } from "@/pages/LoginPage";
import { PasswortAendernPage } from "@/pages/PasswortAendernPage";
import { EntwurfEditorPage } from "@/pages/katalog/EntwurfEditorPage";
import { EntwurfNeuPage } from "@/pages/katalog/EntwurfNeuPage";
import { KatalogHubPage } from "@/pages/katalog/KatalogHubPage";
import { KommandosPage } from "@/pages/katalog/KommandosPage";
import { RoutineEditorPage } from "@/pages/katalog/RoutineEditorPage";
import { RoutinenPage } from "@/pages/katalog/RoutinenPage";
import { VorlagenPage } from "@/pages/katalog/VorlagenPage";
import { BenutzerDetailPage } from "@/pages/identity/BenutzerDetailPage";
import { BenutzerPage } from "@/pages/identity/BenutzerPage";
import { EinweisungenPage } from "@/pages/identity/EinweisungenPage";
import { ProfilePage } from "@/pages/identity/ProfilePage";
import { PrueflaufPage } from "@/pages/PrueflaufPage";
import { StartPage } from "@/pages/StartPage";

export const routes = [
  { path: "/login", element: <LoginPage /> },
  {
    path: "/",
    element: <RequireAuth />,
    children: [
      { path: "passwort-aendern", element: <PasswortAendernPage /> },
      {
        element: <RequireNoForceChange />,
        children: [
          {
            element: <AppLayout />,
            children: [
              { index: true, element: <StartPage /> },
              { path: "health", element: <HealthPage /> },
              { path: "prueflaeufe/:prueflaufId", element: <PrueflaufPage /> },
              { path: "prueflaeufe/:prueflaufId/abschluss", element: <AbschlussPage /> },
              {
                path: "katalog",
                element: <KatalogLayout />,
                children: [
                  { index: true, element: <KatalogHubPage /> },
                  { path: "kommandos", element: <KommandosPage /> },
                  { path: "routinen", element: <RoutinenPage /> },
                  { path: "routinen/neu", element: <RoutineEditorPage /> },
                  { path: "routinen/:routineId", element: <RoutineEditorPage /> },
                  { path: "vorlagen", element: <VorlagenPage /> },
                  { path: "entwuerfe/neu", element: <EntwurfNeuPage /> },
                  { path: "entwuerfe/:produktdefinitionId", element: <EntwurfEditorPage /> },
                ],
              },
              {
                path: "verwaltung",
                element: <RequireIdentityAccess />,
                children: [
                  {
                    element: <VerwaltungLayout />,
                    children: [
                      { index: true, element: <Navigate to="benutzer" replace /> },
                      { path: "benutzer", element: <BenutzerPage /> },
                      { path: "benutzer/:benutzerId", element: <BenutzerDetailPage /> },
                      { path: "profile", element: <ProfilePage /> },
                      { path: "einweisungen", element: <EinweisungenPage /> },
                    ],
                  },
                ],
              },
              { path: "*", element: <Navigate to="/" replace /> },
            ],
          },
        ],
      },
    ],
  },
];
