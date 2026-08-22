export const katalogKommandosKey = ["katalog", "kommandos"] as const;
export const katalogKommandoKey = (id: string) => ["katalog", "kommandos", id] as const;

export const katalogRoutinenKey = ["katalog", "routinen"] as const;
export const katalogRoutineKey = (id: string) => ["katalog", "routinen", id] as const;

export const katalogVorlagenKey = ["katalog", "vorlagen"] as const;
export const katalogVorlageKey = (id: string) => ["katalog", "vorlagen", id] as const;

export const katalogEntwurfKey = (id: string) => ["katalog", "entwuerfe", id] as const;
