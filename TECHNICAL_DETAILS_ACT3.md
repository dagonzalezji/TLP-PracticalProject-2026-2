# Análisis Técnico Detallado - Cambios Actividad 3

Este documento detalla técnica e iterativamente cada requerimiento solicitado en la Actividad 3. Por cada literal se expone qué se hizo, en qué archivos, cómo se programó, por qué se tomaron esas decisiones (enfocado en retrocompatibilidad) y su impacto visible en el juego.

---

## Literal A: Integración de Rotaciones Completas

### 1. ¿Qué se hizo?
Se reescribieron y completaron los estados de rotación (matrices geométricas) para las piezas `I_PIECE` y `L_PIECE` para garantizar que tuvieran 4 estados lógicos sin saltos irregulares.

### 2. ¿Dónde se hizo?
Exclusivamente en el archivo de definición `games/tetris.brick`.

### 3. Código Explícito (.brick):
```brick
DEFINE SHAPE L_PIECE:
  # Estado 1: L Original (mirando hacia arriba)
  STATE 1:
    [0, 1, 0]
    [0, 1, 0]
    [0, 1, 1]
  # Estado 2: L rotada 90° horario
  STATE 2:
    [0, 0, 0]
    [1, 1, 1]
    [1, 0, 0]
  # Estado 3: L rotada 180°
  STATE 3:
    [1, 1, 0]
    [0, 1, 0]
    [0, 1, 0]
  # Estado 4: L rotada 270°
  STATE 4:
    [0, 0, 1]
    [1, 1, 1]
    [0, 0, 0]
END
```
*(Se aplicó una corrección similar para completar los 4 estados de la `I_PIECE`).*

### 4. ¿Cómo funciona y por qué se hizo así?
El código original de la `L_PIECE` tenía un error de diseño: los estados 1 y 3 eran una "L", pero los estados 2 y 4 mutaban matemáticamente a una "J". Se reconstruyeron las matrices simulando una rotación real de 90 grados sobre su eje central en cada paso. Se mantuvo la pieza `T_PIECE` intacta porque ya cumplía geométricamente con sus 4 estados, respetando la regla de no alterar lo que ya funciona.

### 5. ¿Cómo se ve reflejado en el juego?
Al presionar la Flecha Arriba mientras cae la pieza "L" o la pieza "I", estas giran de manera fluida y natural sobre su propio eje, sin transformarse en otra figura distinta ni "teletransportarse" a un lado de la pantalla.

---

## Literal B: Nuevas Figuras y Atributos de Personalización

### B.1: Tres Nuevas Figuras (O, S, Z)

*   **Qué se hizo:** Diseño de matrices 2D y adición al código fuente del juego.
*   **Dónde se hizo:** Al final del archivo `games/tetris.brick`.
*   **Código Explícito:**
```brick
DEFINE SHAPE O_PIECE:
  # ... (etiquetas de color y chance omitidas por brevedad)
  STATE 1:
    [1, 1]
    [1, 1]
END

DEFINE SHAPE S_PIECE:
  STATE 1:
    [0, 1, 1]
    [1, 1, 0]
    [0, 0, 0]
  STATE 2:
    [0, 1, 0]
    [0, 1, 1]
    [0, 0, 1]
  # (Estados 3 y 4 repiten la secuencia geométrica...)
```
*   **Cómo funciona y por qué:** Para el bloque cuadrado `O_PIECE`, se definió una matriz de `2x2` para mantener la escala del juego. Para las piezas `S` y `Z` se utilizaron matrices de `3x3`. Se decidió agregarles 4 estados a todas (aunque la pieza `O` repita siempre el mismo) para que el motor `runtime.py` pueda llamar libremente a la función de rotación sin riesgo de lanzar excepciones por "Index out of bounds".
*   **Reflejo en el juego:** Aparecen en pantalla las clásicas piezas cuadradas y las siluetas zigzagueantes (S y Z) diversificando el juego.

---

### B.2: Colores por Tipo (Procesamiento Dinámico)

*   **Qué se hizo:** Se expandió la sintaxis para aceptar `COLOR: #HEX`. Se protegió el carácter `#` en el analizador léxico, se parseó en el AST y se inyectó al renderizador del juego.
*   **Dónde se hizo:** `gramaticas bnf/tetris.bnf`, `compiler.py` (Lexer y Parser), `runtime.py` (Motor de renderizado) y `games/tetris.brick`.
*   **Código Explícito (compiler.py - Lexer):**
```python
    # Proteger colores hexadecimales antes de borrar comentarios
    colores = re.findall(r'#[0-9A-Fa-f]{6}', codigo_fuente)
    for i, c in enumerate(colores):
        codigo_fuente = codigo_fuente.replace(c, f"__COLOR{i}__")
        
    codigo_fuente = re.sub(r'#.*', '', codigo_fuente) # Borra comentarios
    # ... (restaura colores)
```
*   **Código Explícito (tetris.brick):**
```brick
DEFINE SHAPE L_PIECE:
  COLOR: #FFA500
```
*   **Cómo funciona y por qué:** Originalmente, el compilador borraba todo lo que hubiese después de un `#` al considerarlo un comentario. Modificamos el lexer mediante expresiones regulares para enmascarar códigos de 6 dígitos temporales (`__COLOR0__`), permitiendo la sintaxis habitual del diseño web. En el `parser`, guardamos estas propiedades en un nodo JSON separado llamado `"shape_properties"`. Esto se hizo por **estricta retrocompatibilidad**: un motor viejo seguirá leyendo `"shapes"`, ignorando `"shape_properties"` y usando su color cian por defecto sin crashear.
*   **Reflejo en el juego:** El juego deja de ser monótono. Al caer, cada pieza tiene su propio color (La 'L' es naranja, la 'T' es morada, la cuadrada amarilla, etc.).

