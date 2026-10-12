# Nixdatifier Noctalia Plan

## Ziel

Ein natives, modular aufgebautes Noctalia-Plugin für mehrere Flakes, Systemprofile,
Home Manager, Benutzerpakete und Entwicklungsumgebungen. Die persönliche
`madebycli/nix-config` mit nyx/aether und allen 18 Outputs bleibt vollständig als
eigener Adapter erhalten. `main` enthält die neueste Entwicklung; `master` bleibt
Upstream. Erst ein verifizierter Stable-Release erzeugt eine Versionsbranch.

## Anforderungen

- Linux x86_64/aarch64, native Noctalia API 26+, Nix mit Flakes.
- Klare Zielidentität: Flake, Output-Attribut, Art und Host sind getrennt.
- Mehrere unabhängige Flakes und Nix-Profile, kein Singleton-System-Flake.
- Native Controls und dynamische Palette-Rollen für vollständige Theme-Anbindung.
- Bestehende persönliche Build-/Switch-/Update-/Sync-Sicherheiten erhalten.
- Kein Code-Monolith: Ansichten, Adapter, Prozesse, Cache, Jobs und Werkzeuge getrennt.
- Bestätigte Systemaktionen, sichtbare Terminalprompts, privater Verlauf.
- Lokale Checks, Luau-Kompilierung, Nix-Paketcheck und echter Noctalia-Lint vor Stable.

## Architektur

Verglichene Ansätze: Ein Noctalia-Launcher vor der alten Qt-Anwendung wäre schnell,
behielte aber eine separate UI und den alten großen QML-Kern. Gewählt ist eine
native Luau-Oberfläche vor einem unabhängigen Python-Backend mit JSON-API v1.

Ein Service teilt Zielzustand mit Widget, Shortcut und Panel. Das Panel kombiniert
kleine Ansichts- und Komponentenmodule. Das Backend verwendet ausschließlich
Argumentlisten für dynamische Prozesse. Schreibaktionen werden als geprüfte Pläne
im Terminal gestartet; bestehende Skripte behalten eigene Schutzmechanismen.

Skalierung: Query-Caches verwenden Ziel- und Lock-Identität. Netzwerkfehler werden
nicht als erfolgreiche Checks gecacht. Hintergrundprüfungen betreffen nur das
gewählte Ziel; acht parallele Upstream-Probes sind begrenzt. Große Diff-Ausgaben
werden als begrenzte Ausgabe behandelt. Ein gemeinsamer Mutationslock verhindert
konkurrierende eigene Jobs. Fremde CLI-Aktionen benötigen weiterhin Koordination.

Kosten: keine Cloud, keine kostenpflichtige API, Python-Standardbibliothek und
Noctalias vorhandene UI. Nix-Evaluationen, Downloads und Systembuilds bleiben die
wesentlichen CPU-/Netzwerk-/Speicherkosten. Ein erster Cache-Miss kann teuer sein.

## Dateistruktur

- `nixdatifier-noctalia/`: Manifest, vier Entry-Skripte, `lib/`, `views/`, Übersetzungen.
- `backend/nixdatifier/`: Konfiguration, Adapter, Aktionen, Prozesse, Jobs, Cache,
  Generationen, Flakes, Health, Werkzeuge, CLI.
- `nix/`: NixOS- und Home-Manager-Module.
- `examples/`: Zielkonfiguration und persönliche deklarative Integration.
- `tests/`: Sicherheits-/Verhaltensprüfungen, echte Output-Fixture, UI-Contract-Harness.
- `.ai/`: Route, Index, Architektur, Status, Entscheidungen, Risiken, Aufgaben,
  Quellen, Tests und Graph.

## Umsetzungsschritte

1. Fork, Branches, Registry, persönliche Flake und native API prüfen. Erledigt.
2. Sauberen `main`-Tree mit modularer Implementierung aufbauen. Erledigt.
3. Multi-Target- und persönlichen Adapter mit 18 Outputs testen. Erledigt lokal.
4. Nix-Pakete, Luau und echten Noctalia-Lint über CI prüfen. Siehe `.ai/TESTS.md`.
5. Auf nyx/aether Oberfläche, Themes und echte Aktionen prüfen. Noch erforderlich.
6. Erst danach Stable-Version freigeben und Versionsbranch/Tag erstellen.

## Offene Fragen / UNKLAR:

- UNKLAR: tatsächlich laufender Noctalia-Stand auf nyx/aether, unabhängig vom Repo-Pin.
- UNKLAR: reale Wayland-Darstellung und Verhalten unter Mango, Niri und Hyprland.
- UNKLAR: lokale Hardwaredateien und tatsächliche Benutzer-/Skriptinstallation;
  diese werden weder aus GitHub übernommen noch hier als erfolgreich behauptet.
- UNKLAR: welche optionalen Upstream-Werkzeuge für den ersten Stable-Release noch
  benötigt werden. Keine vollständige Qt-Feature-Parität behaupten.

## Stable-Kriterien

Grüne Checks des exakten `main`-Commits, Tests auf beiden Hosts, Light/Dark/Custom-
Theme- und Skalierungsprüfung, mehr als ein Flake-Ziel, funktionierende persönliche
Profile, beobachtete Authentifizierung und ein kontrollierter Build/Generationentest.
Normale Pushes erzeugen keinen Release. Versionbranch heißt `MAJOR.MINOR.PATCH`;
Release-Tag heißt `vMAJOR.MINOR.PATCH`. Ein vorhandener Versionsbranch wird nicht
überschrieben.
