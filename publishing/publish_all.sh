#!/usr/bin/env bash
# Publishes every indicator folder next to this script as its own PUBLIC GitHub repository.
# Needs git and the GitHub CLI (gh), signed in once with:  gh auth login
# Safe to run again: repos that already exist on your account are skipped.
# Run:  bash publish_all.sh
set -u
here="$(cd "$(dirname "$0")" && pwd)"
cd "$here"

for tool in git gh; do
  command -v "$tool" >/dev/null 2>&1 || { echo "Missing: $tool. Install git and the GitHub CLI (https://cli.github.com), then run this again."; exit 1; }
done
gh auth status >/dev/null 2>&1 || { echo "Not signed in to GitHub. Run:  gh auth login   then run this again."; exit 1; }

login="$(gh api user --jq .login)"
uid="$(gh api user --jq .id)"
gname="$(git config --global user.name || true)"
gemail="$(git config --global user.email || true)"
echo "Publishing to github.com/$login"

topics="tradingview pine-script pinescript trading-indicators futures nasdaq"
made=0; skipped=0; failed=()

# repos.csv: slug,description (descriptions are quoted)
while IFS= read -r line; do
  slug="${line%%,*}"
  desc="${line#*,}"; desc="${desc#\"}"; desc="${desc%\"}"; desc="${desc//\"\"/\"}"
  [ -d "$here/$slug" ] || { echo "skip  $slug (folder missing)"; skipped=$((skipped+1)); continue; }
  if gh repo view "$login/$slug" >/dev/null 2>&1; then echo "skip  $slug (already on GitHub)"; skipped=$((skipped+1)); continue; fi
  (
    set -e
    cd "$here/$slug"
    if [ ! -d .git ]; then
      git init -q
      [ -n "$gname" ]  || git config user.name "$login"
      [ -n "$gemail" ] || git config user.email "$uid+$login@users.noreply.github.com"
      git add -A
      git commit -q -m "Initial commit: $slug (TradingView Pine Script v6)"
      git branch -M main
    fi
    git remote get-url origin >/dev/null 2>&1 && git remote remove origin
    gh repo create "$slug" --public --description "$desc" --source . --remote origin --push
    for t in $topics; do gh repo edit "$login/$slug" --add-topic "$t" >/dev/null 2>&1 || true; done
  ) && { echo "done  $slug  ->  https://github.com/$login/$slug"; made=$((made+1)); } \
    || { echo "FAIL  $slug"; failed+=("$slug"); }
done < <(tail -n +2 "$here/repos.csv" | tr -d '\r')

echo
echo "Created $made, skipped $skipped, failed ${#failed[@]}."
[ ${#failed[@]} -eq 0 ] || { echo "Failed: ${failed[*]}. Fix the message above and run this again; finished repos are skipped."; exit 1; }
