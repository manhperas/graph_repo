# 🎵 MẠNG LƯỚI NGHỆ SĨ ÂM NHẠC US-UK

*Dự án phân tích mạng lưới quan hệ giữa các nghệ sĩ nhạc pop/rock Mỹ-Anh sử dụng dữ liệu Wikipedia*

## 📖 Giới thiệu

Dự án này xây dựng một mạng lưới quan hệ phức tạp giữa các nghệ sĩ nhạc US-UK, sử dụng dữ liệu từ Wikipedia để phân tích các mối liên kết âm nhạc, hợp tác, và thuộc tính nghệ sĩ.

### 🎯 Mục tiêu
- **Phân tích mạng lưới**: Xác định các mối quan hệ giữa nghệ sĩ
- **Khám phá cộng đồng**: Tìm nhóm nghệ sĩ có liên kết chặt chẽ
- **Phân tích xu hướng**: Nghiên cứu thể loại nhạc và hãng thu âm
- **Trực quan hóa**: Tạo biểu đồ mạng có thể tương tác

## 📊 THỐNG KÊ TỔNG QUAN

### Mạng lưới hiện tại
- **🎤 Nghệ sĩ**: 167 (144 artists + 12 solo_artists + 11 bands)
- **🎼 Thể loại**: 68
- **🏢 Hãng thu**: 80
- **🔗 Tổng nodes**: 315
- **📈 Tổng edges**: 458

### Các loại cạnh (Edges)
| Loại cạnh | Số lượng | Ý nghĩa |
|-----------|----------|---------|
| `collaborates_with` | 232 | Hợp tác âm nhạc |
| `plays_genre` | 109 | Chơi thể loại nhạc |
| `signed_to` | 117 | Ký hợp đồng với hãng thu |

## 🚀 CÁC BƯỚC ĐÃ TRIỂN KHAI

### ✅ 1. Thu thập dữ liệu
- **Wikipedia Crawling**: Tải 21 trang nghệ sĩ từ Wikipedia
- **HTML Parsing**: Phân tích cấu trúc trang Wikipedia
- **Data Extraction**: Trích xuất thông tin nghệ sĩ, thể loại, hãng thu

### ✅ 2. Phân tích dữ liệu
- **Infobox Analysis**: Phân tích hộp thông tin Wikipedia
- **Link Discovery**: Phát hiện liên kết giữa các nghệ sĩ
- **Text Mining**: Khai thác thông tin từ nội dung bài viết

### ✅ 3. Xây dựng mạng
- **Node Creation**: Tạo nodes cho nghệ sĩ, thể loại, hãng thu
- **Edge Detection**: Phát hiện và phân loại các mối quan hệ
- **Network Assembly**: Ghép nối thành mạng NetworkX

### ✅ 4. Mở rộng mạng
- **BFS Expansion**: Mở rộng mạng theo chiều rộng
- **Algorithm Enhancement**: Thuật toán tìm kiếm nghệ sĩ liên quan
- **Quality Control**: Kiểm soát chất lượng dữ liệu

### ✅ 5. Triển khai các loại cạnh mới
- **member_of**: Thành viên ban nhạc
- **produced_by**: Quan hệ với producer
- **won_award**: Giành giải thưởng
- **charted_on**: Lọt bảng xếp hạng
- **nominated_for**: Đề cử giải thưởng

### ✅ 6. Hệ thống truy vấn
- **Adjacency List**: Danh sách cạnh kề
- **Edge Selection**: Lựa chọn cạnh theo tiêu chí
- **Edge Ranges**: Phân chia cạnh theo khoảng
- **Network Analysis**: Phân tích mạng chuyên sâu

## 🎨 NGHỆ SĨ NỔI BẬT

### Top 5 nghệ sĩ theo số kết nối
1. **Arctic Monkeys** (35 kết nối) - 24 hợp tác, 6 thể loại, 5 hãng thu
2. **Tame Impala** (33 kết nối) - 13 hợp tác, 13 thể loại, 7 hãng thu
3. **Arcade Fire** (29 kết nối) - 13 hợp tác, 4 thể loại, 12 hãng thu
4. **Vampire Weekend** (27 kết nối) - 12 hợp tác, 12 thể loại, 2 hãng thu
5. **Pearl Jam** (27 kết nối) - 19 hợp tác, 3 thể loại, 5 hãng thu

