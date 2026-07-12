import { Navigate } from "react-router-dom";

import { AppLayout } from "@/components/layout/AppLayout";
import { AbschlussPage } from "@/pages/AbschlussPage";
import { HealthPage } from "@/pages/HealthPage";
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
      { path: "*", element: <Navigate to="/" replace /> },
    ],
  },
];
