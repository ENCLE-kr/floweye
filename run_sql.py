import sqlite3
import pandas as pd

DB_PATH = "db.sqlite3"

EXCEL_PATH = "data/zone_table/kto_zoneTable_v1.3_260115.xlsx"
DEVICE_TABLE_NAME = "home_device"

DEVICE_LOG_CSV_PATH = "data/device_log/encle_data_20251028.csv"
DEVICE_LOG_TABLE_NAME = "home_devicelog"


class DeviceImporter:
    def __init__(
        self,
        db_path: str = DB_PATH,
        excel_path: str = EXCEL_PATH,
        table_name: str = DEVICE_TABLE_NAME,
    ) -> None:
        self.db_path = db_path
        self.excel_path = excel_path
        self.table_name = table_name

    @staticmethod
    def normalize_col(name: str) -> str:
        return "".join(ch for ch in name.strip().lower() if ch.isalnum())

    @classmethod
    def pick_column(cls, normalized_cols: dict[str, str], candidates: list[str]) -> str | None:
        for key in candidates:
            normalized_key = cls.normalize_col(key)
            if normalized_key in normalized_cols:
                return normalized_cols[normalized_key]
        return None

    def build_device_frame(self, df: pd.DataFrame) -> pd.DataFrame:
        normalized_cols = {self.normalize_col(col): col for col in df.columns}
        mapping = {
            "device_number": ["device_number", "device no", "device_no", "deviceid", "단말번호", "디바이스번호"],
            "device_mac": ["device_mac", "mac", "macaddress", "mac주소"],
            "address": ["address", "addr", "주소", "설치주소", "도로명주소", "지번주소"],
            "latitude": ["latitude", "lat", "위도"],
            "longitude": ["longitude", "lon", "lng", "경도"],
            "status": ["status", "상태"],
            "last_ping": ["last_ping", "lastping", "pingtime", "최종통신", "최종통신일시", "최종통신시각"],
        }

        selected = {key: self.pick_column(normalized_cols, candidates) for key, candidates in mapping.items()}

        if not selected["device_mac"]:
            raise ValueError("device_mac 컬럼을 찾지 못했습니다. 엑셀 컬럼명을 확인해주세요.")
        if not selected["address"]:
            raise ValueError("address 컬럼을 찾지 못했습니다. 엑셀 컬럼명을 확인해주세요.")
        if not selected["latitude"] or not selected["longitude"]:
            raise ValueError("위도/경도 컬럼을 찾지 못했습니다. 엑셀 컬럼명을 확인해주세요.")

        device_df = pd.DataFrame()

        if selected["device_number"]:
            device_df["device_number"] = df[selected["device_number"]].astype(str).str.strip()
        else:
            device_df["device_number"] = [f"DEV-{i + 1:04d}" for i in range(len(df))]

        device_df["device_mac"] = df[selected["device_mac"]].astype(str).str.strip()
        device_df["address"] = df[selected["address"]].astype(str).str.strip()
        device_df["latitude"] = pd.to_numeric(df[selected["latitude"]], errors="coerce")
        device_df["longitude"] = pd.to_numeric(df[selected["longitude"]], errors="coerce")

        if selected["status"]:
            device_df["status"] = df[selected["status"]].astype(str).str.strip().str.lower()
        else:
            device_df["status"] = "online"

        if selected["last_ping"]:
            device_df["last_ping"] = pd.to_datetime(df[selected["last_ping"]], errors="coerce")
        else:
            device_df["last_ping"] = pd.NaT

        device_df = device_df.dropna(subset=["device_mac", "address", "latitude", "longitude"])
        device_df = device_df[
            (device_df["latitude"].between(-90, 90)) & (device_df["longitude"].between(-180, 180))
        ]
        device_df = device_df.drop_duplicates(subset=["device_number", "device_mac"])

        return device_df

    def insert(self, device_df: pd.DataFrame) -> int:
        insert_sql = f"""
            INSERT OR IGNORE INTO {self.table_name}
                (device_number, device_mac, address, latitude, longitude, status, last_ping, created_at, updated_at)
            VALUES
                (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """
        payload = [
            (
                row.device_number,
                row.device_mac,
                row.address,
                float(row.latitude),
                float(row.longitude),
                row.status if row.status in {"online", "warning", "offline"} else "online",
                None if pd.isna(row.last_ping) else row.last_ping.to_pydatetime(),
            )
            for row in device_df.itertuples(index=False)
        ]

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.executemany(insert_sql, payload)
            conn.commit()
            return cursor.rowcount

    def run(self) -> int:
        df = pd.read_excel(self.excel_path)
        device_df = self.build_device_frame(df)
        return self.insert(device_df)