### Nghệ sĩ đặc trưng
- **The Beatles**: 23 kết nối, 11 hãng thu, Liverpool
- **Coldplay**: 19 kết nối, 5 hãng thu, London
- **Taylor Swift**: 17 kết nối, 2 hãng thu, Nashville

## 🎼 THỂ LOẠI PHỔ BIẾN

1. **Alternative rock** (4 nghệ sĩ)
2. **Pop rock** (4 nghệ sĩ)
3. **Post-Britpop** (4 nghệ sĩ)
4. **Pop** (4 nghệ sĩ)
5. **Indie rock** (4 nghệ sĩ)

## 🏢 HÃNG THU ÂM

Top hãng thu theo số nghệ sĩ:
1. **Parlophone** - Nhiều nghệ sĩ UK
2. **Capitol Records** - Hãng thu lớn
3. **Domino Records** - Indie labels
4. **Warner Bros.** - Major label

## 🔧 TÍNH NĂNG ĐÃ TRIỂN KHAI

### Core Features
- ✅ **Wikipedia Crawling**: Tự động tải và phân tích
- ✅ **Network Construction**: Xây dựng mạng từ dữ liệu
- ✅ **Relationship Discovery**: Phát hiện quan hệ phức tạp
- ✅ **Multi-format Export**: GEXF, JSON, GraphML

### Advanced Features
- ✅ **Adjacency Operations**: Danh sách kề, lựa chọn cạnh
- ✅ **Range Analysis**: Phân tích khoảng cạnh
- ✅ **Query System**: Hệ thống truy vấn mạnh mẽ
- ✅ **New Edge Types**: 5 loại cạnh mở rộng

### Analysis Capabilities
- ✅ **Centrality Analysis**: Phân tích độ trung tâm
- ✅ **Path Finding**: Tìm đường đi ngắn nhất
- ✅ **Community Detection**: Phát hiện cộng đồng
- ✅ **Genre Analysis**: Phân tích thể loại

## 💻 CÀI ĐẶT VÀ SỬ DỤNG

### Yêu cầu hệ thống
```bash
Python 3.8+
Dependencies: networkx, beautifulsoup4, requests, matplotlib, pandas
```

### Cài đặt
```bash
git clone <repository>
cd music_graph
pip install -r requirements.txt
```

### Sử dụng cơ bản
```bash
# 1. Thu thập dữ liệu mẫu
python src/batch_download.py

# 2. Phân tích Wikipedia
python src/wikipedia_analyzer.py

# 3. Xây dựng mạng
python src/network_builder.py

# 4. Truy vấn mạng
python src/network_queries.py
```

### Sử dụng nâng cao
```python
from src.network_queries import MusicNetworkQuerySystem

# Khởi tạo hệ thống
query_system = MusicNetworkQuerySystem(
    network_file='data/processed/music_network.gexf',
    json_file='data/processed/music_network_network.json'
)

# Truy vấn thông tin nghệ sĩ
info = query_system.get_artist_info("The Beatles")

# Tìm đường đi
path = query_system.find_shortest_path("The Beatles", "Taylor Swift")

# Danh sách cạnh kề
adj_list = query_system.get_adjacency_list("Coldplay", include_edge_data=True)

# Lựa chọn cạnh
collab_edges = query_system.select_edges({'edge_type': 'collaborates_with'})
```

## 📊 KẾT QUẢ CUỐI CÙNG

### File chính
- **`data/processed/final_music_network_results.json`** (341KB)
  - Chứa toàn bộ dữ liệu mạng đã xử lý
  - Thống kê chi tiết và phân tích
  - Sẵn sàng cho nghiên cứu và visualization

### Cấu trúc dữ liệu
```json
{
  "metadata": {...},
  "statistics": {
    "total_nodes": 315,
    "total_edges": 458,
    "total_artists": 167,
    "node_types": {...},
    "edge_types": {...}
  },
  "artists": [...],
  "genres": [...],
  "labels": [...],
  "relationships": {
    "collaborations": [...],
    "genre_associations": [...],
    "label_relationships": [...]
  }
}
```

### Validation
```bash
python validate_final_results.py  # ✅ PASSED
```

## 🎯 ỨNG DỤNG

