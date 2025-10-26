# admin_users_view.py
import tkinter as tk
from tkinter import ttk, messagebox
import db_manager

def create_admin_users_tab(parent):
    """
    Vista de administración de usuarios (profesores y alumnos) para el administrador.
    Compatible con la base de datos 'Usuarios' de calificaciones.db.
    """
    tab = ttk.Frame(parent, style="Main.TFrame")

    # --- Tabla de usuarios ---
    cols = ("id", "username", "nombre_completo", "role")
    tree = ttk.Treeview(tab, columns=cols, show="headings", height=12)

    tree.heading("id", text="ID")
    tree.heading("username", text="Usuario")
    tree.heading("nombre_completo", text="Nombre Completo")
    tree.heading("role", text="Rol")

    tree.column("id", width=40, anchor="center")
    tree.column("username", width=160)
    tree.column("nombre_completo", width=200)
    tree.column("role", width=100, anchor="center")

    tree.pack(fill=tk.BOTH, expand=True, padx=16, pady=8)

    # --- Funciones auxiliares ---
    def load_users():
        tree.delete(*tree.get_children())
        users = db_manager.get_all_users_except_admin()  # función moderna
        for u in users:
            tree.insert("", "end", values=(u["id"], u["username"], u["nombre_completo"], u["role"]))

    def add_user():
        """Ventana para agregar nuevo usuario."""
        win = tk.Toplevel(tab)
        win.title("Agregar Usuario")
        win.geometry("340x420")
        win.resizable(False, False)

        ttk.Label(win, text="Usuario (nombre de inicio de sesión):").pack(anchor="w", padx=10, pady=(10, 3))
        e_user = ttk.Entry(win)
        e_user.pack(fill="x", padx=10)

        ttk.Label(win, text="Contraseña:").pack(anchor="w", padx=10, pady=(10, 3))
        e_pwd = ttk.Entry(win, show="*")
        e_pwd.pack(fill="x", padx=10)

        ttk.Label(win, text="Nombre completo:").pack(anchor="w", padx=10, pady=(10, 3))
        e_name = ttk.Entry(win)
        e_name.pack(fill="x", padx=10)

        ttk.Label(win, text="Apellidos:").pack(anchor="w", padx=10, pady=(10, 3))
        e_ap = ttk.Entry(win)
        e_ap.pack(fill="x", padx=10)

        ttk.Label(win, text="Teléfono:").pack(anchor="w", padx=10, pady=(10, 3))
        e_tel = ttk.Entry(win)
        e_tel.pack(fill="x", padx=10)

        ttk.Label(win, text="Dirección:").pack(anchor="w", padx=10, pady=(10, 3))
        e_dir = ttk.Entry(win)
        e_dir.pack(fill="x", padx=10)

        ttk.Label(win, text="Rol:").pack(anchor="w", padx=10, pady=(10, 3))
        rol = tk.StringVar(value="alumno")
        rol_combo = ttk.Combobox(win, textvariable=rol, values=["alumno", "profesor"], state="readonly")
        rol_combo.pack(fill="x", padx=10, pady=(0, 10))

        def save_user():
            username = e_user.get().strip()
            password = e_pwd.get().strip()
            nombre = e_name.get().strip()
            apellidos = e_ap.get().strip()
            telefono = e_tel.get().strip()
            direccion = e_dir.get().strip()
            role = rol.get()

            if not username or not password:
                messagebox.showwarning("Campos vacíos", "Usuario y contraseña son obligatorios.")
                return

            new_id = db_manager.create_user(username, password, role, nombre, apellidos, telefono, direccion)
            if new_id:
                messagebox.showinfo("Éxito", f"Usuario '{username}' creado correctamente.")
                load_users()
                win.destroy()
            else:
                messagebox.showerror("Error", "No se pudo crear el usuario (puede que ya exista).")

        ttk.Button(win, text="Guardar", command=save_user).pack(pady=12)

    def delete_usr():
        """Elimina el usuario seleccionado."""
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("Selecciona", "Selecciona un usuario para eliminar.")
            return

        item = tree.item(sel[0])
        user_id, username = item["values"][0], item["values"][1]

        if messagebox.askyesno("Confirmar", f"¿Eliminar al usuario '{username}'?"):
            ok = db_manager.delete_user(user_id)
            if ok:
                messagebox.showinfo("Eliminado", f"Usuario '{username}' eliminado correctamente.")
                load_users()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el usuario.")

    def reset_pwd():
        """Reinicia la contraseña del usuario seleccionado."""
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("Selecciona", "Selecciona un usuario para resetear contraseña.")
            return

        user_id, username = tree.item(sel[0], "values")[0:2]
        if messagebox.askyesno("Resetear", f"¿Resetear contraseña de '{username}' a '123456'?"):
            db_manager.update_user_password(user_id, "123456")
            messagebox.showinfo("Éxito", f"Contraseña de '{username}' reiniciada a '123456'.")

    # # --- Botones ---
    # btns = ttk.Frame(tab)
    # btns.pack(pady=10)
    # ttk.Button(btns, text="Agregar", command=add_user).pack(side=tk.LEFT, padx=5)
    # ttk.Button(btns, text="Resetear Contraseña", command=reset_pwd).pack(side=tk.LEFT, padx=5)
    # ttk.Button(btns, text="Eliminar", command=delete_usr).pack(side=tk.LEFT, padx=5)

    load_users()
    return tab
