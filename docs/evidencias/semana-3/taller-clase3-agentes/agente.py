# app/agente.py · bucle del agente · generado en el taller · Grupo 7
# Meta: Explicar los resultados de la calculadora laboral con su fundamento normativo, sin realizar cálculos ni emitir dictámenes jurídicos.
import json
# from app.tools.<nombre> import <nombre>, <Nombre>In   ← importe aquí cada herramienta
# MODELOS = {"<nombre>": <Nombre>In, ...}   ESQUEMAS = [<nombre>.ESQUEMA, ...]

MAX_ITER = 6

# Lista cerrada: lo que el modelo puede pedir (nombre → función de Python)
PERMITIDAS = {
    "calcular_decimos": calcular_decimos,   # libre
    "calcular_vacaciones": calcular_vacaciones,   # libre
    "estimar_liquidacion": estimar_liquidacion,   # libre
    "explicar_resultado": explicar_resultado,   # libre
    "generar_resumen": generar_resumen,   # con confirmación
}

# Requieren el clic de una persona en la interfaz antes de ejecutarse
REQUIEREN_OK = {"generar_resumen"}

# Fuera de la lista (NO se le dan al agente; las hace una persona): realizar_pago


def ejecutar_agente(mensajes):
    for vuelta in range(MAX_ITER):
        msg = cliente.chat.completions.create(model=MODELO,
            messages=mensajes, tools=ESQUEMAS).choices[0].message
        if not msg.tool_calls:
            return {"respuesta": msg.content}
        mensajes.append(msg)
        for tc in msg.tool_calls:
            nombre, args = tc.function.name, json.loads(tc.function.arguments)
            if nombre not in PERMITIDAS:
                res = {"error": "herramienta no permitida"}
            elif nombre in REQUIEREN_OK:
                return {"pendiente": nombre, "args": args, "tool_call_id": tc.id}
            else:
                res = PERMITIDAS[nombre](MODELOS[nombre](**args))
            mensajes.append({"role": "tool", "tool_call_id": tc.id,
                             "content": json.dumps(res, default=str)})
    return {"respuesta": "No pude completar la consulta. Presento lo obtenido e indico qué falta para continuar."}
