# Registro del agente

## Tareas K-M - Contraste, tutor estructurado y evaluadores extensibles - 2026-09-12

- K: todos los `input` y `textarea` existentes (login, registro, tutor, review e interview) usan `.input`, ahora aliasada con `.form-input` en el tema oscuro. Se añadieron color de texto, fondo, foco, placeholder y reglas `:-webkit-autofill` para evitar el fondo claro nativo de Chrome/Edge. El textarea del tutor usa explícitamente `.form-input`.
- L: el prompt socrático exige `En palabras simples:` y `En términos técnicos:` sin cambiar la política de no entregar la solución completa. El fallback local también genera ambas secciones y el frontend las presenta en bloques visuales distintos; si una respuesta externa omite la segunda sección, se muestra la primera sin romper la UI.
- M: `Challenge` ahora tiene `evaluator_type` y `setup_sql`; la migración `0008_challenge_evaluators` prepara ambos campos. `execute_code()` despacha Python, JavaScript o SQL y conserva stdout/stderr/passed/feedback/results.
- M: el evaluador SQL crea SQLite en memoria por caso, ejecuta el `setup_sql` confiable del reto, permite solo una consulta `SELECT`/`WITH`, bloquea mutaciones mediante authorizer y compara filas reales contra `output`. El reto SQL del nivel 10 dejó de usar el arnés `solve(data)`.
- M: Monaco recibe `language="sql"` y muestra extensión `.sql`. Los primeros cinco niveles siguen ofreciendo variantes Python/JavaScript; SQL se modela como un evaluador independiente listo para añadir nuevos tipos sin acoplarlos al arnés de funciones.
- Verificado: 19 pruebas backend antes del último refuerzo del formato tutor, pruebas SQL correcta/incorrecta y mutación, Ruff focal, migración/seed, build y lint frontend. No se detectaron claves `OPENAI_API_KEY` ni `GEMINI_API_KEY` en `.env`; el modo local es el esperado.

## Tareas I-J - JavaScript y tutor pedagógico - 2026-09-12

- Confirmado al iniciar: `execute_code()` rechazaba todo lenguaje distinto de Python y el seed solo creaba retos Python. También se confirmó que `services/tutor.py` ya tenía fallback local y proveedores Gemini/OpenAI, pero ningún componente de Práctica lo consumía.
- I: el API instala Node.js en su imagen y `code_runner.py` ejecuta JavaScript con un arnés JSON compatible, timeout de 5 segundos, límite de CPU y heap V8 de 64 MB. `node --check` valida sintaxis antes de ejecutar. No se aplica `RLIMIT_AS` a Node porque V8 necesita reservar memoria virtual para arrancar; Python sí mantiene 128 MB de AS.
- I: JavaScript bloquea `require` de filesystem, procesos, red y workers, además de `eval`, `Function`, `process.env`, APIs de proceso y runtimes externos. Es análisis estático por patrones, no aislamiento fuerte; comparte kernel y usuario del servicio igual que el sandbox Python.
- I: los primeros cinco niveles tienen variante Python y JavaScript del mismo reto. Práctica guiada incluye selector de lenguaje y anterior/siguiente recorre solo el track activo. No se añadió selección durante registro: el lenguaje es una elección por reto, reversible y visible.
- J: Práctica guiada reemplaza la pista fija por tutor contextual. `Pedir ayuda` envía pregunta, enunciado y código; cada caso fallido ofrece `Explícame por qué falló` con input, esperado, obtenido y código. La UI distingue `TUTOR IA` de `TUTOR LOCAL` usando `mode`.
- J: Review e Interview conservan la evaluación determinista de palabras clave y puntuación existente para no perder feedback reproducible; el tutor contextual se concentra en la práctica, donde puede observar código y casos concretos sin duplicar la evaluación.
- J: los primeros cinco prompts incluyen `Concepto clave` y casos de uso real (formulario, perfil, transacción, cesta y etiquetas).
- Configuración detectada: `.env` local contiene `GOOGLE_CLIENT_ID` y `VITE_GOOGLE_CLIENT_ID`; no contiene `OPENAI_API_KEY` ni `GEMINI_API_KEY`. El tutor local `local-socratic` es el modo esperado en esta validación.
- Corrección pedagógica: el fallback local dejó de devolver una pista idéntica para todos los contextos; ahora menciona el reto y, ante un fallo, el input/esperado/obtenido y propone preguntas de diagnóstico sin entregar la solución.
- Verificado: 9 pruebas focales de runner/tutor, suite backend completa lanzada sobre la imagen actual, Ruff en archivos I-J, build TypeScript/Vite y ESLint. La prueba manual sin código devolvió `local-socratic`; la prueba contextual quedó cubierta por test automatizado y usa el caso fallido específico.

