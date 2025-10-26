# student_subjects_view.py
import tkinter as tk
from tkinter import ttk
import db_manager # Para obtener datos de materias y calificaciones

class MateriaWidget(ttk.Frame):
    """
    Widget (usando ttk) que muestra una materia y se expande/contrae.
    """
    def __init__(self, parent, materia_info, bg_color):
        # Usar el estilo del parent (probablemente "Main.TFrame")
        super().__init__(parent, style="CardBody.TFrame", padding=0)

        self.materia_info = materia_info # Contiene nombre, id, promedio, calificaciones_detalle
        self.bg_color = bg_color
        self.is_expanded = False
        self.card_width = 300 # Ancho fijo para consistencia

        # Frame contenedor principal de la tarjeta
        # Usamos TFrame con estilo para el fondo blanco y borde
        style_name = "BlueCard.TLabelframe" # Default
        if bg_color == "#A92323": style_name = "MaroonCard.TLabelframe"
        elif bg_color == "#F0C000": style_name = "YellowCard.TLabelframe"

        # Usamos un LabelFrame estilizado como contenedor principal
        self.container = ttk.LabelFrame(self, width=self.card_width, style=style_name, labelwidget=tk.Label()) # Labelwidget vacío por ahora
        self.container.pack(fill='x', expand=True)
        self.container.pack_propagate(False) # Controlar tamaño

        # --- Header ---
        self.header_frame = ttk.Frame(self.container, style="CardBody.TFrame") # Frame interno blanco
        self.header_frame.pack(fill='x', expand=True, padx=1, pady=1) # Pequeño padding para ver borde

        # Label para el título que irá en el LabelFrame
        self.lbl_title_widget = tk.Label(
             text=self.materia_info.get('nombre', 'Materia Desconocida'),
             font=("Helvetica", 11, "bold"),
             background=self.bg_color, # Color de fondo del título
             foreground= "white" if bg_color != "#F0C000" else "#333333", # Texto blanco (o negro para amarillo)
             anchor="center",
             padx=10, pady=5
        )
        # Asignar el label como título del LabelFrame
        self.container.configure(labelwidget=self.lbl_title_widget)


        # Promedio (Siempre visible bajo el título)
        promedio_text = self.materia_info.get('promedio', 'N/A')
        promedio_val = "N/A"
        if isinstance(promedio_text, (float, int)):
            promedio_val = f"{promedio_text:.1f}" # Un decimal para el promedio

        self.promedio_label = ttk.Label(
            self.header_frame,
            text=f"Promedio: {promedio_val}",
            style="CardAvg.TLabel", # Estilo para promedio
            anchor="w"
        )
        self.promedio_label.pack(fill='x', padx=10, pady=(5, 10)) # Añadir padding

        # Details frame (oculto al inicio, dentro del header_frame)
        self.details_frame = ttk.Frame(self.header_frame, style="CardBody.TFrame")
        # No se empaqueta aún

        # Hacer header clickeable
        # El LabelFrame maneja el clic en el título, necesitamos el resto
        for widget in [self.header_frame, self.promedio_label, self.container]:
            widget.bind("<Button-1>", self.toggle_expand)
        self.lbl_title_widget.bind("<Button-1>", self.toggle_expand)


    def toggle_expand(self, event=None):
        if self.is_expanded:
            self.details_frame.pack_forget()
            self.is_expanded = False
            # Forzar actualización del layout del contenedor padre
            self.master.master.master.update_idletasks() # Canvas -> materias_frame -> parent_frame -> main_app
            self.master.master.master.event_generate("<Configure>")

        else:
            # Limpiar detalles previos
            for child in self.details_frame.winfo_children():
                child.destroy()

            calificaciones = self.materia_info.get('calificaciones_detalle', {})

            if not calificaciones:
                ttk.Label(self.details_frame, text="No hay calificaciones detalladas.", style="CardDetail.TLabel").pack(pady=5)
            else:
                for nombre_act, calif_dict in calificaciones.items():
                    calif_val = calif_dict.get('calificacion', 'N/A')
                    # Asegurar que se muestre como número si lo es
                    calif_str = f"{calif_val:.1f}" if isinstance(calif_val, (int, float)) else str(calif_val)

                    detail_line = ttk.Frame(self.details_frame, style="CardBody.TFrame")
                    ttk.Label(detail_line, text=f"{nombre_act}:", style="CardDetail.TLabel", anchor="w").pack(side=tk.LEFT, fill='x', expand=True)
                    ttk.Label(detail_line, text=calif_str, style="CardDetail.TLabel", anchor="e").pack(side=tk.RIGHT)
                    detail_line.pack(fill='x', padx=10, pady=1)

            self.details_frame.pack(fill='x', pady=(0, 10))
            self.is_expanded = True
             # Forzar actualización del layout del contenedor padre
            self.master.master.master.update_idletasks()
            self.master.master.master.event_generate("<Configure>")


