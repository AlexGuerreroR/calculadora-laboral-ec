# 03 · Diseño de la arquitectura

Arquitectura en capas: un backend FastAPI expone la API y sirve un frontend HTML/JS simple. Los cálculos viven en código determinista; el modelo solo redacta explicaciones a partir de datos que el backend le entrega.

## 1. Componentes

```mermaid
flowchart LR
    U[Usuario] -->|completa el formulario| F[Frontend HTML/JS<br/>formularios paso a paso]
    F -->|Paso 1: JSON con fechas, remuneraciones,<br/>horas, región y motivo de salida| API[FastAPI]
    subgraph Backend
      API -->|datos del formulario| VAL{Paso 2: Pydantic<br/>¿datos válidos?}
      VAL -->|no: campos inválidos| ERR[Error 422<br/>no llega al modelo]
      VAL -->|sí: datos validados| GR{Paso 3: Control de alcance<br/>¿litigio, incumplir la ley<br/>o fuera de dominio?}
      GR -->|sí| DER[Respuesta de derivación<br/>al Ministerio del Trabajo]
      GR -->|no: consulta permitida| AG[Paso 4: Agente]
      AG -->|remuneraciones y período| T1[calcular_decimos]
      AG -->|fecha de ingreso y remuneración| T2[calcular_vacaciones]
      AG -->|datos de la relación laboral| T3[estimar_liquidacion]
      AG -->|resultado ya calculado| T4[explicar_resultado]
      AG -->|entradas y resultados| T5[generar_resumen]
      CFG[(config/parametros.yaml)] -->|SBU y períodos| T1
      CFG -->|reglas de vacaciones| T2
      CFG -->|recargos, desahucio y topes| T3
      T4 -->|tipo de cálculo| RET[Retriever]
      RET -->|artículo recuperado| T4
      T1 -->|rubros calculados| RESP[Paso 5: Respuesta<br/>desglose, explicación, cita y PDF]
      T2 -->|días y valor| RESP
      T3 -->|rubros y total| RESP
      T4 -->|explicación con cita| RESP
      T5 -->|archivo PDF| RESP
    end
    RET -->|consulta + filtro de metadatos| VDB[(ChromaDB<br/>artículos del Código)]
    VDB -->|fragmentos con artículo y vigencia| RET
    SRC[Fuentes oficiales<br/>data/raw] -->|scripts/ingest.py: fragmentos<br/>por artículo + embeddings| VDB
    T4 -->|resultado + artículo,<br/>sin datos personales| LLM[API Gemini<br/>clave en variable de entorno]
    LLM -->|explicación en lenguaje sencillo| T4
    ERR -->|mensaje de validación| F
    DER -->|orientación y derivación| F
    RESP -->|Paso 6: JSON + PDF descargable| F
    F -->|muestra desglose, explicación,<br/>fuente y PDF| U
```

## 2. Flujo de una consulta de principio a fin

Ejemplo: un trabajador quiere saber su décimo tercero.

1. Completa el formulario (remuneraciones del período) y lo envía.
2. FastAPI valida la entrada con Pydantic. Si hay un salario negativo o una fecha futura, responde **422** y el modelo nunca se llama.
3. **Antes de ejecutar cualquier herramienta**, el control de alcance (guardrail) revisa la consulta. Si es litigiosa, pide incumplir la ley o está fuera del dominio, el flujo termina con una respuesta de derivación al Ministerio del Trabajo y ninguna herramienta se ejecuta.
4. El agente llama a `calcular_decimos`, que lee el salario básico y los períodos de `config/parametros.yaml` y devuelve el resultado desglosado.
5. `explicar_resultado` pide al retriever el artículo aplicable (art. 111) a ChromaDB, filtrando por metadatos.
6. Se arma el prompt con el resultado numérico ya calculado y el fragmento del artículo **delimitado como datos**. Gemini redacta la explicación y cita el artículo. Si no se recuperó ningún artículo, el sistema dice que no tiene fuente verificable.
7. El frontend muestra el desglose, la explicación y la fuente. El usuario puede pedir el resumen en PDF (`generar_resumen`).

## 3. Herramientas del agente (definidas por el caso)

| Herramienta | Entrada | Qué hace | Tipo |
|---|---|---|---|
| `calcular_decimos(remuneraciones, periodo)` | montos por mes, período, región | Décimo tercero y décimo cuarto | Determinista, solo lectura |
| `calcular_vacaciones(fecha_ingreso, remuneracion)` | fechas, remuneración | Días y valor de vacaciones | Determinista, solo lectura |
| `estimar_liquidacion(datos)` | fechas, remuneración, motivo de salida, horas extra | Rubros y total (incluye horas suplementarias y extraordinarias) | Determinista, solo lectura |
| `explicar_resultado(calculo)` | resultado ya calculado | Explicación con cita del artículo recuperado | Modelo + RAG, no calcula |
| `generar_resumen(datos)` | entradas y resultados | PDF descargable | Determinista; se genera solo cuando el usuario lo pide |

Límites: máximo de iteraciones del agente, rechazo de consultas fuera de dominio y ninguna herramienta ejecuta SQL ni comandos generados por el modelo.

## 4. Qué va en código, en configuración y en el modelo

| Elemento | Dónde vive |
|---|---|
| Fórmulas de décimos, vacaciones, horas y liquidación | Código (`app/tools/`), con pruebas |
| Salario básico, recargos, períodos, topes | `config/parametros.yaml` |
| Texto de la norma | Base vectorial (ChromaDB), a partir de `data/raw/` |
| Redacción de la explicación en lenguaje sencillo | Modelo generativo |
| Decisión de derivar un caso | Guardrail en código + instrucción del prompt |

## 5. Tecnologías

| Capa | Tecnología |
|---|---|
| Backend | Python 3.11+ con FastAPI |
| Validación | Pydantic |
| Pruebas | pytest |
| Modelo | Gemini Flash (capa gratuita) |
| Embeddings y base vectorial | Embeddings de Gemini + ChromaDB con persistencia en disco |
| Frontend | HTML + JavaScript servido por FastAPI |
| Despliegue | Render, Railway o Hugging Face Spaces |