### Auditoría M: tema real frente a `language` original

| Nivel / reto | Tema real según título/prompt | `language` original | Corrección |
| --- | --- | --- | --- |
| 1 / Reto 1: Orientación | Identidad de valores y contrato de salida | python | Se mantiene Python; evaluator `python` |
| 2 / Reto 2: Fundamentos | Validación de diccionarios y datos de perfil | python | Se mantiene Python; evaluator `python` |
| 3 / Reto 3: Control de flujo | Condicionales y paridad | python | Se mantiene Python; evaluator `python` |
| 4 / Reto 4: Funciones | Acumuladores y suma de una cesta | python | Se mantiene Python; evaluator `python` |
| 5 / Reto 5: Estructuras | Deduplificación con conjuntos | python | Se mantiene Python; evaluator `python` |
| 6 / Reto 6: Algoritmos | Segundo valor máximo distinto | python | Se mantiene Python; evaluator `python` |
| 7 / Reto 7: POO | Frecuencia de caracteres | python | Se mantiene Python; evaluator `python` |
| 8 / Reto 8: Testing | Palíndromos y casos límite | python | Se mantiene Python; evaluator `python` |
| 9 / Reto 9: Git | Búsqueda binaria | python | Se mantiene Python como reto algorítmico de apoyo; evaluator `python` |
| 10 / Reto 10: SQL | Consulta tabular de usuarios | python | Corregido a `language=sql`, `evaluator_type=sql`, SQLite en memoria y `setup_sql` |
| 11 / Reto 11: APIs | Ordenación/merge de intervalos | python | Se mantiene Python como reto algorítmico de apoyo; evaluator `python` |
| 12 / Reto 12: Backend | Two Sum sobre un contrato de datos | python | Se mantiene Python como reto de servicio; evaluator `python` |
| 13 / Reto 13: Frontend | Conteo de tareas completadas | python | Se mantiene Python como reto de transformación; evaluator `python` |
| 14 / Reto 14: Arquitectura | Transpuesta de matriz | python | Se mantiene Python como reto de transformación; evaluator `python` |
| 15 / Reto 15: Proyecto final | Balanceo de delimitadores | python | Se mantiene Python; evaluator `python` |

La auditoría encontró un desajuste de evaluación crítico en SQL; los nombres de niveles 6-15 son contextos de progresión, no indican por sí solos que el reto deba ejecutarse en otro runtime. El nuevo `evaluator_type` permite corregir esos casos cuando el contenido real evolucione sin acoplar todos los retos a `solve(data)`.

## Tareas G-H - Sandbox Render y navegación - 2026-09-12

- G: se eligió la opción A, un subprocess local de Python, porque funciona igual en Compose y Render sin asumir un socket Docker ni una API key externa. Cada caso usa `-I -S`, timeout de 5 segundos, límite POSIX de 128 MB de memoria y 5 segundos de CPU, stdin cerrado y, cuando el worker corre como root en Linux, intenta ejecutar como `nobody`.
- G: se reemplazó el bloqueo por texto por recorrido AST de imports peligrosos (`os`, `subprocess`, `socket`, `shutil`, `ctypes`) y llamadas a `eval`, `exec`, `__import__` y `open`. Se conserva la interfaz `execute_code()` y los campos `stdout`, `stderr`, `passed`, `feedback` y `results`.
- G: el aislamiento es menor que el de contenedor: el subprocess comparte kernel y entorno del servicio, los límites `resource` son POSIX y el análisis AST no es una frontera completa para código hostil. La documentación deja este riesgo explícito; para amenazas fuertes haría falta una VM o servicio especializado.
- H: la ruta devuelve `completed` por reto según envíos aprobados del usuario. Práctica guiada muestra la posición dentro del nivel, permite volver al reto anterior y habilita el siguiente solo tras aprobación; el último reto aprobado ofrece el primer reto del siguiente nivel desbloqueado.
- Verificado: runner focal en Docker (4 pruebas, incluyendo válido, fallo, sintaxis, import peligroso y timeout), suite backend completa (12 pasadas), Ruff en los archivos modificados, Alembic hasta head, build frontend Vite/TypeScript, ESLint y ausencia del socket Docker en Compose. La revisión visual autenticada del recorrido H queda como QA manual pendiente.

