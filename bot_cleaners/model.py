from mesa.model import Model
from mesa.agent import Agent
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector

import numpy as np


class Celda(Agent):
    def __init__(self, unique_id, model, suciedad: bool = False):
        super().__init__(unique_id, model)
        self.sucia = suciedad

class Repiza(Agent):
    def __init__(self, unique_id, model, pid:int = 1):
        super().__init__(unique_id, model)
        self.product_id = pid

class Estacion(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.carga=0

class Entrada(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

class Salida(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

class RobotLimpieza(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.sig_pos = None
        self.movimientos = 0
        self.carga = 100
        self.cargando = False
        self.casillas_limpiadas = []
        self.casillas_visitadas = set() #Agregue
        

    def limpiar_una_celda(self, lista_de_celdas_sucias):
        celda_a_limpiar = self.random.choice(lista_de_celdas_sucias)
        celda_a_limpiar.sucia = False
        self.sig_pos = celda_a_limpiar.pos
        self.casillas_limpiadas.append(celda_a_limpiar.pos)

    def cargar_bot(self, lista_de_estaciones_recarga):
        celda_a_limpiar = self.random.choice(lista_de_estaciones_recarga)
        self.carga += 1
        self.sig_pos = celda_a_limpiar.pos
        
    def seleccionar_nueva_pos(self, lista_de_vecinos):
        posibles_nuevas_pos = [vecino.pos for vecino in lista_de_vecinos if vecino.pos not in self.casillas_visitadas]#Agregue
        if posibles_nuevas_pos:#Agregue
            self.sig_pos = self.random.choice(posibles_nuevas_pos)#Agregue
        else:
            self.sig_pos = self.random.choice(lista_de_vecinos).pos#Agregue
       
    @staticmethod
    def buscar_celdas_sucia(lista_de_vecinos):
        celdas_sucias = list()
        for vecino in lista_de_vecinos:
            if isinstance(vecino, Celda) and vecino.sucia:
                celdas_sucias.append(vecino)
        return celdas_sucias
    
    def step(self):
        vecinos = self.model.grid.get_neighbors(
            self.pos, moore=True, include_center=False, radius= 1)

        valid_vecinos = []

        for vecino in vecinos:
            if isinstance(vecino, (Repiza, RobotLimpieza)):
                continue 
            if vecino.pos in self.model.posiciones_disponibles:
                valid_vecinos.append(vecino) 
                    
        celdas_sucias = self.buscar_celdas_sucia(valid_vecinos)

        if self.carga <= 40: #and len(self.model.lista_recargas) > 0
            delta_vec = lambda xy: np.array(xy) - np.array(self.pos) 
            lis_dis = [np.linalg.norm(delta_vec(fe)) for fe in self.model.lista_recargas]
            list_dir = [delta_vec(fe) for fe in self.model.lista_recargas]
            nearest_station_index = np.argmin(lis_dis)
            dist_nearest_station = list_dir[nearest_station_index]
            x,y = self.pos
            x = x + np.sign(dist_nearest_station)[0]
            y = y + np.sign(dist_nearest_station)[1]
            possible_sig_pos = (x,y)
            if possible_sig_pos in self.model.posiciones_disponibles:
                self.sig_pos = possible_sig_pos
                self.sucia = False
            else:
                possible_sig_pos = self.seleccionar_nueva_pos(valid_vecinos)
                
        elif len(celdas_sucias) == 0:
            self.seleccionar_nueva_pos(valid_vecinos)
            self.cargando = False

        else:
            self.limpiar_una_celda(celdas_sucias)
            self.cargando = False

    def advance(self):
        if self.pos != self.sig_pos:
            self.movimientos += 1
            self.casillas_visitadas.add(self.pos) #Agregue

        if self.pos in self.model.lista_recargas:
            if self.carga < 100:
                self.cargando = True
                self.carga += 25
                if self.carga > 100:
                    self.carga = 100
            else:
                self.cargando = False
                self.model.cant_cargas += 1
                print("-----cargas",self.model.cant_cargas)

            
        if self.cargando == False and self.carga > 0:
            self.carga -= 1
            self.model.grid.move_agent(self, self.sig_pos) 

class Habitacion(Model):
    def __init__(self, M: int, N: int,
                 num_agentes: int = 5,
                 porc_celdas_sucias: float = 0.6,
                 porc_muebles: float = 0.1,
                 modo_pos_inicial: str = 'Fija',
                 ):

        self.num_agentes = num_agentes
        self.porc_celdas_sucias = porc_celdas_sucias
        self.porc_muebles = porc_muebles
        self.cant_cargas = 0

        self.grid = MultiGrid(M, N, False)
        self.schedule = SimultaneousActivation(self)

        self.posiciones_disponibles = [pos for _, pos in self.grid.coord_iter()]
        self.lista_recargas = []
        self.lista_entradas = []
        self.lista_salidas = []

        # Posicionamiento de estacion de recarga
        posiciones_estaciones = [(M-1,7),(M-1,8)]
        for id, pos in enumerate(posiciones_estaciones):
            est = Estacion(int(f"{num_agentes}2{id}") + 1, self)
            self.grid.place_agent(est, pos)
            self.posiciones_disponibles.remove(pos)
            self.lista_recargas.append(pos)

        # Posicionamiento de entradas
        posiciones_entradas = [(2,0),(3,0)]
        for id, pos in enumerate(posiciones_entradas):
            est = Entrada(int(f"{num_agentes}3{id}") + 1, self)
            self.grid.place_agent(est, pos)
            self.posiciones_disponibles.remove(pos)
            self.lista_entradas.append(pos)

        # Posicionamiento de salidas
        posiciones_salidas = [(M-3,0),(M-4,0)]
        for id, pos in enumerate(posiciones_salidas):
            est = Salida(int(f"{num_agentes}4{id}") + 1, self)
            self.grid.place_agent(est, pos)
            self.posiciones_disponibles.remove(pos)
            self.lista_salidas.append(pos)

        #Posicionamiento de repizas 
        posiciones_muebles = [(1,10),(1,6),(6,10),(6,6),(11,10),(11,6)]
        cont=0
        for pid, pos in enumerate(posiciones_muebles):
            for j in range (0,2):
                for i in range (0,3):
                    x,y = pos
                    n_pos = pos
                    n_pos = x+i,y-j
                    if cont >9:
                        un_id=int(f"{num_agentes}{cont}")+1
                    else:
                        un_id=int(f"{num_agentes}0{cont}")+1
                    mueble = Repiza(un_id, self, pid+1)
                    self.grid.place_agent(mueble, n_pos)
                    #self.schedule.add(mueble)
                    self.posiciones_disponibles.remove(n_pos)
                    cont +=1
                    print("x",n_pos)
                print(pid+1,"id,pos",pos)

        # Posicionamiento de celdas sucias
        self.num_celdas_sucias = int(M * N * porc_celdas_sucias)
        print(f"celdas sucias: {self.num_celdas_sucias}")
        posiciones_celdas_sucias = self.random.sample(self.posiciones_disponibles, k=self.num_celdas_sucias)

        for id, pos in enumerate(self.posiciones_disponibles):
            suciedad = pos in posiciones_celdas_sucias
            celda = Celda(int(f"{num_agentes}{id}") + 1, self, suciedad)
            self.grid.place_agent(celda, pos)
     
        # Posicionamiento de agentes robot
        if modo_pos_inicial == 'Aleatoria':
            pos_inicial_robots = self.random.sample(self.posiciones_disponibles, k=num_agentes)
        else:  # 'Fija'
            pos_inicial_robots = [(M-1,N-1),(M-1,N-2),(M-1,N-3),(M-1,N-6),(M-1,N-7)] * num_agentes

        for id in range(num_agentes):
            robot = RobotLimpieza(id, self)
            self.grid.place_agent(robot, pos_inicial_robots[id])
            self.schedule.add(robot)

        self.datacollector = DataCollector(
            model_reporters={"Grid": get_grid, "Cargas": get_cargas,
                             "CeldasSucias": get_sucias},
        )
        for i in posiciones_estaciones:
            self.posiciones_disponibles.append(i)

    def step(self):
        self.datacollector.collect(self)

        self.schedule.step()


    def todoLimpio(self):
        for (content, x, y) in self.grid.coord_iter():
            for obj in content:
                if isinstance(obj, Celda) and obj.sucia:
                    return False
        return True


def get_grid(model: Model) -> np.ndarray:
    grid = np.zeros((model.grid.width, model.grid.height))
    for cell in model.grid.coord_iter():
        cell_content, pos = cell
        x, y = pos
        for obj in cell_content:
            if isinstance(obj, RobotLimpieza):
                grid[x][y] = 2
            elif isinstance(obj, Celda):
                grid[x][y] = int(obj.sucia)
    return grid


def get_cargas(model: Model):
    return [(agent.unique_id, agent.carga) for agent in model.schedule.agents]


def get_sucias(model: Model) -> int:
    """
    Método para determinar el número total de celdas sucias
    :param model: Modelo Mesa
    :return: número de celdas sucias
    """
    sum_sucias = 0
    for cell in model.grid.coord_iter():
        cell_content, pos = cell
        for obj in cell_content:
            if isinstance(obj, Celda) and obj.sucia:
                sum_sucias += 1
    return sum_sucias / model.num_celdas_sucias


def get_movimientos(agent: Agent) -> dict:
    if isinstance(agent, RobotLimpieza):
        return {agent.unique_id: agent.movimientos}
