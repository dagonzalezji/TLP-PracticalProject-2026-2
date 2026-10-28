# Análisis Técnico Detallado - Cambios Actividad 4
**Integrantes del Equipo (Participación Equitativa 50% - 50%):** David Gonzalez & Daniel David Florez Bocanegra  
**Asignatura:** Teoría de Lenguajes de Programación (TLP 2026-2S)

Este documento detalla técnica, analítica y metodológicamente cada uno de los requerimientos implementados para la **Actividad 4: Evolución del Lenguaje y Lógica de Niveles (Caso Snake)**. Se expone de forma exhaustiva qué se hizo, en qué archivos, función por función, las decisiones de arquitectura tomadas, el impacto visible en el juego y la garantía absoluta de retrocompatibilidad.

---

## 1. Literal A: Personalización Geométrica de la Serpiente

### A.1. Segmentos Circulares y Triangulares desde la Gramática

#### 1. ¿Qué se hizo?
Se habilitó la capacidad para que el programador defina la geometría de los segmentos de la serpiente directamente desde el bloque `DEFINE SHAPE` en el archivo `.brick`, admitiendo formas **circulares** (`TYPE: CIRCULAR`) y **triangulares** (`TYPE: TRIANGULAR`), manteniendo el soporte para rectángulos (`TYPE: RECTANGULAR`).

