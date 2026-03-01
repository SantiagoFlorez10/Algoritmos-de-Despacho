class Proceso:
    def __init__(self, pid, llegada, rafaga, prioridad=0):
        self.pid = pid             # Nombre o ID del proceso (ej. "P1")
        self.llegada = llegada     # Tiempo en el que llega (Arrival Time)
        self.rafaga = rafaga       # Tiempo de ejecución necesario (Burst Time)
        self.rafaga_restante = rafaga # Para algoritmos preemptivos, esto irá disminuyendo
        self.prioridad = prioridad # Prioridad (para el algoritmo de prioridad)
        
        # Estas variables las calculará el algoritmo después
        self.tiempo_finalizacion = 0 # Completion Time (CT)
        self.tiempo_sistema = 0      # Turnaround Time (TAT) = CT - Llegada
        self.tiempo_espera = 0       # Waiting Time (WT) = TAT - Ráfaga
        
    def __repr__(self):
        # Esto es solo para que al imprimir el proceso en consola se vea bonito
        return f"[{self.pid}] Llegada:{self.llegada} Ráfaga:{self.rafaga} | Espera:{self.tiempo_espera} Sistema:{self.tiempo_sistema}"
    

def simular_fifo(lista_procesos):
    # 1. Ordenamos la lista estrictamente por tiempo de llegada
    # Si llegan igual, Python mantiene el orden original de la lista
    procesos = sorted(lista_procesos, key=lambda p: p.llegada)
    
    tiempo_actual = 0
    registro_gantt = [] # Aquí guardaremos los datos para dibujar la gráfica después

    for p in procesos:
        # Si el procesador está libre y el proceso aún no llega, el tiempo avanza "en blanco"
        if tiempo_actual < p.llegada:
            tiempo_actual = p.llegada
            
        tiempo_inicio = tiempo_actual
        
        # El proceso se ejecuta por completo (porque es FIFO)
        tiempo_actual += p.rafaga
        
        # Guardamos los resultados en el objeto proceso
        p.tiempo_finalizacion = tiempo_actual
        p.tiempo_sistema = p.tiempo_finalizacion - p.llegada
        p.tiempo_espera = p.tiempo_sistema - p.rafaga
        
        # Guardamos el bloque para el diagrama de Gantt futuro
        registro_gantt.append({
            "pid": p.pid,
            "inicio": tiempo_inicio,
            "fin": tiempo_actual
        })

    return procesos, registro_gantt

def simular_sjf(lista_procesos):
    # Ordenamos inicialmente por llegada
    procesos_pendientes = sorted(lista_procesos, key=lambda p: p.llegada)
    
    tiempo_actual = 0
    procesos_completados = []
    registro_gantt = []

    # Mientras haya procesos sin ejecutar
    while procesos_pendientes:
        # 1. Miramos cuáles procesos ya llegaron (están en la "sala de espera")
        disponibles = [p for p in procesos_pendientes if p.llegada <= tiempo_actual]
        
        if not disponibles:
            # Si no ha llegado ninguno todavía, el procesador se queda en blanco
            # Avanzamos el reloj hasta que llegue el próximo
            tiempo_actual = procesos_pendientes[0].llegada
            continue
            
        # 2. De los que están disponibles, elegimos el que tenga la ráfaga más corta
        # min() busca el valor mínimo basándose en p.rafaga
        proceso_actual = min(disponibles, key=lambda p: p.rafaga)
        
        tiempo_inicio = tiempo_actual
        
        # 3. Lo ejecutamos
        tiempo_actual += proceso_actual.rafaga
        
        # 4. Calculamos sus tiempos
        proceso_actual.tiempo_finalizacion = tiempo_actual
        proceso_actual.tiempo_sistema = proceso_actual.tiempo_finalizacion - proceso_actual.llegada
        proceso_actual.tiempo_espera = proceso_actual.tiempo_sistema - proceso_actual.rafaga
        
        # 5. Guardamos para el Gantt
        registro_gantt.append({
            "pid": proceso_actual.pid,
            "inicio": tiempo_inicio,
            "fin": tiempo_actual
        })
        
        # 6. Lo movemos a completados y lo quitamos de los pendientes
        procesos_completados.append(proceso_actual)
        procesos_pendientes.remove(proceso_actual)
        
    return procesos_completados, registro_gantt

