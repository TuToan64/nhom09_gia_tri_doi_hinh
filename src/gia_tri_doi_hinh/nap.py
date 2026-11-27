"""Nap du lieu tho tu hai nguon ve DataFrame, dung nhu nguon ghi, chua lam sach.

- Tep .txt cua openfootball  -> NguonVanBanTranDau -> bang tran dau tho
- Tep .csv cua Transfermarkt -> NguonCsv           -> bang ra san tho hoac bang dinh gia tho

nap_du_lieu chon lop theo duoi tep va chi tra ve DataFrame, khong ghi tep.
Viec ghi 3 bang ra data/interim/ do chay.py dam nhiem.
"""

import logging
import re
from pathlib import Path
from typing import Any

import pandas as pd

from .cau_hinh import CauHinh
from .lop_co_so import (
    BangRongError,
    CauHinhSaiError,
    DinhDangTepError,
    NguonDuLieu,
    ThieuCotError,
    ThieuTepError,
)

# Canh bao dong .txt sai khuon di vao day; chay.py gan handler ghi ra nhat_ky.log
nhat_ky = logging.getLogger(__name__)


class NguonVanBanTranDau(NguonDuLieu):
    """Doc mot tep .txt ket qua tran dau cua openfootball thanh bang tran dau tho.

    Hai kieu dong tran dau trong nguon:
        Kieu 1 (Premier League, mot phan La Liga va Bundesliga 2020/21):
            12:30  Hull City                2-1 (1-0)  Leicester City
        Kieu 2 (cac tep con lai):
            20:00  SC Bastia               v Paris Saint-Germain      0-1 (0-0)
    Dong ngay (vd "Sat Aug 13" hoac "Fri Aug 12 2016") ap dung cho cac dong tran
    ngay sau no cho den dong ngay ke tiep.
    """

    COT = ["giai", "mua", "ngay_tho", "doi_nha", "doi_khach", "ty_so_tho"]

    # <giai>_<mua>.txt, vd premier_league_2016-17.txt -> premier_league, 2016-17
    MAU_TEN_TEP = re.compile(r"^(?P<giai>.+)_(?P<mua>\d{4}-\d{2})\.txt$", re.IGNORECASE)

    # Dong khong mang du lieu tran dau: tieu de "=", chu thich "#", ten vong "▪"
    TIEN_TO_BO_QUA = ("=", "#", "▪")

    # Ty so tho: "2-1", "2-1 (1-0)", "0-0 [awarded]", "[cancelled]"
    _TY_SO = (
        r"(?:\d+-\d+(?:\s*\(\d+-\d+\))?(?:\s+\[[a-z]+\])?"
        r"|\[[a-z]+\])"
    )
    _GIO = r"(?:\d{1,2}:\d{2}\s+)?"

    DONG_NGAY = re.compile(
        r"^\s*((?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+[A-Z][a-z]{2}\s+\d{1,2}(?:\s+\d{4})?)\s*$"
    )
    DONG_TRAN_CO_V = re.compile(
        r"^\s*" + _GIO + r"(?P<nha>.+?)\s+v\s+(?P<khach>.+?)\s{2,}(?P<ty_so>" + _TY_SO + r")\s*$"
    )
    DONG_TRAN_TY_SO_GIUA = re.compile(
        r"^\s*" + _GIO + r"(?P<nha>.+?)\s{2,}(?P<ty_so>" + _TY_SO + r")\s+(?P<khach>.+?)\s*$"
    )

    def doc(self) -> pd.DataFrame:
        """Doc tep .txt thanh bang tran dau tho.

        Dong sai khuon khong lam dung chuong trinh: chi ghi canh bao vao nhat ky
        va bo qua dong do. Ngay va ty so giu nhu nguon ghi (chi gop khoang trang
        lien tiep thanh mot dau cach), viec doi kieu de buoc lam sach lo.

        Tra ve:
            Bang gom cac cot giai, mua, ngay_tho, doi_nha, doi_khach, ty_so_tho,
            giai va mua lay tu ten tep.
        Ngoai le:
            ThieuTepError: khi khong co tep.
            DinhDangTepError: khi ten tep khong dung khuon <giai>_<mua>.txt
                hoac tep khong doc duoc bang UTF-8.
            BangRongError: khi tep khong co dong tran dau hop le nao.
        """
        self.kiem_tra_ton_tai()
        khop_ten = self.MAU_TEN_TEP.match(self.ten_tep)
        if khop_ten is None:
            raise DinhDangTepError(f"Ten tep {self.ten_tep} sai khuon <giai>_<mua>.txt")
        giai, mua = khop_ten.group("giai"), khop_ten.group("mua")
        nhat_ky.info("Bat dau doc %s", self.ten_tep)

        cac_dong_tran: list[tuple[str, ...]] = []
        ngay_hien_tai: str | None = None
        so_dong_vao = 0
        so_dong_loai = 0
        try:
            with open(self.duong_dan, encoding="utf-8-sig") as tep:
                for so_dong, dong in enumerate(tep, start=1):
                    so_dong_vao += 1
                    dong = dong.rstrip("\r\n")
                    if not dong.strip() or dong.lstrip().startswith(self.TIEN_TO_BO_QUA):
                        continue

                    khop_ngay = self.DONG_NGAY.match(dong)
                    if khop_ngay:
                        ngay_hien_tai = " ".join(khop_ngay.group(1).split())
                        continue

                    khop_tran = (
                        self.DONG_TRAN_CO_V.match(dong)
                        or self.DONG_TRAN_TY_SO_GIUA.match(dong)
                    )
                    if khop_tran is None:
                        so_dong_loai += 1
                        nhat_ky.warning(
                            "%s dong %d sai khuon, bo qua: %r",
                            self.ten_tep, so_dong, dong.strip(),
                        )
                        continue
                    if ngay_hien_tai is None:
                        so_dong_loai += 1
                        nhat_ky.warning(
                            "%s dong %d la dong tran dau nhung chua co dong ngay "
                            "truoc do, bo qua: %r",
                            self.ten_tep, so_dong, dong.strip(),
                        )
                        continue

                    cac_dong_tran.append((
                        giai,
                        mua,
                        ngay_hien_tai,
                        khop_tran.group("nha").strip(),
                        khop_tran.group("khach").strip(),
                        " ".join(khop_tran.group("ty_so").split()),
                    ))
        except UnicodeDecodeError as loi:
            raise DinhDangTepError(f"Tep {self.ten_tep} khong doc duoc bang UTF-8") from loi

        if not cac_dong_tran:
            raise BangRongError(f"Tep {self.ten_tep} khong co dong tran dau nao")
        nhat_ky.info(
            "Doc %s: vao %d dong, ra %d dong tran dau, loai %d dong (ly do: sai khuon)",
            self.ten_tep, so_dong_vao, len(cac_dong_tran), so_dong_loai,
        )
        return pd.DataFrame(cac_dong_tran, columns=self.COT)


