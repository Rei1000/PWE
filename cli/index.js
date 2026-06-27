#!/usr/bin/env node

import fs from "fs";
import path from "path";
import readline from "readline";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const PROJECT_ROOT = path.join(__dirname, "..");
const CONTEXT_DIR = path.join(PROJECT_ROOT, ".goldstandard");
const CONTEXT_FILE = path.join(CONTEXT_DIR, "context.txt");

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function ask(question) {
  return new Promise((resolve) => {
    rl.question(question, resolve);
  });
}

function loadPromptFiles(relativeDir) {
  const targetDir = path.join(PROJECT_ROOT, relativeDir);

  if (!fs.existsSync(targetDir)) {
    return { error: `Ordner nicht gefunden: ${relativeDir}` };
  }

  const files = fs
    .readdirSync(targetDir)
    .filter((entry) => entry.endsWith(".md"))
    .sort();

  if (files.length === 0) {
    return { error: `Keine Prompt-Dateien gefunden in: ${relativeDir}` };
  }

  return { files, targetDir };
}

function readSavedContext() {
  if (!fs.existsSync(CONTEXT_FILE)) {
    return { error: "Keine gespeicherte Kontextdatei gefunden (.goldstandard/context.txt)." };
  }

  const content = fs.readFileSync(CONTEXT_FILE, "utf8").trim();
  if (!content) {
    return { error: "Die gespeicherte Kontextdatei ist leer. Bitte speichere den Handover-Kontext erneut." };
  }

  return { content };
}

async function captureHandoverContext() {
  console.log("\n🧾 GPT-Handover-Kontext speichern\n");
  console.log("Bitte füge den vollständigen PROJEKTKONTEXT aus prompts/gpt/05-gpt-agent-handover.md ein.");
  console.log("Beende die Eingabe mit einer einzelnen Zeile: END\n");

  const lines = [];
  while (true) {
    const line = await ask("");
    if (line.trim() === "END") {
      break;
    }
    lines.push(line);
  }

  const content = lines.join("\n").trim();
  if (!content) {
    console.log("\nKein Kontext gespeichert: Die Eingabe war leer.\n");
    return;
  }

  fs.mkdirSync(CONTEXT_DIR, { recursive: true });
  fs.writeFileSync(CONTEXT_FILE, `${content}\n`, "utf8");
  console.log(`\nKontext gespeichert unter: ${path.relative(PROJECT_ROOT, CONTEXT_FILE)}\n`);
}

function showSavedContext() {
  console.log("\n📄 Gespeicherter Kontext\n");
  const result = readSavedContext();
  if (result.error) {
    console.log(`${result.error}\n`);
    return;
  }

  console.log(result.content);
  console.log("");
}

async function showPromptList(relativeDir, phaseLabel) {
  const result = loadPromptFiles(relativeDir);
  if (result.error) {
    console.log(`\n${result.error}\n`);
    return;
  }

  const { files, targetDir } = result;

  console.log(`\n${phaseLabel} Prompts:\n`);
  files.forEach((file, index) => {
    console.log(`${index + 1}. ${file}`);
  });
  console.log("");

  const selection = await ask("Bitte wähle eine Prompt-Nummer: ");
  const selectedIndex = Number(selection) - 1;

  if (!Number.isInteger(selectedIndex) || selectedIndex < 0 || selectedIndex >= files.length) {
    console.log("\nUngültige Eingabe.\n");
    return;
  }

  const selectedFile = files[selectedIndex];
  const fullPath = path.join(targetDir, selectedFile);
  const content = fs.readFileSync(fullPath, "utf8");
  const relativePath = path.join(relativeDir, selectedFile).replaceAll("\\", "/");

  console.log(`\nPfad: ${relativePath}\n`);
  console.log(content);
  console.log("");

  if (relativeDir === "prompts/gpt") {
    console.log("Kopiere diesen Prompt in ChatGPT\n");
  } else {
    console.log("Kopiere diesen Prompt in deinen Agenten\n");
  }
}

async function main() {
  console.log("\n🚀 Goldstandard Project Wizard\n");
  console.log("1. GPT-Prompts anzeigen");
  console.log("2. Agent-Prompts anzeigen");
  console.log("3. GPT-Handover-Kontext speichern");
  console.log("4. Gespeicherten Kontext anzeigen");
  console.log("5. Hilfe");
  console.log("6. Beenden\n");

  const answer = await ask("Bitte wähle eine Option: ");

  if (answer === "1") {
    await showPromptList("prompts/gpt", "📘 GPT");
  } else if (answer === "2") {
    const contextState = readSavedContext();
    if (contextState.error) {
      console.log("\n⚠️ Kein gespeicherter Handover-Kontext gefunden. Führe zuerst GPT Prompt 05 aus und speichere den Kontext.\n");
    } else {
      console.log("\n✅ Gespeicherter Handover-Kontext gefunden. Nutze ihn zusammen mit dem Agent-Prompt.\n");
    }
    await showPromptList("prompts/agent", "🤖 Agent");
  } else if (answer === "3") {
    await captureHandoverContext();
  } else if (answer === "4") {
    showSavedContext();
  } else if (answer === "5") {
    console.log("\nℹ️ Hilfe\n");
    console.log("Dieses Tool führt dich durch den Goldstandard-Prozess.\n");
    console.log("GPT = Denken (ChatGPT)");
    console.log("Agent = Umsetzung (Cursor)\n");
  } else if (answer === "6") {
    console.log("\nBis bald.\n");
  } else {
    console.log("\nUngültige Eingabe.\n");
  }
}

main().finally(() => {
  rl.close();
});
