import { NavLink } from "react-router-dom";

import { cn } from "@/lib/utils";

const links = [
  { to: "/verwaltung/benutzer", label: "Benutzer" },
  { to: "/verwaltung/profile", label: "Profile" },
  { to: "/verwaltung/einweisungen", label: "Einweisungen" },
] as const;

export function IdentitySubNav() {
  return (
    <nav className="flex flex-wrap gap-2 border-b pb-3" aria-label="Verwaltung">
      {links.map((link) => (
        <NavLink
          key={link.to}
          to={link.to}
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
