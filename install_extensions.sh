#!/usr/bin/env zsh
# install_extensions.sh
# Installiert alle Extensions aus extensions.txt auf dem Mac.
# Nutzung: ./install_extensions.sh [pfad/zu/extensions.txt]

set -euo pipefail

EXTENSIONS_FILE="${1:-extensions.txt}"
FAILED_FILE="failed_extensions.txt"

# ── CLI ermitteln ─────────────────────────────────────────────
if command -v antigravity &>/dev/null; then
  CLI="antigravity"
elif command -v code &>/dev/null; then
  CLI="code"
else
  echo "❌ Weder 'antigravity' noch 'code' gefunden."
  echo "   → VS Code / Antigravity öffnen, Cmd+Shift+P → 'Shell Command: Install command in PATH'"
  exit 1
fi
echo "✅ Verwende CLI: $CLI"

# ── Datei prüfen ──────────────────────────────────────────────
if [[ ! -f "$EXTENSIONS_FILE" ]]; then
  echo "❌ Datei nicht gefunden: $EXTENSIONS_FILE"
  exit 1
fi

# ── Installation ──────────────────────────────────────────────
total=0
success=0
failed=0
: > "$FAILED_FILE"   # leere failed_extensions.txt anlegen

while IFS= read -r ext || [[ -n "$ext" ]]; do
  # Leerzeilen & Kommentare überspringen
  [[ -z "$ext" || "$ext" == \#* ]] && continue
  ((total++))

  echo -n "  Installing $ext ... "
  if $CLI --install-extension "$ext" --force &>/dev/null; then
    echo "✓"
    ((success++))
  else
    echo "✗ FEHLGESCHLAGEN"
    echo "$ext" >> "$FAILED_FILE"
    ((failed++))
  fi
done < "$EXTENSIONS_FILE"

# ── Zusammenfassung ───────────────────────────────────────────
echo ""
echo "═══════════════════════════════════"
echo "  Gesamt:        $total"
echo "  Erfolgreich:   $success"
echo "  Fehlgeschlagen: $failed"
echo "═══════════════════════════════════"

if [[ $failed -gt 0 ]]; then
  echo "⚠️  Fehlgeschlagene Extensions → $FAILED_FILE"
else
  echo "🎉 Alle Extensions erfolgreich installiert!"
  rm -f "$FAILED_FILE"
fi

# ── Verifikation ──────────────────────────────────────────────
echo ""
echo "── Installierte Extensions (Kurzcheck) ──"
installed=$($CLI --list-extensions | wc -l | tr -d ' ')
wanted=$(grep -cv '^\s*$\|^#' "$EXTENSIONS_FILE" || true)
echo "  Gewünscht: $wanted  |  Installiert (gesamt): $installed"
