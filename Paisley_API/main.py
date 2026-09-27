from fastapi import FastAPI
import osmnx as ox
import networkx as nx

app = FastAPI(title="API Rota Segura - Backend")

print("Iniciando servidor e lendo malha viária de Osasco...")
#Estou usando o arquivo 'mapa_osasco_seguro.graphml' que foi gerado no notebook, este grafo possui dados exclusivos de Osasco por questao de Peso, trocar no notebook as cidades desejadas e extrair para utilizar aqui.
grafo = ox.load_graphml('mapa_osasco_seguro.graphml')
for u, v, key, data in grafo.edges(keys=True, data=True):
    if 'custo_total' in data:
        data['custo_total'] = float(data['custo_total'])

print("Mapa carregado! API pronta para receber requisições.")

@app.get("/")
def status_da_api():
    return {"status": "Online", "mensagem": "Pode mandar as coordenadas, Dev!"}

# --- FUNÇÃO AUXILIAR (Para não repetirmos código) ---
def converter_nos_para_gps(grafo, lista_nos):
    coordenadas = []
    for no in lista_nos:
        lat = grafo.nodes[no]['y']
        lon = grafo.nodes[no]['x']
        coordenadas.append({"latitude": lat, "longitude": lon})
    return coordenadas

# --- O ENDPOINT---
@app.get("/calcular_rota")
def calcular_rota(lat_origem: float, lon_origem: float, lat_destino: float, lon_destino: float):
    # 1. Achando os cruzamentos mais próximos (X = Longitude, Y = Latitude)
    no_origem = ox.distance.nearest_nodes(grafo, X=lon_origem, Y=lat_origem)
    no_destino = ox.distance.nearest_nodes(grafo, X=lon_destino, Y=lat_destino)
    
    # 2. Comparando Algoritmos (Calculando as DUAS opções)
    # Rota Rápida (Focada apenas em distância)
    rota_rapida_nos = nx.shortest_path(G=grafo, source=no_origem, target=no_destino, weight='length')
    
    # Rota Segura (O algoritmo de segurança)
    rota_segura_nos = nx.shortest_path(G=grafo, source=no_origem, target=no_destino, weight='custo_total')
    
    # 3. Transformando matemática em GPS usando nossa função auxiliar
    gps_rota_rapida = converter_nos_para_gps(grafo, rota_rapida_nos)
    gps_rota_segura = converter_nos_para_gps(grafo, rota_segura_nos)
        
    # 4. Entregando o pacote completo e organizado para o Mobile
    return {
        "status": "sucesso",
        "rota_rapida": {
            "total_de_pontos": len(gps_rota_rapida),
            "coordenadas": gps_rota_rapida
        },
        "rota_segura": {
            "total_de_pontos": len(gps_rota_segura),
            "coordenadas": gps_rota_segura
        }
    }