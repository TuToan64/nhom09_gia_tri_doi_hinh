"""Tệp kiểm thử tự động cho mô-đun nap.py sử dụng pytest.

Kiểm tra cả trường hợp thành công (Happy Paths) và tất cả các lỗi ngoại lệ (Exceptions).
"""

from pathlib import Path
import pandas as pd
import pytest

# Import hàm công khai, các lớp nguồn và bộ ngoại lệ tự định nghĩa
# (Thay 'ten_goi' bằng tên thư mục gói thực tế của bạn trong src/)
from src.gia_tri_doi_hinh.lop_co_so import (
    BangRongError,
    CauHinhSaiError,
    DinhDangTepError,
    ThieuCotError,
    ThieuTepError,
)
from src.gia_tri_doi_hinh.nap import NguonCsv, NguonVanBanTranDau, nap_du_lieu

# Đường dẫn thư mục dữ liệu mẫu kiểm thử
THU_MUC_MAU = Path("tests/du_lieu_cho_test_nap")


# ==============================================================================
# 1. KIỂM THỬ NGUỒN VĂN BẢN TRẬN ĐẤU (NguonVanBanTranDau & .txt)
# ==============================================================================


def test_nap_du_lieu_txt_tran_dau_thanh_cong():
  """Kiểm tra đọc tệp .txt trận đấu thành công và tự động trích xuất các cột."""
  path_txt = THU_MUC_MAU / "premier_league_2016-17.txt"

  df = nap_du_lieu(path_txt)

  # Kiểm tra kiểu dữ liệu và độ dài
  assert isinstance(df, pd.DataFrame), "Kết quả phải là một DataFrame"
  assert len(df) == 2, f"Kỳ vọng 2 dòng trận đấu, thực tế nhận {len(df)}"

  # Kiểm tra cấu hình cột
  cot_mong_doi = [
      "giai",
      "mua",
      "ngay_tho",
      "doi_nha",
      "doi_khach",
      "ty_so_tho",
  ]
  assert list(df.columns) == cot_mong_doi

  # Kiểm tra trích xuất tên giải và mùa giải từ tên tệp
  assert (df["giai"] == "premier_league").all()
  assert (df["mua"] == "2016-17").all()

  # Kiểm tra dữ liệu trận đấu
  assert df.iloc[0]["doi_nha"] == "Hull City"
  assert df.iloc[0]["doi_khach"] == "Leicester City"
  assert df.iloc[0]["ty_so_tho"] == "2-1"


def test_nap_du_lieu_txt_ten_tep_sai_khuon_mau():
  """Kiểm tra tên tệp .txt không đúng dạng <giai>_<mua>.txt bắn ra DinhDangTepError."""
  path_sai_ten = THU_MUC_MAU / "ten_sai_khuon.txt"

  with pytest.raises(DinhDangTepError) as exc_info:
    nap_du_lieu(path_sai_ten)

  assert "sai khuon" in str(exc_info.value)


def test_nap_du_lieu_bang_rong():
  """Kiểm tra tệp .txt rỗng hoặc không có dòng trận đấu nào bắn ra BangRongError."""
  path_rong = THU_MUC_MAU / "tran_dau_rong_2016-17.txt"

  with pytest.raises(BangRongError):
    nap_du_lieu(path_rong)


# ==============================================================================
# 2. KIỂM THỬ XỬ LÝ NGOẠI LỆ CHUNG (COMMON EXCEPTIONS)
# ==============================================================================


def test_nap_du_lieu_bao_loi_thieu_tep():
  """Kiểm tra truyền đường dẫn không tồn tại bắn ra lỗi ThieuTepError."""
  path_khong_co = THU_MUC_MAU / "file_khong_ton_tai.txt"

  with pytest.raises(ThieuTepError):
    nap_du_lieu(path_khong_co)


def test_nap_du_lieu_bao_loi_dinh_dang_tep():
  """Kiểm tra truyền tệp có đuôi mở rộng lạ (ví dụ .pdf/.xlsx) bắn ra DinhDangTepError."""
  path_la = THU_MUC_MAU / "loi_dinh_dang.pdf"

  # Tạo giả lập tệp pdf rỗng để kiêm tra đuôi tệp
  if not path_la.exists():
    path_la.touch()

  try:
    with pytest.raises(DinhDangTepError):
      nap_du_lieu(path_la)
  finally:
    if path_la.exists():
      path_la.unlink()  # Dọn dẹp tệp giả lập sau khi test xong


# ==============================================================================
# 3. KIỂM THỬ KHỞI TẠO ĐỐI TƯỢNG HƯỚNG ĐỐI TƯỢNG (OOP CLASS TESTS)
# ==============================================================================


def test_khoi_tao_truc_tiep_nguon_van_ban():
    """Kiểm tra khởi tạo và gọi phương thức .doc() trực tiếp trên đối tượng NguonVanBanTranDau."""
    path_txt = THU_MUC_MAU / "premier_league_2016-17.txt"
    nguon = NguonVanBanTranDau(path_txt)

    df = nguon.doc()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty

def test_nap_du_lieu_thieu_cot():
    """Kiểm tra nạp tệp CSV thiếu cột bắt buộc sẽ bắn ra lỗi ThieuCotError."""
    path_thieu_cot = THU_MUC_MAU / "dinh_gia_thieu_cot.csv"

    # Sử dụng pytest.raises để kiểm tra đúng lỗi ThieuCotError được phát ra
    with pytest.raises(ThieuCotError):
      nap_du_lieu(path_thieu_cot)


# ==============================================================================
# TEST CÁC TỆP MAU_RA_SAN.CSV VÀ MAU_TRAN_DAU_2016-17.TXT TRONG MỤC tests/du_lieu_mau/
# ==============================================================================

def test_nap_du_lieu_txt_mau_co_awarded_va_cancelled():
  """Kiểm tra tệp mẫu mau_tran_dau_2016-17.txt nạp thành công, đọc đúng [awarded], [cancelled] và bỏ qua dòng sai khuôn."""
  path_txt = THU_MUC_MAU / "mau_tran_dau_2016-17.txt"

  df = nap_du_lieu(path_txt)

  assert isinstance(df, pd.DataFrame)
  # Kiểm tra các trận đấu đặc biệt
  assert (df["ty_so_tho"] == "0-0 [awarded]").any()
  assert (df["ty_so_tho"] == "[cancelled]").any()


def test_nap_du_lieu_csv_mau_ra_san_loc_chuan():
  """Kiểm tra tệp mẫu mau_ra_san.csv được lọc chính xác theo giải và khoảng ngày ranh giới."""
  path_csv = THU_MUC_MAU / "mau_ra_san.csv"

  df = nap_du_lieu(path_csv)

  assert isinstance(df, pd.DataFrame)
  # Không còn giải CL trong bảng kết quả
  assert "CL" not in df["competition_id"].values
  # Ngày ranh giới 2016-07-01 và 2021-06-30 được giữ lại
  assert "2016-07-01" in df["date"].values
  assert "2021-06-30" in df["date"].values