def create_student_subjects_view(parent_frame, user_data):
    """Crea la vista de materias con scroll y tarjetas."""

    student_id = user_data['id'] # ID numérico del alumno

    # Contenedor principal que se ajustará al parent_frame
    container = ttk.Frame(parent_frame, style="Main.TFrame")
    container.pack(fill=tk.BOTH, expand=True)
    container.rowconfigure(1, weight=1)
    container.columnconfigure(0, weight=1)

    ttk.Label(container, text="Materias Inscritas", font=("Helvetica", 16, "bold"), style="TLabel").grid(row=0, column=0, pady=10, sticky='nw', padx=10)

    # --- Canvas y Scrollbar ---
    canvas = tk.Canvas(container, bg='#f0f2f5', highlightthickness=0) # Usar color de fondo
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.grid(row=1, column=0, sticky='nsew')
    scrollbar.grid(row=1, column=1, sticky='ns')

    # Frame interior del canvas
    materias_frame = ttk.Frame(canvas, style="Main.TFrame", padding=(10,0)) # Padding superior
    canvas_window = canvas.create_window((0, 0), window=materias_frame, anchor='nw')

    # --- Cargar y procesar datos ---
    materias_inscritas = db_manager.get_subjects_by_student(student_id)
    materia_widgets_list = []

    if not materias_inscritas:
        ttk.Label(materias_frame, text="No tienes materias asignadas.", style="TLabel").pack(pady=20)
    else:
        colores = ["#A92323", "#F0C000", "#007bff"] # Rojo, Amarillo, Azul
        
        for i, materia in enumerate(materias_inscritas):
            materia_id = materia['id']
            # Obtener detalles de calificaciones
            actividades = db_manager.get_activities_by_student_subject(student_id, materia_id)
            calificaciones_detalle = {act['descripcion']: {'calificacion': act['calificacion'], 'id': act['id']} for act in actividades}

            # Calcular promedio
            promedio = db_manager.get_weighted_average(student_id, materia_id)

            materia_info_completa = {
                'id': materia_id,
                'nombre': materia['nombre'],
                'promedio': promedio,
                'calificaciones_detalle': calificaciones_detalle
            }

            color = colores[i % len(colores)]
            materia_widget = MateriaWidget(materias_frame, materia_info_completa, color)
            materia_widgets_list.append(materia_widget)

    # --- Lógica de Layout Responsivo ---
    def layout_materias(event=None):
        canvas_width = canvas.winfo_width()
        if canvas_width <= 1: return # Evitar cálculo si no es visible

        card_width = 300
        padding = 10
        num_columns = max(1, canvas_width // (card_width + padding*2)) # Columnas que caben

        # Limitar columnas si se desea
        # num_columns = min(num_columns, 4)

        for i, widget in enumerate(materia_widgets_list):
            row = i // num_columns
            col = i % num_columns
            widget.grid(row=row, column=col, padx=padding, pady=padding, sticky='nsew')

        # Configurar peso de columnas para centrado/expansión
        for c in range(num_columns):
            materias_frame.columnconfigure(c, weight=1)

        # Actualizar scrollregion
        materias_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        # Ajustar ancho del frame interior al canvas para que el scroll funcione bien
        canvas.itemconfig(canvas_window, width=canvas_width)

    # Binds para responsividad y scroll
    materias_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind('<Configure>', layout_materias)

    # Layout inicial
    layout_materias()

    # Necesario devolver el canvas para la lógica de scroll si se usa mousewheel fuera
    # Pero como la vista ocupa todo el frame, no es estrictamente necesario devolverlo.
    return container # Devolver el contenedor principal