## Tarea 1 - Despliegue

- Hecho: se consolidó el despliegue monolítico; FastAPI sirve `frontend/dist`, las rutas `/api` quedan separadas, el build embebe `VITE_API_URL=/api`, Compose pasa las variables Vite y el seed es idempotente.
- Verificado: build de la imagen raíz, arranque de PostgreSQL/API, `/health`, `/`, recarga de `/dashboard`, 404 de API desconocida y seed repetido sin duplicados.
- Pendiente externo: `RENDER_API_KEY` autentica, pero la cuenta no tiene servicios Render (`/v1/services` devolvió una lista vacía). No se pudo configurar variables ni desplegar hasta que exista un servicio conectado al repositorio.

## Tarea 2 - Google OAuth

- Hecho: se confirmó la cadena `.env` -> Compose -> build Vite -> `GoogleOAuthProvider`; Compose usa el client ID real y la API local queda en `/api` para el build del frontend.
- Verificado: el build monolítico compila con el client ID inyectado.
- Pendiente externo: el origen local es `http://localhost:5173`. El origen de producción y la validación OAuth en Render esperan a que exista un servicio Render; no se pudo modificar Google Cloud Console.

## Tarea 3 - Resultados por caso

- Hecho: `ExecuteOut` incluye resultados individuales; el ejecutor aísla cada caso; la UI muestra checks/X y detalles de entrada, esperado y obtenido cuando falla.
- Verificado: Ruff, 3 tests backend, build frontend y lint en contenedores.
- Pendiente: prueba manual visual con una sesión autenticada.

## Tarea 4 - Code Review

- Hecho: modelo `ReviewSnippet`, migración `0003_review_content`, cinco snippets seed idempotentes, endpoints protegidos de listado/detalle/envío y `ReviewPanel` con Monaco read-only y feedback detectado/omitido.
- Verificado: endpoint de evaluación mediante pytest, Ruff y build/lint frontend.

## Tarea 5 - Entrevista técnica

- Hecho: modelos de preguntas/sesiones/respuestas, migración `0004_interview`, ocho preguntas seed, evaluación conceptual y de código, resumen persistido, cronómetro y `InterviewPanel`.
- Verificado: migraciones hasta `0005_admin`, seed con 8 preguntas, pytest y build frontend.
- Pendiente: recorrido manual completo con una sesión autenticada.

## Tarea 6 - Curaduría IA

- Hecho: `content_curator.py`, validación Pydantic, descarte con logging, `source="ai-curated"`, `is_admin`, migración `0005_admin` y `POST /api/admin/content/refresh`.
- Decisión: se usan los RSS existentes de Hacker News y Python Blog como búsqueda/contexto; se reutilizan `OPENAI_API_KEY` y `GEMINI_API_KEY`, sin nueva clave de búsqueda.
- Verificado: caso de JSON malformado descartado sin insertar ni romper el proceso.
- Pendiente: requiere una clave de IA válida y un usuario con `is_admin=true` para prueba real contra proveedor.

## Tarea 7 - Perfil

- Hecho: progreso por skill, últimos 10 envíos con fecha/título/resultado, fecha de registro, `ProfilePanel`, navegación y tipo `profile`.
- Verificado: compilación TypeScript de la imagen de producción y diagnósticos del código modificado.
- Pendiente: confirmación manual con una cuenta autenticada.

## Cierre

- Migraciones nuevas: `0003_review_content`, `0004_interview`, `0005_admin`.
- Variables locales/Render: `DATABASE_URL`, `JWT_SECRET`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `VITE_GOOGLE_CLIENT_ID`, `VITE_API_URL`, `CORS_ORIGINS`; la curaduría reutiliza opcionalmente `OPENAI_API_KEY` o `GEMINI_API_KEY`.
- Google Cloud pendiente: agregar `http://localhost:5173` como origen autorizado y, cuando exista el servicio Render, agregar su origen HTTPS exacto. La consola no puede ser modificada desde este entorno.
- Render pendiente: la API key autentica, pero la cuenta consultada no tiene servicios (`/v1/services` devolvió cero); no se configuraron variables ni se disparó deploy.
- Validación local: imagen raíz construida, Compose levantado, `/health`, `/`, rutas SPA, migraciones, seed idempotente, Ruff y 6 tests backend verificados; lint frontend con salida 0. No se hizo `git add`, `git commit` ni `git push`.

