"""Doc cau_hinh.yaml va kiem tra du cac khoa bat buoc"""

from pathlib import Path
from typing import Any

import yaml

from .lop_co_so import CauHinhSaiError, ThieuTepError

class CauHinh:
    """Cau hinh cua du an, doc tu cau_hinh.yaml.
    Doc bang cu phap cau_hinh[khoa]"""

    KHOA_BAT_BUOC = [
        "nhom", "thanh_vien", "cau_hoi", "seed", "duong_dan", "mua",
        "giai", "transfermarkt", "lam_sach", "phan_tich", 
        "chuan_hoa_ten_doi", "ten_doi"
    ]

    # chay.py doi gia tri nay khi nhan tham so --cau-hinh khac mac dinh
    duong_dan_mac_dinh = Path("cau_hinh.yaml")

    def __init__(self, du_lieu: dict[str,  Any]) -> None:
        """Nhan noi dung cau hinh da doc va kiem tra ngay.
        Tham so:
            du_lieu: tu dien doc tu cau_hinh.yaml
        Ngoai le:
            CauHinhSaiError: khi thieu khoa bat buoc.
        """
        self._du_lieu = du_lieu
        self.kiem_tra()

    @classmethod
    def tu_tep(cls, duong_dan: str | Path | None = None) -> "CauHinh":
        """Doc cau hinh tu cau_hinh.yaml.
        Tham so:
            duong_dan: duong dan toi cau_hinh.yaml; bo trong thi dung
    duong_dan_mac_dinh.
        Tra ve:
            Doi tuong CauHinh da kiem tra.
        Ngoai le:
            ThieuTepError: khi khong co tep
            CauHinhSaiError: khi tep sai cu phap YAML, rong hoac thieu 
    khoa bat buoc
        """
        duong_dan = Path(duong_dan or cls.duong_dan_mac_dinh)
        if not duong_dan.is_file():
            raise ThieuTepError(f"Khong tim thay tep cau hinh {duong_dan}")
        with open(duong_dan, encoding="utf-8") as tep:
            try:
                du_lieu = yaml.safe_load(tep)
            except yaml.YAMLError as loi:
                raise CauHinhSaiError(f"{duong_dan} sai cu phap YAML: {loi}") from loi
        if not isinstance(du_lieu, dict):
            raise CauHinhSaiError(f"{duong_dan} rong hoac khong phai dang khoa: gia tri")
        return cls(du_lieu)

    def kiem_tra(self) -> None:
        """Kiem tra cau hinh co du cac khoa trong KHOA_BAT_BUOC.
        Ngoai le:
            CauHinhSaiError: khi thieu mot hoac nhieu khoa, thong bao ghi ro
            khoa nao.
        """
        thieu = [khoa for khoa in self.KHOA_BAT_BUOC if khoa not in self._du_lieu]
        if thieu:
            raise CauHinhSaiError(f"cau_hinh.yaml thieu khoa: {','.join(thieu)}")

    def __getitem__(self, khoa: str) -> Any:
        """Lay gia tri cua mot khoa cap ngoai cung, vd: cau_hinh["mua"].
        Tham so:
            khoa: ten khoa trong cau_hinh.yaml
        Tra ve:
            Gia tri cua khoa do.
        Ngoai le:
            CauHinhSaiError: khi khong co khoa nay
        """
        try:
            return self._du_lieu[khoa]
        except KeyError as loi:
            raise CauHinhSaiError(f"cau_hinh.yaml khong co khoa '{khoa}'") from loi
        