#### 2. ¿Dónde se hizo?
- [gramaticas bnf/snake_evolved.bnf](file:///Users/davidgonzalez/Desktop/TLP%202026-2/tlp/gramaticas%20bnf/snake_evolved.bnf) y [gramaticas bnf/snake.bnf](file:///Users/davidgonzalez/Desktop/TLP%202026-2/tlp/gramaticas%20bnf/snake.bnf): Nueva producción `<propiedad_shape> ::= "TYPE" ":" <tipo_figura>`.
- [compiler.py](file:///Users/davidgonzalez/Desktop/TLP%202026-2/tlp/compiler.py) (Método `parsear_shape`): Parseo genérico de atributos clave-valor antes de los estados de la matriz.
- [runtime.py](file:///Users/davidgonzalez/Desktop/TLP%202026-2/tlp/runtime.py) (Método `dibujar_celda`): Renderizado matemático condicional sobre el Canvas de Tkinter.
- [games/snake_evolved.brick](file:///Users/davidgonzalez/Desktop/TLP%202026-2/tlp/games/snake_evolved.brick): Configuración de las piezas con formas y colores.

#### 3. Código Explícito:

**En `games/snake_evolved.brick`:**
```brick
DEFINE SHAPE SNAKE_BODY:
  TYPE: CIRCULAR
  COLOR: #00E676
  STATE 1:
    [1]
END

DEFINE SHAPE POISON_FOOD:
  TYPE: TRIANGULAR
  COLOR: #D500F9
  STATE 1:
    [1]
END
```

**En `runtime.py` (`dibujar_celda`):**
```python
def dibujar_celda(self, x, y, color, forma='RECTANGULAR'):
    ts = self.taman_celda
    x1, y1 = x * ts, y * ts
    x2, y2 = x1 + ts, y1 + ts

    if forma == 'CIRCULAR':
        self.canvas.create_oval(x1 + 1, y1 + 1, x2 - 1, y2 - 1, fill=color, outline='#000000', width=1)
    elif forma == 'TRIANGULAR':
        pts = [(x1 + x2) / 2.0, y1 + 1, x1 + 1, y2 - 1, x2 - 1, y2 - 1]
        self.canvas.create_polygon(pts, fill=color, outline='#000000', width=1)
    else:
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='#000000', width=1)
```

#### 4. ¿Cómo funciona y por qué se diseñó así?
Originalmente, `dibujar_celda` estaba acoplado a rectángulos (`create_rectangle`). Se parametrizó el método para recibir el parámetro `forma`. Al computar las coordenadas del bounding box `[x1, y1, x2, y2]`, si la forma es circular se inscribe una elipse perfecta con un margen de 1 píxel. Para triángulos, se calcula el baricentro y se traza un polígono con su vértice superior centrado y la base alineada horizontalmente.

Además, para facilitar la interacción y evaluación, se mapearon las teclas `C`, `T` y `R` para alternar la forma geométrica en vivo durante la partida.

#### 5. Impacto visible en el juego:
La serpiente y las frutas se visualizan como esferas estilizadas o triángulos nítidos en lugar de los toscos cuadrados originales, modernizando notablemente el aspecto visual.

---

### A.2. Cabeza Especial Nyan Cat y Cola Multicolor Dinámica

#### 1. ¿Qué se hizo?
En el nivel de dificultad máxima (`NYAN_CAT`), la cabeza de la serpiente se transforma en un rostro circular con orejas, ojos y rasgos felinos de Nyan Cat. La cola cambia de color dinámicamente segmento a segmento formando la estela del arcoíris animado.

#### 2. ¿Dónde se hizo?
- [runtime.py](file:///Users/davidgonzalez/Desktop/TLP%202026-2/tlp/runtime.py) (Métodos `dibujar_cabeza_nyan_cat`, `game_loop` y `dibujar`).

#### 3. Código Explícito:
```python
def dibujar_cabeza_nyan_cat(self, x, y):
    ts = self.taman_celda
    x1, y1 = x * ts, y * ts
    x2, y2 = x1 + ts, y1 + ts
    cx, cy = (x1 + x2) / 2.0, (y1 + y2) / 2.0

    # Orejas triangulares rosadas
    self.canvas.create_polygon([x1 + 2, y1 + 7, x1 + 6, y1 + 1, x1 + 10, y1 + 7], fill='#F472B6', outline='#000000')
    self.canvas.create_polygon([x2 - 10, y1 + 7, x2 - 6, y1 + 1, x2 - 2, y1 + 7], fill='#F472B6', outline='#000000')

    # Cabeza circular base (se ilumina dorada si está invulnerable)
    color_cara = '#FCD34D' if self.powerup_activo else '#E5E7EB'
    self.canvas.create_oval(x1 + 2, y1 + 4, x2 - 2, y2 - 1, fill=color_cara, outline='#000000', width=1.5)

    # Ojos y detalles faciales
    self.canvas.create_oval(cx - 5, cy - 2, cx - 2, cy + 1, fill='#000000')
    self.canvas.create_oval(cx + 2, cy - 2, cx + 5, cy + 1, fill='#000000')
    self.canvas.create_oval(cx - 7, cy + 2, cx - 5, cy + 4, fill='#FB7185', outline='') # Mejilla
    self.canvas.create_oval(cx + 5, cy + 2, cx + 7, cy + 4, fill='#FB7185', outline='') # Mejilla
    self.canvas.create_oval(cx - 1, cy + 2, cx + 1, cy + 4, fill='#BE185D', outline='') # Hocico
```

**Algoritmo de la Cola Multicolor con operador módulo `%`:**
```python
# Definición de la paleta arcoíris (7 colores espectrales)
self.colores_rainbow = ['#FF0000', '#FF7F00', '#FFFF00', '#00FF00', '#0099FF', '#4B0082', '#8F00FF']

# Asignación dinámica en cada segmento i > 0
idx_color = (i - 1 + self.rainbow_offset) % len(self.colores_rainbow)
color_seg = self.colores_rainbow[idx_color]
self.dibujar_celda(x, y, color_seg, forma=self.forma_cuerpo)
```

#### 4. ¿Cómo funciona y por qué se diseñó así?
El método de la cabeza combina primitivas vectoriales nativas de Tkinter (`create_polygon` y `create_oval`) garantizando un renderizado nítido y rápido sin requerir archivos de imagen externos ni dependencias de terceros.
Para el efecto multicolor, cada segmento `i` toma un color desfasado por `self.rainbow_offset`. Al incrementar `rainbow_offset` en cada frame del `game_loop`, los colores fluyen a lo largo del cuerpo de la serpiente creando una auténtica animación de arcoíris rodante.

#### 5. Impacto visible en el juego:
Al entrar al nivel Nyan Cat, la serpiente se distingue de inmediato: la cabeza adopta la apariencia del gato cósmico y la cola ondula con vibrantes franjas de colores en constante movimiento.

---

## 2. Literal B: Sistema de Frutas y Obstáculos

### B.1. Frutas Venenosas (`POISON_FOOD`)

* **Definición y Comportamiento:** Aparecen activas a partir del nivel Entusiasta. Se representan en tono morado (`#9900EF`) con una advertencia en cruz.
* **Lógica en `runtime.py`:**
  ```python
  elif self.posicion_veneno and nueva_cabeza == self.posicion_veneno:
      if self.powerup_activo:
          print(">>> Fruta venenosa consumida SIN efecto (Power-Up 'No Morir' activo) <<<")
      else:
          penalizacion = int(self.obtener_prop_nivel('POISON_PENALTY', 10))
          if self.nivel_actual == 'NYAN_CAT' and self.puntuacion <= 0:
              self.juego_terminado = True
              return
          self.puntuacion = max(0, self.puntuacion - penalizacion)
      self.snake_spawn_veneno()
  ```
* **Consecuencias:** Si el jugador no cuenta con el escudo del power-up, comer veneno resta puntos (10 en Entusiasta, 20 en Nyan Cat). En Nyan Cat, si el jugador ya se encuentra en 0 puntos y consume veneno, sobreviene el Game Over instantáneo.

---

### B.2. Nubes Obstáculo Fijas (`CLOUD_OBSTACLE`)

* **Definición:** Entidades estáticas posicionadas en cuadrantes clave del tablero durante el nivel Nyan Cat. Se dibujan en canvas mediante el método `dibujar_nube` utilizando elipses celestes y blancas superpuestas.
* **Lógica de Colisión (Requerimiento Crítico):**
  ```python
  if nueva_cabeza in self.nubes:
      if self.powerup_activo:
          print(">>> Invulnerable a la colision con nube obstaculo gracias a 'No Morir' <<<")
      else:
          if self.puntuacion > 0:
              print(">>> COLISION CON NUBE OBSTACULO! Perdida total de puntos ({}) pero sigue vivo <<<".format(self.puntuacion))
              self.puntuacion = 0
          else:
              print(">>> COLISION CON NUBE OBSTACULO SIN PUNTOS! GAME OVER INMEDIATO <<<")
              self.juego_terminado = True
              return
  ```
* **Impacto en el juego:**
  - Si el jugador tiene 50 puntos y choca contra una nube, su marcador cae estrepitosamente a 0, pero sigue con vida (recibe una segunda oportunidad).
  - Si el jugador choca teniendo 0 puntos, no hay margen de tolerancia y el juego finaliza al instante.
  - Si el jugador tiene activo el Power-Up "No Morir", atraviesa la nube inmune y sin perder puntuación.

---

### B.3. Power-Up "No Morir" (Manejador de Estados / State Manager)

* **Definición:** Fruta especial que adopta la figura de una estrella dorada resplandeciente (`#FBBF24`). Otorga invulnerabilidad absoluta durante `n` segundos (configurado como `6` segundos en el archivo `.brick`).
* **Implementación del State Manager:**
  El temporizador no bloquea el hilo principal con funciones peligrosas como `time.sleep()`. En su lugar, el `game_loop` de Tkinter descuenta progresivamente el delta de tiempo transcurrido (50 ms):
  ```python
  # En game_loop():
  if self.powerup_tiempo_restante > 0:
      self.powerup_tiempo_restante = max(0.0, self.powerup_tiempo_restante - 0.05)
      if self.powerup_tiempo_restante <= 0:
          self.powerup_activo = False
  ```
* **Beneficios de la Invulnerabilidad:**
  1. **Paredes:** En lugar de morir, la serpiente se teletransporta al extremo contrario del grid (efecto toroide / wrap-around: `coord % dimension`).
  2. **Auto-colisión:** Atraviesa su propio cuerpo sin morir.
  3. **Nubes Obstáculo:** Atraviesa las nubes sin perder sus puntos ni perecer.
  4. **Veneno:** Neutraliza las penalizaciones de puntuación.
* **Indicador en Pantalla:** En la barra lateral se ilumina una insignia dorada con el cronómetro en reversa exacto: `★ NO MORIR ★ [5.3s]`.

---

## 3. Literal C: Niveles de Dificultad desde la Gramática

### C.1. Especificación del Bloque `LEVELS`
El archivo `.brick` incluye la definición declarativa de los 3 niveles con sus parámetros de velocidad de tick, umbrales de puntos, duración del power-up y penalizaciones:

```brick
LEVELS:
  LEVEL BABY:
    TICK_SPEED: 0.15
    SCORE_THRESHOLD: 0
  END
  LEVEL ENTUSIASTA:
    TICK_SPEED: 0.10
    POWERUP_DURATION: 6
    SCORE_THRESHOLD: 30
    POISON_PENALTY: 10
  END
  LEVEL NYAN_CAT:
    TICK_SPEED: 0.05
    POWERUP_DURATION: 6
    OBSTACLES: 3
    SCORE_THRESHOLD: 80
    POISON_PENALTY: 20
  END
END
```

### C.2. Matriz de Configuración por Nivel

| Nivel | Velocidad Tick | Obstáculos (Nubes) | Frutas Venenosas | Power-Up "No Morir" | Apariencia Visual | Regla Especial |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **BABY** (Defecto) | `0.15 s` | Desactivados | Desactivadas | Desactivado | Normal (Círculo o Triángulo) | Modo clásico y seguro |
| **ENTUSIASTA** | `0.10 s` | Desactivados | **Activas** (-10 pts) | **Habilitado** (6 seg) | Normal | Mayor velocidad y reflejos |
| **NYAN_CAT** | `0.05 s` | **Activas** (3 nubes fijas) | **Activas** (-20 pts) | **Habilitado** (6 seg) | **Cabeza Gato + Cola Arcoíris** | Colisión con nube resetea puntos a 0; si tiene 0, Game Over |

### C.3. Transición de Niveles Dinámica y Manual
1. **Automática por Puntuación:**
   Al consumir comida normal en `ON_EAT_FOOD`, se ejecuta `verificar_transicion_nivel()`. Al alcanzar 30 puntos se avanza a Entusiasta; al superar 80 puntos se corona en Nyan Cat.
2. **Atajos para Validación y Grabación:**
   Las teclas numéricas `1`, `2` y `3` permiten forzar la transición instantánea a cualquier nivel para facilitar demostraciones en video o inspecciones del docente.

---

## 4. Literal D: Análisis de Retrocompatibilidad y Arquitectura

### D.1. Cambios en `compiler.py`
1. **Soporte Numérico con Punto Flotante:**
   El lexer original solo reconocía enteros (`\d+`), truncando números decimales como `0.15`. Se amplió la expresión regular a `token_regex = r'#[0-9A-Fa-f]{6}|\b[A-Z_]+\b|-?\d+\.\d+|-?\d+|[\[\](),:]'`.
2. **Método `parsear_levels()`:**
   Recolecta la estructura anidada de niveles y sus propiedades en el diccionario `ast['levels']`. Si un `.brick` viejo no incluye el bloque, `ast['levels']` se inicializa como `{}` vacío sin romper el flujo de compilación.
3. **Generalización de `parsear_shape()`:**
   Admite cualquier atributo clave-valor (`TYPE`, `COLOR`, `CHANCE`, `DURATION`) antes de la sección `STATE`, protegiendo la retrocompatibilidad con las matrices clásicas de Tetris y Snake.

### D.2. Cambios en `runtime.py`
1. **Fallback Automático al Nivel Baby:**
   Si `datos_juego.get('levels')` está vacío (como en `snake.brick` original), el motor autogenera la configuración por defecto:
   ```python
   if not self.niveles_config:
       self.niveles_config = {
           'BABY': {'TICK_SPEED': '0.15', 'SCORE_THRESHOLD': '0'}
       }
   ```
2. **Desacoplamiento de Eventos:**
   Las mecánicas avanzadas de colisión solo se ejecutan cuando las entidades correspondientes están presentes en el mapa, dejando la física clásica intacta para archivos originales.
3. **Validación Cruzada con Tetris:**
   Se mantuvieron intactas las funciones `tetris_spawn_pieza`, `tetris_mover_pieza`, `tetris_rotar_pieza` y `tetris_limpiar_lineas`.

---

## 5. Resumen de Pruebas de Aceptación Ejecutadas

Se ejecutó la suite de verificación automatizada [scratch/test_actividad4.py](file:///Users/davidgonzalez/Desktop/TLP%202026-2/tlp/scratch/test_actividad4.py), arrojando un resultado de **100% pruebas aprobadas**:

- `[OK] Compilacion de games/tetris.brick -> games/tetris.json`
- `[OK] Compilacion de games/snake.brick -> games/snake.json`
- `[OK] Compilacion de games/snake_evolved.brick -> games/snake_evolved.json`
- `[OK] Bloque LEVELS verificado en JSON (BABY, ENTUSIASTA, NYAN_CAT)`
- `[OK] Propiedades de formas (TYPE: CIRCULAR/TRIANGULAR, DURATION) verificadas`
- `[OK] snake.brick original sin niveles (retrocompatible en modo BABY)`
- `[OK] Transición a Nivel ENTUSIASTA: velocidad 0.10s y fruta venenosa activa`
- `[OK] Transición a Nivel NYAN_CAT: velocidad 0.05s y 3 nubes obstáculo activas`
- `[OK] Power-Up 'No Morir' activado con timer de 6.0 segundos y State Manager funcional`
- `[OK] Colisión con nube con puntos: puntuación reseteada a 0 y jugador sigue vivo`
- `[OK] Colisión con nube con 0 puntos: GAME OVER inmediato validado`
- `[OK] Colisión con nube con Power-Up 'No Morir': Inmunidad total verificada`
- `[OK] Consumo de fruta venenosa: penalización de puntos aplicada correctamente`
- `[OK] Consumo de fruta venenosa con Power-Up: Inmunidad a penalización verificada`