class DeviceLogImporter:
    def __init__(
        self,
        db_path: str = DB_PATH,
        csv_path: str = DEVICE_LOG_CSV_PATH,
        table_name: str = DEVICE_LOG_TABLE_NAME,
    ) -> None:
        self.db_path = db_path
        self.csv_path = csv_path
        self.table_name = table_name

    @staticmethod
    def normalize_col(name: str) -> str:
        return "".join(ch for ch in name.strip().lower() if ch.isalnum())

    @classmethod
    def pick_column(cls, normalized_cols: dict[str, str], candidates: list[str]) -> str | None:
        for key in candidates:
            normalized_key = cls.normalize_col(key)
            if normalized_key in normalized_cols:
                return normalized_cols[normalized_key]
        return None

    def build_log_frame(self, df: pd.DataFrame) -> pd.DataFrame:
        normalized_cols = {self.normalize_col(col): col for col in df.columns}
        mapping = {
            "mac": ["mac", "device_mac", "수집mac"],
            "src_mac": ["srcmac", "src_mac", "targetmac", "타겟mac"],
            "time": ["time", "log_time", "timestamp", "시각"],
            "rssi": ["rssi", "signal", "신호강도"],
        }

        selected = {key: self.pick_column(normalized_cols, candidates) for key, candidates in mapping.items()}

        if not selected["mac"]:
            raise ValueError("mac 컬럼을 찾지 못했습니다. CSV 컬럼명을 확인해주세요.")
        if not selected["src_mac"]:
            raise ValueError("src_mac 컬럼을 찾지 못했습니다. CSV 컬럼명을 확인해주세요.")
        if not selected["time"]:
            raise ValueError("time 컬럼을 찾지 못했습니다. CSV 컬럼명을 확인해주세요.")

        log_df = pd.DataFrame()
        log_df["mac"] = df[selected["mac"]].astype(str).str.strip()
        log_df["src_mac"] = df[selected["src_mac"]].astype(str).str.strip()
        log_df["time"] = pd.to_datetime(df[selected["time"]], errors="coerce")

        if selected["rssi"]:
            log_df["rssi"] = pd.to_numeric(df[selected["rssi"]], errors="coerce")
        else:
            log_df["rssi"] = pd.NA

        log_df = log_df.dropna(subset=["mac", "src_mac", "time"])
        log_df = log_df.drop_duplicates()

        return log_df

    def insert(self, log_df: pd.DataFrame) -> int:
        insert_sql = f"""
            INSERT INTO {self.table_name}
                (mac, src_mac, time, rssi)
            VALUES
                (?, ?, ?, ?)
        """
        payload = [
            (
                row.mac,
                row.src_mac,
                None if pd.isna(row.time) else row.time.to_pydatetime(),
                None if pd.isna(row.rssi) else int(row.rssi),
            )
            for row in log_df.itertuples(index=False)
        ]

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.executemany(insert_sql, payload)
            conn.commit()
            return cursor.rowcount

    def run(self) -> int:
        df = pd.read_csv(self.csv_path)
        log_df = self.build_log_frame(df)
        return self.insert(log_df)


if __name__ == "__main__":
    # device_importer = DeviceImporter()
    # inserted_devices = device_importer.run()
    # print(f"Inserted device rows: {inserted_devices}")

    log_importer = DeviceLogImporter()
    inserted_logs = log_importer.run()
    print(f"Inserted device_log rows: {inserted_logs}")
    