import { NavLink } from "react-router-dom";

import { cn } from "@/lib/utils";

const links = [
  { to: "/katalog", label: "Übersicht", end: true },
  { to: "/katalog/kommandos", label: "Kommandos" },
  { to: "/katalog/routinen", label: "Routinen" },
  { to: "/katalog/vorlagen", label: "Vorlagen" },
] as const;

export function KatalogSubNav() {
  return (
    <nav className="flex flex-wrap gap-2 border-b pb-3" aria-label="Katalog-Bereich">
      {links.map((link) => (
        <NavLink
          key={link.to}
          to={link.to}
          end={"end" in link ? link.end : false}
          className={({ isActive }) =>
            cn(
              "rounded-md px-3 py-1.5 text-sm",
              isActive
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:bg-accent hover:text-foreground",
            )
          }
        >
          {link.label}
        </NavLink>
      ))}
    </nav>
  );
}
