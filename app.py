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
            return path

        if node not in visited:
            visited.append(node)
            for neighbor in graph.get(node, []):
                new_path = list(path)
                new_path.append(neighbor)
                queue.append(new_path)

    return None

node_coords = load_node_coords(csv_files)

graph = {
    #lantai 1
    'Auto Glaze': ['aglazebonaurum'],
    'aglazebonaurum': ['Auto Glaze', 'Love Bonito', 'Aurum Lab', 'jlneskalatorwest1'],
    'jlneskalatorwest1': ['aglazebonaurum', 'jlnseibu'],
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
    'jlstacato': ['tissotgc', 'Staccato', 'jlmarks'],
    'jlmarks': ['jlstacato', 'Marks & Spencer', 'seibumango', 'jlgues'],
    'seibumango': ['jlmarks', 'Starbuck Coffee - Seibu', 'Mango', 'jlgues'],
    'Starbuck Coffee - Seibu': ['jlnstar', 'seibumango'],
    'Seibu': ['jlnstar', 'jlnseibu'],
    'jlgues': ['seibumango', 'Guess', 'tomybershka', 'jlmarks'],
    'Guess': ['jlgues'],
    'tomybershka': ['jlgues', 'Tommy Hilfiger', 'Bershka', 'vicstradvs'],
    'vicstradvs': ['tomybershka', 'Victoria Secret', 'Stradivarius', 'jlkelvcln'],
    'jlkelvcln': ['vicstradvs', 'Calvin Klein', 'arambath'],
    'arambath': ['jlkelvcln', 'Aramnano Exchange', 'Bath & Body Works', 'jldigimap'],
    'jldigimap': ['arambath', 'Digimap', 'swagior'],
    'swagior': ['jldigimap', 'Swarovski', 'Giardono Ladies', 'Linea', 'Zara (lt 1)', 'jlcntraldept'],
    'jlcntraldept': ['jlcntraldept2', 'swagior'],
    'jlcntraldept2': ['jlcntraldept', 'Central Department Store - Men', 'cntralsocial'],
    'Central Department Store - Men': ['jlcntraldept2', 'cntralsocial'],
    'cntralsocial': ['Central Department Store - Men', 'Social House'],
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
    'Stradivarius': ['vicstradvs'],
    'Calvin Klein': ['jlkelvcln'],
    'Aramnano Exchange': ['arambath'],
    'Bath & Body Works': ['arambath'],
    'Digimap': ['jldigimap'],
    'Swarovski': ['swagior'],
    'Giardono Ladies': ['swagior'],
    'Linea': ['swagior'],
    'Zara (lt 1)': ['swagior'],
    'Social House': ['cntralsocial'],
    
    #lantai 2
    'Mothercare': ['jlnmothercare'],
    'jlnmothercare': ['Mothercare', 'earlychildren', 'jlneskalatorwest'],
    'jlneskalatorwest': ['Genki Suki', 'jlnmothercare'],
    'earlychildren': ['jlnmothercare', 'Early Learning Center', 'The Children Place', 'jlnentertainer'],
    'Early Learning Center': ['earlychildren'],
    'The Children Place': ['earlychildren'],
    'jlnentertainer': ['earlychildren', 'The Entertainer', 'gingerlugua'],
    'The Entertainer': ['jlnentertainer'],
    'gingerlugua': ['jlnentertainer', 'Gingersnaps', 'Lugua', 'moobui'],
    'Gingersnaps': ['gingerlugua'],
    'Lugua': ['gingerlugua'],
    'moobui': ['gingerlugua', 'gcardguess'],
    'gcardguess': ['moobui', 'G Card Counter (West Mall lt 2)', 'Guess Kids', 'jln1A'],
    'G Card Counter (West Mall lt 2)': ['gcardguess'],
    'Guess Kids': ['gcardguess'],
    'jln1A': ['gcardguess', 'Hydro Flask', 'havaiteva'],
    'Hydro Flask': ['jln1A'],
    'havaiteva': ['Havaianas', 'jlnskecherskids', 'Teva', 'jln1A'],
    'Havaianas': ['havaiteva'],
    'Teva': ['havaiteva'],
    'jlnskecherskids': ['havaiteva', 'Skechers Kids', 'jlncotton', 'typoteva'],
    'Skechers Kids': ['jlnskecherskids'],
    'jlncotton': ['jlnskecherskids', 'Cotton On', 'Typo', 'Kids Station - Seibu', 'typoteva'],
    'Cotton On': ['jlncotton'],
    'Typo': ['jlncotton'],
    'Kids Station - Seibu': ['jlncotton', 'Seibu (Home & Children)'],
    'Seibu (Home & Children)': ['Kids Station - Seibu', 'Genki Suki'],
    'Genki Suki': ['Seibu (Home & Children)', 'jlneskalatorwest'],
    'typoteva': ['Typo', 'Teva', 'jlnskecherskids', 'jlnbirken', 'jlncotton'],
    'Typo': ['typoteva'],
    'Teva': ['typoteva'],
    'jlnbirken': ['Birkenstock', 'northdeux', 'typoteva'],
    'northdeux': ['The North Face', 'Deus Ex Machina', 'jlnbirken', 'Superga'],
    'The North Face': ['northdeux'],
    'Deus Ex Machina': ['northdeux'],
    'Superga': ['Nudie Jeans', 'Fossil', 'northdeux', 'conversegior'],
    'Nuide Jeans': ['Superga'],
    'Fossil': ['Superga'],
    'conversegior': ['Converse', 'Giordiano', 'The Watch Co', 'Superga'],
    'Converse': ['conversegior'],
    'Giordiano': ['conversegior'],
    'The Watch Co': ['conversegior', 'kedscasio'],
    'kedscasio': ['Keds', 'Casio', 'mlbfredtimber', 'The Watch Co'],
    'Keds': ['kedscasio'],
    'Casio': ['kedscasio'],
    'mlbfredtimber': ['kedscasio', 'MLB', 'Fred Perry', 'Timberland', 'jlnnewera'],
    'MLB': ['mlbfredtimber'],
    'Fred Perry': ['mlbfredtimber'],
    'Timberland': ['mlbfredtimber'],
    'jlnnewera': ['mlbfredtimber', 'New Era', 'DAMN I LOVE INDONESIA'],
    'New Era': ['jlnnewera'],
    'DAMN I LOVE INDONESIA': ['jlnnewera', 'Atmos Pink', 'jlnourdaily'],
    'Atmos Pink': ['DAMN I LOVE INDONESIA'],
    'jlnourdaily': ['Our Daily Pose', 'DAMN I LOVE INDONESIA', 'jlndope'],
    'Our Daily Pose': ['jlnourdaily'],
    'jlndope': ['Dope & Dapper', 'jlnowndays', 'jlnourdaily'],
    'Dope & Dopper': ['jlndope'],
    'jlnowndays': ['Owndays', 'jlndope', 'acmeinstru'],
    'Owndays': ['jlnowndays'],
    'acmeinstru': ['ADLV (Acme De La Vie)', 'Instrumentum', 'G Card Counter (East Mall lt 2)', 'jlnowndays'],
    'ADLV (Acme De La Vie)': ['acmeinstru'],
    'Instrumentum': ['acmeinstru'],
    'G Card Counter (East Mall lt 2)': ['Instrumentum', 'acmeinstru', 'Lacoste', 'jln35', 'jlneskalatoreast'],
    'Lacoste': ['G Card Counter (East Mall lt 2)', 'jlneskalatoreast'],
    'jlneskalatoreast': ['Zara (lt 2)', 'Lacoste', "Levi's", 'G Card Counter (East Mall lt 2)', 'jln35'],
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
    
    #lantai 3
    'Irwan Team Hair Design': ['jlneverlash'],
    'jlneverlash': ['Irwan Team Hair Design', 'Everlash', 'jlnbrow', 'jlnalunever'],
    'Everlash': ['jlneverlash'],
    'jlnbrow': ['jlneverlash', 'Browhaus & Strip', 'Bathaholic'],
    'jlnalunever': ['jlnalun', 'jlneverlash'],
    'jlnalun': ['jlnalunever', 'Alun-Alun Indonesia'],
    'Alun-Alun Indonesia': ['Pipiltin Cocoa', 'Waroeng Kopi', 'jlnalun'],
    'Pipiltin Cocoa': ['Alun-Alun Indonesia', 'Waroeng Kopi', 'jlnpipil'],
    'Waroeng Kopi': ['Alun-Alun Indonesia', 'Pipiltin Cocoa'],
    'Browhaus & Strip': ['jlnbrow'],
    'Bathaholic': ['Kenko', 'Happy Dental Clinic', 'WL Waxing', 'jlnbrow', 'jlnjohnny'],
    'Kenko': ['Bathaholic'],
    'Happy Dental Clinic': ['Bathaholic'],
    'WL Waxing': ['Bathaholic'],
    'jlnjohnny': ['Johnny Andrean', 'Bathaholic', 'Beauty Haul'],
    'Johnny Andrean': ['jlnjohnny'],
    'Beauty Haul': ['Anna Wijaya Salon', 'jlnjohnny', 'jlnbarberia'],
    'Anna Wijaya Salon': ['Beauty Haul'],
    'jlnbarberia': ['Lighthouse', 'Barberia Shortcut', 'Beauty Haul', 'jlnZAP'],
    'Lighthouse': ['jlnbarberia'],
    'Barberia Shortcut': ['jlnbarberia'],
    'jlnZAP': ['ZAP', 'jlnsaber', 'jlnbarberia'],
    'ZAP': ['jlnZAP'],
    'jlnsaber': ['Sabrina', 'jlnZAP', 'Erha Ultimate', 'jlnurban'],
    'Sabrina': ['jlnsaber'],
    'Erha Ultimate': ['jlnsaber', 'jlnurban'],
    'jlnurban': ['Urban Traveller', 'Erha Ultimate', 'jlnsaber', 'jlnnailvans'],
    'Urban Traveller': ['jlnurban'],
    'jlnnailvans': ['Tokyo Nail Collection', 'The Nail Shop', 'Vans', 'jlnbags', 'jlnurban'],
    'Tokyo Nail Collection': ['jlnnailvans'],
    'The Nail Shop': ['jlnnailvans'],
    'Vans': ['jlnnailvans', 'jlnadivans'],
    'jlnbags': ["Bag's City", 'jlnadidas', 'jlnnailvans', 'jlnadivans'],
    "Bag's City": ['jlnbags'],
    'jlnadidas': ['Adidas', 'jlnbags', 'jlnadids1'],
    'Adidas': ['jlnadidas', 'jlnadivans'],
    'jlnadids1': ['jlnpipiladi', 'jlnadidas'],
    'jlnpipiladi': ['jlnpipil', 'jlnadids1'],
    'jlnpipil': ['jlnpipiladi', 'Pipiltin Cocoa'],
    'jlnadivans': ['jlnadidas', 'jlnbags', 'Vans', 'Adidas', 'CAT Footwear Pop Up'],
    'CAT Footwear Pop Up': ['jlnadivans', 'Fisik Footbal', 'jlnreefil'],
    'Fisik Footbal': ['CAT Footwear Pop Up'],
    'jlnreefil': ['Reebok', 'FILA', 'jlnhoops', 'CAT Footwear Pop Up'],
    'Reebok': ['jlnreefil'],
    'FILA': ['jlnreefil'],
    'jlnhoops': ['Hoops', 'Skechers', 'Timex', 'jlnreefil'],
    'Hoops': ['jlnhoops'],
    'Skechers': ['jlnhoops', 'Timex'],
    'Timex': ['jlnhoops', 'Skechers', 'jlnnikun'],
    'jlnnikun': ['Nike', 'Under Armour', 'Timex', 'Sorcery World'],
    'Nike': ['jlnnikun'],
    'Under Armour': ['jlnnikun'],
    'Sorcery World': ['jlnnikun', 'Puma', 'New Balance', 'Skull Pig'],
    'Puma': ['Sorcery World', 'Skull Pig'],
    'New Balance': ['Sorcery World', 'Skull Pig'],
    'Skull Pig': ['2XU Performance Store', 'Asics', 'Puma', 'New Balance', 'Sorcery World', 'Corkcicle Pop Up'],
    '2XU Performance Store': ['Corkcicle Pop Up', 'Skull Pig'],
    'Asics': ['Corkcicle Pop Up', 'Skull Pig'],
    'Corkcicle Pop Up': ['Stanley', 'Salomon', 'Asics', '2XU Performance Store', 'jlnbridar', 'Skull Pig'],
    'jlnbridar': ['Arena', 'jlnhoka', 'Bridges Eyewear', 'Kettler', 'Corkcicle Pop Up'],
    'Arena': ['jlnbridar'],
    'Kettler': ['jlnbridar'],
    'Bridges Eyewear': ['jlnbridar', 'jlnowlhush'],
    'jlnhoka': ['Crocs', 'Hoka', 'Foot Locker', 'jlnbridar', 'Lego', 'jlnowlhush'],
    'Crocs': ['jlnhoka'],
    'Hoka': ['jlnhoka'],
    'Lego': ['jlnhoka'],
    'Foot Locker': ['jlnhoka'],
    'jlnowlhush': ['OWL', 'Hush Puppies', 'Wood', 'jlnhoka', 'Bridges Eyewear', 'Starbucks Coffee'],
    'OWL': ['jlnowlhush'],
    'Wood': ['jlnowlhush', 'Starbucks Coffee'],
    'Hush Puppies': ['jlnowlhush'],
    'Starbucks Coffee': ['Wood', 'The Executive', 'Minimal', 'Gino Mariani', 'The Body Shop', 'jlnowlhush'],
    'The Executive': ['Starbucks Coffee'],
    'Gino Mariani': ['Starbucks Coffee'],
    'Minimal': ['Starbucks Coffee'],
    'The Body Shop': ['Et Catera', 'Bodies.co', 'jlncrocodile', 'Starbucks Coffee'],
    'Et Catera': ['The Body Shop'],
    'Bodies.co': ['The Body Shop'],
    'jlncrocodile': ['Crocodile', 'Watch Studio', 'The Body Shop'],
    'Crocodile': ['jlncrocodile'],
    'Watch Studio': ['Brodo', 'jlncrocodile', 'Polo', 'jlnniuchi'],
    'Brodo': ['Watch Studio'],
    'Polo': ['Watch Studio'],
    'jlnniuchi': ['CHICHA San Chen', 'Niu', 'jlnsociolla', 'Watch Studio'],
    'CHICHA San Chen': ['jlnniuchi'],
    'Niu': ['jlnniuchi'],
    'jlnsociolla': ['Sociolla', 'jlncalldi', 'jlnniuchi'],
    'Sociolla': ['jlnsociolla'],
    'jlncalldi': ['Gaudi', 'jlnsociolla', 'Callie', 'jlnsoul'],
    'Gaudi': ['jlncalldi'],
    'Callie': ['jlncalldi'],
    'jlnsoul': ['Soul Of God', 'jlnminiso', 'jlncalldi'],
    'Soul of God': ['jlnsoul'],
    'jlnminiso': ['Miniso', '3mongkis', 'Scoop', 'jlnsoul', 'jlnlocal'],
    'Miniso': ['jlnminiso'],
    '3mongkis': ['jlnminiso'],
    'Scoop': ['jlnminiso'],
    'jlnlocal': ['Localstrunk', 'Un Bakers', 'Dynamic Bakery', 'Sensatia Botanicals', 'Oh! Some', 'jlnminiso', 'jlngramed'],
    'Localstrunk': ['jlnlocal'],
    'Un Bakers': ['jlnlocal'],
    'Dynamic Bakery': ['jlnlocal'],
    'Sensatia Botanicals': ['jlnlocal'],
    'Oh! Some': ['jlnlocal'],
    'jlngramed': ['jlnlocal', 'Gramedia'],
    'Gramedia': ['jlngramed'],
}

