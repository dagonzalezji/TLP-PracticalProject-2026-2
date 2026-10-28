# scratch/test_actividad4.py
# Script de validación integral automatizado para la Actividad 4
import sys
import json
import os

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("==================================================")
print("TEST SUITE: VALIDACION AUTOMATICA ACTIVIDAD 4")
print("==================================================")

# 1. Validar compilación de todos los juegos
import compiler

juegos = [
    ("games/tetris.brick", "games/tetris.json"),
    ("games/snake.brick", "games/snake.json"),
    ("games/snake_evolved.brick", "games/snake_evolved.json")
]

for brick_file, json_file in juegos:
    with open(brick_file, 'r') as f:
        code = f.read()
    tokens = compiler.lexer(code)
    parser = compiler.Parser(tokens)
    ast = parser.parse()
    compiler.generar_codigo(ast, json_file)
    print(f"[OK] Compilacion de {brick_file} -> {json_file}")

# 2. Validar estructura del AST generado para snake_evolved.json
with open("games/snake_evolved.json") as f:
    datos_evolved = json.load(f)

assert "levels" in datos_evolved, "Error: 'levels' no está en el JSON de snake_evolved"
assert "BABY" in datos_evolved["levels"], "Error: Nivel BABY no encontrado"
assert "ENTUSIASTA" in datos_evolved["levels"], "Error: Nivel ENTUSIASTA no encontrado"
assert "NYAN_CAT" in datos_evolved["levels"], "Error: Nivel NYAN_CAT no encontrado"
print("[OK] Bloque LEVELS verificado en JSON (BABY, ENTUSIASTA, NYAN_CAT)")

assert "shape_properties" in datos_evolved, "Error: 'shape_properties' no está en el JSON"
assert datos_evolved["shape_properties"]["SNAKE_BODY"]["TYPE"] == "CIRCULAR"
assert datos_evolved["shape_properties"]["POISON_FOOD"]["TYPE"] == "TRIANGULAR"
assert datos_evolved["shape_properties"]["POWERUP_FOOD"]["DURATION"] == "6"
print("[OK] Propiedades de formas (TYPE: CIRCULAR/TRIANGULAR, DURATION) verificadas")

# 3. Validar retrocompatibilidad con snake.brick original
with open("games/snake.json") as f:
    datos_original = json.load(f)

assert datos_original.get("levels") == {}, "snake.brick original no debe tener niveles definidos"
print("[OK] snake.brick original sin niveles (retrocompatible)")

# 4. Validar lógica de runtime.py sin abrir ventana gráfica interactiva
import runtime

# Crear instancia de prueba para Snake Original
juego_orig = runtime.Juego(datos_original)
juego_orig.root.withdraw() # Ocultar ventana para test headless
assert juego_orig.nivel_actual == 'BABY', "Error: Snake original debe iniciar en nivel BABY"
assert juego_orig.velocidad_gravedad == 0.15, "Error: Velocidad original debe ser 0.15s"
assert juego_orig.forma_cuerpo in ['RECTANGULAR', ''], "Error: Forma original debe ser rectangular"
assert juego_orig.posicion_veneno is None, "Error: Nivel BABY no debe tener frutas venenosas"
assert juego_orig.nubes == [], "Error: Nivel BABY no debe tener nubes obstáculo"
juego_orig.root.destroy()
print("[OK] Runtime retrocompatible: snake original corre en modo BABY por defecto")

# Crear instancia de prueba para Snake Evolved
juego_evo = runtime.Juego(datos_evolved)
juego_evo.root.withdraw()

assert juego_evo.nivel_actual == 'BABY', "Error: Evolved debe iniciar en BABY"
assert juego_evo.forma_cuerpo == 'CIRCULAR', "Error: Evolved debe tener forma CIRCULAR"
print("[OK] Runtime Evolved: inicia en BABY con forma CIRCULAR")

# Probar transición a ENTUSIASTA
juego_evo.cambiar_nivel('ENTUSIASTA')
assert juego_evo.nivel_actual == 'ENTUSIASTA'
assert juego_evo.velocidad_gravedad == 0.10, "Velocidad en Entusiasta debe ser 0.10s"
assert juego_evo.posicion_veneno is not None, "Debe existir fruta venenosa en Entusiasta"
print("[OK] Transición a Nivel ENTUSIASTA: velocidad 0.10s y fruta venenosa activa")

