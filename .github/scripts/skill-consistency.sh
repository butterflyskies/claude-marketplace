#!/usr/bin/env bash
# skill-consistency — (relationAll loadsDesignPrinciples PrincipleBoundSkill)
#
# Every skill declares a category in its frontmatter. Skills whose category is
# principle-bound (design, development, code-review, pipeline) must contain the
# canonical principle-loading block.
#
# HONESTY DISCLAIMER: this is a presence-of-incantation lint, not a verified
# load. It proves the instruction exists in the skill text — not that a construct
# executed it. The runtime phantom-set guard (asserting the `principle` tag set
# is non-empty in collective-conscious) lives in the loading block itself and in
# the wheel's periodic sweep; CI has no CC access.
set -uo pipefail

ONTOLOGY_FILE="plugins/SKILL-CATEGORIES.md"
LOADING_MARKER='bsky:load-design-principles'
fail=0

# The ontology lives in SKILL-CATEGORIES.md; this script parses it rather than
# carrying a copy. Table rows look like: | category | yes/no | meaning |
ALL_CATEGORIES=$(awk -F'|' '/^\|/ && $2 !~ /Category|----/ {gsub(/ /,"",$2); print $2}' "$ONTOLOGY_FILE")
PRINCIPLE_BOUND_CATEGORIES=$(awk -F'|' '/^\|/ && $2 !~ /Category|----/ {gsub(/ /,"",$2); gsub(/ /,"",$3); if ($3=="yes") print $2}' "$ONTOLOGY_FILE")

if [ -z "$ALL_CATEGORIES" ]; then
  echo "FAIL: could not parse any categories from $ONTOLOGY_FILE — ontology gone phantom"
  exit 1
fi

for skill_file in plugins/*/skills/*/SKILL.md; do
  category=$(awk '/^---$/{fence++; next} fence==1 && /^category:/{sub(/^category:[[:space:]]*/, ""); print; exit}' "$skill_file")

  if [ -z "$category" ]; then
    echo "FAIL: $skill_file has no category in frontmatter — every skill must classify itself"
    fail=1
    continue
  fi

  if ! printf '%s\n' $ALL_CATEGORIES | grep -qx "$category"; then
    echo "FAIL: $skill_file declares unknown category '$category' — add it to $ONTOLOGY_FILE first"
    fail=1
    continue
  fi

  case " $(echo $PRINCIPLE_BOUND_CATEGORIES) " in
    *" $category "*)
      if grep -qF "$LOADING_MARKER" "$skill_file"; then
        echo "ok:   $skill_file (category: $category, loads principles)"
      else
        echo "FAIL: $skill_file is principle-bound (category: $category) but lacks the principle-loading block"
        fail=1
      fi
      ;;
    *)
      echo "ok:   $skill_file (category: $category, not principle-bound)"
      ;;
  esac
done

# Reverse direction: every declared category must be used by at least one
# skill — orphan entries accreting in the ontology are silent rot.
for declared in $ALL_CATEGORIES; do
  if ! grep -rql "^category: $declared$" plugins/*/skills/*/SKILL.md; then
    echo "FAIL: category '$declared' is declared in $ONTOLOGY_FILE but used by no skill — remove it or use it"
    fail=1
  fi
done

if [ "$fail" -eq 0 ]; then
  echo ""
  echo "PASS: all principle-bound skills carry the loading block."
  echo "(Lint checks the text, not the behavior.)"
else
  echo ""
  echo "FAIL: see above. Principle-bound categories: $PRINCIPLE_BOUND_CATEGORIES"
  echo "The canonical loading block instructs: list scope \"shared\", read every memory whose tags include \`principle\`."
fi
exit "$fail"
