# import pandas as pd

# def load_toko_data(csv_file):
#     df = pd.read_csv(csv_file, skiprows=1, header=None)
#     # Ambil kolom nama toko (kolom 1, index 1)
#     toko_list = df[1].tolist()
#     return toko_list

# def binary_search_prefix(arr, prefix):
#     left, right = 0, len(arr) - 1
#     result = []

#     # Cari indeks pertama kata yang prefix-nya >= prefix input
#     while left <= right:
#         mid = (left + right) // 2
#         # Ambil substring kata sampai panjang prefix
#         substr = arr[mid][:len(prefix)]
        
#         if substr < prefix:
#             left = mid + 1
#         else:
#             right = mid - 1

#     # Setelah loop, left adalah posisi pertama yang mungkin cocok
#     # Ambil semua kata yang cocok dari posisi left dan seterusnya
#     i = left
#     while i < len(arr) and arr[i].startswith(prefix):
#         result.append(arr[i])
#         i += 1
    
#     return result


# # Contoh data yang sudah diurutkan
# list_toko = load_toko_data('toko.csv')

# # Contoh pemakaian
# prefix_input = "Ce"
# hasil = binary_search_prefix(list_toko, prefix_input)
# print("Hasil autocomplete:", hasil)

import pandas as pd

# def load_toko_data(csv_file):
#     df = pd.read_csv(csv_file, skiprows=1, header=None, encoding='utf-8')
#     # Ambil kolom nama toko (kolom 1, index 1) dan hapus spasi depan/belakang
#     toko_list = df[1].astype(str).str.strip().tolist()
    
#     # Urutkan supaya binary search berjalan benar
#     toko_list.sort(key=lambda x: x.lower())  # Urutkan pakai lowercase
    
#     return toko_list

def load_toko_data(csv_file):
    df = pd.read_csv(csv_file, skiprows=1, header=None)
    return df[1].tolist()

def binary_search_prefix(arr, prefix):
    left, right = 0, len(arr) - 1
    result = []
    
    # Lowercase prefix agar pencarian tidak sensitif huruf besar/kecil
    prefix_lower = prefix.lower()

    while left <= right:
        mid = (left + right) // 2
        # Substring huruf kecil
        substr = arr[mid][:len(prefix)].lower()
        
        if substr < prefix_lower:
            left = mid + 1
        else:
            right = mid - 1

    # Dari left, ambil semua yang cocok (pakai startswith juga lowercase)
    i = left
    while i < len(arr) and arr[i][:len(prefix)].lower() == prefix_lower:
        result.append(arr[i])  # Tetap simpan versi asli
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

marker = load_marker('toko.csv')
# Contoh data
list_toko = load_toko_data('toko.csv')

# Tes prefix input
print(marker)
# prefix_input = "Cal"
# hasil = binary_search_prefix(list_toko, prefix_input)
# print("Hasil autocomplete:", hasil)