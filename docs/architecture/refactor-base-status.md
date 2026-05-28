# Refactor Base Status

> Generado: 2026-04-28  
> Rama de trabajo: `codex/prepare-structure-for-refactor-without-changes`

## Situación previa

| Elemento | Valor |
|---|---|
| Rama de refactor (remota) | `origin/codex/prepare-structure-for-refactor-without-changes` |
| Base de esa rama | `cbc5b07` (tip de `main`) |
| Commits únicos en esa rama | 1 (`e852d80` — chore: crear estructura base segura para refactor) |
| Commits en `docs/project-readme` que no estaban | 15 (desde `c1d6fef` hasta `7bf6c74`) |

La rama `codex/prepare-structure-for-refactor-without-changes` estaba **desalineada**: fue creada sobre `main`
ignorando los 15 commits funcionales y de refactor de `docs/project-readme`.
Todo lo que el único commit del codex añadía (`app_core/` vacío, `tests/__init__.py`, `.gitignore`)
ya estaba presente en `docs/project-readme` en versión más completa.

## Acción realizada

Se recreó la rama localmente sobre el tip de `docs/project-readme`:

```
git checkout -b codex/prepare-structure-for-refactor-without-changes docs/project-readme
```

No hubo conflictos porque se trata de una creación limpia, no de un rebase.

## Estado actual (post-alineación)

| Elemento | Valor |
|---|---|
| Rama local | `codex/prepare-structure-for-refactor-without-changes` |
| Base | `7bf6c74` (tip de `docs/project-readme`) |
| Alineada | ✓ Sí |
| Conflictos | Ninguno |

## Archivos de Fase 0 preservados

Todos los 9 archivos originales del commit `e852d80` están presentes en la nueva base
(en versión igual o más completa que la del commit de codex):

| Archivo | Estado |
|---|---|
| `.gitignore` | ✓ presente (versión más completa) |
| `app_core/__init__.py` | ✓ presente |
| `app_core/db/__init__.py` | ✓ presente |
| `app_core/integrations/__init__.py` | ✓ presente |
| `app_core/public_booking/__init__.py` | ✓ presente |
| `app_core/security/__init__.py` | ✓ presente |
| `app_core/services/__init__.py` | ✓ presente |
| `docs/architecture/current-structure.md` | ✓ presente (versión expandida) |
| `tests/__init__.py` | ✓ presente |

## Contenido adicional heredado de docs/project-readme

Al rebasarse sobre `docs/project-readme`, la rama ahora incluye también:

- `app_core/db/connection.py` — funciones de conexión DB extraídas de `app.py`
- `app_core/db/safe_queries.py` — helpers de consulta seguros
- `app_core/public_booking/flow.py`, `state.py`, `steps.py` — booking público separado
- `app_core/security/tenant_access.py` — control de acceso por tenant
- `app_core/services/availability_service.py` — servicio de disponibilidad
- `tests/test_smoke_imports.py` — smoke tests de imports
- `docs/architecture/current-structure.md` — descripción detallada de estructura
- `styles/theme.css`, instrucciones de Copilot, README actualizado

## Próximo paso

La rama ya está lista para continuar extracciones de funciones desde `app.py`
hacia los módulos de `app_core/`. La siguiente extracción sugerida es
`app_core/db/safe_queries.py` (funciones `safe_fetch_one`, `safe_fetch_all`, `safe_execute`).

## Nota sobre el remote

La rama `origin/codex/prepare-structure-for-refactor-without-changes` sigue apuntando
al commit `e852d80` (basado en `main`). Para sincronizar el remote es necesario un
`git push --force-with-lease`. **Esto debe hacerse de forma consciente** ya que
sobreescribe el historial del remote de esa rama.
