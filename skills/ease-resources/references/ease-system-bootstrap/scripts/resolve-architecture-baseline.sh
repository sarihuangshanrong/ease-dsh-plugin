#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="."

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root)
      [[ $# -ge 2 ]] || { printf 'missing value for --root\n' >&2; exit 2; }
      PROJECT_ROOT="$2"
      shift 2
      ;;
    --help|-h)
      printf 'Usage: %s [--root PROJECT_ROOT]\n' "$0"
      exit 0
      ;;
    *)
      printf 'unknown argument: %s\n' "$1" >&2
      exit 2
      ;;
  esac
done

[[ -d "$PROJECT_ROOT" ]] || { printf 'project root does not exist: %s\n' "$PROJECT_ROOT" >&2; exit 2; }

has_code=false
has_implementation_evidence=false
has_target=false
has_observed=false

for marker in pom.xml build.gradle build.gradle.kts settings.gradle settings.gradle.kts package.json go.mod Cargo.toml pyproject.toml; do
  if [[ -f "$PROJECT_ROOT/$marker" ]]; then
    has_code=true
    break
  fi
done

if [[ "$has_code" = false ]]; then
  for source_root in src app lib services apps packages cmd; do
    if [[ -d "$PROJECT_ROOT/$source_root" ]] && find "$PROJECT_ROOT/$source_root" -type f \
      \( -name '*.java' -o -name '*.kt' -o -name '*.go' -o -name '*.py' -o -name '*.ts' -o -name '*.tsx' -o -name '*.js' -o -name '*.rs' \) \
      -print -quit 2>/dev/null | grep -q .; then
      has_code=true
      break
    fi
  done
fi

has_implementation_evidence="$has_code"

if [[ "$has_implementation_evidence" = false ]]; then
  for evidence_marker in Dockerfile docker-compose.yml docker-compose.yaml application.yml application.yaml application.properties; do
    if [[ -f "$PROJECT_ROOT/$evidence_marker" ]]; then
      has_implementation_evidence=true
      break
    fi
  done
fi

if [[ "$has_implementation_evidence" = false ]]; then
  for evidence_root in config deploy k8s helm infra terraform tests test; do
    if [[ -d "$PROJECT_ROOT/$evidence_root" ]] && find "$PROJECT_ROOT/$evidence_root" -type f \
      \( -name '*.yaml' -o -name '*.yml' -o -name '*.json' -o -name '*.toml' -o -name '*.tf' -o -name '*.hcl' -o -name '*.xml' -o -name '*.properties' \
         -o -name '*.java' -o -name '*.kt' -o -name '*.go' -o -name '*.py' -o -name '*.ts' -o -name '*.tsx' -o -name '*.js' -o -name '*.rs' \) \
      -print -quit 2>/dev/null | grep -q .; then
      has_implementation_evidence=true
      break
    fi
  done
fi

TARGET_MANIFEST="$PROJECT_ROOT/docs/architecture/target/manifest.json"
if [[ -f "$TARGET_MANIFEST" ]] && grep -Eq '"status"[[:space:]]*:[[:space:]]*"accepted"' "$TARGET_MANIFEST"; then
  has_target=true
fi

has_six_documents() {
  local docs_dir="$1"
  local document
  for legacy_doc in \
    01_SYSTEM_OVERVIEW.md \
    02_CORE_MODULES.md \
    03_API_INTERFACE.md \
    04_DATA_MODEL.md \
    05_CONFIG_MANAGEMENT.md \
    06_UTILS_LIBRARIES.md; do
    document="$docs_dir/$legacy_doc"
    if [[ ! -s "$document" ]]; then
      return 1
    fi
  done
  return 0
}

if has_six_documents "$PROJECT_ROOT/docs/system"; then
  has_observed=true
elif [[ -f "$PROJECT_ROOT/docs/system/00_TOPOLOGY.md" ]]; then
  found_subsystem=false
  complete_subsystems=true
  while IFS= read -r subsystem_metadata; do
    found_subsystem=true
    subsystem_dir="$(dirname "$subsystem_metadata")"
    if ! has_six_documents "$subsystem_dir"; then
      complete_subsystems=false
      break
    fi
  done < <(find "$PROJECT_ROOT/docs/system" -mindepth 2 -maxdepth 2 -name metadata.json -type f -print 2>/dev/null)
  if [[ "$found_subsystem" = true && "$complete_subsystems" = true ]]; then
    has_observed=true
  fi
fi

if [[ "$has_target" = true && "$has_observed" = true ]]; then
  lifecycle_state="hybrid"
  architecture_source="hybrid"
  action="use_observed_and_target"
elif [[ "$has_target" = true ]]; then
  lifecycle_state="target_only"
  architecture_source="target"
  action="use_target"
elif [[ "$has_observed" = true ]]; then
  lifecycle_state="observed_only"
  architecture_source="observed"
  action="use_observed"
elif [[ "$has_implementation_evidence" = true ]]; then
  lifecycle_state="observed_missing"
  architecture_source="none"
  action="generate_observed_baseline"
else
  lifecycle_state="empty"
  architecture_source="none"
  action="bootstrap_required"
fi

printf '{"lifecycle_state":"%s","architecture_source":"%s","action":"%s","has_code":%s,"has_implementation_evidence":%s,"has_target":%s,"has_observed":%s}\n' \
  "$lifecycle_state" "$architecture_source" "$action" "$has_code" "$has_implementation_evidence" "$has_target" "$has_observed"
