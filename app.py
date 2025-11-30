from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import pandas as pd
import os

app = Flask(__name__)
csv_files = ['toko.csv', 'jalan.csv']

def binary_search(arr, key):
    left, right = 0, len(arr) - 1
    result = []
    key_lower = key.lower()
    while left <= right:
        mid = (left + right) // 2
        substr = arr[mid][:len(key)].lower()
        if substr < key_lower:
            left = mid + 1
        else:
            right = mid - 1
    i = left
    while i < len(arr) and arr[i][:len(key)].lower() == key_lower:
        result.append(arr[i])
        i += 1
    return result

def load_marker(csv_file):
    df = pd.read_csv(csv_file, skiprows=1, header=None, names=['lantai', 'toko', 'x', 'y'])
    markers = {}
    for lantai, group in df.groupby('lantai'):
        key = f'floor-{lantai}'
        records = group[['toko', 'x', 'y']].rename(columns={'toko': 'name'}).to_dict(orient='records')
        for marker in records:
            marker['x'] = int(marker['x'])
            marker['y'] = int(marker['y'])
        markers[key] = records
    return markers

def load_node_coords(csv_files):
    node_coords = {}
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        for _, row in df.iterrows():
            name = row['toko']
            x = int(row['x'])
            y = int(row['y'])
            lantai = str(row['lantai']).strip()
            if lantai == '3':
                y -= 25
            node_coords[name] = { 'coord': (x, y), 'lantai': lantai }
    return node_coords

def load_toko_data(csv_file):
    df = pd.read_csv(csv_file, skiprows=1, header=None)
    return df[1].tolist()

def bfs(graph, start, goal):
    visited = []
    queue = [[start]] 
    while queue:
        path = queue.pop(0)
        node = path[-1]
        if node == goal:
            # Hapus node "Tangga_" dari hasil rute agar visualisasi bersih
            clean_path = [p for p in path if not p.startswith("Tangga_")]
            return clean_path
        if node not in visited:
            visited.append(node)
            for neighbor in graph.get(node, []):
                new_path = list(path)
                new_path.append(neighbor)
                queue.append(new_path)
    return None

node_coords = load_node_coords(csv_files)

