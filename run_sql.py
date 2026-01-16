import sqlite3
import pandas as pd

DB_PATH = "db.sqlite3"
EXCEL_PATH = "data/zone_table/kto_zoneTable_v1.3_260115.xlsx"
TABLE_NAME = "home_device"


def normalize_col(name: str) -> str:
    return "".join(ch for ch in name.strip().lower() if ch.isalnum())


def pick_column(normalized_cols: dict[str, str], candidates: list[str]) -> str | None:
    for key in candidates:
        normalized_key = normalize_col(key)
        if normalized_key in normalized_cols:
            return normalized_cols[normalized_key]
    return None


def build_device_frame(df: pd.DataFrame) -> pd.DataFrame:
    normalized_cols = {normalize_col(col): col for col in df.columns}
    mapping = {
        "device_number": ["device_number", "device no", "device_no", "deviceid", "단말번호", "디바이스번호"],
        "device_mac": ["device_mac", "mac", "macaddress", "mac주소"],
        "address": ["address", "addr", "주소", "설치주소", "도로명주소", "지번주소"],
        "latitude": ["latitude", "lat", "위도"],
        "longitude": ["longitude", "lon", "lng", "경도"],
        "status": ["status", "상태"],
        "last_ping": ["last_ping", "lastping", "pingtime", "최종통신", "최종통신일시", "최종통신시각"],
    }

    selected = {key: pick_column(normalized_cols, candidates) for key, candidates in mapping.items()}

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


def insert_devices(device_df: pd.DataFrame) -> int:
    insert_sql = f"""
        INSERT OR IGNORE INTO {TABLE_NAME}
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

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.executemany(insert_sql, payload)
        conn.commit()
        return cursor.rowcount


if __name__ == "__main__":
    df = pd.read_excel(EXCEL_PATH)
    device_df = build_device_frame(df)
    inserted = insert_devices(device_df)
    print(f"Inserted rows: {inserted}")
    