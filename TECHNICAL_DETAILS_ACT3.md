# Análisis Técnico Detallado - Cambios Actividad 3

Este documento expone a un nivel técnico la arquitectura de los cambios realizados en el compilador `compiler.py` y el motor `runtime.py` para cumplir con las extensiones del lenguaje solicitadas, detallando el código explícito insertado y la justificación detrás de cada decisión de diseño para preservar la retrocompatibilidad.

---

## 1. Modificación del Analizador Léxico (Lexer)
**Archivo:** `compiler.py`

**El Problema:**
El lenguaje `.brick` originalmente utilizaba el símbolo `#` de forma exclusiva para los comentarios de una línea. Al requerir la inserción de la etiqueta `COLOR: #FFFFFF`, el analizador léxico (`lexer`) estaba configurado con la expresión regular `re.sub(r'#.*', '', codigo_fuente)`, lo que provocaba que cualquier color hexadecimal fuera detectado como un comentario y eliminado antes del parseo, rompiendo la compilación.

**Código Añadido / Modificado:**
```python
def lexer(codigo_fuente):
    # 1. Extraer y proteger los colores hexadecimales
    colores = re.findall(r'#[0-9A-Fa-f]{6}', codigo_fuente)
    for i, c in enumerate(colores):
        codigo_fuente = codigo_fuente.replace(c, f"__COLOR{i}__")
        
    # 2. Eliminar comentarios estándar
    codigo_fuente = re.sub(r'#.*', '', codigo_fuente)
    
    # 3. Restaurar los colores
    for i, c in enumerate(colores):
        codigo_fuente = codigo_fuente.replace(f"__COLOR{i}__", c)
        
    token_regex = r'#[0-9A-Fa-f]{6}|\b[A-Z_]+\b|\d+|[\[\](),:]'
    tokens = re.findall(token_regex, codigo_fuente)
    return tokens
```

**Por qué y su Impacto:**
En lugar de forzar a los usuarios a escribir colores sin el `#` (lo cual va en contra de la UX esperada en desarrollo web y diseño), se diseñó un paso de "pre-procesamiento". El Lexer escanea temporalmente el código buscando patrones hexadecimales estrictos de 6 dígitos. Si los encuentra, los reemplaza por un comodín temporal (`__COLOR0__`). Luego elimina todos los comentarios destructivamente, y finalmente restaura los comodines a sus valores originales. 
*Impacto:* Permite el uso de sintaxis hexadecimal natural (`#FF0000`) sin cambiar drásticamente la gramática de los comentarios del lenguaje.

---

## 2. Expansión del Abstract Syntax Tree (Parser)
**Archivo:** `compiler.py`

**El Problema:**
Había que agregar soporte para parsear `COLOR` y `CHANCE` dentro de las piezas, pero si se alteraba el array `shapes` dentro del archivo `.json` de salida (ej. pasando de una lista de matrices a un diccionario de atributos), **todo juego compilado bajo la nueva versión dejaría de ser ejecutable por el motor antiguo, rompiendo la retrocompatibilidad exigida**.

**Código Añadido / Modificado:**
```python
    def parsear_shape(self):
        # ... (parseo del nombre)
        self.ast['shape_properties'][nombre_shape] = {}
        
        while self.posicion < len(self.tokens) and self.tokens[self.posicion] in ['COLOR', 'CHANCE']:
            prop = self.consumir()
            self.consumir(':')
            val = self.consumir()
            self.ast['shape_properties'][nombre_shape][prop] = val
        # ... (continúa parseo de matrices inalterado)
```

**Por qué y su Impacto:**
Se decidió separar las metadatas. Se creó un nuevo nodo raíz en el árbol sintáctico (AST) de salida llamado `"shape_properties"`. La definición geométrica pura de las piezas se sigue inyectando en `"shapes"`.
*Impacto:* Un `.json` compilado con el nuevo sistema es 100% retrocompatible. Si un motor antiguo lee el archivo, simplemente ignorará la llave `"shape_properties"` y seguirá renderizando los arrays de `"shapes"`.

---

## 3. Lógica de Probabilidades Ponderadas
**Archivo:** `runtime.py`

**El Problema:**
El requisito exige que la selección aleatoria de piezas no sea uniforme, sino ponderada (basada en el `CHANCE` de cada `.brick`), usando Python 2.7 nativo sin librerías externas (sin `numpy.random.choice`).

**Código Añadido / Modificado:**
```python
    def tetris_spawn_pieza(self):
        shapes = list(self.datos_juego['shapes'].keys())
        shape_props = self.datos_juego.get('shape_properties', {})
        
        # 1. Extracción de pesos con fallback a 10
        weights = []
        for shape in shapes:
            props = shape_props.get(shape, {})
            chance = int(props.get('CHANCE', 10))
            weights.append(chance)
            
        # 2. Algoritmo de Ruleta (Roulette Wheel Selection)
        total = sum(weights)
        r = random.uniform(0, total)
        upto = 0
        nombre_pieza = shapes[0]
        # (Lógica de PowerUp inyectada aquí...)
        else:
            for i, w in enumerate(weights):
                if upto + w >= r:
                    nombre_pieza = shapes[i]
                    break
                upto += w
```

**Por qué y su Impacto:**
Se implementó el algoritmo matemático clásico de *Roulette Wheel Selection*. Se suman todos los pesos (ej. total = 100). Se lanza un aleatorio uniforme entre 0 y el total. Luego se iteran los pesos sumándolos consecutivamente hasta que superan el número aleatorio, seleccionando así la pieza. El uso del `get('CHANCE', 10)` garantiza que si se corre el juego original sin `CHANCE`, todas las piezas asumirán un peso igualitario de `10`, cayendo elegantemente a una probabilidad uniforme.

---

## 4. Inyección del Power-Up por Condición Dinámica
**Archivo:** `runtime.py`

**El Problema:**
El `POWERUP_PIECE` debe insertarse en el ciclo del juego bajo demanda (en este caso, tras limpiar 2 líneas) sin que afecte la entropía matemática del sistema probabilístico principal.

**Código Añadido / Modificado:**
```python
    # En tetris_limpiar_lineas()
    self.lineas_limpias_total += lineas_limpias
    if self.lineas_limpias_total >= 2:
        self.spawn_powerup = True
        self.lineas_limpias_total = 0

    # En tetris_spawn_pieza()
    if getattr(self, 'spawn_powerup', False) and 'POWERUP_PIECE' in shapes:
        nombre_pieza = 'POWERUP_PIECE'
        self.spawn_powerup = False
```

**Por qué y su Impacto:**
El diseño usa el patrón de "Banderas de Interrupción" (Flag interruption). En lugar de modificar los pesos del `POWERUP` en tiempo real (lo cual requeriría recalcular el arreglo de pesos), se le asigna a la pieza un `CHANCE: 0` constante en el `.brick`. El recolector de líneas limpias evalúa la condición matemática (≥ 2 líneas acumuladas). De ser cierta, levanta el flag `spawn_powerup`.
Cuando se ejecuta la función principal de `spawn`, si el flag está levantado, el algoritmo hace un *short-circuit* (ignora por completo el cálculo aleatorio de la ruleta) y fuerza el objeto, apagando de nuevo la bandera.
*Impacto:* Sistema modular que no ensucia la lógica probabilística y permite expandir el concepto de PowerUps múltiples en el futuro simplemente añadiendo variables booleanas que interrumpan la cola de generación.