### Nghiên cứu âm nhạc
- **Six Degrees of Separation**: Nghệ sĩ A có liên quan gì với nghệ sĩ B?
- **Influence Networks**: Mạng lưới ảnh hưởng âm nhạc
- **Genre Evolution**: Sự phát triển của các thể loại nhạc

### Phân tích mạng
- **Community Detection**: Nhóm nghệ sĩ theo phong cách
- **Centrality Measures**: Xác định nghệ sĩ quan trọng
- **Network Flow**: Luồng thông tin trong cộng đồng nhạc

### Visualization
- **Interactive Graphs**: Sử dụng D3.js, Gephi
- **Web Applications**: Dashboard phân tích mạng
- **Academic Papers**: Minh họa cho nghiên cứu

## 🔬 PHÂN TÍCH SÂU

### Metrics mạng
- **Density**: 0.0093 (Mạng thưa, phù hợp với mạng thực tế)
- **Components**: 2 thành phần liên thông
- **Average Path Length**: ~4.2 bước giữa các nghệ sĩ

### Community Insights
- **UK vs US Artists**: Sự khác biệt văn hóa
- **Genre Clusters**: Nhóm theo thể loại âm nhạc
- **Label Networks**: Mạng lưới hãng thu âm

## 🚀 MỞ RỘNG TƯƠNG LAI

### Dữ liệu bổ sung
- **Album Data**: Thông tin album và track listings
- **Song Credits**: Tác giả, producers, featured artists
- **Award History**: Giải Grammy, Billboard, etc.
- **Chart Performance**: Billboard Hot 100, UK Charts

### Thuật toán nâng cao
- **Machine Learning**: Dự đoán hợp tác mới
- **Temporal Analysis**: Phân tích theo thời gian
- **Recommendation System**: Gợi ý nghệ sĩ tương tự

### Tích hợp
- **MusicBrainz API**: Dữ liệu metadata chuẩn
- **Spotify API**: Streaming statistics
- **Last.fm API**: Listening patterns

## 📚 TÀI LIỆU

### Files quan trọng
- `README.md`: Tài liệu tiếng Anh
- `docs/network_concepts.md`: Thiết kế mạng chi tiết
- `docs/crawler_usage_guide.md`: Hướng dẫn crawler
- `FINAL_RESULTS_README.md`: Tài liệu kết quả cuối

### Scripts demo
- `demo_adjacency_edges.py`: Demo các loại cạnh
- `test_new_edge_queries.py`: Test truy vấn
- `validate_final_results.py`: Validate dữ liệu

## 👥 ĐÓNG GÓP

### Cách đóng góp
1. Fork repository
2. Tạo feature branch
3. Implement improvements
4. Test thoroughly
5. Submit pull request

### Lĩnh vực cần hỗ trợ
- **Data Quality**: Cải thiện accuracy của dữ liệu
- **Algorithm Optimization**: Tối ưu hóa performance
- **New Features**: Thêm tính năng phân tích mới
- **Documentation**: Viết tài liệu và tutorials

## 📄 GIẤY PHÉP

Dự án sử dụng dữ liệu Wikipedia cho mục đích nghiên cứu và giáo dục. Tuân thủ các điều khoản sử dụng của Wikipedia và tôn trọng bản quyền.

## 🙏 LỜI CẢM ƠN

- **Wikipedia Contributors**: Cung cấp dữ liệu phong phú
- **NetworkX Team**: Thư viện mạng mạnh mẽ
- **Open Source Community**: Hỗ trợ kỹ thuật

---

## 🎵 TÓM TẮT

Dự án **Music Network Graph** đã thành công xây dựng một hệ thống phân tích mạng lưới nghệ sĩ âm nhạc US-UK toàn diện với:

- **167 nghệ sĩ** được phân tích chi tiết
- **458 mối quan hệ** được phát hiện và phân loại
- **8 loại cạnh** (3 core + 5 extended)
- **Hệ thống truy vấn** mạnh mẽ với adjacency, selection, ranges
- **Kết quả cuối cùng** được export thành JSON chuẩn

**Sẵn sàng cho nghiên cứu, visualization và ứng dụng thực tế!** ✨🎶📊

---

*Generated on: 2025-10-17*
*Version: 2.0 - Vietnamese Documentation*
