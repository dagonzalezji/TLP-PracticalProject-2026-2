# -*- coding: utf-8 -*-
# runtime.py (VERSION CON INTERFAZ GRAFICA USANDO Tkinter y caracteres ASCII unicamente)
# Adaptado para Python 3 - Soporte Ecosistema BrickScript (Tetris, Snake Original y Snake Evolved)

import sys
import json
import time
import random
# tkinter es la libreria GUI estandar de Python
import tkinter as tk
from tkinter import messagebox as tkMessageBox

class Juego:
    def __init__(self, datos_juego):
        self.datos_juego = datos_juego
        self.tipo_juego = self.datos_juego.get('tipo_juego', 'TETRIS')
        config = self.datos_juego.get('config', {})
        self.ancho = config.get('grid_size', [10, 20])[0]
        self.alto = config.get('grid_size', [10, 20])[1]
        self.grid = [[0 for _ in range(self.ancho)] for _ in range(self.alto)]
        self.puntuacion = 0
        self.juego_terminado = False
        
        # --- Configuracion de la GUI ---
        self.root = tk.Tk()
        self.root.title("BrickScript - " + self.tipo_juego)
        # Configurar la accion al cerrar la ventana ('X' de la barra de titulo)
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)
        
        self.taman_celda = 25 # Pixeles por celda
        self.ancho_canvas = self.ancho * self.taman_celda
        self.alto_canvas = self.alto * self.taman_celda
        
        # Canvas para dibujar el juego con estilo retro oscuro
        self.canvas = tk.Canvas(self.root, width=self.ancho_canvas, height=self.alto_canvas, bg='#111827', highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)

        # Marco lateral para la puntuacion, niveles, estados y controles
        self.marco_score = tk.Frame(self.root, width=190, height=self.alto_canvas, bg='#1F2937')
        self.marco_score.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Titulo del juego en lateral
        self.label_titulo = tk.Label(self.marco_score, text=self.tipo_juego, bg='#1F2937', fg='#60A5FA', font=('Consolas', 14, 'bold'))
        self.label_titulo.pack(pady=(15, 5), padx=10)

        # Puntuacion
        self.label_score = tk.Label(self.marco_score, text="PUNTUACION\n0", bg='#1F2937', fg='white', font=('Consolas', 15, 'bold'))
        self.label_score.pack(pady=10, padx=10)
        
        # Nivel de dificultad (Snake)
        self.label_nivel = tk.Label(self.marco_score, text="", bg='#1F2937', fg='#10B981', font=('Consolas', 11, 'bold'))
        self.label_nivel.pack(pady=5, padx=10)

        # Estado del Power-Up (Snake)
        self.label_powerup = tk.Label(self.marco_score, text="", bg='#1F2937', fg='#9CA3AF', font=('Consolas', 10, 'bold'))
        self.label_powerup.pack(pady=5, padx=10)

        # Forma de la serpiente
        self.label_forma = tk.Label(self.marco_score, text="", bg='#1F2937', fg='#A78BFA', font=('Consolas', 9))
        self.label_forma.pack(pady=2, padx=10)

        # Controles
        controles_texto = "CONTROLES\nFlechas: Mover\nQ: Salir"
        if self.tipo_juego == 'SNAKE':
            controles_texto = "CONTROLES\nFlechas: Mover\n1/2/3: Nivel\nP: Power-Up\nC/T/R: Forma\nQ: Salir"
        self.label_controles = tk.Label(self.marco_score, text=controles_texto, bg='#1F2937', fg='#9CA3AF', font=('Consolas', 9), justify=tk.LEFT)
        self.label_controles.pack(side=tk.BOTTOM, pady=15, padx=10)

        # Configurar eventos de teclado. Usamos <Key> para capturar cualquier tecla
        self.root.bind('<Key>', self.manejar_input_gui)
        
        if self.tipo_juego == 'TETRIS':
            self.pieza_actual = None
            self.pieza_x, self.pieza_y, self.pieza_rotacion = 0, 0, 0
            self.velocidad_gravedad = 0.4
            self.lineas_limpias_total = 0
            self.spawn_powerup = False
        
        if self.tipo_juego == 'SNAKE':
            self.serpiente_cuerpo = []
            self.serpiente_direccion = (1, 0)
            self.posicion_comida = None
            self.posicion_veneno = None
            self.posicion_powerup = None
            self.nubes = []
            
            # --- Configuracion de Niveles (Retrocompatibilidad) ---
            # Si el archivo .brick no incluye el bloque LEVELS, se asume Baby por defecto
            self.niveles_config = self.datos_juego.get('levels', {})
            if not self.niveles_config:
                self.niveles_config = {
                    'BABY': {'TICK_SPEED': '0.15', 'SCORE_THRESHOLD': '0'}
                }
            
            # Estado actual de nivel
            self.nivel_actual = 'BABY'
            self.velocidad_gravedad = float(self.obtener_prop_nivel('TICK_SPEED', 0.15))
            
            # --- Manejador de Estados (State Manager) para Power-Up "No Morir" ---
            self.powerup_activo = False
            self.powerup_tiempo_restante = 0.0
            
            # Obtener duracion configurada del power-up desde el JSON
            props_shapes = self.datos_juego.get('shape_properties', {})
            props_powerup = props_shapes.get('POWERUP_FOOD', {})
            self.powerup_duracion_config = float(props_powerup.get('DURATION', self.niveles_config.get('ENTUSIASTA', {}).get('POWERUP_DURATION', 6)))

            # --- Personalizacion Geometrica de la Serpiente ---
            props_body = props_shapes.get('SNAKE_BODY', {})
            props_pixel = props_shapes.get('PIXEL', {})
            self.forma_cuerpo = props_body.get('TYPE', props_pixel.get('TYPE', 'RECTANGULAR')).upper()
            
            # Colores base
            self.color_cabeza = props_shapes.get('SNAKE_HEAD', {}).get('COLOR', '#00FF00')
            self.color_cuerpo = props_body.get('COLOR', '#33CC33')
            self.color_comida = props_shapes.get('FOOD', {}).get('COLOR', '#FF1744')
            self.color_veneno = props_shapes.get('POISON_FOOD', {}).get('COLOR', '#9900EF')
            self.color_powerup = props_shapes.get('POWERUP_FOOD', {}).get('COLOR', '#FFD700')
            self.color_nube = props_shapes.get('CLOUD_OBSTACLE', {}).get('COLOR', '#BAE6FD')

            # Paleta de colores dinamica para la cola multicolor de Nyan Cat
            self.colores_rainbow = ['#FF0000', '#FF7F00', '#FFFF00', '#00FF00', '#0099FF', '#4B0082', '#8F00FF']
            self.rainbow_offset = 0

        self.timer_gravedad = 0
        self.ejecutar_evento('ON_START')
        self.timer_id = None # Para controlar el loop de Tkinter

    def obtener_prop_nivel(self, prop, default=None):
        nivel_datos = self.niveles_config.get(self.nivel_actual, {})
        return nivel_datos.get(prop, default)

    def run(self):
        # Inicia el ciclo principal de juego de Tkinter
        self.root.after(50, self.game_loop) 
        self.root.mainloop() 

    def game_loop(self):
        if self.juego_terminado:
            self.mostrar_game_over()
            return

        # Logica del Manejador de Estados (State Manager) para Power-Up
        if self.tipo_juego == 'SNAKE':
            if self.powerup_tiempo_restante > 0:
                self.powerup_tiempo_restante = max(0.0, self.powerup_tiempo_restante - 0.05)
                if self.powerup_tiempo_restante <= 0:
                    self.powerup_activo = False
                    print(">>> EL POWER-UP 'NO MORIR' HA EXPIRADO <<<")
            
            # Ciclar efecto multicolor dinamico de Nyan Cat
            if self.nivel_actual == 'NYAN_CAT':
                self.rainbow_offset = (self.rainbow_offset + 1) % len(self.colores_rainbow)

        # Logica de TICK/Gravedad
        # El loop se ejecuta cada 50ms (0.05 segundos)
        self.timer_gravedad += 0.05 
        if self.timer_gravedad >= self.velocidad_gravedad:
            self.timer_gravedad = 0
            self.ejecutar_evento('ON_TICK')

        self.dibujar()

        # Programa el siguiente ciclo de juego
        self.timer_id = self.root.after(50, self.game_loop)
        
    def cerrar_ventana(self):
        # Detiene el loop de juego de forma segura
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.root.destroy()
        sys.exit(0)

    def manejar_input_gui(self, event):
        key = event.keysym.upper()
        
        if key == 'Q':
            self.cerrar_ventana()
            return

        # Mapeo de teclas para Tetris
        if self.tipo_juego == 'TETRIS':
            if key == 'UP': self.ejecutar_evento('ON_KEY_UP')
            elif key == 'DOWN': self.ejecutar_evento('ON_KEY_DOWN')
            elif key == 'LEFT': self.ejecutar_evento('ON_KEY_LEFT')
            elif key == 'RIGHT': self.ejecutar_evento('ON_KEY_RIGHT')

        # Mapeo de teclas para Snake
        elif self.tipo_juego == 'SNAKE':
            # Movimiento
            if key == 'UP': self.snake_cambiar_direccion('UP')
            elif key == 'DOWN': self.snake_cambiar_direccion('DOWN')
            elif key == 'LEFT': self.snake_cambiar_direccion('LEFT')
            elif key == 'RIGHT': self.snake_cambiar_direccion('RIGHT')
            
            # Cambio de niveles en tiempo real (util para demostracion en video y validacion)
            elif key == '1':
                self.cambiar_nivel('BABY')
            elif key == '2':
                self.cambiar_nivel('ENTUSIASTA')
            elif key == '3':
                self.cambiar_nivel('NYAN_CAT')
                
            # Hotkey para probar el Power-Up "No Morir"
            elif key == 'P':
                print(">>> TECLA 'P' PULSADA: Activando Power-Up 'No Morir' <<<")
                dur = float(self.obtener_prop_nivel('POWERUP_DURATION', self.powerup_duracion_config))
                self.activar_powerup(dur)

            # Hotkey para probar la Fruta Venenosa
            elif key == 'V':
                self.snake_spawn_veneno()

            # Hotkeys para alternar la forma geometrica en vivo
            elif key == 'C':
                self.forma_cuerpo = 'CIRCULAR'
                print(">>> FORMA GEOMÉTRICA CAMBIADA A: CIRCULAR <<<")
            elif key == 'T':
                self.forma_cuerpo = 'TRIANGULAR'
                print(">>> FORMA GEOMÉTRICA CAMBIADA A: TRIANGULAR <<<")
            elif key == 'R':
                self.forma_cuerpo = 'RECTANGULAR'
                print(">>> FORMA GEOMÉTRICA CAMBIADA A: RECTANGULAR <<<")

    # =========================================================================
    # METODOS DE DIBUJO Y RENDERIZADO GRAFICO
    # =========================================================================

    def dibujar_celda(self, x, y, color, forma='RECTANGULAR'):
        ts = self.taman_celda
        x1, y1 = x * ts, y * ts
        x2, y2 = x1 + ts, y1 + ts

        if forma == 'CIRCULAR':
            self.canvas.create_oval(x1 + 1, y1 + 1, x2 - 1, y2 - 1, fill=color, outline='#000000', width=1)
        elif forma == 'TRIANGULAR':
            # Triangulo centrado dentro de la celda
            pts = [(x1 + x2) / 2.0, y1 + 1, x1 + 1, y2 - 1, x2 - 1, y2 - 1]
            self.canvas.create_polygon(pts, fill=color, outline='#000000', width=1)
        else:
            # Rectangular por defecto
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='#000000', width=1)

    def dibujar_cabeza_nyan_cat(self, x, y):
        """Renderiza una cabeza circular con rasgos distintivos de gato para el Nivel Nyan Cat."""
        ts = self.taman_celda
        x1, y1 = x * ts, y * ts
        x2, y2 = x1 + ts, y1 + ts
        cx, cy = (x1 + x2) / 2.0, (y1 + y2) / 2.0

        # Oreja izquierda (triangulo rosa)
        oreja_izq = [x1 + 2, y1 + 7, x1 + 6, y1 + 1, x1 + 10, y1 + 7]
        self.canvas.create_polygon(oreja_izq, fill='#F472B6', outline='#000000')

        # Oreja derecha (triangulo rosa)
        oreja_der = [x2 - 10, y1 + 7, x2 - 6, y1 + 1, x2 - 2, y1 + 7]
        self.canvas.create_polygon(oreja_der, fill='#F472B6', outline='#000000')

        # Cabeza circular (color gris claro/gato)
        color_cara = '#FCD34D' if self.powerup_activo else '#E5E7EB'
        self.canvas.create_oval(x1 + 2, y1 + 4, x2 - 2, y2 - 1, fill=color_cara, outline='#000000', width=1.5)

        # Ojos negros
        self.canvas.create_oval(cx - 5, cy - 2, cx - 2, cy + 1, fill='#000000')
        self.canvas.create_oval(cx + 2, cy - 2, cx + 5, cy + 1, fill='#000000')

        # Mejillas rosadas
        self.canvas.create_oval(cx - 7, cy + 2, cx - 5, cy + 4, fill='#FB7185', outline='')
        self.canvas.create_oval(cx + 5, cy + 2, cx + 7, cy + 4, fill='#FB7185', outline='')

        # Nariz / boca
        self.canvas.create_oval(cx - 1, cy + 2, cx + 1, cy + 4, fill='#BE185D', outline='')

    def dibujar_nube(self, x, y):
        """Renderiza una entidad fija de nube obstaculo en el mapa."""
        ts = self.taman_celda
        x1, y1 = x * ts, y * ts
        x2, y2 = x1 + ts, y1 + ts

        # Dibujar circulos superpuestos acolchonados para efecto de nube
        self.canvas.create_oval(x1 + 1, y1 + 6, x1 + 15, y2 - 2, fill='#BAE6FD', outline='#38BDF8', width=1)
        self.canvas.create_oval(x1 + 10, y1 + 5, x2 - 1, y2 - 2, fill='#BAE6FD', outline='#38BDF8', width=1)
        self.canvas.create_oval(x1 + 5, y1 + 2, x1 + 19, y2 - 4, fill='#FFFFFF', outline='#38BDF8', width=1.5)

    def dibujar_fruta_venenosa(self, x, y):
        """Renderiza una fruta venenosa (morada con detalles de advertencia)."""
        ts = self.taman_celda
        x1, y1 = x * ts, y * ts
        x2, y2 = x1 + ts, y1 + ts
        cx, cy = (x1 + x2) / 2.0, (y1 + y2) / 2.0

        # Cuerpo venenoso
        self.canvas.create_oval(x1 + 3, y1 + 3, x2 - 3, y2 - 3, fill=self.color_veneno, outline='#4C1D95', width=1.5)
        # Tallo
        self.canvas.create_line(cx, y1 + 3, cx + 3, y1 + 7, fill='#22C55E', width=2)
        # Simbolo de veneno (X pequena)
        self.canvas.create_text(cx, cy + 1, text="X", fill='#FFFFFF', font=('Consolas', 9, 'bold'))

    def dibujar_powerup(self, x, y):
        """Renderiza la fruta especial Power-Up 'No Morir' (estrella dorada brillante)."""
        ts = self.taman_celda
        x1, y1 = x * ts, y * ts
        x2, y2 = x1 + ts, y1 + ts
        cx, cy = (x1 + x2) / 2.0, (y1 + y2) / 2.0

        # Circulo dorado con resplandor
        self.canvas.create_oval(x1 + 2, y1 + 2, x2 - 2, y2 - 2, fill='#FBBF24', outline='#D97706', width=2)
        # Estrella central
        self.canvas.create_text(cx, cy, text="★", fill='#FFFFFF', font=('Arial', 13, 'bold'))

    def dibujar(self):
        self.canvas.delete("all") # Borrar todo en cada frame
        
        # Actualizar Etiquetas de la barra lateral
        self.label_score.config(text="PUNTUACION\n" + str(self.puntuacion))
        
        if self.tipo_juego == 'SNAKE':
            # Indicador de Nivel
            colores_nivel = {'BABY': '#10B981', 'ENTUSIASTA': '#F59E0B', 'NYAN_CAT': '#EC4899'}
            color_lbl = colores_nivel.get(self.nivel_actual, '#10B981')
            self.label_nivel.config(text="NIVEL:\n" + self.nivel_actual.replace('_', ' '), fg=color_lbl)
            
            # Indicador de Power-Up "No Morir"
            if self.powerup_activo:
                self.label_powerup.config(
                    text="★ NO MORIR ★\n[{:.1f}s]".format(self.powerup_tiempo_restante),
                    fg='#FBBF24'
                )
            else:
                self.label_powerup.config(text="ESTADO: NORMAL", fg='#6B7280')

            # Indicador de Forma
            self.label_forma.config(text="FORMA: " + self.forma_cuerpo)

        # 1. Dibujar la cuadricula estatica (grid base)
        COLOR_GRID_FIJA = '#374151' # Gris oscuro para las celdas fijadas (Tetris)
        for y in range(self.alto):
            for x in range(self.ancho):
                if self.grid[y][x] == 1:
                    self.dibujar_celda(x, y, COLOR_GRID_FIJA, forma='RECTANGULAR')

        # 2. Dibujar la pieza actual de Tetris
        if self.tipo_juego == 'TETRIS' and self.pieza_actual:
            matriz_pieza = self.pieza_actual[self.pieza_rotacion]
            for y_offset, fila in enumerate(matriz_pieza):
                for x_offset, celda in enumerate(fila):
                    if celda == 1:
                        self.dibujar_celda(self.pieza_x + x_offset, self.pieza_y + y_offset, getattr(self, 'color_pieza_actual', '#00FFFF'))
        
        # 3. Dibujar elementos de Snake
        if self.tipo_juego == 'SNAKE':
            # Dibujar Nubes Obstaculo (fijas en el mapa en nivel Nyan Cat)
            for nube_pos in self.nubes:
                self.dibujar_nube(nube_pos[0], nube_pos[1])

            # Dibujar Comida Normal
            if self.posicion_comida:
                x, y = self.posicion_comida
                self.dibujar_celda(x, y, self.color_comida, forma='CIRCULAR')

            # Dibujar Fruta Venenosa (si esta activa en el mapa)
            if self.posicion_veneno:
                x, y = self.posicion_veneno
                self.dibujar_fruta_venenosa(x, y)

            # Dibujar Power-Up "No Morir" (si esta activo en el mapa)
            if self.posicion_powerup:
                x, y = self.posicion_powerup
                self.dibujar_powerup(x, y)

            # Dibujar la Serpiente
            for i, segmento in enumerate(self.serpiente_cuerpo):
                x, y = segmento
                
                # Cabeza
                if i == 0:
                    if self.nivel_actual == 'NYAN_CAT':
                        self.dibujar_cabeza_nyan_cat(x, y)
                    else:
                        color_cabeza = '#FBBF24' if self.powerup_activo else self.color_cabeza
                        self.dibujar_celda(x, y, color_cabeza, forma=self.forma_cuerpo)
                
                # Segmentos del Cuerpo / Cola
                else:
                    if self.nivel_actual == 'NYAN_CAT':
                        # Cola multicolor dinamica para Nyan Cat usando operador modulo %
                        idx_color = (i - 1 + self.rainbow_offset) % len(self.colores_rainbow)
                        color_seg = self.colores_rainbow[idx_color]
                    else:
                        color_seg = '#FDE68A' if self.powerup_activo else self.color_cuerpo
                    
                    self.dibujar_celda(x, y, color_seg, forma=self.forma_cuerpo)

    def ejecutar_evento(self, nombre_evento):
        if nombre_evento in self.datos_juego.get('events', {}):
            for accion in self.datos_juego['events'][nombre_evento]:
                verbo, objeto = accion.get('accion'), accion.get('objeto')
                
                if verbo == 'INCREASE_SCORE': self.puntuacion += int(objeto)
                if verbo == 'GAME_OVER': self.juego_terminado = True

                if self.tipo_juego == 'TETRIS':
                    if verbo == 'SPAWN': self.tetris_spawn_pieza()
                    if verbo == 'MOVE': self.tetris_mover_pieza(accion['params'][0])
                    if verbo == 'ROTATE': self.tetris_rotar_pieza()
                
                if self.tipo_juego == 'SNAKE':
                    if verbo == 'SPAWN' and objeto == 'PLAYER': self.snake_spawn_jugador(accion)
                    if verbo == 'SPAWN' and objeto == 'FOOD': self.snake_spawn_comida()
                    if verbo == 'MOVE' and objeto == 'PLAYER': self.snake_mover_jugador()
                    if verbo == 'GROW': self.snake_crecer()

    # =========================================================================
    # METODOS DE LOGICA DE TETRIS (PRESERVADOS INTACTOS)
    # =========================================================================

    def tetris_spawn_pieza(self):
        shapes = list(self.datos_juego['shapes'].keys())
        shape_props = self.datos_juego.get('shape_properties', {})
        
        # Calculate weights for probabilities
        weights = []
        for shape in shapes:
            props = shape_props.get(shape, {})
            chance = int(props.get('CHANCE', 10))
            weights.append(chance)
            
        total = sum(weights)
        r = random.uniform(0, total)
        upto = 0
        nombre_pieza = shapes[0]
        
        if getattr(self, 'spawn_powerup', False) and 'POWERUP_PIECE' in shapes:
            nombre_pieza = 'POWERUP_PIECE'
            self.spawn_powerup = False
        else:
            for i, w in enumerate(weights):
                if upto + w >= r:
                    nombre_pieza = shapes[i]
                    break
                upto += w
            
        self.pieza_actual = self.datos_juego['shapes'][nombre_pieza]
        
        props = shape_props.get(nombre_pieza, {})
        self.color_pieza_actual = props.get('COLOR', '#00FFFF')
        
        self.pieza_x, self.pieza_y, self.pieza_rotacion = self.ancho // 2 - 2, 0, 0
        if self.tetris_verificar_colision(self.pieza_x, self.pieza_y, self.pieza_rotacion):
            self.juego_terminado = True

    def tetris_mover_pieza(self, direccion):
        if not self.pieza_actual: return
        dx, dy = 0, 0
        if direccion == 'LEFT': dx = -1
        elif direccion == 'RIGHT': dx = 1
        elif direccion == 'DOWN': dy = 1
        if not self.tetris_verificar_colision(self.pieza_x + dx, self.pieza_y + dy, self.pieza_rotacion):
            self.pieza_x += dx
            self.pieza_y += dy
        elif dy > 0:
            self.tetris_fijar_pieza()

    def tetris_rotar_pieza(self):
        if not self.pieza_actual: return
        nueva_rotacion = (self.pieza_rotacion + 1) % len(self.pieza_actual)
        if not self.tetris_verificar_colision(self.pieza_x, self.pieza_y, nueva_rotacion):
            self.pieza_rotacion = nueva_rotacion

    def tetris_fijar_pieza(self):
        matriz_pieza = self.pieza_actual[self.pieza_rotacion]
        for y_offset, fila in enumerate(matriz_pieza):
            for x_offset, celda in enumerate(fila):
                if celda == 1:
                    if 0 <= self.pieza_y + y_offset < self.alto and 0 <= self.pieza_x + x_offset < self.ancho:
                        self.grid[self.pieza_y + y_offset][self.pieza_x + x_offset] = 1
        self.pieza_actual = None
        self.tetris_limpiar_lineas()
        self.ejecutar_evento('ON_START')

    def tetris_verificar_colision(self, x, y, rotacion):
        if not self.pieza_actual: return False
        matriz_pieza = self.pieza_actual[rotacion]
        for y_offset, fila in enumerate(matriz_pieza):
            for x_offset, celda in enumerate(fila):
                if celda == 1:
                    nuevo_x, nuevo_y = x + x_offset, y + y_offset
                    if not (0 <= nuevo_x < self.ancho and 0 <= nuevo_y < self.alto and self.grid[nuevo_y][nuevo_x] == 0):
                        return True
        return False

    def tetris_limpiar_lineas(self):
        nuevo_grid = [fila for fila in self.grid if not all(fila)]
        lineas_limpias = self.alto - len(nuevo_grid)
        if lineas_limpias > 0:
            self.grid = [[0] * self.ancho for _ in range(lineas_limpias)] + nuevo_grid
            for _ in range(lineas_limpias): self.ejecutar_evento('ON_LINE_CLEAR')
            
            self.lineas_limpias_total += lineas_limpias
            if self.lineas_limpias_total >= 2:
                self.spawn_powerup = True
                self.lineas_limpias_total = 0

    # =========================================================================
    # METODOS DE LOGICA DE SNAKE EVOLVED (ACTIVIDAD 4)
    # =========================================================================

    def snake_spawn_jugador(self, accion):
        coords = accion['params'][0] if accion.get('params') else [self.ancho // 2, self.alto // 2]
        self.serpiente_cuerpo = [(coords[0], coords[1])]
        self.serpiente_direccion = (0, 0) # Inicia quieto hasta presionar una tecla

    def posiciones_ocupadas(self):
        ocupadas = set(self.serpiente_cuerpo)
        if self.posicion_comida: ocupadas.add(self.posicion_comida)
        if self.posicion_veneno: ocupadas.add(self.posicion_veneno)
        if self.posicion_powerup: ocupadas.add(self.posicion_powerup)
        for n in self.nubes: ocupadas.add(n)
        return ocupadas

    def snake_spawn_comida(self):
        ocupadas = self.posiciones_ocupadas()
        libres = [(x, y) for x in range(self.ancho) for y in range(self.alto) if (x, y) not in ocupadas]
        if libres:
            self.posicion_comida = random.choice(libres)

    def snake_spawn_veneno(self):
        """Genera una fruta venenosa en el mapa (solo activa en niveles Entusiasta y Nyan Cat)."""
        if self.nivel_actual in ['ENTUSIASTA', 'NYAN_CAT']:
            ocupadas = self.posiciones_ocupadas()
            libres = [(x, y) for x in range(self.ancho) for y in range(self.alto) if (x, y) not in ocupadas]
            if libres:
                self.posicion_veneno = random.choice(libres)
        else:
            self.posicion_veneno = None

    def snake_spawn_powerup(self):
        """Genera el Power-Up 'No Morir' en el mapa."""
        if self.nivel_actual in ['ENTUSIASTA', 'NYAN_CAT'] and not self.posicion_powerup and not self.powerup_activo:
            ocupadas = self.posiciones_ocupadas()
            libres = [(x, y) for x in range(self.ancho) for y in range(self.alto) if (x, y) not in ocupadas]
            if libres:
                self.posicion_powerup = random.choice(libres)

    def inicializar_nubes(self):
        """Genera entidades fijas de obstaculo (nubes) para el nivel Nyan Cat."""
        self.nubes = []
        if self.nivel_actual == 'NYAN_CAT':
            cant_nubes = int(self.obtener_prop_nivel('OBSTACLES', 3))
            posibles = [
                (4, 4), (self.ancho - 5, 4),
                (self.ancho // 2, self.alto // 2),
                (4, self.alto - 5), (self.ancho - 5, self.alto - 5)
            ]
            cabeza = self.serpiente_cuerpo[0] if self.serpiente_cuerpo else (self.ancho // 2, self.alto // 2)
            candidatas = [p for p in posibles if p != cabeza and 0 <= p[0] < self.ancho and 0 <= p[1] < self.alto]
            random.shuffle(candidatas)
            self.nubes = candidatas[:cant_nubes]

    def activar_powerup(self, duracion=None):
        """Manejador de Estados: Activa la invulnerabilidad temporal durante n segundos."""
        if duracion is None:
            duracion = float(self.obtener_prop_nivel('POWERUP_DURATION', self.powerup_duracion_config))
        self.powerup_activo = True
        self.powerup_tiempo_restante = float(duracion)
        print(">>> POWER-UP 'NO MORIR' ACTIVADO! Duracion: {:.1f} segundos <<<".format(duracion))

    def cambiar_nivel(self, nuevo_nivel):
        """Transiciona entre niveles de dificultad actualizando velocidad y entidades."""
        self.nivel_actual = nuevo_nivel
        self.velocidad_gravedad = float(self.obtener_prop_nivel('TICK_SPEED', 0.15))
        
        print("\n=======================================================")
        print(">>> CAMBIO DE NIVEL ACTIVADO: {} <<<".format(nuevo_nivel))
        print("Velocidad de Tick: {}s".format(self.velocidad_gravedad))
        
        if nuevo_nivel == 'BABY':
            self.posicion_veneno = None
            self.posicion_powerup = None
            self.nubes = []
            print("Configuracion: Estandar (Sin veneno ni obstaculos)")
        elif nuevo_nivel == 'ENTUSIASTA':
            self.nubes = []
            self.snake_spawn_veneno()
            self.snake_spawn_powerup()
            print("Configuracion: Frutas venenosas y Power-Up 'No Morir' habilitados")
        elif nuevo_nivel == 'NYAN_CAT':
            self.snake_spawn_veneno()
            self.snake_spawn_powerup()
            self.inicializar_nubes()
            print("Configuracion: Nubes obstaculo activas, Cola Multicolor y Cabeza Nyan Cat")
        print("=======================================================\n")

    def verificar_transicion_nivel(self):
        """Comprueba si la puntuacion amerita una transicion automatica de nivel."""
        if not self.niveles_config:
            return

        nyan_cfg = self.niveles_config.get('NYAN_CAT')
        if nyan_cfg:
            umbral_nyan = int(nyan_cfg.get('SCORE_THRESHOLD', 80))
            if self.puntuacion >= umbral_nyan and self.nivel_actual != 'NYAN_CAT':
                self.cambiar_nivel('NYAN_CAT')
                return

        ent_cfg = self.niveles_config.get('ENTUSIASTA')
        if ent_cfg:
            umbral_ent = int(ent_cfg.get('SCORE_THRESHOLD', 30))
            if self.puntuacion >= umbral_ent and self.nivel_actual == 'BABY':
                self.cambiar_nivel('ENTUSIASTA')
                return

    def snake_mover_jugador(self):
        if not self.serpiente_cuerpo: return
        cabeza_x, cabeza_y = self.serpiente_cuerpo[0]
        dir_x, dir_y = self.serpiente_direccion
        if dir_x == 0 and dir_y == 0:
            return # No mover hasta que haya una direccion inicial
            
        nueva_cabeza = (cabeza_x + dir_x, cabeza_y + dir_y)

        # 1. Gestion de Colision con Paredes
        if not (0 <= nueva_cabeza[0] < self.ancho and 0 <= nueva_cabeza[1] < self.alto):
            if self.powerup_activo:
                # Con Power-Up "No Morir", la serpiente no muere por paredes (rebobina o atraviesa)
                nueva_cabeza = (nueva_cabeza[0] % self.ancho, nueva_cabeza[1] % self.alto)
            else:
                self.ejecutar_evento('ON_COLLISION_WALL')
                return
            
        # 2. Gestion de Auto-colision
        if nueva_cabeza in self.serpiente_cuerpo[:-1]:
            if not self.powerup_activo:
                self.ejecutar_evento('ON_COLLISION_SELF')
                return

        # 3. Gestion de Colision con Nubes Obstaculo
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

        # Insertar nueva cabeza
        self.serpiente_cuerpo.insert(0, nueva_cabeza)
        crecio = False

        # 4. Consumo de Comida Normal
        if nueva_cabeza == self.posicion_comida:
            crecio = True
            self.ejecutar_evento('ON_EAT_FOOD')
            self.verificar_transicion_nivel()
            # Probabilidad de aparicion de power-up en niveles avanzados
            if self.nivel_actual in ['ENTUSIASTA', 'NYAN_CAT'] and not self.posicion_powerup and not self.powerup_activo:
                if random.random() < 0.4:
                    self.snake_spawn_powerup()

        # 5. Consumo de Fruta Venenosa
        elif self.posicion_veneno and nueva_cabeza == self.posicion_veneno:
            if self.powerup_activo:
                print(">>> Fruta venenosa consumida SIN efecto (Power-Up 'No Morir' activo) <<<")
            else:
                penalizacion = int(self.obtener_prop_nivel('POISON_PENALTY', 10))
                print(">>> FRUTA VENENOSA CONSUMIDA! Penalizacion: -{} puntos <<<".format(penalizacion))
                if self.nivel_actual == 'NYAN_CAT' and self.puntuacion <= 0:
                    print(">>> Consumo de veneno con 0 puntos en Nivel Nyan Cat: GAME OVER! <<<")
                    self.juego_terminado = True
                    return
                self.puntuacion = max(0, self.puntuacion - penalizacion)
            self.snake_spawn_veneno()

        # 6. Consumo de Power-Up "No Morir"
        elif self.posicion_powerup and nueva_cabeza == self.posicion_powerup:
            dur = float(self.obtener_prop_nivel('POWERUP_DURATION', self.powerup_duracion_config))
            self.activar_powerup(dur)
            self.posicion_powerup = None

        # Si no comio fruta normal, retirar el ultimo segmento para mantener longitud
        if not crecio:
            self.serpiente_cuerpo.pop()

    def snake_cambiar_direccion(self, direccion):
        if direccion == 'UP' and self.serpiente_direccion[1] != 1:
            self.serpiente_direccion = (0, -1)
        elif direccion == 'DOWN' and self.serpiente_direccion[1] != -1:
            self.serpiente_direccion = (0, 1)
        elif direccion == 'LEFT' and self.serpiente_direccion[0] != 1:
            self.serpiente_direccion = (-1, 0)
        elif direccion == 'RIGHT' and self.serpiente_direccion[0] != -1:
            self.serpiente_direccion = (1, 0)

    def snake_crecer(self):
        pass

    # =========================================================================
    # METODOS DE SALIDA (ADAPTADOS A GUI)
    # =========================================================================

    def mostrar_game_over(self):
        # Muestra mensaje en consola y cierra ventana de forma limpia
        print("GAME OVER! Puntuacion Final:", self.puntuacion)
        try:
            self.root.destroy()
        except Exception:
            pass
        sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 runtime.py <archivo_juego.json>")
        sys.exit(1)
    archivo_juego = sys.argv[1]
    try:
        with open(archivo_juego, 'r') as f:
            datos_juego = json.load(f)
    except IOError:
        print("Error: No se pudo encontrar el archivo " + archivo_juego)
        sys.exit(1)
    juego = Juego(datos_juego)
    juego.run()
