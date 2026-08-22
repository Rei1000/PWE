import { Navigate } from "react-router-dom";

import { AppLayout } from "@/components/layout/AppLayout";
import { KatalogLayout } from "@/components/layout/KatalogLayout";
import { AbschlussPage } from "@/pages/AbschlussPage";
import { HealthPage } from "@/pages/HealthPage";
import { KatalogHubPage } from "@/pages/katalog/KatalogHubPage";
import { KommandosPage } from "@/pages/katalog/KommandosPage";
import { RoutineEditorPage } from "@/pages/katalog/RoutineEditorPage";
import { RoutinenPage } from "@/pages/katalog/RoutinenPage";
import { VorlagenPage } from "@/pages/katalog/VorlagenPage";
import { PrueflaufPage } from "@/pages/PrueflaufPage";
import { StartPage } from "@/pages/StartPage";

export const routes = [
  {
    path: "/",
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
        ],
      },
      { path: "*", element: <Navigate to="/" replace /> },
    ],
  },
];
