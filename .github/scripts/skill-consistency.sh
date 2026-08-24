#!/usr/bin/env bash
# skill-consistency — (relationAll loadsDesignPrinciples PrincipleBoundSkill)
#
# The category ontology is a tree declared in plugins/SKILL-CATEGORIES.md
# (adjacency list: category, parent, declares). A skill's category is
# principle-bound iff `principle-bound` appears on its path to the root.
#
# DISCLAIMER: this is a presence-of-incantation lint, not a verified load.
# It proves the instruction exists in the skill text — not that a construct
# executed it. The runtime phantom-set guard lives in
# bsky:load-design-principles itself and in the wheel's sweep; CI has no CC
# access.
set -uo pipefail

ONTOLOGY_FILE="plugins/SKILL-CATEGORIES.md"
LOADING_MARKER='bsky:load-design-principles'
BOUND_ANCESTOR='principle-bound'
fail=0

# ---- parse the ontology table: | category | parent | declares | ----------
ontology=$(awk -F'|' '
  /^\|/ {
    c=$2; p=$3; d=$4
    gsub(/^[ \t]+|[ \t]+$/, "", c); gsub(/^[ \t]+|[ \t]+$/, "", p); gsub(/^[ \t]+|[ \t]+$/, "", d)
    if (c == "Category" || c ~ /^-+$/) next
    print c "\t" p "\t" d
  }' "$ONTOLOGY_FILE")

if [ -z "$ontology" ]; then
  echo "FAIL: could not parse any categories from $ONTOLOGY_FILE — ontology gone phantom"
  exit 1
fi

category_exists() { printf '%s\n' "$ontology" | cut -f1 | grep -qx "$1"; }
parent_of()       { printf '%s\n' "$ontology" | awk -F'\t' -v c="$1" '$1==c{print $2}'; }
declares_of()     { printf '%s\n' "$ontology" | awk -F'\t' -v c="$1" '$1==c{print $3}'; }
is_parent()       { printf '%s\n' "$ontology" | cut -f2 | grep -qx "$1"; }

is_bound() {
  # walk ancestry; true iff BOUND_ANCESTOR is on the path to root
  cur="$1"
  depth=0
  while [ -n "$cur" ] && [ "$cur" != "(root)" ] && [ "$depth" -lt 20 ]; do
    [ "$cur" = "$BOUND_ANCESTOR" ] && return 0
    cur=$(parent_of "$cur")
    depth=$((depth + 1))
  done
  return 1
}

# ---- forward direction: every Claude skill declares a valid leaf; bound ⇒ loads
# Codex plugins intentionally use Codex's minimal name/description frontmatter and
# are validated separately. Do not force Claude marketplace category metadata
# into their SKILL.md files.
for plugin_manifest in plugins/*/.claude-plugin/plugin.json; do
  plugin_dir=$(dirname "$(dirname "$plugin_manifest")")
  for skill_file in "$plugin_dir"/skills/*/SKILL.md; do
    [ -f "$skill_file" ] || continue
  category_count=$(awk '/^---$/{fence++; next} fence==1 && /^category:/{n++} END{print n+0}' "$skill_file")
  category=$(awk '/^---$/{fence++; next} fence==1 && /^category:/{sub(/^category:[[:space:]]*/, ""); print; exit}' "$skill_file")

  if [ "$category_count" -gt 1 ]; then
    echo "FAIL: $skill_file declares $category_count categories — exactly one per skill"
    fail=1; continue
  fi
  if [ -z "$category" ]; then
    echo "FAIL: $skill_file has no category in frontmatter — every skill must classify itself"
    fail=1; continue
  fi
  if ! category_exists "$category"; then
    echo "FAIL: $skill_file declares unknown category '$category' — add it to $ONTOLOGY_FILE first"
    fail=1; continue
  fi
  if is_parent "$category"; then
    echo "FAIL: $skill_file declares abstract category '$category' — skills declare leaves only"
    fail=1; continue
  fi

  if is_bound "$category"; then
    if grep -qF "$LOADING_MARKER" "$skill_file"; then
      echo "ok:   $skill_file ($category, principle-bound by ancestry, loads principles)"
    else
      echo "FAIL: $skill_file is principle-bound ($category descends from $BOUND_ANCESTOR) but lacks the $LOADING_MARKER reference"
      fail=1
    fi
  else
    echo "ok:   $skill_file ($category, not principle-bound)"
  fi
  done
done

# ---- reverse direction: the ontology cannot rot -----------------------------
printf '%s\n' "$ontology" | while IFS=$(printf '\t') read -r cat par dec; do
  if [ "$par" = "(root)" ]; then
    continue  # the root is structural
  fi
  if is_parent "$cat"; then
    # abstract node: legitimate iff it declares something of its own
    # (children exist by construction of being a parent)
    if [ -z "$dec" ]; then
      echo "FAIL: abstract category '$cat' declares nothing of its own — no-direct-skills ∧ no-own-declaration"
    fi
  else
    # leaf: needs at least one member skill
    if ! grep -rql "^category: $cat$" plugins/*/skills/*/SKILL.md; then
      echo "FAIL: leaf category '$cat' is declared in $ONTOLOGY_FILE but used by no skill — remove it or use it"
    fi
  fi
done | grep FAIL && fail=1

if [ "$fail" -eq 0 ]; then
  echo ""
  echo "PASS: ontology coherent; all principle-bound skills carry the loading reference."
  echo "(Lint checks the text, not the behavior.)"
else
  echo ""
  echo "FAIL: see above. Ontology: $ONTOLOGY_FILE — boundness is ancestry under '$BOUND_ANCESTOR', never a flag."
fi
exit "$fail"
