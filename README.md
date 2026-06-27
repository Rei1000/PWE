# Projekt-Template (Goldstandard)

## Start eines neuen Projekts

Dieses Repository ist ein Goldstandard-Template für neue Softwareprojekte.

Der Projektstart erfolgt **geführt** und in zwei Phasen:

1. **GPT-Phase** – Denken, Strukturieren und Definieren  
2. **Agent-Phase** – Umsetzung im Repository (Dokumente, Struktur, Git)

### Verbindliche Reihenfolge

Öffne die Prompts **in der angegebenen Reihenfolge**. Zuerst immer die komplette GPT-Liste, danach die Agent-Liste.

#### Phase 1 – GPT

Offizieller Startpunkt:

👉 [prompts/gpt/01-gpt-project-start.md](prompts/gpt/01-gpt-project-start.md)

1. [01 – Project Start](prompts/gpt/01-gpt-project-start.md)  
2. [02 – Project Definition](prompts/gpt/02-gpt-project-definition.md)  
3. [03 – Use Case Definition](prompts/gpt/03-gpt-usecase-definition.md)  
4. [04 – Pflichtenheft Preparation](prompts/gpt/04-gpt-pflichtenheft-prep.md)  

---

#### Phase 2 – Agent

1. [01 – Project Bootstrap](prompts/agent/01-agent-project-bootstrap.md)  
2. [02 – Write Pflichtenheft](prompts/agent/02-agent-write-pflichtenheft.md)  
3. [03 – Architecture Setup](prompts/agent/03-agent-architecture-setup.md)  
4. [04 – Project Structure](prompts/agent/04-agent-project-structure.md)  

### Wichtig

- Nicht direkt mit dem Agent starten
- Nicht direkt mit der Implementierung beginnen
- Erst die GPT-Phase vollständig abschließen
- Danach die strukturierte Übergabe an den Agent

## CLI Wizard (empfohlen)

Du kannst den Goldstandard-Prozess auch über die CLI starten:

```bash
node cli/index.js
```

Die CLI führt dich durch den gleichen Prompt-Flow (GPT → Agent) und hilft bei der strukturierten Übergabe.

### Dokumentation im Repository

- **`docs/`** – dauerhafte Projektdokumentation  
- **`prompts/`** – operative Startprompts (siehe oben)  
- **`meta/`** – Goldstandard-Systemdokumentation (z. B. [Prompt Index](meta/prompt-index.md))  

---

Dieses Projekt basiert auf dem Goldstandard Template.

## Zweck

Dieses Repository dient als neutrale Ausgangsbasis fuer neue Projekte.

## Platzhalter-Hinweis

Die Inhalte in diesem Template sind bewusst generisch und muessen projektspezifisch ergaenzt oder ersetzt werden.