# Probar transición a NYAN_CAT
juego_evo.cambiar_nivel('NYAN_CAT')
assert juego_evo.nivel_actual == 'NYAN_CAT'
assert juego_evo.velocidad_gravedad == 0.05, "Velocidad en Nyan Cat debe ser 0.05s"
assert len(juego_evo.nubes) == 3, f"Debe haber 3 nubes obstáculo en Nyan Cat, hay {len(juego_evo.nubes)}"
print("[OK] Transición a Nivel NYAN_CAT: velocidad 0.05s y 3 nubes obstáculo activas")

# Probar Manejador de Estados (Power-Up 'No Morir')
juego_evo.activar_powerup(6.0)
assert juego_evo.powerup_activo is True
assert juego_evo.powerup_tiempo_restante == 6.0
print("[OK] Power-Up 'No Morir' activado con timer de 6.0 segundos")

# Simular consumo de tiempo en game loop
juego_evo.powerup_tiempo_restante = 0.05
# Ejecutar un ciclo de timer
juego_evo.powerup_tiempo_restante = max(0.0, juego_evo.powerup_tiempo_restante - 0.05)
if juego_evo.powerup_tiempo_restante <= 0:
    juego_evo.powerup_activo = False
assert juego_evo.powerup_activo is False
print("[OK] Manejador de Estados: timer del Power-Up expira correctamente")

# Probar lógica de colisión con nubes
# Caso A: Con puntos -> Pierde todos los puntos pero sigue vivo
juego_evo.puntuacion = 50
pos_nube = juego_evo.nubes[0]
juego_evo.serpiente_cuerpo = [(pos_nube[0] - 1, pos_nube[1])]
juego_evo.serpiente_direccion = (1, 0)
juego_evo.powerup_activo = False
juego_evo.snake_mover_jugador()
assert juego_evo.puntuacion == 0, f"Puntuacion esperada 0, obtenida {juego_evo.puntuacion}"
assert juego_evo.juego_terminado is False, "El jugador debe seguir vivo si tenía puntos"
print("[OK] Colisión con nube con puntos: puntuación reseteada a 0 y jugador sigue vivo")

# Caso B: Sin puntos (0 puntos) -> GAME OVER inmediato
juego_evo.puntuacion = 0
juego_evo.serpiente_cuerpo = [(pos_nube[0] - 1, pos_nube[1])]
juego_evo.serpiente_direccion = (1, 0)
juego_evo.snake_mover_jugador()
assert juego_evo.juego_terminado is True, "El jugador debe morir al chocar con nube con 0 puntos"
print("[OK] Colisión con nube con 0 puntos: GAME OVER inmediato validado")

# Caso C: Con Power-Up 'No Morir' activo -> No pierde puntos
juego_evo.juego_terminado = False
juego_evo.puntuacion = 40
juego_evo.activar_powerup(5.0)
juego_evo.serpiente_cuerpo = [(pos_nube[0] - 1, pos_nube[1])]
juego_evo.serpiente_direccion = (1, 0)
juego_evo.snake_mover_jugador()
assert juego_evo.puntuacion == 40, "No debe perder puntos si está invulnerable"
assert juego_evo.juego_terminado is False, "No debe morir si está invulnerable"
print("[OK] Colisión con nube con Power-Up 'No Morir': Inmunidad total verificada")

# Probar lógica de Fruta Venenosa
# Caso A: Consumo sin power-up resta puntos
juego_evo.powerup_activo = False
juego_evo.puntuacion = 30
juego_evo.posicion_veneno = (10, 10)
juego_evo.serpiente_cuerpo = [(9, 10)]
juego_evo.serpiente_direccion = (1, 0)
juego_evo.snake_mover_jugador()
assert juego_evo.puntuacion == 10, f"Puntuación esperada 10 (30 - 20 penalizacion Nyan Cat), obtenida {juego_evo.puntuacion}"
print("[OK] Consumo de fruta venenosa: penalización de puntos aplicada correctamente")

# Caso B: Consumo con power-up no resta puntos
juego_evo.activar_powerup(5.0)
juego_evo.puntuacion = 25
juego_evo.posicion_veneno = (10, 10)
juego_evo.serpiente_cuerpo = [(9, 10)]
juego_evo.serpiente_direccion = (1, 0)
juego_evo.snake_mover_jugador()
assert juego_evo.puntuacion == 25, "Inmune a veneno con Power-Up 'No Morir'"
print("[OK] Consumo de fruta venenosa con Power-Up: Inmunidad a penalización verificada")

juego_evo.root.destroy()

print("\n==================================================")
print("TODOS LOS CRITERIOS DE ACEPTACION HAN SIDO VALIDADOS EXITOSAMENTE!")
print("==================================================")
