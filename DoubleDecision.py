import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw, ImageEnhance
import random
import math
import os

class DoubleDecisionGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Ruta 66 - Entrenamiento de Enfoque")
        self.root.geometry("1000x800")
        self.root.configure(bg="#1a1a1a")
        
        # Sistema de niveles según la narrativa
        self.level_times = {
            0: {"vehicle": 1000, "signal": 500, "total": 1500},  # Práctica
            1: {"vehicle": 800, "signal": 400, "total": 1200},   # Nivel 1
            2: {"vehicle": 650, "signal": 350, "total": 1000},   # Nivel 2
            3: {"vehicle": 500, "signal": 300, "total": 800},    # Nivel 3
            4: {"vehicle": 400, "signal": 250, "total": 650},    # Nivel 4
            5: {"vehicle": 300, "signal": 200, "total": 500},    # Modo PRO
            6: {"vehicle": 200, "signal": 150, "total": 350},    # Modo Extremo
            7: {"vehicle": 150, "signal": 120, "total": 270},    # Nivel Extra 1
            8: {"vehicle": 120, "signal": 100, "total": 220},    # Nivel Extra 2
            9: {"vehicle": 100, "signal": 80, "total": 180}      # Nivel Máximo
        }
        self.response_time = 2000
        
        # Variables del juego
        self.score = 0
        self.level = 0
        self.current_vehicle = None
        self.route66_position = None
        self.route66_sector = None  # NUEVO: Para identificar el sector de RUTA 66
        self.vehicle_options = []
        self.game_state = "menu"
        
        # Paths de imágenes
        self.images_folder = "assets"
        self.vehicles_folder = os.path.join(self.images_folder, "vehicles")
        self.signs_folder = os.path.join(self.images_folder, "signs")
        self.backgrounds_folder = os.path.join(self.images_folder, "backgrounds")
        
        # Almacenar imágenes cargadas
        self.vehicle_images = {}
        self.route66_image = None
        self.background_image = None
        self.sector_images = {}
        self.sector_image_ids = {}
        self.sign_images = {}
        
        # Variables para la selección de posición
        self.canvas = None
        self.sector_highlight = None
        self.current_highlighted_sector = -1
        self.response_timer_id = None
        
        self.load_images()
        self.create_menu()

    def get_canvas_dimensions(self):
        """Obtiene las dimensiones actuales de la ventana"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        return width, height

    def get_scaled_background(self, width, height):
        """Redimensiona el fondo al tamaño actual de la ventana"""
        if hasattr(self, 'background_pil') and self.background_pil:
            img = self.background_pil.resize((width, height), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        return None

    def create_transparent_sector(self, canvas_width, canvas_height, center_x, center_y, 
                                angle_start, angle_end, color_rgb, alpha, is_highlighted=False):
        """Crea un sector triangular con transparencia real usando PIL"""
        img = Image.new('RGBA', (canvas_width, canvas_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        max_distance = max(canvas_width, canvas_height)
        
        rad_start = math.radians(angle_start)
        rad_end = math.radians(angle_end)
        
        x1 = center_x + max_distance * math.cos(rad_start)
        y1 = center_y + max_distance * math.sin(rad_start)
        x2 = center_x + max_distance * math.cos(rad_end)
        y2 = center_y + max_distance * math.sin(rad_end)
        
        if is_highlighted:
            color_rgba = (255, 204, 136, alpha)
            outline_color = (255, 204, 0, 255)
        else:
            color_rgba = (*color_rgb, alpha)
            outline_color = (68, 68, 68, 180)
        
        draw.polygon([(center_x, center_y), (x1, y1), (x2, y2)], 
                    fill=color_rgba, outline=outline_color, width=2)
        
        return ImageTk.PhotoImage(img)
    
    def load_images(self):
        """Carga todas las imágenes necesarias"""
        try:
            for i in range(1, 9):
                try:
                    img_path = os.path.join(self.vehicles_folder, f"vehicle{i}.png")
                    if os.path.exists(img_path):
                        img = Image.open(img_path)
                        img = img.resize((150, 150), Image.Resampling.LANCZOS)
                        self.vehicle_images[i-1] = ImageTk.PhotoImage(img)
                except Exception as e:
                    print(f"Error cargando vehicle{i}.png: {e}")
            
            try:
                route66_path = os.path.join(self.signs_folder, "route66.png")
                if os.path.exists(route66_path):
                    img = Image.open(route66_path)
                    img = img.resize((80, 80), Image.Resampling.LANCZOS)
                    self.route66_image = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Error cargando route66.png: {e}")
            
            for i in range(1, 8):
                try:
                    sign_path = os.path.join(self.signs_folder, f"sign{i}.png")
                    if os.path.exists(sign_path):
                        img = Image.open(sign_path)
                        img = img.resize((70, 70), Image.Resampling.LANCZOS)
                        self.sign_images[i-1] = ImageTk.PhotoImage(img)
                except Exception as e:
                    print(f"Error cargando sign{i}.png: {e}")
            
            try:
                bg_path = os.path.join(self.backgrounds_folder, "road_background.png")
                if os.path.exists(bg_path):
                    self.background_pil = Image.open(bg_path)
            except Exception as e:
                print(f"Error cargando road_background.png: {e}")
                self.background_pil = None
                
        except Exception as e:
            print(f"Error general cargando imágenes: {e}")
    
    def get_num_total_signs(self):
        """Calcula el número total de señales según el nivel"""
        # Progresión: 3, 5, 7, 9, 11, 13, 15, 17, 19, 21+ señales
        num_signs = 3 + (self.level * 2)
        return num_signs
    
    def create_menu(self):
        self.clear_screen()
        
        bg_frame = tk.Frame(self.root, bg="#1a1a1a")
        bg_frame.pack(fill="both", expand=True)
        
        title_frame = tk.Frame(bg_frame, bg="#1a1a1a")
        title_frame.pack(pady=40)
        
        tk.Label(title_frame, text="RUTA 66", 
                font=("Arial", 48, "bold"), 
                bg="#1a1a1a", fg="#ffcc00").pack()
        
        tk.Label(title_frame, text="ENTRENAMIENTO DE ENFOQUE", 
                font=("Arial", 20), 
                bg="#1a1a1a", fg="#ffffff").pack(pady=10)
        
        info_card = tk.Frame(bg_frame, bg="#2a2a2a", relief="raised", bd=2)
        info_card.pack(pady=20, padx=100, fill="x")
        
        total_signs = self.get_num_total_signs()
        
        tk.Label(info_card, 
                text=f"Entrena tu visión periférica mientras conduces por la legendaria Ruta 66.\n"
                     f"Mantén el enfoque en el vehículo central y detecta las señales de peligro.\n\n"
                     f"Nivel actual: {total_signs} señales en pantalla",
                font=("Arial", 14), 
                bg="#2a2a2a", fg="#cccccc", justify="center",
                pady=20).pack()
        
        stats_frame = tk.Frame(bg_frame, bg="#1a1a1a")
        stats_frame.pack(pady=20)
        
        tk.Label(stats_frame, text=f"NIVEL ACTUAL: {self.level + 1}", 
                font=("Arial", 16, "bold"), 
                bg="#1a1a1a", fg="#ffcc00").pack(side="left", padx=20)
        
        tk.Label(stats_frame, text=f"PUNTUACIÓN: {self.score}", 
                font=("Arial", 16, "bold"), 
                bg="#1a1a1a", fg="#44ff44").pack(side="left", padx=20)
        
        start_btn = tk.Button(bg_frame, text="INICIAR VIAJE", 
                             font=("Arial", 20, "bold"),
                             bg="#ffcc00", fg="#000000",
                             command=self.start_game,
                             padx=40, pady=15,
                             cursor="hand2",
                             relief="raised",
                             bd=4)
        start_btn.pack(pady=30)
        
        controls_info = tk.Label(bg_frame, 
                               text="🎯 OBJETIVO: Identifica el vehículo y recuerda el SECTOR de la señal RUTA 66\n"
                                    "⏱️  Los tiempos se reducen y las señales aumentan en cada nivel - ¡Mantén tu enfoque!",
                               font=("Arial", 12), 
                               bg="#1a1a1a", fg="#888888",
                               justify="center")
        controls_info.pack(pady=20)
    
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
        
        total_signs = self.get_num_total_signs()
        
        tk.Label(info_frame, 
                text=f"Nivel: {self.level + 1} | Puntuación: {self.score} | Señales: {total_signs}", 
                font=("Arial", 16), bg="#1a1a1a", fg="#ffffff").pack()
        
        tk.Label(self.root, text="Memoriza estos vehículos:", 
                font=("Arial", 18, "bold"), 
                bg="#1a1a1a", fg="#ffcc00").pack(pady=20)
        
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
        
        canvas_width, canvas_height = self.get_canvas_dimensions()
        
        self.canvas = tk.Canvas(self.root, width=canvas_width, height=canvas_height, 
                            bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, pady=20)
        
        self.background_image = self.get_scaled_background(canvas_width, canvas_height)
        if self.background_image:
            self.canvas.create_image(canvas_width//2, canvas_height//2, image=self.background_image)
        
        center_x, center_y = canvas_width // 2, canvas_height // 2
        
        if self.current_vehicle in self.vehicle_images:
            self.canvas.create_image(center_x, center_y, 
                                    image=self.vehicle_images[self.current_vehicle])
        
        # NUEVO: Calcular posiciones para múltiples señales por sector
        num_total_signs = self.get_num_total_signs()
        
        # Generar todas las posiciones posibles (8 sectores x 3 distancias = 24 posiciones)
        all_positions = []
        for sector in range(8):
            for distance_multiplier in [0.25, 0.35, 0.45]:  # 3 anillos de distancia
                all_positions.append({
                    'sector': sector,
                    'distance_multiplier': distance_multiplier
                })
        
        # Seleccionar posiciones aleatorias para las señales
        selected_positions = random.sample(all_positions, min(num_total_signs, len(all_positions)))
        
        # Una de ellas será RUTA 66
        route66_index = random.randint(0, len(selected_positions) - 1)
        route66_position_data = selected_positions[route66_index]
        self.route66_sector = route66_position_data['sector']
        self.route66_position = route66_position_data  # Guardar toda la info
        
        available_signs = list(self.sign_images.keys())
        
        # Colocar todas las señales
        for i, pos_data in enumerate(selected_positions):
            sector = pos_data['sector']
            distance_mult = pos_data['distance_multiplier']
            
            # Calcular posición
            angle_degrees = sector * 45
            # Añadir variación aleatoria dentro del sector para que no estén perfectamente alineadas
            angle_variation = random.uniform(-15, 15)
            angle_degrees += angle_variation
            
            angle_radians = math.radians(angle_degrees)
            sign_distance = min(canvas_width, canvas_height) * distance_mult
            
            x = center_x + sign_distance * math.cos(angle_radians)
            y = center_y + sign_distance * math.sin(angle_radians)
            
            # Decidir si es RUTA 66 o distractor
            if i == route66_index:
                if self.route66_image:
                    self.canvas.create_image(x, y, image=self.route66_image)
            else:
                if available_signs:
                    sign_idx = random.choice(available_signs)
                    self.canvas.create_image(x, y, image=self.sign_images[sign_idx])
        
        # Obtener el tiempo de visualización según el nivel
        display_time = self.level_times.get(self.level, self.level_times[9])["total"]
        
        self.time_remaining = display_time / 1000
        
        self.timer_text = self.canvas.create_text(canvas_width//2, 50, 
                                                text=f"Tiempo: {self.time_remaining:.1f}s",
                                                font=("Arial", 16, "bold"),
                                                fill="#ffcc00")
        
        self.update_timer()
        self.root.after(display_time, self.show_response_screen)
        
    def update_timer(self):
        if hasattr(self, 'timer_text') and self.time_remaining > 0:
            self.time_remaining -= 0.1
            self.canvas.itemconfig(self.timer_text, text=f"Tiempo: {self.time_remaining:.1f}s")
            if self.time_remaining > 0:
                self.root.after(100, self.update_timer)
    
    def show_response_screen(self):
        self.clear_screen()
        
        canvas_width, canvas_height = self.get_canvas_dimensions()
    
        self.canvas = tk.Canvas(self.root, width=canvas_width, height=canvas_height, 
                            bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.background_image = self.get_scaled_background(canvas_width, canvas_height)
        if self.background_image:
            self.canvas.create_image(canvas_width//2, canvas_height//2, image=self.background_image)
        
        center_x, center_y = canvas_width // 2, canvas_height // 2

        self.vehicle_time_remaining = 2.0
        self.vehicle_timer_text = self.canvas.create_text(canvas_width//2, 50, 
                                                text=f"Tiempo para elegir vehículo: {self.vehicle_time_remaining:.1f}s",
                                                font=("Arial", 16, "bold"),
                                                fill="#ffcc00")
        
        self.vehicle_normal_images = {}
        self.vehicle_bright_images = {}
        self.vehicle_positions = {}
        
        vehicle_spacing = 200
        
        for i, vehicle_idx in enumerate(self.vehicle_options):
            if vehicle_idx in self.vehicle_images:
                x_offset = (i - 0.5) * vehicle_spacing
                x_pos = center_x + x_offset
                y_pos = center_y
                
                original_img = self.vehicle_images[vehicle_idx]
                
                try:
                    img_path = os.path.join(self.vehicles_folder, f"vehicle{vehicle_idx+1}.png")
                    if os.path.exists(img_path):
                        pil_img = Image.open(img_path)
                        pil_img = pil_img.resize((150, 150), Image.Resampling.LANCZOS)
                        
                        enhancer = ImageEnhance.Brightness(pil_img)
                        bright_img = enhancer.enhance(1.3)
                        
                        glow_img = Image.new('RGBA', (160, 160), (255, 255, 0, 50))
                        glow_img.paste(bright_img, (5, 5), bright_img)
                        
                        bright_photoimage = ImageTk.PhotoImage(glow_img)
                        
                        self.vehicle_normal_images[vehicle_idx] = original_img
                        self.vehicle_bright_images[vehicle_idx] = bright_photoimage
                except Exception as e:
                    self.vehicle_normal_images[vehicle_idx] = original_img
                    self.vehicle_bright_images[vehicle_idx] = original_img
                
                vehicle_id = self.canvas.create_image(x_pos, y_pos, 
                                                     image=self.vehicle_normal_images[vehicle_idx],
                                                     tags=f"vehicle_{vehicle_idx}")
                
                self.vehicle_positions[vehicle_idx] = {
                    'id': vehicle_id,
                    'x': x_pos,
                    'y': y_pos
                }
                
                self.canvas.tag_bind(f"vehicle_{vehicle_idx}", "<Button-1>", 
                                   lambda event, v=vehicle_idx: self.check_vehicle(v))
                self.canvas.tag_bind(f"vehicle_{vehicle_idx}", "<Enter>", 
                                   lambda event, v=vehicle_idx: self.highlight_vehicle(v))
                self.canvas.tag_bind(f"vehicle_{vehicle_idx}", "<Leave>", 
                                   lambda event, v=vehicle_idx: self.unhighlight_vehicle(v))
        
        self.update_vehicle_timer()
        self.response_timer_id = self.root.after(2000, self.vehicle_timeout)
    
    def update_vehicle_timer(self):
        if hasattr(self, 'vehicle_timer_text') and self.vehicle_time_remaining > 0:
            self.vehicle_time_remaining -= 0.1
            if hasattr(self, 'canvas') and self.canvas.winfo_exists():
                try:
                    self.canvas.itemconfig(self.vehicle_timer_text, 
                                        text=f"Tiempo para elegir vehículo: {self.vehicle_time_remaining:.1f}s")
                    if self.vehicle_time_remaining > 0:
                        self.root.after(100, self.update_vehicle_timer)
                except:
                    pass

    def vehicle_timeout(self):
        messagebox.showerror("¡Tiempo Agotado!", 
                            "No seleccionaste un vehículo a tiempo\n\nLa carretera no perdona la indecisión")
        self.game_over()

    def highlight_vehicle(self, vehicle_idx):
        if vehicle_idx in self.vehicle_positions and vehicle_idx in self.vehicle_bright_images:
            vehicle_id = self.vehicle_positions[vehicle_idx]['id']
            self.canvas.itemconfig(vehicle_id, image=self.vehicle_bright_images[vehicle_idx])
    
    def unhighlight_vehicle(self, vehicle_idx):
        if vehicle_idx in self.vehicle_positions and vehicle_idx in self.vehicle_normal_images:
            vehicle_id = self.vehicle_positions[vehicle_idx]['id']
            self.canvas.itemconfig(vehicle_id, image=self.vehicle_normal_images[vehicle_idx])
    
    def check_vehicle(self, selected_vehicle):
        if self.response_timer_id is not None:
            self.root.after_cancel(self.response_timer_id)
            self.response_timer_id = None
        
        if selected_vehicle == self.current_vehicle:
            if selected_vehicle in self.vehicle_positions:
                vehicle_id = self.vehicle_positions[selected_vehicle]['id']
                self.canvas.itemconfig(vehicle_id, image=self.vehicle_bright_images[selected_vehicle])
            
            self.root.after(500, self.show_position_selection)
        else:
            messagebox.showerror("¡Señal de Peligro!", 
                            "Vehículo incorrecto\n\nRecuerda: La carretera exige máxima atención")
            self.game_over()
    
    def show_position_selection(self):
        self.clear_screen()
        
        tk.Label(self.root, text="¡Correcto! Ahora selecciona el SECTOR donde estaba RUTA 66", 
                font=("Arial", 18, "bold"), 
                bg="#1a1a1a", fg="#44ff44").pack(pady=20)
        
        canvas_width, canvas_height = self.get_canvas_dimensions()
        canvas_height -= 60
        
        self.canvas = tk.Canvas(self.root, width=canvas_width, height=canvas_height, 
                            bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        center_x, center_y = canvas_width // 2, canvas_height // 2
    
        self.background_image = self.get_scaled_background(canvas_width, canvas_height)
        if self.background_image:
            self.canvas.create_image(center_x, center_y, image=self.background_image)
        
        self.sectors = []
        self.sector_images = {}
        self.sector_image_ids = {}
                
        for i in range(8):
            angle_start = i * 45 - 22.5
            angle_end = angle_start + 45
            
            sector_image = self.create_transparent_sector(
                canvas_width, canvas_height, center_x, center_y,
                angle_start, angle_end, 
                color_rgb=(42, 42, 42),
                alpha=100
            )
            
            self.sector_images[f"sector_{i}"] = sector_image
            
            image_id = self.canvas.create_image(center_x, center_y, image=sector_image, tags=f"sector_{i}")
            self.sector_image_ids[f"sector_{i}"] = image_id
            self.sectors.append(image_id)
        
        if self.current_vehicle in self.vehicle_images:
            self.canvas.create_image(center_x, center_y, 
                                    image=self.vehicle_images[self.current_vehicle])
        
        # CREAR EL TEMPORIZADOR AL FINAL para que esté al frente
        self.signal_time_remaining = 2.0
        self.signal_timer_text = self.canvas.create_text(canvas_width//2, canvas_height - 30, 
                                                text=f"Tiempo para elegir sector: {self.signal_time_remaining:.1f}s",
                                                font=("Arial", 16, "bold"),
                                                fill="#ffcc00")
        
        self.current_center_x = center_x
        self.current_center_y = center_y
        self.current_canvas_width = canvas_width
        self.current_canvas_height = canvas_height

        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Button-1>", self.on_sector_click)
        
        self.sector_highlight = None
        self.current_highlighted_sector = -1

        self.update_signal_timer()
        self.response_timer_id = self.root.after(2000, self.signal_timeout)

    def update_signal_timer(self):
        if hasattr(self, 'signal_timer_text') and self.signal_time_remaining > 0:
            self.signal_time_remaining -= 0.1
            if hasattr(self, 'canvas') and self.canvas.winfo_exists():
                try:
                    self.canvas.itemconfig(self.signal_timer_text, 
                                        text=f"Tiempo para elegir sector: {self.signal_time_remaining:.1f}s")
                    if self.signal_time_remaining > 0:
                        self.root.after(100, self.update_signal_timer)
                except:
                    pass

    def signal_timeout(self):
        messagebox.showerror("¡Tiempo Agotado!", 
                            "No seleccionaste el sector a tiempo\n\nLa carretera exige reflejos rápidos")
        self.game_over()
    
    def on_mouse_move(self, event):
        center_x = self.current_center_x
        center_y = self.current_center_y
        
        dx = event.x - center_x
        dy = event.y - center_y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 10:
            # Calcular ángulo desde el eje X positivo (mismo método que para dibujar)
            angle = math.degrees(math.atan2(dy, dx))
            
            # Normalizar ángulo a rango [0, 360)
            if angle < 0:
                angle += 360
            
            # Los sectores están centrados en: 0°, 45°, 90°, 135°, 180°, 225°, 270°, 315°
            # Cada sector va desde (centro - 22.5°) hasta (centro + 22.5°)
            # Sector 0: -22.5° a 22.5° (o 337.5° a 22.5°)
            # Sector 1: 22.5° a 67.5°
            # etc.
            
            # Ajustar ángulo para que el sector 0 comience en -22.5° (337.5°)
            adjusted_angle = (angle + 22.5) % 360
            sector = int(adjusted_angle / 45)
            
            # Asegurar que el sector esté en rango [0, 7]
            if sector >= 8:
                sector = 0
            
            if sector != self.current_highlighted_sector:
                if self.current_highlighted_sector != -1:
                    angle_start_prev = self.current_highlighted_sector * 45 - 22.5
                    angle_end_prev = angle_start_prev + 45
                    
                    normal_image = self.create_transparent_sector(
                        self.current_canvas_width, self.current_canvas_height,
                        center_x, center_y,
                        angle_start_prev, angle_end_prev,
                        color_rgb=(42, 42, 42),
                        alpha=100
                    )
                    
                    self.sector_images[f"sector_{self.current_highlighted_sector}"] = normal_image
                    self.canvas.itemconfig(self.sector_image_ids[f"sector_{self.current_highlighted_sector}"], 
                                        image=normal_image)
                
                angle_start_new = sector * 45 - 22.5
                angle_end_new = angle_start_new + 45
                
                highlighted_image = self.create_transparent_sector(
                    self.current_canvas_width, self.current_canvas_height,
                    center_x, center_y,
                    angle_start_new, angle_end_new,
                    color_rgb=(255, 204, 136),
                    alpha=150,
                    is_highlighted=True
                )
                
                self.sector_images[f"sector_{sector}"] = highlighted_image
                self.canvas.itemconfig(self.sector_image_ids[f"sector_{sector}"], 
                                    image=highlighted_image)
                
                self.current_highlighted_sector = sector
        else:
            if self.current_highlighted_sector != -1:
                angle_start_prev = self.current_highlighted_sector * 45 - 22.5
                angle_end_prev = angle_start_prev + 45
                
                normal_image = self.create_transparent_sector(
                    self.current_canvas_width, self.current_canvas_height,
                    center_x, center_y,
                    angle_start_prev, angle_end_prev,
                    color_rgb=(42, 42, 42),
                    alpha=100
                )
                
                self.sector_images[f"sector_{self.current_highlighted_sector}"] = normal_image
                self.canvas.itemconfig(self.sector_image_ids[f"sector_{self.current_highlighted_sector}"], 
                                    image=normal_image)
                self.current_highlighted_sector = -1
    
    def on_sector_click(self, event):
        if self.current_highlighted_sector != -1:
            if self.response_timer_id is not None:
                self.root.after_cancel(self.response_timer_id)
                self.response_timer_id = None
            
            self.check_position(self.current_highlighted_sector)
    
    def check_position(self, selected_sector):
        """Verifica si el sector seleccionado es correcto"""
        center_x = self.current_center_x
        center_y = self.current_center_y
        
        if selected_sector == self.route66_sector:
            # Correcto - Iluminar sector en verde
            correct_image = self.create_transparent_sector(
                self.current_canvas_width, self.current_canvas_height,
                center_x, center_y,
                selected_sector * 45 - 22.5, selected_sector * 45 + 22.5,
                color_rgb=(68, 255, 68),
                alpha=200,
                is_highlighted=True
            )
            
            self.sector_images[f"sector_{selected_sector}"] = correct_image
            self.canvas.itemconfig(self.sector_image_ids[f"sector_{selected_sector}"], 
                                image=correct_image)
            
            # Mostrar la señal RUTA 66 en su posición original
            route66_angle = self.route66_position['sector'] * 45
            route66_angle += random.uniform(-15, 15)  # Recrear variación
            route66_radians = math.radians(route66_angle)
            route66_distance = min(self.current_canvas_width, self.current_canvas_height) * self.route66_position['distance_multiplier']
            
            x = center_x + route66_distance * math.cos(route66_radians)
            y = center_y + route66_distance * math.sin(route66_radians)
            
            if self.route66_image:
                self.canvas.create_image(x, y, image=self.route66_image)
            
            self.score += 10 * (self.level + 1)
            self.root.after(1500, lambda: self.show_success_message())
        else:
            # Incorrecto - Iluminar sector seleccionado en rojo
            incorrect_image = self.create_transparent_sector(
                self.current_canvas_width, self.current_canvas_height,
                center_x, center_y,
                selected_sector * 45 - 22.5, selected_sector * 45 + 22.5,
                color_rgb=(255, 68, 68),
                alpha=200,
                is_highlighted=True
            )
            
            self.sector_images[f"sector_{selected_sector}"] = incorrect_image
            self.canvas.itemconfig(self.sector_image_ids[f"sector_{selected_sector}"], 
                                image=incorrect_image)
            
            # Mostrar sector correcto en verde
            correct_image = self.create_transparent_sector(
                self.current_canvas_width, self.current_canvas_height,
                center_x, center_y,
                self.route66_sector * 45 - 22.5, self.route66_sector * 45 + 22.5,
                color_rgb=(68, 255, 68),
                alpha=200,
                is_highlighted=True
            )
            
            self.sector_images[f"sector_{self.route66_sector}"] = correct_image
            self.canvas.itemconfig(self.sector_image_ids[f"sector_{self.route66_sector}"], 
                                image=correct_image)
            
            # Mostrar la señal RUTA 66 en su posición correcta
            route66_angle = self.route66_position['sector'] * 45
            route66_angle += random.uniform(-15, 15)
            route66_radians = math.radians(route66_angle)
            route66_distance = min(self.current_canvas_width, self.current_canvas_height) * self.route66_position['distance_multiplier']
            
            x = center_x + route66_distance * math.cos(route66_radians)
            y = center_y + route66_distance * math.sin(route66_radians)
            
            if self.route66_image:
                self.canvas.create_image(x, y, image=self.route66_image)
            
            self.root.after(2000, lambda: self.game_over())
    
    def show_success_message(self):
        points_earned = 10 * (self.level + 1)
        
        if self.level < 9:
            self.level += 1
            total_signs = self.get_num_total_signs()
            messagebox.showinfo("¡Excelente!", 
                              f"¡Correcto! +{points_earned} puntos\n\n"
                              f"Avanzando al nivel {self.level + 1}\n"
                              f"Próximo desafío: {total_signs} señales")
        else:
            messagebox.showinfo("¡Increíble!", 
                              f"¡Perfecto! +{points_earned} puntos\n\n"
                              f"Has alcanzado el nivel máximo con {self.get_num_total_signs()} señales")
        
        self.start_game()
    
    def game_over(self):
        self.clear_screen()
        
        if self.level >= 7:
            performance = "¡Maestro de la Carretera!"
            color = "#ffcc00"
        elif self.level >= 4:
            performance = "¡Conductor Experto!"
            color = "#44ff44"
        elif self.level >= 2:
            performance = "Buen Manejo"
            color = "#88ff88"
        else:
            performance = "Sigue Practicando"
            color = "#ff4444"
        
        main_frame = tk.Frame(self.root, bg="#1a1a1a")
        main_frame.pack(fill="both", expand=True, pady=50)
        
        tk.Label(main_frame, text="FIN DEL VIAJE", 
                font=("Arial", 40, "bold"), 
                bg="#1a1a1a", fg="#ff4444").pack(pady=20)
        
        tk.Label(main_frame, text=performance, 
                font=("Arial", 24, "bold"), 
                bg="#1a1a1a", fg=color).pack(pady=10)
        
        stats_frame = tk.Frame(main_frame, bg="#2a2a2a", relief="sunken", bd=2)
        stats_frame.pack(pady=30, padx=100, fill="x")
        
        tk.Label(stats_frame, text=f"Puntuación Final: {self.score}", 
                font=("Arial", 20), 
                bg="#2a2a2a", fg="#ffffff").pack(pady=15)
        
        tk.Label(stats_frame, text=f"Nivel Alcanzado: {self.level + 1}", 
                font=("Arial", 18), 
                bg="#2a2a2a", fg="#cccccc").pack(pady=10)
        
        max_signs = self.get_num_total_signs()
        tk.Label(stats_frame, text=f"Máximo de señales manejadas: {max_signs}", 
                font=("Arial", 16), 
                bg="#2a2a2a", fg="#cccccc").pack(pady=5)
        
        btn_frame = tk.Frame(main_frame, bg="#1a1a1a")
        btn_frame.pack(pady=40)
        
        restart_btn = tk.Button(btn_frame, text="NUEVO VIAJE", 
                               font=("Arial", 16, "bold"),
                               bg="#44ff44", fg="#000000",
                               command=self.restart_game,
                               padx=25, pady=12,
                               cursor="hand2")
        restart_btn.pack(side="left", padx=15)
        
        menu_btn = tk.Button(btn_frame, text="MENÚ PRINCIPAL", 
                            font=("Arial", 16, "bold"),
                            bg="#ffcc00", fg="#000000",
                            command=self.create_menu,
                            padx=25, pady=12,
                            cursor="hand2")
        menu_btn.pack(side="left", padx=15)
        
        quit_btn = tk.Button(btn_frame, text="SALIR", 
                            font=("Arial", 16, "bold"),
                            bg="#ff4444", fg="#ffffff",
                            command=self.root.quit,
                            padx=25, pady=12,
                            cursor="hand2")
        quit_btn.pack(side="left", padx=15)
    
    def restart_game(self):
        self.score = 0
        self.level = 0
        self.create_menu()

if __name__ == "__main__":
    root = tk.Tk()
    game = DoubleDecisionGame(root)
    root.mainloop()