---

### B.3: Probabilidad de Aparición Ponderada

*   **Qué se hizo:** Inserción de pesos por pieza mediante `CHANCE: num` y actualización del selector pseudo-aleatorio.
*   **Dónde se hizo:** `compiler.py`, `runtime.py` y `games/tetris.brick`.
*   **Código Explícito (runtime.py - Algoritmo de Ruleta):**
```python
    # 1. Extracción de pesos con fallback a 10 (retrocompatibilidad)
    weights = []
    for shape in shapes:
        props = shape_props.get(shape, {})
        chance = int(props.get('CHANCE', 10))
        weights.append(chance)
        
    # 2. Selección por peso (Roulette Wheel)
    total = sum(weights)
    r = random.uniform(0, total)
    upto = 0
    nombre_pieza = shapes[0]
    for i, w in enumerate(weights):
        if upto + w >= r:
            nombre_pieza = shapes[i]
            break
        upto += w
```
*   **Código Explícito (tetris.brick):**
```brick
DEFINE SHAPE O_PIECE:
  COLOR: #FFFF00
  CHANCE: 20
```
*   **Cómo funciona y por qué:** Se reemplazó la función plana `random.choice()` por el algoritmo matemático *Roulette Wheel Selection*. Se extrae el peso de la etiqueta `CHANCE`. Si un `.brick` viejo no lo tiene, se usa el `get('CHANCE', 10)` (todos asumen peso 10, volviéndose uniformes de nuevo, logrando **retrocompatibilidad**). Se empleó `random.uniform` de la librería estándar para evitar la instalación prohibida de paquetes de terceros como `numpy`.
*   **Reflejo en el juego:** Piezas a las que le dimos un peso alto (ej. la cuadrada con 20) invadirán el tablero mucho más frecuentemente que las piezas con pesos bajos (ej. S y Z con peso 5).

---

## Literal C: Implementación de Power-Ups (Objetos Especiales)

### 1. ¿Qué se hizo?
Se creó una pieza de ayuda (`POWERUP_PIECE`) de tamaño 1x1, blanca, que el jugador "desbloquea" al jugar bien (después de limpiar 2 líneas del tablero).

### 2. ¿Dónde se hizo?
`games/tetris.brick` (Definición de la entidad) y `runtime.py` (Interceptación del Spawn).

### 3. Código Explícito (.brick):
```brick
DEFINE SHAPE POWERUP_PIECE:
  COLOR: #FFFFFF
  CHANCE: 0
  STATE 1:
    [1]
  # ... (4 estados idénticos)
```

### 4. Código Explícito (runtime.py):
```python
    # Evaluador de condición (Al limpiar líneas)
    self.lineas_limpias_total += lineas_limpias
    if self.lineas_limpias_total >= 2:
        self.spawn_powerup = True
        self.lineas_limpias_total = 0

    # Interceptación del Spawn (tetris_spawn_pieza)
    if getattr(self, 'spawn_powerup', False) and 'POWERUP_PIECE' in shapes:
        nombre_pieza = 'POWERUP_PIECE'
        self.spawn_powerup = False
```

### 5. ¿Cómo funciona y por qué se hizo así?
El Power-Up recibe una probabilidad matemática base de `CHANCE: 0` en el archivo de texto, lo que asegura que el algoritmo de ruleta (descrito en el literal anterior) jamás lo arroje por accidente. 
En paralelo, el motor vigila las líneas limpiadas. Cuando el contador supera las 2 líneas, activa una variable de estado (`spawn_powerup = True`). 
En el próximo turno, la función de generación detecta esta bandera activa y hace un *short-circuit*: ignora la matemática de ruleta y empuja directamente la pieza `POWERUP_PIECE` a la pantalla. Se decidió este método de interrupción de banderas ("Flag Interruption") para no contaminar la lista estática de pesos con probabilidades dinámicas.

### 6. ¿Cómo se ve reflejado en el juego?
El jugador juega normalmente su partida. Cuando su nivel de habilidad le permite romper 2 líneas apiladas (es decir, consigue 200 puntos), el juego "premia" al jugador haciendo que la siguiente pieza en caer sea un diminuto cuadro blanco de `1x1` píxeles, el cual puede utilizarse de comodín para tapar cualquier hueco profundo del tablero.
