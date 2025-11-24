import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw, ImageEnhance
import random
import math
import os

class DoubleDecisionGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Double Decision - Ruta 66")
        self.root.geometry("1000x800")
        self.root.configure(bg="#1a1a1a")
        
        # Variables del juego
        self.score = 0
        self.level = 1
        self.display_time = 2500
        self.current_vehicle = None
        self.route66_position = None
        self.vehicle_options = []
        self.game_state = "menu"
        
        # Paths de imágenes (ajusta según tu estructura de carpetas)
        self.images_folder = "assets"
        self.vehicles_folder = os.path.join(self.images_folder, "vehicles")
        self.signs_folder = os.path.join(self.images_folder, "signs")
        self.backgrounds_folder = os.path.join(self.images_folder, "backgrounds")
        
        # Almacenar imágenes cargadas
        self.vehicle_images = {}
        self.route66_image = None
        self.background_image = None
        self.sector_images = {}  # Para almacenar las imágenes de sectores transparentes
        self.sector_image_ids = {}  # Para almacenar los IDs de las imágenes en el canvas
        self.sign_images = {}
        
        # Variables para la selección de posición
        self.canvas = None
        self.sector_highlight = None
        self.current_highlighted_sector = 1
        
        self.load_images()
        self.create_menu()
    
    def create_transparent_sector(self, canvas_width, canvas_height, center_x, center_y, 
                                angle_start, angle_end, color_rgb, alpha, is_highlighted=False):
        """Crea un sector triangular con transparencia real usando PIL"""
        # Crear imagen transparente
        img = Image.new('RGBA', (canvas_width, canvas_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        max_distance = max(canvas_width, canvas_height)
        
        # Calcular puntos del triángulo
        rad_start = math.radians(angle_start)
        rad_end = math.radians(angle_end)
        
        x1 = center_x + max_distance * math.cos(rad_start)
        y1 = center_y + max_distance * math.sin(rad_start)
        x2 = center_x + max_distance * math.cos(rad_end)
        y2 = center_y + max_distance * math.sin(rad_end)
        
        # Color con transparencia
        if is_highlighted:
            # Color más brillante para highlight
            color_rgba = (255, 204, 136, alpha)  # Amarillo dorado transparente
            outline_color = (255, 204, 0, 255)   # Borde amarillo sólido
        else:
            # Color base
            color_rgba = (*color_rgb, alpha)
            outline_color = (68, 68, 68, 180)     # Gris transparente
        
        # Dibujar triángulo con transparencia
        draw.polygon([(center_x, center_y), (x1, y1), (x2, y2)], 
                    fill=color_rgba, outline=outline_color, width=2)
        
        return ImageTk.PhotoImage(img)
    
    def load_images(self):
        """Carga todas las imágenes necesarias"""
        try:
            # Intentar cargar imágenes de vehículos (vehicle1.png, vehicle2.png, etc.)
            for i in range(1, 9):
                try:
                    img_path = os.path.join(self.vehicles_folder, f"vehicle{i}.png")
                    if os.path.exists(img_path):
                        img = Image.open(img_path)
                        img = img.resize((150, 150), Image.Resampling.LANCZOS)
                        self.vehicle_images[i-1] = ImageTk.PhotoImage(img)
                except Exception as e:
                    print(f"Error cargando vehicle{i}.png: {e}")
            
            # Cargar señal RUTA 66
            try:
                route66_path = os.path.join(self.signs_folder, "route66.png")
                if os.path.exists(route66_path):
                    img = Image.open(route66_path)
                    img = img.resize((80, 80), Image.Resampling.LANCZOS)
                    self.route66_image = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Error cargando route66.png: {e}")
            
            # Cargar señales distractoras (sign1.png, sign2.png, etc.)
            for i in range(1, 8):
                try:
                    sign_path = os.path.join(self.signs_folder, f"sign{i}.png")
                    if os.path.exists(sign_path):
                        img = Image.open(sign_path)
                        img = img.resize((70, 70), Image.Resampling.LANCZOS)
                        self.sign_images[i-1] = ImageTk.PhotoImage(img)
                except Exception as e:
                    print(f"Error cargando sign{i}.png: {e}")
            
            # Cargar fondo
            try:
                bg_path = os.path.join(self.backgrounds_folder, "road_background.png")
                if os.path.exists(bg_path):
                    img = Image.open(bg_path)
                    img = img.resize((800, 800), Image.Resampling.LANCZOS)
                    self.background_image = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Error cargando road_background.png: {e}")
                
        except Exception as e:
            print(f"Error general cargando imágenes: {e}")
    
    def create_menu(self):
        self.clear_screen()
        
        # Título
        title = tk.Label(self.root, text="DOUBLE DECISION", 
                        font=("Arial", 40, "bold"), 
                        bg="#1a1a1a", fg="#ffcc00")
        title.pack(pady=50)
        
        subtitle = tk.Label(self.root, text="RUTA 66", 
                           font=("Arial", 30), 
                           bg="#1a1a1a", fg="#ffffff")
        subtitle.pack(pady=10)
        
        instructions = tk.Label(self.root, 
                               text="Memoriza el vehículo central\ny la posición de la señal RUTA 66", 
                               font=("Arial", 16), 
                               bg="#1a1a1a", fg="#cccccc",
                               justify="center")
        instructions.pack(pady=30)
        
        start_btn = tk.Button(self.root, text="INICIAR JUEGO", 
                             font=("Arial", 20, "bold"),
                             bg="#ffcc00", fg="#000000",
                             command=self.start_game,
                             padx=30, pady=15,
                             cursor="hand2")
        start_btn.pack(pady=20)
        
        info_frame = tk.Frame(self.root, bg="#1a1a1a")
        info_frame.pack(pady=30)
        
        self.score_label = tk.Label(info_frame, text=f"Puntuación: {self.score}", 
                                    font=("Arial", 18), 
                                    bg="#1a1a1a", fg="#ffffff")
        self.score_label.pack(side="left", padx=20)
        
        self.level_label = tk.Label(info_frame, text=f"Nivel: {self.level}", 
                                    font=("Arial", 18), 
                                    bg="#1a1a1a", fg="#ffffff")
        self.level_label.pack(side="left", padx=20)
        
        # Instrucciones de imágenes
        note = tk.Label(self.root, 
                       text="Nota: Coloca tus imágenes PNG en:\n" +
                            "assets/vehicles/ (vehicle1.png a vehicle8.png)\n" +
                            "assets/signs/ (route66.png, sign1.png a sign7.png)\n" +
                            "assets/backgrounds/ (road_background.png)", 
                       font=("Arial", 10), 
                       bg="#1a1a1a", fg="#666666",
                       justify="left")
        note.pack(side="bottom", pady=20)
    
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def start_game(self):
        self.game_state = "preview"
        self.show_preview()
    
    def show_preview(self):
        self.clear_screen()
        
        info_frame = tk.Frame(self.root, bg="#1a1a1a")
        info_frame.pack(pady=10)
        
        tk.Label(info_frame, text=f"Nivel: {self.level} | Puntuación: {self.score}", 
                font=("Arial", 16), bg="#1a1a1a", fg="#ffffff").pack()
        
        tk.Label(self.root, text="Memoriza estos vehículos:", 
                font=("Arial", 18, "bold"), 
                bg="#1a1a1a", fg="#ffcc00").pack(pady=20)
        
        # Generar dos vehículos diferentes
        available_vehicles = list(self.vehicle_images.keys())
        self.vehicle_options = random.sample(available_vehicles, 
                                            min(2, len(available_vehicles)))
        
        preview_frame = tk.Frame(self.root, bg="#1a1a1a")
        preview_frame.pack(pady=20)
        
        for vehicle_idx in self.vehicle_options:
            vehicle_frame = tk.Frame(preview_frame, bg="#2a2a2a", 
                                    highlightbackground="#ffcc00", 
                                    highlightthickness=3)
            vehicle_frame.pack(side="left", padx=40)
            
            if vehicle_idx in self.vehicle_images:
                img_label = tk.Label(vehicle_frame, 
                                    image=self.vehicle_images[vehicle_idx],
                                    bg="#2a2a2a")
                img_label.pack(padx=20, pady=20)
        
        continue_btn = tk.Button(self.root, text="¡LISTO! Continuar", 
                                font=("Arial", 16, "bold"),
                                bg="#44ff44", fg="#000000",
                                command=self.show_stimulus,
                                padx=20, pady=10,
                                cursor="hand2")
        continue_btn.pack(pady=40)
    
    def show_stimulus(self):
        self.clear_screen()
        
        self.current_vehicle = random.choice(self.vehicle_options)
        self.route66_position = random.randint(0, 7)
        
        # Canvas principal
        self.canvas = tk.Canvas(self.root, width=800, height=750, 
                               bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(pady=20)
        
        # Fondo si existe
        if self.background_image:
            self.canvas.create_image(400, 350, image=self.background_image)
        
        center_x, center_y = 400, 350
        
        # Vehículo central
        if self.current_vehicle in self.vehicle_images:
            self.canvas.create_image(center_x, center_y, 
                                    image=self.vehicle_images[self.current_vehicle])
        
        # Colocar señales alrededor
        num_distractors = min(4 + self.level // 2, 7)
        positions = list(range(8))
        distractor_positions = [p for p in positions if p != self.route66_position]
        selected_distractors = random.sample(distractor_positions, 
                                            min(num_distractors, len(distractor_positions)))
        
        all_signs = selected_distractors + [self.route66_position]
        
        for pos in all_signs:
            # Usar el mismo sistema que la detección del mouse
            # pos=0→derecha (0°), pos=2→abajo (90°), pos=4→izquierda (180°), pos=6→arriba (270°)
            angle_degrees = pos * 45  # 0°, 45°, 90°, etc.
            angle_radians = math.radians(angle_degrees)
            x = center_x + 280 * math.cos(angle_radians)
            y = center_y + 280 * math.sin(angle_radians)
            
            if pos == self.route66_position:
                if self.route66_image:
                    self.canvas.create_image(x, y, image=self.route66_image)
            else:
                available_signs = list(self.sign_images.keys())
                if available_signs:
                    sign_idx = random.choice(available_signs)
                    self.canvas.create_image(x, y, image=self.sign_images[sign_idx])
        
        display_ms = max(1200, self.display_time - (self.level * 80))
        self.root.after(display_ms, self.show_response_screen)
    
    def show_response_screen(self):
        self.clear_screen()
        
        # Canvas para mostrar solo las opciones de vehículos
        self.canvas = tk.Canvas(self.root, width=800, height=700, 
                               bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(expand=True)
        
        # Fondo si existe
        if self.background_image:
            self.canvas.create_image(400, 350, image=self.background_image)
        
        center_x, center_y = 400, 350
        
        # Almacenar las imágenes originales y brillantes para cada vehículo
        self.vehicle_normal_images = {}
        self.vehicle_bright_images = {}
        self.vehicle_positions = {}
        
        # Mostrar las 2 opciones de vehículos sin texto
        vehicle_spacing = 200  # Separación entre vehículos
        
        for i, vehicle_idx in enumerate(self.vehicle_options):
            if vehicle_idx in self.vehicle_images:
                # Posicionar vehículos horizontalmente centrados
                x_offset = (i - 0.5) * vehicle_spacing  # -100 para el primer vehículo, +100 para el segundo
                x_pos = center_x + x_offset
                y_pos = center_y
                
                # Crear versión brillante del vehículo
                original_img = self.vehicle_images[vehicle_idx]
                
                # Obtener la imagen PIL original para crear una versión brillante
                try:
                    # Cargar la imagen original nuevamente
                    img_path = os.path.join(self.vehicles_folder, f"vehicle{vehicle_idx+1}.png")
                    if os.path.exists(img_path):
                        pil_img = Image.open(img_path)
                        pil_img = pil_img.resize((150, 150), Image.Resampling.LANCZOS)
                        
                        # Crear versión brillante
                        enhancer = ImageEnhance.Brightness(pil_img)
                        bright_img = enhancer.enhance(1.3)  # 30% más brillante
                        
                        # Crear glow effect
                        glow_img = Image.new('RGBA', (160, 160), (255, 255, 0, 50))  # Amarillo semi-transparente
                        glow_img.paste(bright_img, (5, 5), bright_img)
                        
                        # Convertir a PhotoImage
                        bright_photoimage = ImageTk.PhotoImage(glow_img)
                        
                        self.vehicle_normal_images[vehicle_idx] = original_img
                        self.vehicle_bright_images[vehicle_idx] = bright_photoimage
                except Exception as e:
                    # Si falla, usar la imagen normal como backup
                    self.vehicle_normal_images[vehicle_idx] = original_img
                    self.vehicle_bright_images[vehicle_idx] = original_img
                
                # Crear imagen del vehículo en el canvas
                vehicle_id = self.canvas.create_image(x_pos, y_pos, 
                                                     image=self.vehicle_normal_images[vehicle_idx],
                                                     tags=f"vehicle_{vehicle_idx}")
                
                # Almacenar información del vehículo
                self.vehicle_positions[vehicle_idx] = {
                    'id': vehicle_id,
                    'x': x_pos,
                    'y': y_pos
                }
                
                # Eventos para iluminación y click
                self.canvas.tag_bind(f"vehicle_{vehicle_idx}", "<Button-1>", 
                                   lambda event, v=vehicle_idx: self.check_vehicle(v))
                self.canvas.tag_bind(f"vehicle_{vehicle_idx}", "<Enter>", 
                                   lambda event, v=vehicle_idx: self.highlight_vehicle(v))
                self.canvas.tag_bind(f"vehicle_{vehicle_idx}", "<Leave>", 
                                   lambda event, v=vehicle_idx: self.unhighlight_vehicle(v))
    
    def highlight_vehicle(self, vehicle_idx):
        """Ilumina el vehículo cuando el mouse está sobre él"""
        if vehicle_idx in self.vehicle_positions and vehicle_idx in self.vehicle_bright_images:
            vehicle_id = self.vehicle_positions[vehicle_idx]['id']
            self.canvas.itemconfig(vehicle_id, image=self.vehicle_bright_images[vehicle_idx])
    
    def unhighlight_vehicle(self, vehicle_idx):
        """Quita la iluminación del vehículo cuando el mouse sale"""
        if vehicle_idx in self.vehicle_positions and vehicle_idx in self.vehicle_normal_images:
            vehicle_id = self.vehicle_positions[vehicle_idx]['id']
            self.canvas.itemconfig(vehicle_id, image=self.vehicle_normal_images[vehicle_idx])
    
    def check_vehicle(self, selected_vehicle):
        if selected_vehicle == self.current_vehicle:
            self.show_position_selection()
        else:
            messagebox.showerror("¡Incorrecto!", 
                               "El vehículo no era el correcto")
            self.game_over()
    
    def show_position_selection(self):
        self.clear_screen()
        
        tk.Label(self.root, text="¡Correcto! Ahora selecciona dónde estaba RUTA 66", 
                font=("Arial", 18, "bold"), 
                bg="#1a1a1a", fg="#44ff44").pack(pady=20)
        
        # Canvas para selección interactiva
        self.canvas = tk.Canvas(self.root, width=800, height=700, 
                               bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack()
        
        center_x, center_y = 400, 350
        
        # Fondo si existe
        if self.background_image:
            self.canvas.create_image(center_x, center_y, image=self.background_image)
        
        # Dibujar sectores (8 divisiones como conos con transparencia)
        self.sectors = []
        self.sector_images = {}
        self.sector_image_ids = {}
        
        # Dimensiones del canvas
        canvas_width, canvas_height = 800, 700
        
        for i in range(8):
            # Ángulos para cada sector (45° cada uno)
            angle_start = i * 45 - 22.5
            angle_end = angle_start + 45
            
            # Crear imagen del sector con transparencia
            sector_image = self.create_transparent_sector(
                canvas_width, canvas_height, center_x, center_y,
                angle_start, angle_end, 
                color_rgb=(42, 42, 42),  # Gris oscuro
                alpha=100  # Transparencia (0-255)
            )
            
            # Almacenar la imagen
            self.sector_images[f"sector_{i}"] = sector_image
            
            # Crear imagen en el canvas
            image_id = self.canvas.create_image(center_x, center_y, image=sector_image, tags=f"sector_{i}")
            self.sector_image_ids[f"sector_{i}"] = image_id
            self.sectors.append(image_id)
        
        # Vehículo en el centro (referencia)
        if self.current_vehicle in self.vehicle_images:
            self.canvas.create_image(center_x, center_y, 
                                    image=self.vehicle_images[self.current_vehicle])
        
        # Bindings para hover y click
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Button-1>", self.on_sector_click)
        
        self.sector_highlight = None
        self.current_highlighted_sector = -1
    
    def on_mouse_move(self, event):
        """Ilumina el sector donde está el mouse"""
        center_x, center_y = 400, 350
        
        # Calcular ángulo del mouse
        dx = event.x - center_x
        dy = event.y - center_y
        distance = math.sqrt(dx**2 + dy**2)
        
        # Permitir selección en toda el área (sin restricción de círculo central)
        if distance > 10:  # Solo evitar el punto exacto del centro para evitar errores
            # Calcular ángulo desde arriba (0°) en sentido horario
            angle = math.degrees(math.atan2(dx, -dy))
            if angle < 0:
                angle += 360
            
            # Convertir a la misma lógica que show_stimulus
            # show_stimulus usa: angle = pos * (2 * math.pi / 8) - math.pi / 2
            # Esto significa: pos=0→derecha, pos=2→abajo, pos=4→izquierda, pos=6→arriba
            # Ajustar ángulo para que coincida: restar 90° y dividir
            angle_for_pos = (angle - 90 + 360) % 360
            sector = int(angle_for_pos / 45)
            
            # Asegurar que el sector esté en rango válido
            if sector >= 8:
                sector = 0
            
            if sector != self.current_highlighted_sector:
                # Limpiar highlight anterior
                if self.current_highlighted_sector != -1:
                    # Restaurar imagen normal del sector anterior
                    angle_start_prev = self.current_highlighted_sector * 45 - 22.5
                    angle_end_prev = angle_start_prev + 45
                    
                    normal_image = self.create_transparent_sector(
                        800, 700, 400, 350,
                        angle_start_prev, angle_end_prev,
                        color_rgb=(42, 42, 42),
                        alpha=100
                    )
                    
                    self.sector_images[f"sector_{self.current_highlighted_sector}"] = normal_image
                    self.canvas.itemconfig(self.sector_image_ids[f"sector_{self.current_highlighted_sector}"], 
                                          image=normal_image)
                
                # Aplicar nuevo highlight
                angle_start_new = sector * 45 - 22.5
                angle_end_new = angle_start_new + 45
                
                highlighted_image = self.create_transparent_sector(
                    800, 700, 400, 350,
                    angle_start_new, angle_end_new,
                    color_rgb=(255, 204, 136),  # Color dorado
                    alpha=150,  # Más opaco para el highlight
                    is_highlighted=True
                )
                
                self.sector_images[f"sector_{sector}"] = highlighted_image
                self.canvas.itemconfig(self.sector_image_ids[f"sector_{sector}"], 
                                      image=highlighted_image)
                
                self.current_highlighted_sector = sector
        else:
            # Muy cerca del centro exacto - limpiar highlight
            if self.current_highlighted_sector != -1:
                # Restaurar imagen normal
                angle_start_prev = self.current_highlighted_sector * 45 - 22.5
                angle_end_prev = angle_start_prev + 45
                
                normal_image = self.create_transparent_sector(
                    800, 700, 400, 350,
                    angle_start_prev, angle_end_prev,
                    color_rgb=(42, 42, 42),
                    alpha=100
                )
                
                self.sector_images[f"sector_{self.current_highlighted_sector}"] = normal_image
                self.canvas.itemconfig(self.sector_image_ids[f"sector_{self.current_highlighted_sector}"], 
                                      image=normal_image)
                self.current_highlighted_sector = 1
    
    def on_sector_click(self, event):
        """Maneja el click en un sector"""
        if self.current_highlighted_sector != 1:
            self.check_position(self.current_highlighted_sector)
    
    def check_position(self, selected_position):
        """Verifica si la posición es correcta y muestra la señal"""
        center_x, center_y = 400, 350
        
        # Usar el mismo sistema que la detección del mouse y show_stimulus
        angle_degrees = selected_position * 45  # 0°, 45°, 90°, etc.
        angle_radians = math.radians(angle_degrees)
        x = center_x + 230 * math.cos(angle_radians)
        y = center_y + 230 * math.sin(angle_radians)
        
        if selected_position == self.route66_position:
            # Correcto - mostrar señal RUTA 66 con sector verde
            correct_image = self.create_transparent_sector(
                800, 700, 400, 350,
                selected_position * 45 - 22.5, selected_position * 45 + 22.5,
                color_rgb=(68, 255, 68),  # Verde brillante
                alpha=200,
                is_highlighted=True
            )
            
            self.sector_images[f"sector_{selected_position}"] = correct_image
            self.canvas.itemconfig(self.sector_image_ids[f"sector_{selected_position}"], 
                                  image=correct_image)
            
            if self.route66_image:
                self.canvas.create_image(x, y, image=self.route66_image)
            
            self.score += 10 * self.level
            self.root.after(1500, lambda: self.show_success_message())
        else:
            # Incorrecto - mostrar señal correcta con sector rojo para la selección incorrecta
            incorrect_image = self.create_transparent_sector(
                800, 700, 400, 350,
                selected_position * 45 - 22.5, selected_position * 45 + 22.5,
                color_rgb=(255, 68, 68),  # Rojo brillante
                alpha=200,
                is_highlighted=True
            )
            
            self.sector_images[f"sector_{selected_position}"] = incorrect_image
            self.canvas.itemconfig(self.sector_image_ids[f"sector_{selected_position}"], 
                                  image=incorrect_image)
            
            # Mostrar la posición correcta con sector verde
            correct_angle_degrees = self.route66_position * 45
            correct_angle_radians = math.radians(correct_angle_degrees)
            correct_x = center_x + 230 * math.cos(correct_angle_radians)
            correct_y = center_y + 230 * math.sin(correct_angle_radians)
            
            correct_image = self.create_transparent_sector(
                800, 700, 400, 350,
                self.route66_position * 45 - 22.5, self.route66_position * 45 + 22.5,
                color_rgb=(68, 255, 68),  # Verde brillante
                alpha=200,
                is_highlighted=True
            )
            
            self.sector_images[f"sector_{self.route66_position}"] = correct_image
            self.canvas.itemconfig(self.sector_image_ids[f"sector_{self.route66_position}"], 
                                  image=correct_image)
            
            if self.route66_image:
                self.canvas.create_image(correct_x, correct_y, image=self.route66_image)
            
            self.root.after(2000, lambda: self.game_over())
    
    def show_success_message(self):
        """Muestra mensaje de éxito y avanza de nivel"""
        messagebox.showinfo("¡Excelente!", 
                          f"¡Correcto! +{10 * self.level} puntos\n\nNivel {self.level + 1}")
        self.level += 1
        self.start_game()
    
    def game_over(self):
        self.clear_screen()
        
        tk.Label(self.root, text="GAME OVER", 
                font=("Arial", 50, "bold"), 
                bg="#1a1a1a", fg="#ff4444").pack(pady=50)
        
        tk.Label(self.root, text=f"Puntuación Final: {self.score}", 
                font=("Arial", 30), 
                bg="#1a1a1a", fg="#ffffff").pack(pady=20)
        
        tk.Label(self.root, text=f"Nivel Alcanzado: {self.level}", 
                font=("Arial", 25), 
                bg="#1a1a1a", fg="#ffffff").pack(pady=10)
        
        btn_frame = tk.Frame(self.root, bg="#1a1a1a")
        btn_frame.pack(pady=40)
        
        restart_btn = tk.Button(btn_frame, text="JUGAR DE NUEVO", 
                               font=("Arial", 16, "bold"),
                               bg="#44ff44", fg="#000000",
                               command=self.restart_game,
                               padx=20, pady=10,
                               cursor="hand2")
        restart_btn.pack(side="left", padx=10)
        
        quit_btn = tk.Button(btn_frame, text="SALIR", 
                            font=("Arial", 16, "bold"),
                            bg="#ff4444", fg="#ffffff",
                            command=self.root.quit,
                            padx=20, pady=10,
                            cursor="hand2")
        quit_btn.pack(side="left", padx=10)
    
    def restart_game(self):
        self.score = 0
        self.level = 1
        self.display_time = 2500
        self.create_menu()

if __name__ == "__main__":
    root = tk.Tk()
    game = DoubleDecisionGame(root)
    root.mainloop()