class NguonCsv(NguonDuLieu):
    """Doc mot tep CSV cua Transfermarkt, chi giu cac cot can dung.

    Ten tep, cot can giu, co loc pham vi va khoang ngay moi mua deu lay tu muc
    transfermarkt trong cau_hinh.yaml. Loai bang nhan ra tu ten tep: ten trung
    khoa tep (vd appearances.csv) hoac co chua ten loai (vd mau_ra_san.csv).
    Moi o doc ve dang chuoi dung nhu nguon ghi; o trong giu la chuoi rong.
    """

    def __init__(self, duong_dan: str | Path, cau_hinh: CauHinh | None = None) -> None:
        """Ghi nho duong dan, chua doc tep.

        Tham so:
            duong_dan: duong dan toi tep CSV.
            cau_hinh: doi tuong CauHinh; bo trong thi doc cau_hinh.yaml mac dinh luc can.
        """
        super().__init__(duong_dan)
        self._cau_hinh = cau_hinh

    @property
    def loai(self) -> str:
        """Loai bang cua tep, ten mot muc con cua transfermarkt trong cau hinh.

        Ngoai le:
            DinhDangTepError: khi ten tep khong thuoc loai nao trong cau hinh.
        """
        muc_transfermarkt = self._lay_cau_hinh()["transfermarkt"]
        ten_day_du, ten_khong_duoi = self.ten_tep.lower(), self.duong_dan.stem.lower()
        for loai, muc in muc_transfermarkt.items():
            if not isinstance(muc, dict):
                continue  # so_dong_moi_khoi la mot so, khong phai mot loai bang
            if ten_day_du == str(muc.get("tep", "")).lower() or loai in ten_khong_duoi:
                return loai
        raise DinhDangTepError(
            f"Khong nhan ra loai CSV cua tep {self.ten_tep}: ten tep khong trung "
            "khoa 'tep' va khong chua ten loai nao trong muc transfermarkt cua cau_hinh.yaml"
        )

    def doc(self) -> pd.DataFrame:
        """Doc tep CSV theo khoi, giu cot can dung va (voi bang ra san) loc pham vi.

        Bang ra san chi giu dong thuoc cac giai trong muc giai (ma_transfermarkt) va
        cac mua trong muc mua; moi mua chay tu mua_bat_dau den mua_ket_thuc, gom ca
        hai ngay ranh gioi. Bang dinh gia giu moi dong.

        Tra ve:
            Bang co dung cac cot trong transfermarkt.<loai>.cot, theo thu tu do.
        Ngoai le:
            ThieuTepError: khi khong co tep.
            DinhDangTepError: khi duoi tep khong phai .csv, ten tep khong nhan ra
                duoc loai, hoac noi dung khong doc duoc thanh CSV.
            ThieuCotError: khi tep thieu mot hoac nhieu cot can dung.
            BangRongError: khi tep khong co dong du lieu nao, hoac khong con dong
                nao sau khi loc pham vi.
            CauHinhSaiError: khi cau_hinh.yaml thieu khoa can cho viec doc tep.
        """
        self.kiem_tra_ton_tai()
        if self.duong_dan.suffix.lower() != ".csv":
            raise DinhDangTepError(f"Tep {self.ten_tep} khong co duoi .csv")
        cau_hinh = self._lay_cau_hinh()
        loai = self.loai
        muc_transfermarkt = cau_hinh["transfermarkt"]
        muc = muc_transfermarkt[loai]
        cot = list(self._khoa_bat_buoc(muc, "cot", f"transfermarkt.{loai}"))
        so_dong_moi_khoi = self._khoa_bat_buoc(
            muc_transfermarkt, "so_dong_moi_khoi", "transfermarkt"
        )
        co_loc_pham_vi = bool(muc.get("loc_pham_vi", False))
        nhat_ky.info("Bat dau doc %s (loai %s)", self.ten_tep, loai)

        self._kiem_tra_cot(cot)

        cac_khoi: list[pd.DataFrame] = []
        so_dong_vao = 0
        try:
            doc_khoi = pd.read_csv(
                self.duong_dan,
                usecols=cot,
                dtype=str,
                keep_default_na=False,
                chunksize=so_dong_moi_khoi,
                encoding="utf-8-sig",
            )
            for khoi in doc_khoi:
                so_dong_vao += len(khoi)
                khoi = khoi[cot]
                if co_loc_pham_vi:
                    khoi = khoi[self._trong_pham_vi(khoi, cau_hinh, muc, loai)]
                cac_khoi.append(khoi)
        except (pd.errors.ParserError, UnicodeDecodeError) as loi:
            raise DinhDangTepError(f"Tep {self.ten_tep} khong doc duoc thanh CSV: {loi}") from loi

        if so_dong_vao == 0:
            raise BangRongError(f"Tep {self.ten_tep} khong co dong du lieu nao")
        bang = pd.concat(cac_khoi, ignore_index=True)
        if bang.empty:
            raise BangRongError(
                f"Tep {self.ten_tep} co {so_dong_vao} dong nhung khong con dong nao "
                "trong pham vi giai va mua da cau hinh"
            )
        nhat_ky.info(
            "Doc %s: vao %d dong, ra %d dong, loai %d dong (ly do: ngoai pham vi giai va mua)",
            self.ten_tep, so_dong_vao, len(bang), so_dong_vao - len(bang),
        )
        return bang

    def _lay_cau_hinh(self) -> CauHinh:
        """Tra ve cau hinh da nhan luc khoi tao, hoac doc cau_hinh.yaml mac dinh mot lan.

        Ngoai le:
            ThieuTepError: khi can doc cau_hinh.yaml nhung khong co tep.
            CauHinhSaiError: khi cau_hinh.yaml sai dinh dang hoac thieu khoa bat buoc.
        """
        if self._cau_hinh is None:
            self._cau_hinh = CauHinh.tu_tep()
        return self._cau_hinh

    @staticmethod
    def _khoa_bat_buoc(muc: dict[str, Any], khoa: str, ten_muc: str) -> Any:
        """Lay gia tri mot khoa trong muc cau hinh, bao loi ro rang neu thieu.

        Tham so:
            muc: tu dien cua mot muc trong cau_hinh.yaml.
            khoa: ten khoa can lay.
            ten_muc: ten muc de ghi vao thong bao loi, vd "transfermarkt.ra_san".
        Tra ve:
            Gia tri cua khoa.
        Ngoai le:
            CauHinhSaiError: khi muc khong co khoa nay.
        """
        if khoa not in muc:
            raise CauHinhSaiError(f"cau_hinh.yaml thieu khoa '{khoa}' trong muc {ten_muc}")
        return muc[khoa]

    @staticmethod
    def _doc_thang_ngay(gia_tri: str, ten_khoa: str) -> tuple[int, int]:
        """Doi chuoi "MM-DD" trong cau hinh thanh cap (thang, ngay).

        Tham so:
            gia_tri: chuoi dang "07-01".
            ten_khoa: ten khoa de ghi vao thong bao loi.
        Tra ve:
            Cap (thang, ngay).
        Ngoai le:
            CauHinhSaiError: khi chuoi khong phai mot ngay thang hop le.
        """
        try:
            thang, ngay = (int(phan) for phan in str(gia_tri).split("-"))
            pd.Timestamp(2000, thang, ngay)
        except ValueError as loi:
            raise CauHinhSaiError(
                f"cau_hinh.yaml: {ten_khoa}='{gia_tri}' khong phai dang MM-DD hop le"
            ) from loi
        return thang, ngay

    def _kiem_tra_cot(self, cot: list[str]) -> None:
        """Doc dong tieu de va kiem tra co du cac cot can dung.

        Tham so:
            cot: danh sach cot bat buoc.
        Ngoai le:
            BangRongError: khi tep trong, khong co ca dong tieu de.
            DinhDangTepError: khi dong tieu de khong doc duoc.
            ThieuCotError: khi thieu cot, thong bao ghi ro cot nao.
        """
        try:
            tieu_de = pd.read_csv(
                self.duong_dan, nrows=0, dtype=str, encoding="utf-8-sig"
            ).columns
        except pd.errors.EmptyDataError as loi:
            raise BangRongError(f"Tep {self.ten_tep} rong, khong co ca dong tieu de") from loi
        except (pd.errors.ParserError, UnicodeDecodeError) as loi:
            raise DinhDangTepError(f"Tep {self.ten_tep} khong doc duoc thanh CSV: {loi}") from loi
        thieu = [ten_cot for ten_cot in cot if ten_cot not in tieu_de]
        if thieu:
            raise ThieuCotError(f"Tep {self.ten_tep} thieu cot: {', '.join(thieu)}")

    def _trong_pham_vi(
        self, khoi: pd.DataFrame, cau_hinh: CauHinh, muc: dict[str, Any], loai: str
    ) -> pd.Series:
        """Danh dau dong thuoc cac giai va cac mua trong cau hinh.

        Tham so:
            khoi: mot khoi dong cua bang ra san (cot dang chuoi).
            cau_hinh: cau hinh co muc giai va muc mua.
            muc: muc transfermarkt.<loai> co mua_bat_dau va mua_ket_thuc.
            loai: ten loai bang, dung trong thong bao loi.
        Tra ve:
            Chuoi True/False cung chi so voi khoi.
        Ngoai le:
            CauHinhSaiError: khi cau hinh thieu khoa hoac ngay thang sai dang.
        """
        ten_muc = f"transfermarkt.{loai}"
        thang_dau, ngay_dau = self._doc_thang_ngay(
            self._khoa_bat_buoc(muc, "mua_bat_dau", ten_muc), f"{ten_muc}.mua_bat_dau"
        )
        thang_cuoi, ngay_cuoi = self._doc_thang_ngay(
            self._khoa_bat_buoc(muc, "mua_ket_thuc", ten_muc), f"{ten_muc}.mua_ket_thuc"
        )
        ma_giai = [
            self._khoa_bat_buoc(giai, "ma_transfermarkt", "giai")
            for giai in cau_hinh["giai"].values()
        ]
        # date khong doc duoc thanh ngay -> NaT -> khong thuoc mua nao -> bi loai
        ngay = pd.to_datetime(khoi["date"], format="ISO8601", errors="coerce")
        trong_mua = pd.Series(False, index=khoi.index)
        for mua in cau_hinh["mua"]:
            nam_dau = int(mua[:4])
            tu_ngay = pd.Timestamp(nam_dau, thang_dau, ngay_dau)
            den_ngay = pd.Timestamp(nam_dau + 1, thang_cuoi, ngay_cuoi)
            trong_mua |= ngay.between(tu_ngay, den_ngay)  # gom ca hai ngay ranh gioi
        return khoi["competition_id"].isin(ma_giai) & trong_mua