graph = {
    # === LANTAI 1 ===
    'Auto Glaze': ['aglazebonaurum'],
    'aglazebonaurum': ['Auto Glaze', 'Love Bonito', 'Aurum Lab', 'jlneskalatorwest1'],
    'jlneskalatorwest1': ['aglazebonaurum', 'jlnseibu', 'Tangga_West_1'], # Masuk Rantai
    'jlnseibu': ['Seibu', 'jlneskalatorwest1'],
    'jlnstar': ['Seibu', 'Starbuck Coffee - Seibu'],
    'Love Bonito': ['Aurum Lab', 'Auto Glaze', 'aglazebonaurum'],
    'Aurum Lab': ['aglazebonaurum', 'Love Bonito', 'HMNS', 'Melissa'],
    'HMNS': ['Melissa', 'Pamelo', 'Urban Icon', 'Aurum Lab', 'stevhmns'],
    'stevhmns': ['HMNS', 'Steven Madden', 'aldomarhen'],
    'aldomarhen': ['stevhmns', 'Aldo', 'Marhen J', 'jlpedro'],
    'jlpedro': ['aldomarhen', 'Pedro', 'jlwatchzone'],
    'jlwatchzone': ['jlpedro', 'Watch Zone', 'kurasucarles'],
    'kurasucarles': ['jlwatchzone', 'Kurasu Coffee', 'Charles & Keith', 'tissotgc'],
    'tissotgc': ['kurasucarles', 'Tissot', 'GC (Guess Collection)', 'jlstacato'],
    'jlstacato': ['tissotgc', 'Staccato', 'jlmarks', 'jln1A'], 
    'jlmarks': ['jlstacato', 'Marks & Spencer', 'seibumango', 'jlgues', 'Tangga_Tengah_Marks_1'], # Masuk Rantai
    'seibumango': ['jlmarks', 'Starbuck Coffee - Seibu', 'Mango', 'jlgues'],
    'Starbuck Coffee - Seibu': ['jlnstar', 'seibumango'],
    'Seibu': ['jlnstar', 'jlnseibu'],
    'jlgues': ['seibumango', 'Guess', 'tomybershka', 'jlmarks'],
    'Guess': ['jlgues'],
    'tomybershka': ['jlgues', 'Tommy Hilfiger', 'Bershka', 'vicstradvs'],
    'vicstradvs': ['tomybershka', 'Victoria Secret', 'Stradivius', 'jlkelvcln', 'Tangga_Tengah_VS_1'], # Masuk Rantai
    'jlkelvcln': ['vicstradvs', 'Calvin Klein', 'arambath', 'Tangga_Tengah_Daily_1'], # Masuk Rantai
    'arambath': ['jlkelvcln', 'Aramnano Exchange', 'Bath & Body Works', 'jldigimap'],
    'jldigimap': ['arambath', 'Digimap', 'swagior'],
    'swagior': ['jldigimap', 'Swarovski', 'Giardono Ladies', 'Linea', 'Zara (lt 1)', 'jlcntraldept', 'Tangga_East_1'], # Masuk Rantai
    'jlcntraldept': ['jlcntraldept2', 'swagior'],
    'jlcntraldept2': ['jlcntraldept', 'Central Department Store - Men', 'cntralsocial'],
    'Central Department Store - Men': ['jlcntraldept2', 'cntralsocial'],
    'cntralsocial': ['Central Department Store - Men', 'Social House'],
    
    # Toko Leaf Nodes Lt 1
    'Melissa': ['HMNS', 'Aurum Lab'],
    'Pamelo': ['HMNS'],
    'Urban Icon': ['HMNS'],
    'Steven Madden': ['stevhmns'],
    'Aldo': ['aldomarhen'],
    'Marhen J': ['aldomarhen'],
    'Pedro': ['jlpedro'],
    'Watch Zone': ['jlwatchzone'],
    'Kurasu Coffee': ['kurasucarles'],
    'Charles & Keith': ['kurasucarles'],
    'Tissot': ['tissotgc'],
    'GC (Guess Collection)': ['tissotgc'],
    'Staccato': ['jlstacato'],
    'Marks & Spencer': ['jlmarks'],
    'Mango': ['seibumango'],
    'Tommy Hilfiger': ['tomybershka'],
    'Bershka': ['tomybershka'],
    'Victoria Secret': ['vicstradvs'],
    'Stradivius': ['vicstradvs'],
    'Calvin Klein': ['jlkelvcln'],
    'Aramnano Exchange': ['arambath'],
    'Bath & Body Works': ['arambath'],
    'Digimap': ['jldigimap'],
    'Swarovski': ['swagior'],
    'Giardono Ladies': ['swagior'],
    'Linea': ['swagior'],
    'Zara (lt 1)': ['swagior'],
    'Social House': ['cntralsocial'],

    # === SUPER CHAIN DUMMY NODES (Biaya = 5 Langkah per Tangga) ===
    # Chain West
    'Tangga_West_1': ['jlneskalatorwest1', 'Tangga_West_2'],
    'Tangga_West_2': ['Tangga_West_1', 'Tangga_West_3'],
    'Tangga_West_3': ['Tangga_West_2', 'Tangga_West_4'],
    'Tangga_West_4': ['Tangga_West_3', 'Tangga_West_5'],
    'Tangga_West_5': ['Tangga_West_4', 'jlneskalatorwest'], # Nyampe Lt 2

    # Chain Tengah Marks
    'Tangga_Tengah_Marks_1': ['jlmarks', 'Tangga_Tengah_Marks_2'],
    'Tangga_Tengah_Marks_2': ['Tangga_Tengah_Marks_1', 'Tangga_Tengah_Marks_3'],
    'Tangga_Tengah_Marks_3': ['Tangga_Tengah_Marks_2', 'Tangga_Tengah_Marks_4'],
    'Tangga_Tengah_Marks_4': ['Tangga_Tengah_Marks_3', 'Tangga_Tengah_Marks_5'],
    'Tangga_Tengah_Marks_5': ['Tangga_Tengah_Marks_4', 'jlnskecherskids'],

    # Chain Tengah VS
    'Tangga_Tengah_VS_1': ['vicstradvs', 'Tangga_Tengah_VS_2'],
    'Tangga_Tengah_VS_2': ['Tangga_Tengah_VS_1', 'Tangga_Tengah_VS_3'],
    'Tangga_Tengah_VS_3': ['Tangga_Tengah_VS_2', 'Tangga_Tengah_VS_4'],
    'Tangga_Tengah_VS_4': ['Tangga_Tengah_VS_3', 'Tangga_Tengah_VS_5'],
    'Tangga_Tengah_VS_5': ['Tangga_Tengah_VS_4', 'mlbfredtimber'],

    # Chain Tengah Daily
    'Tangga_Tengah_Daily_1': ['jlkelvcln', 'Tangga_Tengah_Daily_2'],
    'Tangga_Tengah_Daily_2': ['Tangga_Tengah_Daily_1', 'Tangga_Tengah_Daily_3'],
    'Tangga_Tengah_Daily_3': ['Tangga_Tengah_Daily_2', 'Tangga_Tengah_Daily_4'],
    'Tangga_Tengah_Daily_4': ['Tangga_Tengah_Daily_3', 'Tangga_Tengah_Daily_5'],
    'Tangga_Tengah_Daily_5': ['Tangga_Tengah_Daily_4', 'jlnourdaily'],

    # Chain East
    'Tangga_East_1': ['swagior', 'Tangga_East_2'],
    'Tangga_East_2': ['Tangga_East_1', 'Tangga_East_3'],
    'Tangga_East_3': ['Tangga_East_2', 'Tangga_East_4'],
    'Tangga_East_4': ['Tangga_East_3', 'Tangga_East_5'],
    'Tangga_East_5': ['Tangga_East_4', 'jlneskalatoreast'],

    # === LANTAI 2 ===
    'Mothercare': ['jlnmothercare'],
    'jlnmothercare': ['Mothercare', 'earlychildren', 'jlneskalatorwest'],
    'jlneskalatorwest': ['Genki Suki', 'jlnmothercare', 'Tangga_West_5'], # Konek ke Rantai Akhir
    'earlychildren': ['jlnmothercare', 'Early Learning Center', 'The Children Place', 'jlnentertainer'],
    'Early Learning Center': ['earlychildren'],
    'The Children Place': ['earlychildren'],
    'jlnentertainer': ['earlychildren', 'The Entertainer', 'gingerlugua'],
    'The Entertainer': ['jlnentertainer'],
    'gingerlugua': ['jlnentertainer', 'Gingersnaps', 'Lugua', 'moobui', 'Wilio', 'Mooimom'],
    'Gingersnaps': ['gingerlugua'],
    'Lugua': ['gingerlugua'],
    'moobui': ['gingerlugua', 'gcardguess', 'Wilio', 'Mooimom', 'Buiboo'],
    'Buiboo': ['jlnmothercare'],
    'Wilio': ['gingerlugua'],
    'Mooimom': ['gingerlugua'],
    'gcardguess': ['moobui', 'G Card Counter (West Mall lt 2)', 'Guess Kids', 'jln1A'],
    'G Card Counter (West Mall lt 2)': ['gcardguess'],
    'Guess Kids': ['gcardguess'],
    'jln1A': ['gcardguess', 'Hydro Flask', 'havaiteva', 'jlstacato', 'Kiddy Cuts'],
    'Kiddy Cuts': ['jln1A'],
    'Hydro Flask': ['jln1A'],
    'havaiteva': ['Havaianas', 'jlnskecherskids', 'Teva', 'jln1A'],
    'Havaianas': ['havaiteva'],
    'Teva': ['havaiteva', 'typoteva'],
    'jlnskecherskids': ['havaiteva', 'Skechers Kids', 'jlncotton', 'typoteva', 'Tangga_Tengah_Marks_5'], # Konek ke Rantai Akhir
    'Skechers Kids': ['jlnskecherskids'],
    'jlncotton': ['jlnskecherskids', 'Cotton On', 'Typo', 'Kids Station - Seibu', 'typoteva'],
    'Cotton On': ['jlncotton'],
    'Typo': ['jlncotton', 'typoteva'],
    'Kids Station - Seibu': ['jlncotton', 'Seibu (Home & Children)'],
    'Seibu (Home & Children)': ['Kids Station - Seibu', 'Genki Suki'],
    'Genki Suki': ['Seibu (Home & Children)', 'jlneskalatorwest'],
    'typoteva': ['Typo', 'Teva', 'jlnskecherskids', 'jlnbirken', 'jlncotton'],
    'jlnbirken': ['Birkenstock', 'northdeux', 'typoteva'],
    'Birkenstock': ['jlnbirken'],
    'northdeux': ['The North Face', 'Deus Ex Machina', 'jlnbirken', 'Superga'],
    'The North Face': ['northdeux'],
    'Deus Ex Machina': ['northdeux'],
    'Superga': ['Nudie Jeans', 'Fossil', 'northdeux', 'conversegior'],
    'Nudie Jeans': ['Superga'],
    'Fossil': ['Superga'],
    'conversegior': ['Converse', 'Giordano', 'The Watch Co', 'Superga'],
    'Converse': ['conversegior'],
    'Giordano': ['conversegior'],
    'The Watch Co': ['conversegior', 'kedscasio'],
    'kedscasio': ['Keds', 'Casio', 'mlbfredtimber', 'The Watch Co'],
    'Keds': ['kedscasio'],
    'Casio': ['kedscasio'],
    'mlbfredtimber': ['kedscasio', 'MLB', 'Fred Perry', 'Timberland', 'jlnnewera', 'Tangga_Tengah_VS_5'], # Konek ke Rantai Akhir
    'MLB': ['mlbfredtimber'],
    'Fred Perry': ['mlbfredtimber'],
    'Timberland': ['mlbfredtimber'],
    'jlnnewera': ['mlbfredtimber', 'New Era', 'DAMN I LOVE INDONESIA'],
    'New Era': ['jlnnewera'],
    'DAMN I LOVE INDONESIA': ['jlnnewera', 'Atmos Pink', 'jlnourdaily'],
    'Atmos Pink': ['DAMN I LOVE INDONESIA'],
    'jlnourdaily': ['Our Daily Dose', 'DAMN I LOVE INDONESIA', 'jlndope', 'Tangga_Tengah_Daily_5'], # Konek ke Rantai Akhir
    'Our Daily Dose': ['jlnourdaily'],
    'jlndope': ['Dope & Dapper', 'jlnowndays', 'jlnourdaily'],
    'Dope & Dapper': ['jlndope'],
    'jlnowndays': ['Owndays', 'jlndope', 'acmeinstru'],
    'Owndays': ['jlnowndays'],
    'acmeinstru': ['ADLV (Acme De La Vie)', 'Instrumentum', 'G Card Counter (East Mall lt 2)', 'jlnowndays'],
    'ADLV (Acme De La Vie)': ['acmeinstru'],
    'Instrumentum': ['acmeinstru'],
    'G Card Counter (East Mall lt 2)': ['Instrumentum', 'acmeinstru', 'Lacoste', 'jln35', 'jlneskalatoreast'],
    'Lacoste': ['G Card Counter (East Mall lt 2)', 'jlneskalatoreast'],
    'jlneskalatoreast': ['Zara (lt 2)', 'Lacoste', "Levi's", 'G Card Counter (East Mall lt 2)', 'jln35', 'Tangga_East_5'], # Konek ke Rantai Akhir
    'Zara (lt 2)': ['jlneskalatoreast'],
    "Levi's": ['jlneskalatoreast'],
    'jln35': ['Dr. Martens', 'G Card Counter (East Mall lt 2)', 'Instrumentum', 'jlnDS1', 'jlneskalatoreast'],
    'Dr. Martens': ['jln35'],
    'jlnDS1': ['Central Department Store - Kids', 'jln35'],
    'Central Department Store - Kids': ['jlnDS1', 'Kopi Kenangan'],
    'Kopi Kenangan': ['jln10', 'Central Department Store - Kids'],
    'jln10': ['Kopi Kenangan', 'Kempideli'],
    'Kempideli': ['jln10', 'Paulaner Brauhaus'],
    'Paulaner Brauhaus': ['Kempideli'],
}

@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    username = 'User'
    floors = [
        {"name": "Floor 1", "image": "/static/images/floor-1.png", "key": "floor-1"},
        {"name": "Floor 2", "image": "/static/images/floor-2.png", "key": "floor-2"}
    ]
    
    markers = load_marker(csv_files[0])
    list_toko = load_toko_data(csv_files[0])

    return render_template("home_page.html", username=username, floors=floors, markers=markers, list_toko=list_toko, node_coords=node_coords)

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    key = data.get('query')
    toko = load_toko_data('toko.csv')
    list_toko = binary_search(toko, key)
    return jsonify({"list_toko": list_toko})

@app.route('/route')
def route():
    start_node = request.args.get('start')
    goal_node = request.args.get('goal')
    rute = bfs(graph, start_node, goal_node)
    
    if not rute:
        return jsonify({"error": "Rute tidak ditemukan!"})

    coords_rute = []
    for node in rute:
        if node in node_coords:
            coord = node_coords.get(node)['coord']
            coords_rute.append({"name": node, "coord": coord})

    return jsonify({
        "route": rute,
        "coordinates": coords_rute
    })

if __name__ == '__main__':
    app.run(debug=True)