@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    username = 'User'
    floors = [
        {"name": "Floor 1", "image": "/static/images/floor-1.png", "key": "floor-1"},
        {"name": "Floor 2", "image": "/static/images/floor-2.png", "key": "floor-2"},
        {"name": "Floor 3", "image": "/static/images/floor-3.png", "key": "floor-3"},
        {"name": "Floor 3A", "image": "/static/images/floor-3A.png", "key": "floor-3A"},
        {"name": "Floor 5", "image": "/static/images/floor-5.png", "key": "floor-5"},
        {"name": "Floor 8", "image": "/static/images/floor-8.png", "key": "floor-8"},
        {"name": "Floor B", "image": "/static/images/floor-B.png", "key": "floor-B"},
        {"name": "Floor G", "image": "/static/images/floor-G.png", "key": "floor-G"},
        {"name": "Floor LG", "image": "/static/images/floor-LG.png", "key": "floor-LG"},
        {"name": "Floor UG", "image": "/static/images/floor-UG.png", "key": "floor-UG"},
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
    
    coords_rute = []
    for node in rute:
        coord = node_coords.get(node)['coord']
        coords_rute.append({"name": node, "coord": coord})

    return jsonify({
        "route": rute,
        "coordinates": coords_rute
    })

if __name__ == '__main__':
    app.run(debug=True)