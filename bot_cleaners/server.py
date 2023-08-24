import mesa

from .model import Habitacion, RobotLimpieza, Celda, Repiza, Estacion, Entrada, Salida

MAX_NUMBER_ROBOTS = 20
lis_colores = ["#c34a36","#f9a076","#f1c232","#c17f98","#002955","#6a329f"]

def agent_portrayal(agent):
    if isinstance(agent, RobotLimpieza):
        return {"Shape": "circle", "Filled": "false", "Color": "Cyan", "Layer": 4, "r": 0.9,
                "text": f"{agent.carga}", "text_color": "black"}
    elif isinstance(agent, Repiza):
        portrayal = {"Shape": "rect", "Filled": "true", "Layer": 0, "w": 0.9, "h": 0.9, "text_color": "Black"}
        print("Uid:",agent.unique_id,"Pid:",agent.product_id)
        if agent.product_id == 1:
            portrayal["Color"] = lis_colores[0]
        elif agent.product_id == 2:
            portrayal["Color"] = lis_colores[1] 
        elif agent.product_id == 3:
            portrayal["Color"] = lis_colores[2] 
        elif agent.product_id == 4:
            portrayal["Color"] = lis_colores[3] 
        elif agent.product_id == 5:
            portrayal["Color"] = lis_colores[4]
        elif agent.product_id == 6:
            portrayal["Color"] = lis_colores[5]
        return portrayal
    elif isinstance(agent, Estacion):
        return {"Shape": "circle", "Filled": "false", "Color": "#a5ff1c", "Layer": 1,
                 "r": 0.9, "text":"⚡", "text_color": "black"}
    elif isinstance(agent, Entrada):
        return {"Shape": "rect", "Filled": "true", "Layer": 0, "w": 0.9, "h": 0.9, "text_color": "Black","Color":"#38761d","text_color": "#FFFFFF","text":"In"}
    elif isinstance(agent, Salida):
        return {"Shape": "rect", "Filled": "true", "Layer": 0, "w": 0.9, "h": 0.9, "text_color": "Black","Color":"#b45f06","text_color": "#FFFFFF","text":"Out"}
    elif isinstance(agent, Celda):
        return {"Shape": "rect", "Filled": "true", "Layer": 0, "w": 0.9, "h": 0.9, "text_color": "Black","Color":"#D3D3D3"}



grid = mesa.visualization.CanvasGrid(
    agent_portrayal, 16, 12, 400, 300)
chart_celdas = mesa.visualization.ChartModule(
    [{"Label": "CeldasSucias", "Color": '#36A2EB', "label": "Celdas Sucias"}],
    50, 200,
    data_collector_name="datacollector"
)

model_params = {
    "num_agentes": mesa.visualization.Slider(
        "Número de Robotz",
        5,
        2,
        MAX_NUMBER_ROBOTS,
        1,
        description="Escoge cuántos robots deseas implementar en el modelo",
    ),
    "porc_celdas_sucias": mesa.visualization.Slider(
        "Porcentaje de Celdas Sucias",
        0.3,
        0.0,
        0.75,
        0.05,
        description="Selecciona el porcentaje de celdas sucias",
    ),
    "porc_muebles": mesa.visualization.Slider(
        "Porcentaje de Muebles",
        0.1,
        0.0,
        0.25,
        0.01,
        description="Selecciona el porcentaje de muebles",
    ),
    "modo_pos_inicial": mesa.visualization.Choice(
        "Posición Inicial de los Robots",
        "Aleatoria",
        ["Fija", "Aleatoria"],
        "Seleciona la forma se posicionan los robots"
    ),
    "M": 16, #X
    "N": 12, #Y
}

server = mesa.visualization.ModularServer(
    Habitacion, [grid, chart_celdas],
    "botCleaner", model_params, 8521
)
