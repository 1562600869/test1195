import fcntl
import json
import os


DATA_FILE = os.environ.get(
    "FIRE_VOLUNTEER_DATA_FILE",
    os.path.join(os.path.expanduser("~"), ".fire_volunteer.json"),
)
LOCK_FILE = DATA_FILE + ".lock"


def _init_data():
    return {
        "volunteers": {},
        "schedules": {},
        "checkins": {},
    }


def _normalize(data):
    if "volunteers" not in data:
        data["volunteers"] = {}
    if "schedules" not in data:
        data["schedules"] = {}
    if "checkins" not in data:
        data["checkins"] = {}
    return data


def load_data():
    """只读加载（stats / absent 等纯查询用，不参与事务写入）"""
    if not os.path.exists(DATA_FILE):
        return _init_data()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        return _init_data()
    return _normalize(data)


class _DataTransaction:
    """文件锁保护的读-检查-写事务上下文管理器"""

    def __init__(self):
        self._lock_fd = None
        self.data = None

    def __enter__(self):
        lock_dir = os.path.dirname(LOCK_FILE) or "."
        os.makedirs(lock_dir, exist_ok=True)
        self._lock_fd = open(LOCK_FILE, "w")
        fcntl.flock(self._lock_fd, fcntl.LOCK_EX)

        if not os.path.exists(DATA_FILE):
            self.data = _init_data()
        else:
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.data = _init_data()
            self.data = _normalize(self.data)
        return self.data

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None and self.data is not None:
                tmp_file = DATA_FILE + ".tmp"
                with open(tmp_file, "w", encoding="utf-8") as f:
                    json.dump(self.data, f, ensure_ascii=False, indent=2)
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(tmp_file, DATA_FILE)
        finally:
            try:
                fcntl.flock(self._lock_fd, fcntl.LOCK_UN)
            except Exception:
                pass
            try:
                self._lock_fd.close()
            except Exception:
                pass
        return False


def transaction():
    """
    用法：
        with transaction() as data:
            # 检查 + 修改 data（全程排他锁）
            # 无异常则原子写回，异常则回滚（不写）
    """
    return _DataTransaction()
