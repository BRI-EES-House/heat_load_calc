import pytest
import json
import os
import logging

from heat_load_calc import core

#@unittest.skip("")
class ListHandler(logging.Handler):

    """ログをリストに貯めるHandler"""
    def __init__(self, level=logging.NOTSET):
        super().__init__(level)
        self.records = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)

@pytest.fixture
def house_data():
    data_dir = os.path.join(os.path.dirname(__file__), "data_example1")
    with open(os.path.join(data_dir, "example_single_room_floor_heating.json"), "r", encoding="utf-8") as f:
        return json.load(f)

def test_all_at_once_verify_by_handler(house_data):

    print('\n testing all at once floor heating')

    # --- [MOD] ここから: Handlerでログ捕捉 ---
    # まずは確実に拾うため root logger に付けます（必要なら特定loggerに変更可）
    root = logging.getLogger()

    handler = ListHandler(level=logging.ERROR)  # ERROR以上だけ貯める
    old_level = root.level

    root.addHandler(handler)
    root.setLevel(logging.ERROR)
    try:
        dd_i, _, _, _ = core.calc(
            d=house_data,
            entry_point_dir=os.path.dirname(__file__),
            exe_verify=True,
        )
    finally:
        root.removeHandler(handler)
        root.setLevel(old_level)
    
    # --- ERROR/CRITICALが出ていないことを検証 ---
    errors = [r for r in handler.records if r.levelno >= logging.ERROR]
    assert not errors, "Verification logged ERROR/CRITICAL:\n" + "\n".join(
        f"{r.name} {r.levelname}: {r.getMessage()}" for r in errors
    )

    # 既存の数値検証（例）
    assert dd_i["rm0_t_r"]["1989/8/6  17:00:00"] == pytest.approx(43.3140093358602, abs=0.001)
    assert dd_i["rm0_x_r"]["1989/8/6  17:00:00"] == pytest.approx(0.0129410048596679, abs=0.001)
    assert dd_i["b1_t_s"]["1989/8/6  17:00:00"] == pytest.approx(37.1353348426815, abs=0.001)

if __name__ == '__main__':

    pytest.main()