def simular_prioridad(lista_procesos):
    # Ordenamos inicialmente por llegada
    procesos_pendientes = sorted(lista_procesos, key=lambda p: p.llegada)
    
    tiempo_actual = 0
    procesos_completados = []
    registro_gantt = []

    while procesos_pendientes:
        # 1. Miramos quiénes están en la sala de espera
        disponibles = [p for p in procesos_pendientes if p.llegada <= tiempo_actual]
        
        if not disponibles:
            # Si no hay nadie, avanzamos el reloj
            tiempo_actual = procesos_pendientes[0].llegada
            continue
            
        # 2. LA DIFERENCIA ESTÁ AQUÍ: Elegimos el de MAYOR prioridad 
        # (Usamos min() porque asumimos que el número 1 es más importante que el 5)
        # Si en tu clase el profesor dijo que números altos = mayor prioridad, 
        # simplemente cambia "min" por "max".
        proceso_actual = min(disponibles, key=lambda p: p.prioridad)
        
        tiempo_inicio = tiempo_actual
        
        # 3. Lo ejecutamos
        tiempo_actual += proceso_actual.rafaga
        
        # 4. Calculamos sus tiempos
        proceso_actual.tiempo_finalizacion = tiempo_actual
        proceso_actual.tiempo_sistema = proceso_actual.tiempo_finalizacion - proceso_actual.llegada
        proceso_actual.tiempo_espera = proceso_actual.tiempo_sistema - proceso_actual.rafaga
        
        # 5. Guardamos para el diagrama
        registro_gantt.append({
            "pid": proceso_actual.pid,
            "inicio": tiempo_inicio,
            "fin": tiempo_actual
        })
        
        # 6. Actualizamos las listas
        procesos_completados.append(proceso_actual)
        procesos_pendientes.remove(proceso_actual)
        
    return procesos_completados, registro_gantt

def simular_round_robin(lista_procesos, quantum, modo="FIFO"):
    for p in lista_procesos:
        p.rafaga_restante = p.rafaga
        # Le damos un "ticket" a cada proceso para la ronda
        p.ejecutado_en_ronda = False 

    # Ordenamos a todos por su tiempo de llegada inicialmente
    procesos = sorted(lista_procesos, key=lambda p: p.llegada)
    
    tiempo_actual = 0
    registro_gantt = []
    procesos_completados = []
    cola_listos = []
    
    indice_llegada = 0
    n = len(procesos)

    while indice_llegada < n or cola_listos:
        
        # 1. Ingresan los que van llegando (entran con ticket nuevo)
        while indice_llegada < n and procesos[indice_llegada].llegada <= tiempo_actual:
            nuevo_p = procesos[indice_llegada]
            nuevo_p.ejecutado_en_ronda = False 
            cola_listos.append(nuevo_p)
            indice_llegada += 1

        # Si no hay nadie, saltamos en el tiempo al próximo proceso
        if not cola_listos:
            tiempo_actual = procesos[indice_llegada].llegada
            continue

        # 2. Filtramos quiénes NO han pasado en esta ronda (los que aún tienen ticket)
        disponibles = [p for p in cola_listos if not p.ejecutado_en_ronda]

        # 3. Si TODOS ya pasaron, ¡Inicia una NUEVA RONDA!
        if not disponibles:
            for p in cola_listos:
                p.ejecutado_en_ronda = False
            disponibles = cola_listos[:] # Ahora todos vuelven a estar disponibles

        # 4. APLICAMOS TU IDEA (SJF, Prioridad o FIFO) SOLO A LOS DISPONIBLES
        if modo == "FIFO":
            proceso_actual = disponibles[0]
        elif modo == "SJF":
            # El de menor ráfaga restante (si hay empate, escoge el que llegó antes)
            proceso_actual = min(disponibles, key=lambda p: p.rafaga_restante)
        elif modo == "Prioridad":
            # El de menor número de prioridad
            proceso_actual = min(disponibles, key=lambda p: p.prioridad)

        # 5. Lo ejecutamos
        tiempo_inicio = tiempo_actual
        tiempo_ejecucion = min(proceso_actual.rafaga_restante, quantum)
        
        tiempo_actual += tiempo_ejecucion
        proceso_actual.rafaga_restante -= tiempo_ejecucion
        proceso_actual.ejecutado_en_ronda = True # "Quema" su ticket de esta ronda
        
        registro_gantt.append({
            "pid": proceso_actual.pid,
            "inicio": tiempo_inicio,
            "fin": tiempo_actual
        })

        # 6. Agregamos a los que llegaron MIENTRAS se ejecutaba este proceso
        while indice_llegada < n and procesos[indice_llegada].llegada <= tiempo_actual:
            nuevo_p = procesos[indice_llegada]
            nuevo_p.ejecutado_en_ronda = False # Llegan con su ticket listo
            cola_listos.append(nuevo_p)
            indice_llegada += 1

        # 7. Si ya terminó toda su ráfaga, lo sacamos del sistema
        if proceso_actual.rafaga_restante == 0:
            proceso_actual.tiempo_finalizacion = tiempo_actual
            proceso_actual.tiempo_sistema = proceso_actual.tiempo_finalizacion - proceso_actual.llegada
            proceso_actual.tiempo_espera = proceso_actual.tiempo_sistema - proceso_actual.rafaga
            procesos_completados.append(proceso_actual)
            cola_listos.remove(proceso_actual)

    return procesos_completados, registro_gantt

