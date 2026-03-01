import flet as ft
import algoritmos 

def main(page: ft.Page):
    page.title = "Simulador de Algoritmos de Despacho"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 50
    page.scroll = ft.ScrollMode.AUTO 

    datos_crudos = [] 
    colores_procesos = ["blue400", "green400", "orange400", "purple400", "red400", "cyan400", "pink400"]

    # --- COMPONENTES DE ENTRADA ---
    llegada_input = ft.TextField(label="Tiempo Llegada", width=130, border_color="white24")
    rafaga_input = ft.TextField(label="Ráfaga CPU", width=130, border_color="white24")
    prioridad_input = ft.TextField(label="Prioridad", width=130, border_color="white24")
    quantum_input = ft.TextField(label="Quantum", width=130, border_color="white24")
    
    dropdown_algoritmo = ft.Dropdown(
        label="Selecciona el Algoritmo",
        width=300,
        options=[
            ft.dropdown.Option("FIFO"),
            ft.dropdown.Option("SJF"),
            ft.dropdown.Option("Prioridad"),
            ft.dropdown.Option("Round Robin - FIFO"),
            ft.dropdown.Option("Round Robin - SJF"),
            ft.dropdown.Option("Round Robin - Prioridad"),
        ],
        value="FIFO"
    )

    lista_procesos_ui = ft.Column(spacing=5, scroll=ft.ScrollMode.AUTO,expand=True)
    resultados_texto = ft.Text(size=18, weight="bold", color="white70")
    gantt_container = ft.Column(spacing=2)

    # --- FUNCIÓN: CAJA DE MENSAJE EMERGENTE ---
    def mostrar_mensaje(mensaje):
        caja_alerta = ft.AlertDialog(
            title=ft.Text("Aviso del Sistema", weight="bold", color="red400"),
            content=ft.Text(mensaje),
            actions=[ft.TextButton("Entendido", on_click=lambda e: page.pop_dialog())],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(caja_alerta)

    # --- FUNCIONES DE LOS BOTONES ---
    def agregar_proceso(e):
        val_llegada = str(llegada_input.value).strip()
        val_rafaga = str(rafaga_input.value).strip()
        val_prioridad = str(prioridad_input.value).strip()

        if not val_llegada.isdigit() or not val_rafaga.isdigit() or not val_prioridad.isdigit():
            mostrar_mensaje("Se deben ingresar solo datos numéricos y no dejar campos en blanco.")
            return

        pid = f"P{len(datos_crudos) + 1}"
        color = colores_procesos[len(datos_crudos) % len(colores_procesos)]
        
        datos_crudos.append({
            "pid": pid,
            "llegada": int(val_llegada),
            "rafaga": int(val_rafaga),
            "prioridad": int(val_prioridad),
            "color": color
        })

        lista_procesos_ui.controls.append(
            ft.Container(
                content=ft.Text(f"{pid} | Llegada: {val_llegada} | Ráfaga: {val_rafaga} | Prioridad: {val_prioridad}"),
                padding=10,
                bgcolor=color,
                border_radius=5
            )
        )
        
        llegada_input.value = ""
        rafaga_input.value = ""
        prioridad_input.value = ""
        page.update()

    def ejecutar_simulacion(e):
        if not datos_crudos:
            mostrar_mensaje("Debes agregar al menos un proceso para simular.")
            return
        
        seleccion = dropdown_algoritmo.value
        quantum = 0
        
        if "Round Robin" in seleccion:
            val_quantum = str(quantum_input.value).strip()
            if not val_quantum.isdigit():
                mostrar_mensaje("El algoritmo Round Robin requiere que ingreses un Quantum numérico.")
                return
            quantum = int(val_quantum)

        gantt_container.controls.clear()
        
        procesos_limpios = []
        for d in datos_crudos:
            procesos_limpios.append(algoritmos.Proceso(d["pid"], d["llegada"], d["rafaga"], d["prioridad"]))

        if seleccion == "FIFO":
            res, gantt = algoritmos.simular_fifo(procesos_limpios)
        elif seleccion == "SJF":
            res, gantt = algoritmos.simular_sjf(procesos_limpios)
        elif seleccion == "Prioridad":
            res, gantt = algoritmos.simular_prioridad(procesos_limpios)
        elif seleccion == "Round Robin - FIFO":
            res, gantt = algoritmos.simular_round_robin(procesos_limpios, quantum, "FIFO")
        elif seleccion == "Round Robin - SJF":
            res, gantt = algoritmos.simular_round_robin(procesos_limpios, quantum, "SJF")
        elif seleccion == "Round Robin - Prioridad":
            res, gantt = algoritmos.simular_round_robin(procesos_limpios, quantum, "Prioridad")

        n = len(res)
        espera_total = sum([p.tiempo_espera for p in res])
        sistema_total = sum([p.tiempo_sistema for p in res])
        
        resultados_texto.value = f"Promedio Espera: {espera_total/n:.2f} | Promedio Sistema: {sistema_total/n:.2f}"

        if not gantt:
            page.update()
            return

        escala = 35 
        max_tiempo = max([b["fin"] for b in gantt])

        eje_stack = ft.Stack(height=20, width=max_tiempo * escala)
        for i in range(max_tiempo + 1):
            eje_stack.controls.append(
                ft.Container(content=ft.Text(str(i), size=12, color="white54"), left=i * escala, top=0)
            )

        cabecera = ft.Row([
            ft.Container(width=50), 
            eje_stack
        ])
        gantt_container.controls.append(cabecera)
        gantt_container.controls.append(ft.Divider(height=1, color="white24"))

        for d in datos_crudos:
            pid = d["pid"]
            color_bloque = d["color"]
            bloques_proceso = [b for b in gantt if b["pid"] == pid]
            
            track_stack = ft.Stack(height=35, width=max_tiempo * escala)
            
            for i in range(max_tiempo):
                track_stack.controls.append(
                    ft.Container(
                        width=escala, height=35, left=i * escala, top=0,
                        border=ft.Border.only(left=ft.BorderSide(1, "white10"))
                    )
                )

            for b in bloques_proceso:
                inicio = b["inicio"]
                fin = b["fin"]
                duracion = fin - inicio
                
                track_stack.controls.append(
                    ft.Container(
                        width=duracion * escala,
                        height=25,
                        left=inicio * escala, 
                        top=5,
                        bgcolor=color_bloque,
                        border_radius=4,
                        tooltip=f"Inicio: {inicio} | Fin: {fin}" 
                    )
                )

            fila_proceso = ft.Row([
                ft.Container(content=ft.Text(pid, weight="bold"), width=50),
                track_stack
            ])
            gantt_container.controls.append(fila_proceso)
        
        page.update()

    def limpiar_datos(e):
        datos_crudos.clear()
        lista_procesos_ui.controls.clear()
        gantt_container.controls.clear()
        resultados_texto.value = ""
        llegada_input.value = ""
        rafaga_input.value = ""
        prioridad_input.value = ""
        quantum_input.value = ""
        page.update()

    def eliminar_ultimo_proceso(e):
        if not datos_crudos:
            mostrar_mensaje("No hay procesos en la cola para eliminar.")
            return
        datos_crudos.pop()
        lista_procesos_ui.controls.pop()
        gantt_container.controls.clear()
        resultados_texto.value = ""
        page.update()

    # --- DISEÑO FINAL CON PANELES (TARJETAS) ---

    # PANEL 1: ENTRADA DE DATOS
    panel_entradas = ft.Container(
        width=900,
        content=ft.Column([
            ft.Text("Ingrese los datos", weight="bold", size=20, color="blue400"),
            ft.Row([llegada_input, rafaga_input, prioridad_input, quantum_input]),
            ft.Button("Agregar Proceso", icon=ft.Icons.ADD, on_click=agregar_proceso, bgcolor="blue700", color="white"),
        ]),
        padding=30,
        bgcolor="#1e1e24", # Fondo gris azulado oscuro
        border_radius=10,
        border=ft.Border.all(1, "white10")
    )

    # PANEL 2: PROCESOS EN COLA
    panel_cola = ft.Container(
        height=275,
        width=500,
        content=ft.Column([
            ft.Text("Procesos en cola", weight="bold", size=20, color="orange400"),
            lista_procesos_ui
        ]),
        padding=20,
        bgcolor="#1e1e24",
        border_radius=10,
        border=ft.Border.all(1, "white10"),
    )

    # PANEL 3: CONTROLES DE SIMULACIÓN
    panel_controles = ft.Container(
        height=275,
        content=ft.Column([
            ft.Text("Controles de Simulación", weight="bold", size=20, color="green400"),
            dropdown_algoritmo,
            ft.Divider(height=10, color="transparent"),
            ft.Button("EJECUTAR ALGORITMO", icon=ft.Icons.PLAY_ARROW, on_click=ejecutar_simulacion, bgcolor="green700", color="white"),
            ft.Button("Eliminar Último Proceso", icon=ft.Icons.UNDO, on_click=eliminar_ultimo_proceso, bgcolor="orange700", color="white"),
            ft.Button("Limpiar Todos los Datos", icon=ft.Icons.DELETE, on_click=limpiar_datos, bgcolor="red700", color="white"),
        ], spacing=10),
        padding=20,
        bgcolor="#1e1e24",
        border_radius=10,
        border=ft.Border.all(1, "white10"),
        width=390,
    )

    # PANEL 4: RESULTADOS Y GANTT
    panel_resultados = ft.Container(
        width=900,
        content=ft.Column([
            ft.Text("Resultados", size=24, weight="bold", color="purple400"),
            resultados_texto,
            ft.Text("Diagrama de Gantt", size=22, weight="bold", color="purple400"),
            ft.Divider(height=10, color="transparent"),
            ft.Row([gantt_container], scroll=ft.ScrollMode.AUTO)
            
        ]),
        
        padding=20,
        bgcolor="#1e1e24",
        border_radius=10,
        border=ft.Border.all(1, "white10")
    )

    # Ensamblamos todo en la página principal
    page.add(
        ft.Text("Simulador de Algoritmos de Despacho", size=32, weight="bold"),
        ft.Divider(height=10, color="transparent"),
        
        panel_entradas,
        
        # Juntamos Cola y Controles en una fila para que estén lado a lado
        ft.Row([panel_cola, panel_controles], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START),
        
        panel_resultados,
        
        ft.Divider(height=60, color="transparent") 
    )

if __name__ == "__main__":
    ft.run(main)