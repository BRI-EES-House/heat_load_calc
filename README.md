# Heat Load Calculation

本リポジトリでは、暖冷房負荷計算の開発を行っています。  

[![Build Status](https://travis-ci.com/BRI-EES-House/heat_load_calc.svg?branch=master)](https://travis-ci.com/BRI-EES-House/heat_load_calc)
[![test](https://github.com/BRI-EES-House/heat_load_calc/workflows/test/badge.svg)](https://github.com/BRI-EES-House/heat_load_calc/actions?query=workflow%3Atest)


## 仕様書・根拠

https://bri-ees-house.github.io/heat_load_calc/

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
