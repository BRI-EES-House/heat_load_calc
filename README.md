# Heat Load Calculation

本リポジトリでは、暖冷房負荷計算の開発を行っています。  

[![test](https://github.com/BRI-EES-House/heat_load_calc/workflows/test/badge.svg)](https://github.com/BRI-EES-House/heat_load_calc/actions?query=workflow%3Atest)


## Quick Start

You can run a sample that executes the following command.

```
$ git clone git@github.com:BRI-EES-House/heat_load_calc.git
$ cd heat_load_calc
$ mkdir out
$ python3 src/heat_load_calc/heat_load_calc.py src/heat_load_calc//example/data_example1/mid_data_house.json -o out
```

The files will be generated in the `out` folder.

## How to create original data

See `docs/data_spec/spec_mid_data_house.csv` and create a file.


## Generated files

The following file will be generated.

### Echo back

Save the file with the calculation conditions for later checking.

* mid_data_house.json ... 住宅計算条件JSONファイル

### Schedule

These files will be generated when the `--generate-schedule-only` flag is specified.

* mid_data_local_vent.csv ...  ステップnの室iにおける局所換気量
* mid_data_heat_generation.csv ... ステップnの室iにおける内部発熱
* mid_data_moisture_generation.csv ... ステップnの室iにおける人体発湿を除く内部発湿
* mid_data_occupants.csv ... ステップnの室iにおける在室人数
* mid_data_ac_demand.csv ... ステップnの室iにおける空調需要

### Weather data

This file will be generated when the `--generate-weather-only` flag is specified.

* weather.csv ... 気象データ

### Calculation result

* result_detail_a.csv ... 15分ごとの計算結果（簡易版）(CSV)
* result_detail_i.csv ... 15分ごとの計算結果（詳細版）(CSV)

See `docs/data_spec/spec_core_output_detail.csv` for `result_detail_i.csv`.

## Command options

`-o=<output-folder>` ... Specifies the output folder. If not specified, the output will be in the current folder.

`--generate-weather-only` ... Execute only the generation of weather data. It does not perform load calculations.

`--generate-schedule-only` ... Executes only schedule generation. It does not perform load calculations.

`--load-weather=<weather-folder>` ... Loads a weather file from a specified folder without generating a schedule.

`--load-schedule=<schedule-folder>` ... Loads schedule files from a specified folder without generating schedules.


## 仕様書・根拠

https://heat-load-calc-document.readthedocs.io/ja/latest/

## How to build the document

```
sphinx-build -b html docs/source/ dist
python3 -m http.server --directory dist 8080
```

See `http://localhost:8080`



=== 以下、旧文章（修正中） ===

外皮に関する入力情報の変換の仕方について記述しています。

外皮に関する入力情報として、入力情報の多さ等の観点から、下記のようにいくつかのレベルを設定しています。
なお、用途別の床面積については、下記のレベルに関わらず、すべての段階において入力されるとしています。

# Lv.1

外皮の簡易計算法における入力情報
屋根・天井、壁、床、開口部といった部位の種類ごとにU値やη値が入力される。

# Lv.2

部位ごとの断熱・日射熱取得性能が入力される。

# Lv.3

Lv.2の情報に加えて、部位ごとに、その部位が接する空間用途（主たる居室、その他の居室、非居室、床下）が入力される。

# Lv.4

Lv.3の情報に加えて、内壁の面積や熱物性値の情報を持つ。

# Lv.5

熱バランスを室用途ごとに集約した、簡易熱負荷計算に必要な入力情報である。


設計実務者は、LV.1～LV.3までの入力方法を選択して入力する。