if __name__ == "__main__":
    print("=== PRUEBA GLOBAL DE ALGORITMOS DE DESPACHO ===")
    n = int(input("¿Cuántos procesos deseas ejecutar?: "))
    
    # 1. Recolectamos los datos puros
    datos_crudos = []
    for i in range(n):
        print(f"\n--- Datos del Proceso P{i+1} ---")
        llegada = int(input(f"Tiempo de llegada: "))
        rafaga = int(input(f"Ráfaga de CPU: "))
        prioridad = int(input(f"Prioridad (1 es la más alta): "))
        
        datos_crudos.append({
            "pid": f"P{i+1}", 
            "llegada": llegada, 
            "rafaga": rafaga, 
            "prioridad": prioridad
        })
        
    quantum = int(input("\nIngresa el valor del Quantum (para Round Robin): "))

    # 2. Función auxiliar para crear procesos "limpios" cada vez que probamos un algoritmo
    def obtener_procesos_limpios():
        lista_limpia = []
        for d in datos_crudos:
            lista_limpia.append(Proceso(d["pid"], d["llegada"], d["rafaga"], d["prioridad"]))
        return lista_limpia

    # 3. Función auxiliar para imprimir resultados y no repetir código 6 veces
    def imprimir_resultados(nombre_algoritmo, procesos_resueltos, gantt):
        print(f"\n{'='*15} {nombre_algoritmo} {'='*15}")
        tiempo_espera_total = 0
        tiempo_sistema_total = 0
        
        for p in procesos_resueltos:
            print(p)
            tiempo_espera_total += p.tiempo_espera
            tiempo_sistema_total += p.tiempo_sistema
            
        print(f"\n-> Promedio Espera (WT): {tiempo_espera_total / n:.2f}")
        print(f"-> Promedio Sistema (TAT): {tiempo_sistema_total / n:.2f}")
        
        # Imprimimos el Gantt de forma simplificada
        print("-> Secuencia Gantt:")
        secuencia = " | ".join([f"{paso['pid']} ({paso['inicio']}-{paso['fin']})" for paso in gantt])
        print(f"   {secuencia}")

    # --- EJECUCIÓN DE TODAS LAS PRUEBAS ---
    
    # FIFO
    res, gantt = simular_fifo(obtener_procesos_limpios())
    imprimir_resultados("FIFO", res, gantt)
    
    # SJF
    res, gantt = simular_sjf(obtener_procesos_limpios())
    imprimir_resultados("SJF (No apropiativo)", res, gantt)
    
    # Prioridad
    res, gantt = simular_prioridad(obtener_procesos_limpios())
    imprimir_resultados("PRIORIDAD (No apropiativo)", res, gantt)
    
    # Round Robin - Variante FIFO
    res, gantt = simular_round_robin(obtener_procesos_limpios(), quantum, modo="FIFO")
    imprimir_resultados("ROUND ROBIN (Variante FIFO)", res, gantt)
    
    # Round Robin - Variante SJF
    res, gantt = simular_round_robin(obtener_procesos_limpios(), quantum, modo="SJF")
    imprimir_resultados("ROUND ROBIN (Variante SJF)", res, gantt)
    
    # Round Robin - Variante Prioridad
    res, gantt = simular_round_robin(obtener_procesos_limpios(), quantum, modo="Prioridad")
    imprimir_resultados("ROUND ROBIN (Variante Prioridad)", res, gantt)

    print("\n" + "="*50)
    print("¡Pruebas finalizadas con éxito!")