## Despliegue Render - 2026-09-12

- Confirmado: la API key pertenece al workspace `DevCoach` y ve `devcoach-api` (`srv-daid6o7qj5pc739k76f0`) y `devcoach-db` (`dpg-daid67fqj5pc739k4s50-a`, estado `available`).
- Deploy live: `dep-daid9qlg1s2s73bjmirg`, commit `b7070e2eb021ae3bfad77063531451cb2c952742`, rama `main`.
- URL pública: `https://devcoach-api-4gri.onrender.com`.
- Variables configuradas vía API: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `VITE_GOOGLE_CLIENT_ID`, `VITE_API_URL=/api`, `CORS_ORIGINS=https://devcoach-api-4gri.onrender.com`. No había `OPENAI_API_KEY` ni `GEMINI_API_KEY` locales configuradas.
- Verificado vía API/HTTP: `/health` devuelve `200` con estado `ok`; `/` devuelve React; logs Render muestran solicitudes periódicas `GET /health` con `200 OK`.
- Pendiente del usuario: agregar `https://devcoach-api-4gri.onrender.com` en Google Cloud Console como Authorized JavaScript origin y confirmar que quedó guardado. Después se puede validar OAuth y el recorrido autenticado de producción.

## Validación OAuth producción - 2026-09-12

- Hallazgo: el sitio live cargaba, pero Google Identity Services registraba `Parameter client_id is not set correctly`. Las variables estaban presentes en Render, pero Vite las había necesitado durante el build y un Docker service no las inyectó como `ARG` automáticamente.
- Corrección local pendiente de push: `frontend/src/main.tsx` obtiene el client ID desde `/api/auth/google/login` en runtime y conserva fallback a `VITE_GOOGLE_CLIENT_ID`; `frontend/src/api.ts` exporta la URL API.
- Verificado localmente: el Dockerfile raíz recompila el frontend y la API; el servicio público actual sigue healthy.
- Pendiente: hacer push manual del fix, esperar el nuevo deploy live y repetir la prueba OAuth. No se hizo ningún commit ni push.

## Ronda de experiencia real - Tareas A-F

- A: `dashboard/path` calcula estado por `user.level`; `Level.status` se conserva por compatibilidad de esquema pero se ignora. El seed ya no asigna estados demo. Se añadió la prueba de dos usuarios con rutas independientes.
- B: usuarios nuevos empiezan en nivel `0` (primer nivel sembrado) y racha `0`. Migración `0007_user_defaults` cambia defaults futuros sin resetear cuentas existentes; se decidió conservar el progreso existente.
- C: envíos exitosos actualizan `last_activity_at` y racha: mismo día no duplica, día consecutivo incrementa y cualquier hueco mayor a un día reinicia en 1. Migración `0006_user_activity`.
- D: Overview visible consume progreso real, dominio promedio de skills y fecha actual; se eliminó tiempo enfocado y cifras demo de la vista activa.
- E: los 15 retos tienen prompts completos, starters y casos coherentes; el seed actualiza contenido seed existente sin modificar contenido generado.
- F: se añadió limpieza inmediata ante `401` y refresco de ruta/progreso tras enviar un reto. Queda pendiente el recorrido visual autenticado contra producción después del siguiente deploy.

### QA ejecutada

- Dos cuentas locales nuevas: ambas empezaron con nivel interno `0`, racha `0`, cero envíos y solo el nivel `0` activo. Tras un envío exitoso de la primera, quedó en nivel interno `1`/racha `1` con nivel `1` activo; la segunda permaneció en nivel `0`/racha `0`/nivel `0` activo.
- Navegación manual local: Resumen, Ruta, Práctica, Code Review, Entrevista y Perfil cargaron contenido; la recarga mantuvo la sesión; cerrar sesión y volver a entrar funcionó; el menú móvil abrió y cerró correctamente.
- Contenido seed verificado: 15 retos, 0 prompts cortos, 5 snippets y 8 preguntas.
- El `403` del widget Google visto en `localhost:5173` es esperado mientras ese origen no esté agregado en Google Cloud; la validación de producción requiere el siguiente deploy de estos cambios.
- Validación final: backend Ruff + 9 tests, migraciones Alembic hasta `0007_user_defaults`, seed idempotente, frontend build Vite y ESLint en Docker. No se ejecutó `git add`, `git commit` ni `git push`.