# Duoi tep -> lop nguon doc tep do
_LOP_THEO_DUOI = {".txt": NguonVanBanTranDau, ".csv": NguonCsv}


def _chon_nguon(duong_dan: str | Path) -> NguonDuLieu:
    """Tao doi tuong nguon phu hop voi duoi cua tep.

    Tham so:
        duong_dan: duong dan toi tep du lieu tho.
    Tra ve:
        Doi tuong NguonVanBanTranDau (.txt) hoac NguonCsv (.csv), chua doc tep.
    Ngoai le:
        ThieuTepError: khi khong co tep.
        DinhDangTepError: khi duoi tep khong phai .txt hay .csv.
    """
    duong_dan = Path(duong_dan)
    if not duong_dan.is_file():
        raise ThieuTepError(f"Khong tim thay tep {duong_dan}")
    lop_nguon = _LOP_THEO_DUOI.get(duong_dan.suffix.lower())
    if lop_nguon is None:
        raise DinhDangTepError(
            f"Tep {duong_dan.name} co duoi '{duong_dan.suffix}' la, chi doc .txt va .csv"
        )
    return lop_nguon(duong_dan)


def nap_du_lieu(duong_dan: str | Path) -> pd.DataFrame:
    """Nap mot tep du lieu tho thanh DataFrame, khong ghi tep nao.

    Tham so:
        duong_dan: duong dan toi tep du lieu tho (.txt cua openfootball hoac .csv
            cua Transfermarkt).
    Tra ve:
        Bang tran dau tho (.txt), bang ra san tho hoac bang dinh gia tho (.csv).
    Ngoai le:
        ThieuTepError: khi khong co tep.
        DinhDangTepError: khi duoi tep la, hoac ten tep sai khuon.
        BangRongError: khi tep khong co dong du lieu nao.
        ThieuCotError: khi tep CSV thieu cot can dung.
        CauHinhSaiError: khi cau_hinh.yaml thieu khoa can cho viec doc tep.
    """
    return _chon_nguon(duong_dan).doc()