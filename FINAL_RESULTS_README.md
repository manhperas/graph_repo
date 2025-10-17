# 🎵 FINAL MUSIC NETWORK RESULTS

## 📋 Tổng quan

File `data/processed/final_music_network_results.json` chứa kết quả cuối cùng của dự án Music Network Graph - phân tích mạng lưới nghệ sĩ US-UK.

## 📊 Thống kê Tổng quan

- **Tổng số nodes:** 315
- **Tổng số edges:** 458
- **Số nghệ sĩ:** 167 (144 artists + 12 solo_artists + 11 bands)
- **Số thể loại nhạc:** 68
- **Số hãng thu âm:** 80

## 📁 Cấu trúc File JSON

### 1. metadata
```json
{
  "project": "Music Network Graph - US-UK Artists",
  "description": "Comprehensive music network analysis",
  "generated_at": "2025-10-17T11:34:50.757075",
  "version": "2.0"
}
```

### 2. statistics
```json
{
  "total_nodes": 315,
  "total_edges": 458,
  "total_artists": 167,
  "total_genres": 68,
  "total_labels": 80,
  "node_types": {
    "band": 11,
    "genre": 68,
    "label": 80,
    "artist": 144,
    "solo_artist": 12
  },
  "edge_types": {
    "plays_genre": 109,
    "signed_to": 117,
    "collaborates_with": 232
  }
}
```

### 3. network_data
Chứa dữ liệu mạng thô từ NetworkX:
- **nodes**: Dictionary của tất cả nodes với attributes
- **edges**: Array của tất cả edges với source, target, type, weight

### 4. artists
Array chi tiết của 167 nghệ sĩ:
```json
{
  "id": "Coldplay",
  "name": "Coldplay",
  "type": "band",
  "origin": "London, England",
  "genres": ["Alternative rock", "pop rock", "post-Britpop"],
  "labels": ["Parlophone", "Capitol"],
  "years_active": "1997-present",
  "connections": {
    "collaborators": 10,
    "genres": 4,
    "labels": 5
  },
  "wikipedia_analysis": {...}  // Dữ liệu phân tích Wikipedia
}
```

### 5. genres
Array của 68 thể loại nhạc:
```json
{
  "id": "genre_Alternative rock",
  "name": "Alternative rock",
  "category": "musical_genre"
}
```

### 6. labels
Array của 80 hãng thu âm:
```json
{
  "id": "label_Parlophone",
  "name": "Parlophone",
  "category": "record_label"
}
```

### 7. relationships
Phân loại chi tiết các mối quan hệ:

#### collaborations (232 relationships)
```json
{
  "artist1": "Coldplay",
  "artist2": "Seal",
  "weight": 1.0,
  "detected_from": "wikipedia_links"
}
```

#### genre_associations (109 relationships)
```json
{
  "artist": "Coldplay",
  "genre": "genre_Alternative rock",
  "weight": 2.0,
  "priority": 1
}
```

#### label_relationships (117 relationships)
```json
{
  "artist": "Coldplay",
  "label": "label_Parlophone",
  "weight": 1.0,
  "relationship": "record_label"
}
```

## 🔍 Cách sử dụng

### Load và phân tích dữ liệu:
```python
import json

with open('data/processed/final_music_network_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Truy cập thống kê
stats = data['statistics']
print(f"Total artists: {stats['total_artists']}")

# Liệt kê nghệ sĩ
for artist in data['artists']:
    print(f"{artist['name']} ({artist['origin']}) - {artist['connections']['collaborators']} collaborators")

# Phân tích collaborations
for collab in data['relationships']['collaborations'][:10]:
    print(f"{collab['artist1']} ↔ {collab['artist2']}")
```

### Load vào NetworkX:
```python
import networkx as nx

# Từ network_data
G = nx.Graph()
for node_id, node_attrs in data['network_data']['nodes'].items():
    G.add_node(node_id, **node_attrs)

for edge in data['network_data']['edges']:
    G.add_edge(edge['source'], edge['target'],
               edge_type=edge['edge_type'],
               weight=edge['weight'],
               **edge.get('attributes', {}))
```

## 📈 Phân tích có thể thực hiện

1. **Network Metrics:**
   - Degree centrality
   - Betweenness centrality
   - Clustering coefficient

2. **Community Detection:**
   - Tìm nhóm nghệ sĩ liên kết chặt chẽ
   - Phân tích theo thể loại

3. **Path Analysis:**
   - Đường đi ngắn nhất giữa nghệ sĩ
   - Six degrees of separation trong nhạc pop

4. **Genre Analysis:**
   - Thể loại phổ biến nhất
   - Mối quan hệ giữa các thể loại

5. **Label Analysis:**
   - Hãng thu có nhiều nghệ sĩ nhất
   - Mạng lưới hãng thu

## 🎯 Nghệ sĩ nổi bật

### Top 5 nghệ sĩ theo số kết nối:
1. **Arctic Monkeys** (35 connections)
2. **Tame Impala** (33 connections)
3. **Arcade Fire** (29 connections)
4. **Vampire Weekend** (27 connections)
5. **Pearl Jam** (27 connections)

### Thể loại phổ biến:
1. Alternative rock
2. Pop rock
3. Post-Britpop
4. Pop
5. Indie rock

## 📝 Ghi chú

- Dữ liệu được tạo từ việc phân tích Wikipedia pages
- Một số node có thể thiếu thông tin đầy đủ
- Các kết nối được phát hiện tự động từ liên kết Wikipedia
- File có kích thước 341KB với thông tin chi tiết

## 🔄 Cập nhật tương lai

File này có thể được mở rộng với:
- Thông tin giải thưởng (awards)
- Dữ liệu bảng xếp hạng (charts)
- Quan hệ producer
- Thông tin về các thành viên ban nhạc

---

**Generated on:** 2025-10-17
**File size:** 341KB
**Format:** JSON
