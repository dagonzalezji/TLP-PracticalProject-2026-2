# Guión Oficial para Video Demostrativo - Actividad 4 (Snake Evolved)
**Asignatura:** Teoría de Lenguajes de Programación (TLP 2026-2S)  
**Tiempo estimado de video:** 2 a 3 minutos  
**Herramienta recomendada de grabación en Mac:** Atajo nativo de macOS `Cmd + Shift + 5` o `QuickTime Player` -> *Nueva grabación de pantalla*.

---

## 1. Configuración Previa de Grabación

1. **Resolución de Pantalla:** 1080p (Full HD) o área seleccionada nítida.
2. **Disposición de Ventanas:**
   - Mitad izquierda de la pantalla: Terminal abierta en el directorio `/tlp`.
   - Mitad derecha de la pantalla: Se abrirá la ventana gráfica del juego (Tkinter).
3. **Comando de arranque:**
   ```bash
   ./jugar.sh snake_evolved
   ```

---

## 2. Cronograma y Escenas Paso a Paso

### Escena 1: Introducción y Compilación (0:00 - 0:25)
* **Acción en Pantalla:**
  1. Mostrar brevemente el archivo `games/snake_evolved.brick` en la terminal o editor, señalando el bloque `LEVELS:`, `DEFINE SHAPE` (`TYPE: CIRCULAR`, `TYPE: TRIANGULAR`) y `DURATION: 6`.
  2. Ejecutar el comando:
     ```bash
     ./jugar.sh snake_evolved
     ```
  3. Mostrar el mensaje de compilación exitosa y cómo se lanza la ventana gráfica retro.
* **Guión de Voz / Locución:**
  > *"Hola a todos. En este video presentamos la demostración de la Actividad 4: Evolución del Lenguaje y Lógica de Niveles para Snake en BrickScript. Observamos en nuestro archivo .brick la definición formal de los bloques de niveles Baby, Entusiasta y Nyan Cat, así como las geometrías circular y triangular. Compilamos con ./jugar.sh snake_evolved y vemos que el compilador procesa todo el AST sin errores e inicia el runtime."*

---

### Escena 2: Nivel 1 - BABY (0:25 - 0:50)
* **Acción en Pantalla:**
  1. Destacar en la barra lateral el indicador verde: `NIVEL: BABY`, `PUNTUACION: 0`, `FORMA: CIRCULAR`.
  2. Mover la serpiente usando las flechas de dirección.
  3. Comer una o dos frutas rojas normales: el puntaje sube (+10, +20) y la serpiente crece.
  4. Presionar la tecla `T` para mostrar en vivo cómo el cuerpo cambia a **triángulos** y luego `C` para volver a **círculos** (demostrando la personalización geométrica).
* **Guión de Voz / Locución:**
  > *"Iniciamos en el nivel por defecto: BABY. La velocidad de tick es moderada (0.15 segundos), la forma geométrica de los segmentos es circular y la comida es estándar. Al pulsar la tecla 'T', vemos cómo los segmentos alternan inmediatamente a triángulos y con 'C' regresan a círculos, cumpliendo la personalización geométrica desde la gramática."*

---

### Escena 3: Nivel 2 - ENTUSIASTA y Power-Up "No Morir" (0:50 - 1:30)
* **Acción en Pantalla:**
  1. Comer frutas hasta superar los 30 puntos o presionar la tecla `2` para forzar la transición a `ENTUSIASTA`.
  2. Mostrar en consola el anuncio: `>>> CAMBIO DE NIVEL ACTIVADO: ENTUSIASTA <<<`.
  3. En la barra lateral se observa el nivel en ámbar y la mayor velocidad de tick (0.10s).
  4. En el tablero aparece la **fruta venenosa** (morada con cruz) y el **Power-Up "No Morir"** (estrella dorada brillante).
  5. Recoger la estrella dorada:
     - La serpiente resplandece en dorado.
     - En la barra lateral se activa el cronómetro regresivo en vivo: `★ NO MORIR ★ [6.0s -> 0.0s]`.
  6. Mientras está activa la invulnerabilidad, chocar intencionalmente contra la pared o contra la fruta venenosa para mostrar que **no muere ni pierde puntos**.
  7. Dejar que el contador llegue a `0.0s` y mostrar que el estado vuelve a `NORMAL`.
