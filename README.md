## Cach chay

Yêu cầu: Python 3.12.10

1. Tạo môi trường ảo và cài thư viện (chạy tại thư mục của kho):
    ```
    py -3.12 -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt
    ```

2. Lấy data theo hướng dẫn ở file `data/raw/CACH_LAY_DU_LIEU.md`.
3. Chạy chương trình:
    ```
    python chay.py --giai-doan tat-ca
    ```