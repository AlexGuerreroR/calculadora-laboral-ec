# Evidencias de la semana 4

## Taller «Tablero, credenciales y riesgos» (4/11/2026)

`taller-credenciales/taller_credenciales_grupo7.json` es el respaldo descargado del taller
(versión final enviada a las 20:26). No contiene claves: el taller solo pide nombres de archivos,
cantidades y textos sin valores secretos.

| Misión | Resultado | Dónde quedó en el proyecto |
|---|---|---|
| 1 · Tablero del proyecto | Tablero Kanban con los 6 entregables de la semana 4 como issues (#66–#71) | https://github.com/users/bladi23/projects/3 |
| 2 · Encuentren el secreto | Reto 6/6. gitleaks sobre 105 commits de todas las ramas: **no leaks found** | `docs/10-riesgos.md` |
| 3 · Rotar y limpiar | Orden 3/3 y reto 2/2. Sin claves reales que rotar; `.env.example` y `.gitignore` validados | `docs/10-riesgos.md` |
| 4 · Riesgos de su producto | Reto 6/6. Matriz de 5 riesgos con mitigación verificable | `docs/10-riesgos.md` |
| 5 · ¿Dónde se despliega? | Reto 3/3. Decisión: Google Cloud Run | ADR-005 en `docs/09-decisiones.md` |
| 6 · Prevenir y cerrar | gitleaks en GitHub Actions en cada push y pull request; 0 hallazgos | `.github/workflows/secretos.yml` (PR #72) |

Puntaje de los retos (primer intento): 23/23.