* **Guión de Voz / Locución:**
  > *"Avanzamos al nivel ENTUSIASTA. Notamos que la velocidad de tick aumenta a 0.10 segundos y aparecen dos nuevas entidades: la fruta venenosa morada y el Power-Up dorado 'No Morir'. Al recoger el power-up, nuestro State Manager inicia la cuenta regresiva de 6 segundos en la interfaz. Mientras el escudo está activo, la serpiente es totalmente inmune a colisiones y veneno. Al agotarse el temporizador, el estado regresa a normal."*

---

### Escena 4: Nivel 3 - NYAN CAT (Cola Arcoíris y Cabeza Especial) (1:30 - 2:10)
* **Acción en Pantalla:**
  1. Superar los 80 puntos o presionar la tecla `3` para ingresar al nivel `NYAN_CAT`.
  2. Resaltar visualmente:
     - La velocidad de tick sube a máxima velocidad (0.05 segundos).
     - La **cabeza** se convierte en el rostro circular de Nyan Cat (con orejas rosadas, ojos y mejillas).
     - La **cola** ondula dinámicamente con los 7 colores del arcoíris en movimiento continuo.
     - Aparecen **3 nubes obstáculo** fijas en el mapa.
* **Guión de Voz / Locución:**
  > *"Ingresamos ahora al nivel de dificultad máxima: NYAN CAT. La velocidad se triplica a 0.05 segundos por tick. Aprecien el detalle estético: la cabeza adopta los rasgos faciales de Nyan Cat con sus orejas y mejillas, y la cola despliega una animación arcoíris multicolor dinámica que fluye segmento a segmento mediante el operador módulo."*

---

### Escena 5: Colisión con Nubes Obstáculo (2:10 - 2:40)
* **Acción en Pantalla:**
  1. **Prueba A (Con puntos):** Teniendo puntos (ej. 40 o 50 puntos), dirigir la serpiente contra una nube obstáculo. Mostrar cómo la puntuación cae a 0, pero la serpiente sigue viva.
  2. **Prueba B (Sin puntos):** Dirigir la serpiente con 0 puntos hacia una nube obstáculo: se produce el `GAME OVER` inmediato.
* **Guión de Voz / Locución:**
  > *"Validamos ahora la regla crítica de colisión con las nubes obstáculo. Al impactar una nube teniendo 40 puntos, el marcador se resetea por completo a 0 pero la serpiente continúa viva. Acto seguido, al colisionar nuevamente teniendo 0 puntos, el impacto es letal y se desencadena el Game Over inmediato, cumpliendo al 100% el requerimiento B."*

---

### Escena 6: Prueba Rápida de Retrocompatibilidad (2:40 - 3:00)
* **Acción en Pantalla:**
  1. En la terminal ejecutar:
     ```bash
     ./jugar.sh tetris
     ```
     Mostrar que Tetris compila y juega perfectamente con sus piezas de colores y rotaciones.
  2. Ejecutar:
     ```bash
     ./jugar.sh snake
     ```
     Mostrar que el Snake original compila e inicia en modo Baby sin errores.
* **Guión de Voz / Locución:**
  > *"Finalmente, verificamos la retrocompatibilidad total: el mismo compilador y runtime ejecutan sin modificaciones tanto el Tetris de la Actividad 3 como el Snake original en modo Baby por defecto. Con esto concluimos la entrega de la Actividad 4."*

---

## 3. Atajos de Teclado Disponibles durante la Grabación

Para que la grabación sea ágil y perfecta sin depender del azar, puedes usar estos atajos en cualquier momento:

| Tecla | Acción en el Juego |
| :---: | :--- |
| `1` | Cambiar inmediatamente al Nivel **BABY** |
| `2` | Cambiar inmediatamente al Nivel **ENTUSIASTA** (activa veneno y power-up) |
| `3` | Cambiar inmediatamente al Nivel **NYAN CAT** (activa nubes, arcoíris y gato) |
| `P` | Activar / Spawnear de inmediato el Power-Up **"No Morir"** |
| `V` | Spawnear una **Fruta Venenosa** en el grid |
| `C` | Cambiar forma de segmentos a **CÍRCULO** |
| `T` | Cambiar forma de segmentos a **TRIÁNGULO** |
| `R` | Cambiar forma de segmentos a **RECTÁNGULO** |
| `Q` | Salir del juego limpiamente |
