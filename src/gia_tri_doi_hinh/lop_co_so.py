"""Lop truu tuong va cac lop dung chung cho ca du an."""

from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd


class LoiDuAn(Exception):
    """Lop cha cua moi loi do chuong trinh chu dong phat ra.
    chay.py chi can bat LoiDuAn la bat duoc moi loi cua du an,
    roi in thong bao gon thay vi de truy vet tran ra man hinh.
    """


class ThieuTepError(LoiDuAn):
    """Tep can doc khong ton tai."""


class DinhDangTepError(LoiDuAn):
    """Tep co duoi tep hoac ten tep khong dung khuon chuong trinh doc duoc."""


class BangRongError(LoiDuAn):
    """Bang khong co dong du lieu nao."""


class ThieuCotError(LoiDuAn):
    """Bang thieu mot hoac nhieu cot bat buoc."""


class CauHinhSaiError(LoiDuAn):
    """cau_hinh.yaml sai dinh dang hoac thieu khoa bat buoc."""


class NguonDuLieu(ABC):
    """Mot nguon du lieu tho doc tu mot tep.
    Moi loai tep (van ban, CSV...) la mot lop con va tu cai dat phuong thuc doc().
    Nho vay noi goi chi can goi nguon.doc() ma khong can biet tep thuoc loai nao.
    """

    def __init__(self, duong_dan: str | Path) -> None:
        """Ghi nho duong dan toi tep, chua doc tep.
        Tham so:
            duong_dan: duong dan toi tep du lieu tho.
        """
        self.duong_dan = Path(duong_dan)

    @property
    def ten_tep(self) -> str:
        """Ten tep khong kem thu muc, dung trong thong bao loi va nhat ky.
        Tra ve:
            Ten tep, vi du "appearances.csv".
        """
        return self.duong_dan.name

    def kiem_tra_ton_tai(self) -> None:
        """Kiem tra tep co ton tai truoc khi doc.
        Ngoai le:
            ThieuTepError: khi khong co tep o duong dan da cho.
        """
        if not self.duong_dan.is_file():
            raise ThieuTepError(f"Khong tim thay tep {self.duong_dan}")

    @abstractmethod
    def doc(self) -> pd.DataFrame:
        """Doc tep thanh bang tho, chua lam sach.
        Tra ve:
            Bang du lieu tho.
        Ngoai le:
            ThieuTepError, DinhDangTepError, BangRongError, ThieuCotError: tuy lop con.
        """

    def __repr__(self) -> str:
        """Chuoi mo ta nguon, dung khi ghi nhat ky, vi du NguonCsv('data/raw/a.csv')."""
        return f"{type(self).__name__}('{self.duong_dan}')"
