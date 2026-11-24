# Phan tich moi lien he giua gia tri doi hinh va thu hang o nam giai bong da hang dau chau Au, mua 2016/17-2020/21

## Cau hoi phan tich

Ở 5 giải bóng đá lớn nhất châu Âu (2016/17–2020/21), đội có đội hình đắt hơn có xếp hạng cao hơn không,
và đội nào đá tốt nhất so với giá trị đội hình?

## Nguon du lieu

| Nguồn | Tệp dùng | Nội dung | Giấy phép |
|---|---|---|---|
| Transfermarkt trên Kaggle (`davidcariboo/player-scores`, phiên bản 679) | `appearances.csv`, `player_valuations.csv` | Cầu thủ ra sân từng trận (số phút), giá trị cầu thủ theo ngày | CC0 |
| openfootball (GitHub: england, espana, deutschland, italy, europe) | 25 tệp `.txt` (5 giải × 5 mùa) | Kết quả từng trận: ngày, đội nhà, đội khách, tỷ số | CC0 1.0 |

Hai nguồn ghép với nhau theo khoá `(ngay, club_id)`.

## Cach chay

Yêu cầu: Python 3.12.10

1. Tạo môi trường ảo và cài thư viện (chạy tại thư mục gốc của kho):
   Windows:
   ```
   py -3.12 -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
   macOS/Linux:
   ```
   python3.12 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Lấy dữ liệu thô (làm một lần, cần mạng):

    **a. Nguồn 1: Transfermarkt (2 tệp).** 

    Tải tay từ
   [Kaggle](https://www.kaggle.com/datasets/davidcariboo/player-scores) (Version 679): giải nén file tải về `archive.zip`, sau đó đặt 2 file `appearances.csv` và `player_valuations.csv` vào thư mục `data/raw/transfermarkt/`.

   **b. Nguồn 2: openfootball (25 tệp).** 
   
   Trong terminal tại thư mục gốc, dán lệnh dưới đây:

   ```
   curl.exe -fsSL --create-dirs "https://raw.githubusercontent.com/openfootball/england/9ee7a0c351805c99cc334478a9bf04b7d0432fec/{2016-17,2017-18,2018-19,2019-20,2020-21}/1-premierleague.txt" -o "data/raw/openfootball/premier_league_#1.txt"
   curl.exe -fsSL --create-dirs "https://raw.githubusercontent.com/openfootball/espana/80035a93dd4920985af52aa097a54a6fb888563b/{2016-17,2017-18,2018-19,2019-20,2020-21}/1-liga.txt" -o "data/raw/openfootball/la_liga_#1.txt"
   curl.exe -fsSL --create-dirs "https://raw.githubusercontent.com/openfootball/deutschland/c34532ab6950aa0089ef1c736ffdb8c818c3356f/{2016-17,2017-18,2018-19,2019-20,2020-21}/1-bundesliga.txt" -o "data/raw/openfootball/bundesliga_#1.txt"
   curl.exe -fsSL --create-dirs "https://raw.githubusercontent.com/openfootball/italy/48954d163c312aa705efacb64f771267031fe6eb/{2016-17,2017-18,2018-19,2019-20,2020-21}/1-seriea.txt" -o "data/raw/openfootball/serie_a_#1.txt"
   curl.exe -fsSL --create-dirs "https://raw.githubusercontent.com/openfootball/europe/63df627f3c87ce71708f016522ea236cf74332c3/france/{2016-17,2017-18,2018-19,2019-20,2020-21}_fr1.txt" -o "data/raw/openfootball/ligue_1_#1.txt"
   ```

   Để tải trên macOS/Linux, thay `curl.exe` bằng `curl`.

   Kết quả: 25 tệp trong `data/raw/openfootball/`.

   Khi chạy, chương trình tự kiểm tra 27 tệp này và báo nếu thiếu tệp hoặc sai phiên bản.

3. Chạy toàn bộ chương trình (không cần mạng):
   ```
   python chay.py --giai-doan tat-ca
   ```

4. Chạy kiểm thử:
   ```
   pytest -q
   ```

## Cau truc thu muc

```
nhom09_gia_tri_doi_hinh/
|-- README.md                    # mô tả dự án
|-- PHAN_CONG.md                 # bảng phân công và số commit
|-- requirements.txt             # thư viện, ghim phiên bản
|-- cau_hinh.yaml                # đường dẫn, tham số, quy tắc chuẩn hoá tên đội
|-- chay.py                      # điểm vào duy nhất của chương trình
|-- .gitignore
|-- data/                        # không đưa lên GitHub
|   |-- raw/                     # dữ liệu gốc, chỉ đọc
|   |   |-- openfootball/        # 25 tệp <giai>_<mua>.txt, ví dụ premier_league_2016-17.txt
|   |   `-- transfermarkt/       # appearances.csv, player_valuations.csv
|   |-- external/                # để trống: quy tắc chuẩn hoá nằm trong cau_hinh.yaml
|   |-- interim/                 # tran_dau_tho.csv, ra_san_tho.csv, dinh_gia_tho.csv
|   `-- processed/               # tran_dau.csv, cau_thu_tran.csv
|-- src/
|   `-- gia_tri_doi_hinh/
|       |-- __init__.py          # xuất 6 hàm công khai
|       |-- cau_hinh.py          # đọc và kiểm tra cau_hinh.yaml
|       |-- lop_co_so.py         # lớp trừu tượng, lớp ngoại lệ, kiểm tra SHA-256
|       |-- nap.py               # đọc tệp .txt và .csv
|       |-- lam_sach.py          # làm sạch và ghép hai nguồn
|       |-- phan_tich.py         # tổng hợp, trả lời câu hỏi
|       `-- bieu_do.py           # vẽ biểu đồ
|-- tests/
|   |-- du_lieu_mau/             # tệp mẫu nhỏ (dưới 100 KB) cho kiểm thử
|   |-- test_nap.py
|   |-- test_lam_sach.py
|   |-- test_phan_tich.py
|   `-- test_bieu_do.py
|-- notebooks/
|   `-- 1.0-khao-sat-ban-dau.ipynb   # khảo sát dữ liệu ban đầu
|-- ket_qua/                     # do chương trình sinh ra, không đưa lên GitHub
|   |-- hinh/                    # biểu đồ .png
|   |-- bang/                    # bảng kết quả .csv
|   |-- tom_tat.json             # các con số chính
|   `-- nhat_ky.log              # nhật ký lần chạy gần nhất
`-- tai_lieu/
    |-- BAO_CAO.pdf
    |-- SLIDE.pdf
    `-- tu_dien_du_lieu.md       # ý nghĩa, đơn vị, miền giá trị từng cột
```

## Danh sach lop

| Lớp | Tệp | Trách nhiệm |
|---|---|---|
| `NguonDuLieu` | `lop_co_so.py` | Lớp trừu tượng quy định mọi nguồn dữ liệu phải có phương thức `doc()`. |
| `KiemTraMaBam` | `lop_co_so.py` | Kiểm tra mã SHA-256 của các tệp dữ liệu thô. |
| `LoiDuAn` (và các lớp con) | `lop_co_so.py` | Lớp ngoại lệ chung của chương trình. |
| `CauHinh` | `cau_hinh.py` | Đọc và kiểm tra giá trị trong `cau_hinh.yaml`. |
| `NguonVanBanTranDau` | `nap.py` | Đọc tệp `.txt` của openfootball thành bảng trận đấu thô. |
| `NguonCsv` | `nap.py` | Đọc tệp CSV của Transfermarkt theo khối, chỉ giữ các cột cần dùng. |
| `ChuanHoaTenDoi` | `lam_sach.py` | Tra `club_id` từ tên đội theo quy tắc trong cấu hình. |
| `LamSachTranDau` | `lam_sach.py` | Đưa tỷ số và ngày về đúng kiểu, chuẩn hoá tên đội. |
| `LamSachRaSan` | `lam_sach.py` | Đưa bảng ra sân và bảng định giá về đúng kiểu. |
| `HopNhatNguon` | `lam_sach.py` | Ghép trận đấu với đội hình ra sân và giá trị trước mùa. |
| `TongHop` | `phan_tich.py` | Tính giá trị trên sân, điểm và bảng xếp hạng. |
| `PhanTichGiaTri` | `phan_tich.py` | Trả lời ba mức của câu hỏi phân tích. |
| `VeBieuDo` | `bieu_do.py` | Vẽ và lưu các biểu đồ vào `ket_qua/hinh/`. |

## Quyet dinh lam sach du lieu

| Khuyết tật | Cách xử lý | Lý do |
|---|---|---|
| Tỷ số lưu dạng chuỗi nhiều khuôn (`2-1 (1-0)`, `[cancelled]`, `[awarded]`) | Tách bằng biểu thức chính quy thành hai số | Cần số để tính điểm |
| Ngày thiếu năm (`Sat Aug 13`) | Chọn năm (đầu mùa hoặc cuối mùa) khớp với thứ trong tuần | Suy năm theo tháng dễ sai với mùa kéo dài vì COVID |
| Tên đội viết nhiều kiểu (171 cách viết cho 139 đội) | Ánh xạ sang `club_id` theo `cau_hinh.yaml` | Tạo khoá chung để ghép với Transfermarkt |
| 101 trận Ligue 1 mùa 2019/20 bị huỷ, không có tỷ số | Loại khỏi bảng trận; xếp hạng theo điểm mỗi trận | Giải dừng sớm vì COVID, các đội đá số trận khác nhau |
| Trận Bastia – Lyon 2016/17 ghi 0-0, kết quả chính thức 0-3 | Sửa theo mục `sua_ket_qua` trong cấu hình | Dùng kết quả chính thức (quyết định kỷ luật của LFP) |
| 3 trận xử thắng | Giữ khi tính bảng xếp hạng, loại ở phân tích mức trận | Tỷ số không phản ánh trận đấu thực tế |
| Ngày lệch 1 ngày giữa hai nguồn (8 lượt đội × trận) | Cho phép lệch tối đa 1 ngày khi ghép | Khác biệt do giờ đá muộn |
| Granada ngày 13/12/2020 không có đội hình | Loại ở phân tích mức trận | Không có dữ liệu để tính giá trị |
| 31 lượt đội × trận thiếu cầu thủ, tổng phút khác 990 | Tính giá trị theo tỷ trọng số phút | Giá trị không bị thổi phồng hay hụt vì tổng phút sai |
| Cầu thủ không có định giá trước mùa (0,78% số phút) | Tính bằng 0 | Đã kiểm tra độ nhạy: lấy lần định giá đầu mùa cho cùng kết quả |

Số lượng trước và sau xử lý: xem `thong_ke_lam_sach` trong `ket_qua/tom_tat.json`.

## Ket qua chinh

(Điền sau khi chạy xong. Mọi con số phải trùng với khoá `ket_qua` trong `ket_qua/tom_tat.json`.)

## Moi truong

- Python 3.12.10
- Hệ điều hành: Windows 11
- Thư viện: xem `requirements.txt`