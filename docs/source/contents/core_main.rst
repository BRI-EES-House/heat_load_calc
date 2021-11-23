.. include:: definition.txt

************************************************************************************************************************
負荷計算（主要部分）
************************************************************************************************************************

========================================================================================================================
I. 評価法
========================================================================================================================

------------------------------------------------------------------------------------------------------------------------
1 はじめに
------------------------------------------------------------------------------------------------------------------------

------------------------------------------------------------------------------------------------------------------------
2 記号及び単位
------------------------------------------------------------------------------------------------------------------------

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2.1 記号
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

この計算で用いる記号及び単位を次に示す。

:math:`A_{s,j}`
    | 境界 |j| の面積, |m2|
:math:`c_a`
    | 空気の比熱, J/(kg K)
:math:`C_{lh,frt,i}`
    | 室 |i| の備品等の湿気容量, kg/(kg/kg(DA))
:math:`C_{sh,frt,i}`
    | 室 |i| の備品等の熱容量, J/K
:math:`f_{flr,c,i,j}`
    | 室 |i| の放射冷房設備の放熱量の放射成分に対する境界 |j| の室内側表面の吸収比率, -
:math:`f_{flr,h,i,j}`
    | 室 |i| の放射暖房設備の放熱量の放射成分に対する境界 |j| の室内側表面の吸収比率, -
:math:`\hat{f}_{flr,i,j,n}`
    | ステップ |n| からステップ |n+1| における室 |i| の放射暖冷房設備の放熱量の放射成分に対する境界 |j| の室内側表面の吸収比率, -
:math:`f_{mrt,hum,i,j}`
    | 室 |i| の人体に対する境界 |j| の形態係数, -
:math:`f_{mrt,i,j}`
    | 室 |i| の微小球に対する境界 |j| の形態係数, -
:math:`G_{lh,frt,i}`
    | 室 |i| の備品等と空気間の湿気コンダクタンス, kg/(s kg/kg(DA))
:math:`G_{sh,frt,i}`
    | 室 |i| の備品等と空気間の熱コンダクタンス, W/K
:math:`h_{hum,c,i,n}`
    | ステップ |n| における室 |i| の人体表面の対流熱伝達率, W/(|m2| K)
:math:`h_{hum,r,i,n}`
    | ステップ |n| における室 |i| の人体表面の放射熱伝達率, W/(|m2| K)
:math:`h_{s,c,j}`
    | 境界 |j| の室内側対流熱伝達率, W/(|m2| K)
:math:`h_{s,r,j}`
    | 境界 |j| の室内側放射熱伝達率, W/(|m2| K)
:math:`k_{ei,j,j*}`
    | 境界 |j| の裏面温度に境界　|j*| の等価温度が与える影響, -
:math:`k_{eo,j}`
    | 境界 |j| の温度差係数, -
:math:`k_{c,i,n}`
    | ステップ |n| における室 |i| の人体表面の対流熱伝達率が総合熱伝達率に占める割合, -
:math:`k_{r,i,n}`
    | ステップ |n| における室 |i| の人体表面の放射熱伝達率が総合熱伝達率に占める割合, -
:math:`\hat{L}_{CL,i,n}`
    | ステップ |n| からステップ |n+1| における室 |i| の対流暖冷房設備の潜熱処理量（加湿を正・除湿を負とする）, W
:math:`\hat{L}_{CS,i,n}`
    | ステップ |n| からステップ |n+1| における室 |i| の対流暖冷房設備の顕熱処理量（暖房を正・冷房を負とする）, W
:math:`\hat{L}_{RS,i,n}`
    | ステップ |n| からステップ |n+1| における室 |i| に放射暖冷房設備の顕熱処理量（暖房を正・冷房を負とする）, W
:math:`l_{wtr}`
    | 水の蒸発潜熱, J/kg
:math:`\hat{n}_{hum,i,n}`
    | ステップ |n| からステップ |n+1| における室 |i| の在室人数, -
:math:`p_{i,j}`
    | 室 |i| と境界 |j| の接続に関する係数（境界 |j| が室 |i| に接している場合は :math:`1` とし、それ以外の場合は :math:`0` とする。）, -
:math:`p_{s,sol,abs,j}`
    | 境界 |j| において透過日射を吸収するか否かを表す係数（吸収する場合は :math:`1` とし、吸収しない場合は :math:`0` とする。）, -
:math:`\hat{q}_{gen,i,n}`
    | ステップ |n| からステップ |n+1| における室 |i| の人体発熱を除く内部発熱, W
:math:`\hat{q}_{hum,i,n}`
    | ステップ |n| からステップ |n+1| における室 |i| の人体発熱, W
:math:`\hat{q}_{hum,psn,i,n}`
    | ステップ |n| からステップ |n+1| における室 |i| の1人あたりの人体発熱, W
:math:`q_{RS,c,max,i}`
    | 室 |i| の放射暖房設備の最大放熱量（放熱を正とする）, W
:math:`q_{RS,h,max,i}`
    | 室 |i| の放射冷房設備の最大吸熱量（吸熱を負とする）, W
:math:`q_{s,j,n}`
    | ステップ |n| における境界 |j| の表面熱流（壁体吸熱を正とする）, W/|m2|
:math:`q_{s,sol,j,n}`
    | ステップ |n| における境界 |j| の透過日射吸収熱量, W/|m2|
:math:`\hat{q}_{sol,frt,i,n}`
    | ステップ |n| からステップ |n+1| における室 |i| に設置された備品等による透過日射吸収熱量時間平均値, W
:math:`q_{trs,sol,i,n}`
    | ステップ |n| における室 |i| の透過日射熱量, W
:math:`r_{j,m}`
    | 境界 |j| の項別公比法の指数項 |m| の公比, -
:math:`\hat{r}_{ac,demand,i,n}`
    | ステップ |n| からステップ |n+1| における室 |i| の空調需要, -
:math:`\hat{V}_{leak,i,n}`
    | ステップ |n| からステップ |n+1| における室 |i| のすきま風量, |m3|/s
:math:`V_{rm,i}`
    | 室 |i| の容積, |m3|
:math:`\hat{V}_{vent,int,i,i*,n}`
    | ステップ |n| からステップ |n+1| における室 |i*| から室 |i| への室間の空気移動量（流出換気量を含む）, |m3|/s
:math:`\hat{V}_{vent,mec,i,n}`
    | ステップ |n| からステップ |n+1| における室 |i| の機械換気量（全般換気量と局所換気量の合計値）, |m3|/s
:math:`\hat{V}_{vent,mec,general,i}`
    | ステップ |n| からステップ |n+1| における室 |i| の機械換気量（全般換気量）, |m3|/s
:math:`\hat{V}_{vent,mec,local,i,n}`
    | ステップ |n| からステップ |n+1| における室 |i| の機械換気量（局所換気量）, |m3|/s
:math:`\hat{V}_{vent,ntr,i,n}`
    | ステップ |n| からステップ |n+1| における室 |i| の自然風利用による換気量, |m3|/s
:math:`\hat{V}_{vent,ntr,set,i}`
    | 室 |i| の自然風利用時の換気量, |m3|/s
:math:`\hat{V}_{vent,out,i,n}`
    | ステップ |n| からステップ |n+1| における室 |i| の換気・すきま風・自然風の利用による外気の流入量, |m3|/s
:math:`X_{frt,i,n}`
    | ステップ |n| における室 |i| の備品等の絶対湿度, kg/kg(DA)
:math:`\hat{X}_{gen,i,n}`
    | ステップ |n| からステップ |n+1| における室 |i| の人体発湿を除く内部発湿, kg/s
:math:`\hat{X}_{hum,i,n}`
    | ステップ |n| からステップ |n+1| における室 |i| の人体発湿, kg/s
:math:`\hat{X}_{hum,psn,i,n}`
    | ステップ |n| からステップ |n+1| における室 |i| の1人あたりの人体発湿, kg/s
:math:`X_{o,n}`
    | ステップ |n| における外気絶対湿度, kg/kg(DA)
:math:`X_{r,i,n}`
    | ステップ |n| における室 |i| の絶対湿度, kg/kg(DA)
:math:`X_{r,ntr,i,n}`
    | ステップ |n| における室 |i| の加湿・除湿を行わない場合の絶対湿度, kg/kg(DA)
:math:`\hat{\beta}_{i,n}`
    | ステップ |n| からステップ |n+1| における室 |i| の放射暖冷房設備の対流成分比率, -
:math:`\beta_{c,i}`
    | 室 |i| の放射冷房設備の対流成分比率, -
:math:`\beta_{h,i}`
    | 室 |i| の放射暖房設備の対流成分比率, -
:math:`\Delta t`
    | 1ステップの時間間隔, s
:math:`\theta_{dstrb,j,n}`
    | ステップ |n| の境界 |j| における外気側等価温度の外乱成分, ℃
:math:`\theta_{ei,j,n}`
    | ステップ |n| における境界 |j| の等価温度, ℃
:math:`\theta_{frt,i,n}`
    | ステップ |n| における室 |i| の備品等の温度, ℃
:math:`\theta_{lower,target,i,n}`
    | ステップ |n| における室 |i| の目標作用温度の下限値 , ℃
:math:`\theta_{mrt,hum,i,n}`
    | ステップ |n| における室 |i| の人体の平均放射温度, ℃
:math:`\theta_{o,n}`
    | ステップ |n| における外気温度, ℃
:math:`\theta_{o,eqv,j,n}`
    | ステップ |n| における境界 |j| の相当外気温度, ℃
:math:`\theta_{OT,i,n}`
    | ステップ |n| における室 |i| の作用温度, ℃
:math:`\theta_{r,i,n}`
    | ステップ |n| における室 |i| の温度, ℃
:math:`\theta_{r,OT,ntr,i,n}`
    | ステップ |n| における室 |i| の自然作用温度 , ℃
:math:`\theta_{rear,j,n}`
    | ステップ |n| における境界 |j| の裏面温度, ℃
:math:`\theta_{s,j,n}`
    | ステップ |n| における境界 |j| の表面温度, ℃
:math:`\theta'_{s,a,j,m,n}`
    | ステップ |n| における境界 |j| の項別公比法の指数項 |m| の吸熱応答の項別成分, ℃
:math:`\theta'_{s,t,j,m,n}`
    | ステップ |n| における境界 |j| の項別公比法の指数項 |m| の貫流応答の項別成分, ℃
:math:`\theta_{upper,target,i,n}`
    | ステップ |n| における室 |i| の目標作用温度の上限値 , ℃
:math:`\rho_a`
    | 空気の密度, kg/|m3|
:math:`\phi_{a0,j}`
    | 境界 |j| の吸熱応答係数の初項, |m2| K/W
:math:`\phi_{a1,j,m}`
    | 境界 |j| の項別公比法の指数項 |m| の吸熱応答係数, |m2| K/W
:math:`\phi_{t0,j}`
    | 境界 |j| の貫流応答係数の初項, -
:math:`\phi_{t1,j,m}`
    | 境界 |j| の項別公比法の指数項 |m| の貫流応答係数, -


^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2.2 記号（ベクトル）
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

この計算で用いる記号及び単位を次に示す。

:math:`\pmb{A}_{s}`
    | :math:`A_{s,j}` を要素にもつ :math:`J \times J` の対角化行列, |m2|
:math:`\pmb{C}_{frt}`
    | :math:`C_{frt,i}` を要素にもつ :math:`I \times I` の対角化行列, J/K
:math:`\pmb{C}_{lh,frt}`
    | :math:`C_{lh,frt,i}` を要素にもつ :math:`I \times I` の対角化行列, kg/(kg/kg(DA))
:math:`\hat{\pmb{f}}_{flr,n}`
    | :math:`\hat{f}_{flr,i,j,n}` を要素にもつ :math:`J \times I` の行列, -
:math:`\pmb{f}_{mrt}`
    | :math:`f_{mrt,i,j}` を要素にもつ :math:`I \times J` の行列 , -
:math:`\pmb{G}_{frt}`
    | :math:`G_{frt,i}` を要素にもつ :math:`I \times I` の対角化行列, W / K
:math:`\pmb{h}_{s,c}`
    | :math:`h_{s,c,j}` を要素にもつ :math:`J \times J` の対角化行列
:math:`\pmb{h}_{s,r}`
    | :math:`h_{s,r,j}` を要素にもつ :math:`J \times J` の対角化行列
:math:`\pmb{k}_{c,n}`
    | :math:`k_{c,i,n}` を要素にもつ :math:`I \times I` の対角化行列
:math:`\pmb{k}_{ei}`
    | :math:`k_{ei,j,j*}` を要素にもつ :math:`J \times J` の行列, -
:math:`\pmb{k}_{r,n}`
    | :math:`k_{r,i,n}` を要素にもつ :math:`I \times I` の対角化行列
:math:`\hat{\pmb{L}}_{CL,n}`
    | :math:`\hat{L}_{CL,i,n}` を要素にもつ :math:`I \times 1` の縦行列, W
:math:`\hat{\pmb{L}}_{CS,n}`
    | :math:`\hat{L}_{CS,i,n}` を要素にもつ :math:`I \times 1` で表される縦行列, W
:math:`\hat{\pmb{L}}_{RS,n}`
    | :math:`\hat{L}_{RS,i,n}` を要素にもつ :math:`I \times 1` の縦行列, W
:math:`\pmb{p}_{ij}`
    | :math:`p_{i,j}` を要素にもつ :math:`I \times J` の行列, -
:math:`\pmb{p}_{ji}`
    | :math:`p_{i,j}` を要素にもつ :math:`J \times I` の行列, -
:math:`\hat{\pmb{q}}_{gen,n}`
    | :math:`\hat{q}_{gen,i,n}` を要素にもつ :math:`I \times 1` の縦行列, W
:math:`\hat{\pmb{q}}_{hum,n}`
    | :math:`\hat{q}_{hum,i,n}` を要素にもつ :math:`I \times 1` の縦行列, W
:math:`\pmb{q}_{s,sol,n}`
    | :math:`q_{s,sol,j,n}` を要素にもつ :math:`J \times 1` の縦行列, W/|m2|
:math:`\hat{\pmb{V}}_n`
    | :math:`V_{i,n}` を要素にもつ :math:`I \times I` の対角化行列, |m3| |s-1|
:math:`\hat{\pmb{V}}_{vent,int,n}`
    | :math:`\hat{V}_{vent,int,i,i*,n}` を要素にもつ :math:`I \times I` の行列, |m3| |s-1|
:math:`\hat{\pmb{V}}_{vent,out,n}`
    | :math:`\hat{V}_{vent,out,i,n}` を要素にもつ :math:`I \times 1` の縦行列, |m3| |s-1|
:math:`\pmb{X}_{r,n}`
    | :math:`X_{r,i,n}` を要素にもつ :math:`I \times 1` の縦行列, kg/kg(DA)
:math:`\pmb{X}_{r,ntr,n+1}`
    | :math:`X_{r,ntr,i,n+1}` を要素にもつ :math:`I \times 1` の縦行列, kg/kg(DA)
:math:`\hat{\pmb{\beta}}_{n}`
    | :math:`\hat{\beta}_{i,n}` を要素にもつ :math:`I \times I` の対角化行列
:math:`\pmb{\theta}_{dstrb,n}`
    | :math:`\theta_{dstrb,j,n}` を要素にもつ :math:`J \times 1` の縦行列, ℃
:math:`\pmb{\theta}_{frt,n}`
    | :math:`\theta_{frt,i,n}` を要素にもつ :math:`I \times 1` の縦行列, ℃
:math:`\pmb{\theta}_{o,n}`
    | :math:`I \times 1` の縦行列であり、 :math:`\theta_{o,i,n} = \theta_{o,n}` , ℃
:math:`\pmb{\theta}_{OT,n}`
    | :math:`\theta_{OT,i,n}` を要素にもつ :math:`I \times 1` で表される縦行列, -
:math:`\pmb{\theta}_{r,n}`
    | :math:`\theta_{r,i,n}` を要素にもつ :math:`I \times 1` の縦行列, ℃
:math:`\pmb{\theta}_{rear,n}`
    | :math:`\theta_{rear,j,n}` を要素にもつ :math:`J \times 1` の縦行列, ℃
:math:`\pmb{\theta}_{s,n}`
    | :math:`\theta_{s,j,n}` を要素にもつ :math:`J \times 1` の縦行列, ℃
:math:`\pmb{\phi}_{a0}`
    | :math:`\phi_{a0,j}` を要素にもつ :math:`J \times J` の対角化行列, |m2| K/W
:math:`\pmb{\phi}_{t0}`
    | :math:`\phi_{t0,j}` を要素にもつ :math:`J \times J` の対角化行列, -

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2.3 温度バランス・熱バランスに関する係数
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ステップ |n+1| における境界 |j| の表面温度 :math:`\theta_{s,j,n+1}`　、
ステップ |n+1| における室 |j| の温度 :math:`\theta,j,n+1` 、及び
ステップ |n| からステップ |n+1| における室 |i| の放射暖冷房設備の顕熱処理量（暖房を正・冷房を負とする）  :math:`\hat{L}_{RS,i,n}`
の関係は次式で表されるとする。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{f}_{AX} \cdot \pmb{\theta}_{s,n+1}
        = \pmb{f}_{FIA} \cdot \pmb{\theta}_{r,n+1}
        + \pmb{f}_{CRX,n+1}
        + \pmb{f}_{FLB,n+1} \cdot \hat{\pmb{L}}_{RS,n}
        + \pmb{f}_{CVL,n+1}
    \end{align*}

    \begin{align*}
        \pmb{\theta}_{s,n+1}
        = \pmb{f}_{WSR} \cdot \pmb{\theta}_{r,n+1}
        + \pmb{f}_{WSC, n+1}
        + \pmb{f}_{WSB, n+1} \cdot \pmb{\hat{L}}_{RS,n}
        + \pmb{f}_{WSV,n+1}
    \end{align*}

ステップ |n+1| における室 |i| の温度 :math:`\theta_{r,i,n+1}` 、
ステップ |n| からステップ |n+1| における室 |i| の対流暖冷房設備の顕熱処理量（暖房を正・冷房を負とする） :math:`\hat{\pmb{L}}_{CS,i,n}` 、および
ステップ |n| からステップ |n+1| における室 |i| の放射暖冷房設備の顕熱処理量（暖房を正・冷房を負とする） :math:`\hat{\pmb{L}}_{RS,i,n}`
の関係は次式で表されるとする。

.. math::
    :nowrap:

    \begin{align*}
        \hat{\pmb{f}}_{BRM,n} \cdot \pmb{\theta}_{r,n+1}
        = \hat{\pmb{f}}_{BRC,n}
        + \hat{\pmb{L}}_{CS,n}
        + \pmb{f}_{BRL, n} \cdot \hat{\pmb{L}}_{RS,n}
    \end{align*}

ステップ |n+1| における室 |i| の温度 :math:`\theta_{r,i,n+1}` 、
ステップ |n+1| における室 |i| の作用温度 :math:`\theta_{OT,i,n+1}` 、および
ステップ |n| からステップ |n+1| における室 |i| の放射暖冷房設備の顕熱処理量（暖房を正・冷房を負とする） :math:`\hat{\pmb{L}}_{RS,i,n}`
の関係は次式で表されるとする。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{\theta}_{r,n+1}
        = \pmb{f}_{XOT,n+1} \cdot \pmb{\theta}_{OT,n+1}
        + \pmb{f}_{XLR,n+1} \cdot \hat{\pmb{L}}_{RS,n}
        + \pmb{f}_{XC,n+1}
    \end{align*}

ステップ |n+1| における室 |i| の作用温度 :math:`\theta_{OT,i,n+1}` 、
ステップ |n| からステップ |n+1| における室 |i| の対流暖冷房設備の顕熱処理量（暖房を正・冷房を負とする） :math:`\hat{\pmb{L}}_{CS,i,n}` 、および
ステップ |n| からステップ |n+1| における室 |i| の放射暖冷房設備の顕熱処理量（暖房を正・冷房を負とする） :math:`\hat{\pmb{L}}_{RS,i,n}`
の関係は次式で表されるとする。

.. math::
    :nowrap:

    \begin{align*}
        \hat{\pmb{f}}_{BRM,OT,n} \cdot \pmb{\theta}_{OT,n+1}
        = \hat{\pmb{f}}_{BRC,OT,n}
        + \hat{\pmb{L}}_{CS,n}
        + \pmb{f}_{BRL,OT,n} \cdot \hat{\pmb{L}}_{RS,n}
    \end{align*}

ここで、

:math:`\pmb{f}_{AX}`
    | :math:`f_{AX,j,j*}` を要素にもつ、:math:`J \times J` の行列, -
:math:`\pmb{f}_{FIA}`
    | :math:`f_{FIA,j,i}` を要素にもつ、:math:`J \times I` の行列, -
:math:`\pmb{f}_{CRX,n}`
    | :math:`f_{CRX,j,j*,n}` を要素にもつ :math:`I \times 1` で表される縦行列, ℃
:math:`\pmb{F}_{FLB,n}`
    | :math:`f_{FLB,j，i,n}` を要素にもつ、:math:`J \times I` の行列, K/W
:math:`\pmb{f}_{CVL,n}`
    | :math:`f_{CVL,j,n}` を要素にもつ :math:`J \times 1` で表される縦行列, ℃

:math:`\pmb{ｆ}_{WSR}`
    | :math:`f_{WSR,j,i}` を要素にもつ :math:`J \times I` で表される行列, -
:math:`\pmb{f}_{WSC,n}`
    | :math:`f_{WSC,j,n}` を要素にもつ :math:`J \times 1` で表される縦行列, ℃
:math:`\pmb{f}_{WSB,n}`
    | :math:`f_{WSB,j,i,n}` を要素にもつ :math:`J \times I` で表される行列, K/W
:math:`\pmb{f}_{WSV,n}`
    | :math:`f_{WSV,j,n}` を要素にもつ :math:`J \times 1` で表される縦行列, ℃

:math:`\hat{\pmb{f}}_{BRM,n}`
    | :math:`\hat{f}_{BRM,i,i,n}` を要素にもつ :math:`I \times I` で表される行列, W / K
:math:`\hat{\pmb{f}}_{BRC,n}`
    | :math:`\hat{f}_{BRC,i,n}` を要素にもつ :math:`I \times 1` で表される縦行列, W
:math:`\hat{\pmb{f}}_{BRL,n}`
    | :math:`\hat{f}_{BRL,i,i,n}` を要素にもつ :math:`I \times I` で表される行列, -

:math:`\pmb{f}_{XOT,n}`
    | :math:`f_{XOT,i,i,n}` を要素にもつ :math:`I \times I` で表される行列, -
:math:`\pmb{f}_{XLR,n}`
    | :math:`f_{XLR,i,i,n}` を要素にもつ :math:`I \times I` で表される行列, K/W
:math:`\pmb{f}_{XC,n}`
    | :math:`f_{XC,i,n}` を要素にもつ :math:`I \times 1` で表される縦行列, ℃

:math:`\hat{\pmb{f}}_{BRM,OT,n}`
    | :math:`\hat{f}_{BRM,OT,i,i,n}` を要素にもつ :math:`I \times I` で表される行列, W/K
:math:`\hat{\pmb{f}}_{BRC,OT,n}`
    | :math:`\hat{f}_{BRC,OT,i,i,n}` を要素にもつ :math:`I \times I` で表される行列, W
:math:`\hat{\pmb{f}}_{BRL,OT,n}`
    | :math:`\hat{f}_{BRL,OT,i,i,n}` を要素にもつ :math:`I \times I` で表される縦行列, -

である。本資料では、各要素は単に係数と呼び、例えば、
行列 :math:`\pmb{f}_{AX}` の要素は単に、「係数 :math:`f_{AX,j,j*}` 」と呼ぶ。

:math:`\pmb{f}_{h,cst,n}`
    | :math:`f_{h,cst,i,n}` を要素にもつ :math:`I \times 1` の縦行列, kg/s
:math:`\pmb{f}_{h,wgt,n}`
    | :math:`f_{h,wgt,i,i*,n}` を要素にもつ :math:`I \times I` の行列, kg/(s　(kg/kg(DA)))
:math:`\hat{\pmb{f}}_{L,CL,cst,n}`
    | :math:`\hat{f}_{L,CL,cst,i,n}` を要素にもつ :math:`I \times 1` の縦行列, kg/s
:math:`\hat{\pmb{f}}_{L,CL,wgt,n}`
    | :math:`\hat{f}_{L,CL,wgt,i,i*,n}` を要素にもつ :math:`I \times I` の行列, kg/(s (kg/kg(DA)))

:math:`f_{h,cst,i,n}`
    | ステップ |n| における室 |i| の潜熱バランスに関する係数, kg/s
:math:`f_{h,wgt,i,i*,n}`
    | ステップ |n| における室 |i*| の絶対湿度が室 |i| の潜熱バランスに与える影響を表す係数, kg/(s (kg/kg(DA)))
:math:`\hat{f}_{L,CL,cst,i,n}`
    | ステップ |n| から |n+1| における室 |i| の潜熱負荷に与える影響を表す係数, kg/s
:math:`\hat{f}_{L,CL,wgt,i,i*,n}`
    | ステップ |n+1| における室 |i*| の絶対湿度がステップ |n| から |n+1| における室 |i| の潜熱負荷に与える影響を表す係数, kg/(s (kg/kg(DA)))


^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2.4 添え字
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

この計算で用いる添え字を次に示す。

:math:`i`
    | 室
:math:`j`
    | 境界

------------------------------------------------------------------------------------------------------------------------
3 繰り返し計算（建物全般）
------------------------------------------------------------------------------------------------------------------------

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
3.1 湿度と潜熱処理量
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ステップ |n+1| における室 |i| の備品等の絶対湿度 :math:`X_{frt,i,n+1}` は、式(1.1)により表される。

.. math::
    :nowrap:

    \begin{align*}
        X_{frt,i,n+1} = \frac{ C_{lh,frt,i} \cdot X_{frt,i,n} + \Delta t \cdot G_{lh,frt,i} \cdot X_{r,i,n+1} }
        { C_{lh,frt,i} + \Delta t \cdot G_{lh,frt,i} }
        \tag{1.1}
    \end{align*}

ステップ |n| からステップ |n+1| における室 |i| の対流暖冷房設備の潜熱処理量（加湿を正・除湿を負とする） :math:`\hat{L}_{CL,i,n}` は、
式(1.2)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{\hat{L}}_{CL,n}
        = l_{wtr} \cdot ( \pmb{\hat{f}}_{L,CL,wgt,n} \cdot \pmb{X}_{r,n+1} + \pmb{\hat{f}}_{L,CL,cst,n} )
        \tag{1.2}
    \end{align*}

ステップ |n+1| における室 |i| の絶対湿度 :math:`X_{r,i,n+1}` は、式(1.3)で表される。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{X}_{r,n+1}　= ( \hat{\pmb{f}}_{h,wgt,n} - \hat{\pmb{f}}_{L,CL,wgt,n} )^{-1} \cdot ( \hat{\pmb{f}}_{h,cst,n} + \hat{\pmb{f}}_{L,CL,cst,n} )
        \tag{1.3}
    \end{align*}

係数 :math:`\hat{f}_{L,CL,wgt,i,i*,n}` 及び係数 :math:`\hat{f}_{L,CL,cst,i,n}` は、
ステップ |n| からステップ |n+1| における室 |i| の暖冷房設備の顕熱処理量（暖房を正・冷房を負とする） :math:`\hat{L}_{CS,i,n}` 、
ステップ |n+1| における室 |i| の温度 :math:`\theta_{r,i,n+1}` 、および
ステップ |n+1| における室 |i| の加湿・除湿を行わない場合の絶対湿度 :math:`X_{r,ntr,i,n+1}` に応じて定まり、
その計算方法を????に示す。

ステップ |n+1| における室 |i| の加湿・除湿を行わない場合の絶対湿度 :math:`X_{r,ntr,i,n+1}` は、式(1.4)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{X}_{r,ntr,n+1}　= \hat{\pmb{f}}_{h,wgt,n}^{-1} \cdot \hat{\pmb{f}}_{h,cst,n}
        \tag{1.4}
    \end{align*}

係数 :math:`f_{h,wgt,i,i*,n}` は、式(1.5)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \hat{f}_{h,wgt,i,i*,n}
        &= \left( \rho_a \cdot \left( \frac{ V_{rm,i} }{ \Delta t } + \hat{V}_{vent,out,i,n} \right) + \frac{ G_{lh,frt,i} \cdot C_{lh,frt,i} }{ C_{lh,frt,i} + \Delta t \cdot G_{lh,frt,i} } \right) \cdot \delta_{ii*} \\
    	&- \rho_a \cdot \hat{V}_{vent,int,i,i*}
        \tag{1.5}
    \end{align*}

係数 :math:`\hat{f}_{h,cst,i,n}` は、式(1.6)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \hat{f}_{h,cst,i,n}
        &= \rho_a \cdot \frac{ V_{rm,i} }{ \Delta t } \cdot X_{r,i,n}
        + \rho_a \cdot \hat{V}_{vent,out,i,n} \cdot X_{o,n+1} \\
	    &+ \frac{G_{lh,frt,i} \cdot C_{lh,frt,i} }{ C_{lh,frt,i} + \Delta t \cdot G_{lh,frt,i} } \cdot X_{frt,i,n}
        + \hat{X}_{gen,i,n} + \hat{X}_{hum,i,n}
        \tag{1.6}
    \end{align*}


ステップ |n| からステップ |n+1| における室 |i| の人体発湿 :math:`\hat{X}_{hum,i,n}` は、式(1.7)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \hat{X}_{hum,i,n} = \hat{X}_{hum,psn,i,n} \cdot \hat{n}_{hum,i,n} \tag{1.7}
    \end{align*}

ステップ |n| からステップ |n+1| における室 |i| の1人あたりの人体発湿　:math:`\hat{X}_{hum,psn,i,n}` は、
ステップ |n| における室 |i| の温度 :math:`\theta_{r,i,n}` に応じて定まり、
その計算方法を????に示す。

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
3.2 温度と顕熱処理量
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ステップ |n+1| における境界 |j| の表面熱流（壁体吸熱を正とする） :math:`q_{s,j,n+1}` は、式(2.1)により与えられる。

.. math::
    :nowrap:

    \begin{align*}
        q_{s,j,n+1} = ( \theta_{ei,j,n+1} - \theta_{s,j,n+1} ) \cdot ( h_{s,c,j} + h_{s,r,j} ) \tag{2.1}
    \end{align*}

ステップ |n+1| における境界 |j| の等価温度 :math:`\theta_{ei,j,n+1}` は、式(2.2)のように表される。

.. math::
    :nowrap:

    \begin{align*}
        \begin{split}
            \pmb{\theta}_{ei,n+1}
            &= (\pmb{h}_{s,c} + \pmb{h}_{s,r})^{-1} \cdot \\
            & \left( \pmb{h}_{s,c} \cdot \pmb{p}_{ji} \cdot \pmb{\theta}_{r,n+1}
            + \pmb{h}_{s,r} \cdot \pmb{p}_{ji} \cdot \pmb{f}_{mrt} \cdot \pmb{\theta}_{s,,n+1} \right. \\
            & \left. + \pmb{q}_{s,sol,n+1}
            + \pmb{A}_{s}^{-1} \cdot \hat{\pmb{f}}_{flr,n} \cdot \hat{\pmb{L}}_{RS,n} \cdot (\pmb{I} - \hat{\pmb{\beta}}_{n}) \right)
        \end{split}
        \tag{2.2}
    \end{align*}


ステップ |n+1| における室 |i| の人体の平均放射温度 :math:`\theta_{mrt,hum,i,n+1}` は、式(2.3)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \theta_{mrt,hum,i,n+1} = f_{mrt,hum,i,j} \cdot \theta_{s,j,n+1} \tag{2.3}
    \end{align*}

ステップ |n+1| における室 |i| の備品等の温度 :math:`\theta_{frt,i,n+1}` は、式(2.4)で表される。

.. math::
    :nowrap:

    \begin{align*}
        \theta_{frt,i,n+1} = \frac{
            C_{sh,frt,i} \cdot \theta_{frt,i,n} + \Delta t \cdot G_{sh,frt,i} \cdot \theta_{r,i,n+1}
            + \Delta t \cdot \hat{q}_{sol,frt,i,n}
        }{ C_{sh,frt,i} + \Delta t \cdot G_{sh,frt,i} }
        \tag{2.4}
    \end{align*}

ステップ |n+1| における境界 |j| の表面温度 :math:`\theta_{s,j,n+1}` は式(2.5)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{\theta}_{s,n+1}
        = \pmb{f}_{WSR} \cdot \pmb{\theta}_{r,n+1} + \pmb{f}_{WSC,n+1} + \pmb{f}_{WSB} \cdot \hat{\pmb{L}}_{RS,n} + \pmb{f}_{WSV,n+1}
        \tag{2.5}
    \end{align*}

ステップ |n+1| における室 |i| の温度 :math:`\theta_{r,i,n+1}` は式(2.6)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{\theta}_{r,n+1}
        = \pmb{f}_{XOT,n+1} \cdot \pmb{\theta}_{OT,n+1} - \pmb{f}_{XLR,n+1} \cdot \hat{\pmb{L}}_{RS,n} - \pmb{f}_{XC,n+1}
        \tag{2.6}
    \end{align*}

ステップ |n+1| における室の作用温度　:math:`\pmb{\theta}_{OT,i,n+1}` は式(2.7)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \hat{\pmb{f}}_{BRM,OT,n} \cdot \pmb{\theta}_{OT,n+1}
        = \hat{\pmb{L}}_{CS,n}
        + \hat{\pmb{f}}_{BRL,OT,n+1} \cdot \hat{\pmb{L}}_{RS,n}
        + \hat{\pmb{f}}_{BRC,OT,n+1}
        \tag{2.7}
    \end{align*}

作用温度（左辺の :math:`\theta_{OT,i,n+1}` ）を与えて
負荷（右辺の :math:`\hat{L}_{CS,i,n}` 及び :math:`\hat{L}_{RS,i,n}` ）を未知数として計算する場合（いわゆる負荷計算）と、
負荷（右辺の :math:`\hat{L}_{CS,i,n}` 及び :math:`\hat{L}_{RS,i,n}` を与えて
作用温度（左辺の :math:`\theta_{OT,i,n+1}` ）を未知数として計算する場合（いわゆる成り行き温度）があり、
どちらの計算を行うのかは各室 :math:`i` ごとに定められる運転スケジュールにより決定される。

また、運転スケジュールから空調を行う場合でも、自然室温（空調しない場合の室温）が設定温度以上（暖房時）または設定温度以下（冷房時）の場合は、
自然室温計算を行うことになる。

負荷の :math:`\hat{L}_{CS,i,n}` 及び :math:`\hat{L}_{RS,i,n}` の内訳は、
対流暖冷房設備・放射暖冷房設備の設置の有無及びそれらの最大能力等に依存する。

負荷計算を行うか、成り行き温度計算を行うかの如何に関わらず、
作用温度 :math:`\theta_{OT,i,n+1}`　及び負荷 :math:`\hat{L}_{CS,i,n}` 及び :math:`\hat{L}_{RS,i,n}` を計算することになる。

まとめると、この計算は、

入力値

* 係数 :math:`\hat{\pmb{f}}_{BRM,OT,n+1}` , W / K
* 係数 :math:`\hat{\pmb{f}}_{BRL,OT,n+1}` , -
* 係数 :math:`\hat{\pmb{f}}_{BRC,OT,n+1}` , W
* ステップ |n| から |n+1| における室 |i| の運転モード（暖房・冷房・暖房・冷房停止で窓「開」・暖房・冷房停止で窓「閉」）
* ステップ |n+1| における室 |i| の目標作用温度の上限値 :math:`\theta_{OT,upper,target,i,n+1}`
* ステップ |n+1| における室 |i| の目標作用温度の下限値 :math:`\theta_{OT,lower,target,i,n+1}`
* ステップ |n| から |n+1| における室 |i| の空調需要 :math:`\hat{r}_{ac,demand,i,n}`
* 室 |i| の放射暖房の有無
* 室 |i| の放射冷房の有無
* 室 |i| の放射暖房設備の最大放熱量（放熱を正とする） :math:`q_{RS,h,max,i}`, W
* 室 |i| の放射冷房設備の最大吸熱量（吸熱を負とする） :math:`q_{RS,c,max,i}`, W
* ステップ |n+1| における室 |i| の自然作用温度 :math:`\theta_{r,OT,ntr,i,n+1}`, ℃

出力値

* ステップ |n+1| における室 |i| の作用温度 :math:`\theta_{OT,i,n+1}` , ℃
* ステップ |n| からステップ |n+1| における室 |i| の対流暖冷房設備の顕熱処理量（暖房を正、冷房を負とする） :math:`\hat{L}_{CS,i,n}` , W
* ステップ |n| からステップ |n+1| における室 |i| の放射暖冷房設備の顕熱処理量（暖房を正、冷房を負とする） :math:`\hat{L}_{RS,i,n}` , W

である。これらの計算方法は、付録・・・に示す。

係数 :math:`\hat{\pmb{f}}_{BRL,OT,i,i*,n}` は、式(2.8)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \hat{\pmb{f}}_{BRL,OT,n} = \hat{\pmb{f}}_{BRL,n} + \hat{\pmb{f}}_{BRM,n} \cdot \pmb{f}_{XLR,n+1}
        \tag{2.8}
    \end{align*}

係数 :math:`\pmb{f}_{XLR,n+1}` は、式(2.9)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{f}_{XLR,n+1} = \pmb{f}_{XOT,n+1} \cdot \pmb{k}_{r,n+1} \cdot \pmb{f}_{mrt,hum} \cdot \pmb{f}_{WSB,n+1}
        \tag{2.9}
    \end{align*}

係数 :math:`\pmb{f}_{BRL,n}` は、式(2.10)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{f}_{BRL,n} = \pmb{p}_{ij} \cdot \pmb{h}_{s,c} \cdot \pmb{A}_{s} \cdot \pmb{F}_{WSB,n+1} + \hat{\pmb{\beta}}_{n}
        \tag{2.10}
    \end{align*}

また、 :math:`\pmb{p}_{ij}` は :math:`p_{i,j}` を要素にもつ、室 |i| と境界 |j| との関係を表す行列であり、

:math:`\pmb{p}_{ij}`
    | :math:`p_{i,j}` を要素にもつ :math:`I \times J` の対角化行列

とし、この転置行列を :math:`\pmb{p}_{ji}` と表記する。つまり、

.. math::
    :nowrap:

    \begin{align*}
        \pmb{p}_{ij} = \pmb{p}_{ji}^{T}
    \end{align*}

と定義する。

係数 :math:`\pmb{f}_{WSB,n+1}` は、式(2.11)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{f}_{WSB,n+1} = \pmb{f}_{AX}^{-1} \cdot \pmb{f}_{FLB,n+1}
        \tag{2.11}
    \end{align*}

係数 :math:`f_{FLB,j,i,n+1}` は、式(2.12)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \begin{split}
            f_{FLB,j,i,n+1}
            &= \frac{ \phi_{A0,j} \cdot ( 1 - \hat{\beta}_{i,n} ) \cdot f_{flr,i,j,n+1} }{ A_{s,j} } \\
            &+ \phi_{T0,j} \cdot \sum_{j*=0}^{J-1}{
            \frac{ k_{EI,j,j*}  \cdot ( 1 - \hat{\beta}_{i,n} ) \cdot f_{flr,i,j*,n+1} }{ A_{s,j*} \cdot ( h_{s,c,j*} + h_{s,r,j*} ) }
            }
        \end{split}
        \tag{2.12}
    \end{align*}

ステップ |n| からステップ |n+1| における室 |i| の放射暖冷房設備の対流成分比率 :math:`\hat{\beta}_{i,n}` および、
ステップ |n| からステップ |n+1| における室 |i| の放射暖冷房設備の放熱量のうち放射成分に対する境界 |j| の室内側表面の吸収比率 :math:`{\hat{f}_{flr,i,j,n}}` は、

ステップ |n| からステップ |n+1| における室 |i| の運転が暖房運転時の場合

.. math::
    :nowrap:

    \begin{align*}
        \hat{\beta}_{i,n} = \beta_{h,i} \tag{2.13a}
    \end{align*}

    \begin{align*}
        \hat{f}_{flr,i,j,n} = f_{flr,h,i,j} \tag{2.14a}
    \end{align*}

ステップ |n| からステップ |n+1| における室 |i| の運転が冷房運転時の場合

.. math::
    :nowrap:

    \begin{align*}
        \hat{\beta}_{i,n} = \beta_{c,i} \tag{2.13b}
    \end{align*}

    \begin{align*}
        \hat{f}_{flr,i,j,n} = f_{flr,c,i,j} \tag{2.14b}
    \end{align*}

それ以外の場合

.. math::
    :nowrap:

    \begin{align*}
        \hat{\beta}_{i,n} = 0 \tag{2.13c}
    \end{align*}

    \begin{align*}
        \hat{f}_{flr,i,j,n} = 0 \tag{2.14c}
    \end{align*}

とする。

「ステップ |n| からステップ |n+1| における室 |i| の運転が暖房運転時の場合」とは、
運転モードが「暖房」であり、かつ式(2.15a)を満たす場合をいう。

.. math::
    :nowrap:

    \begin{align*}
        \theta_{r,OT,ntr,i,n+1} < \theta_{lower,target,i,n+1}
        \tag{2.15a}
    \end{align*}

「ステップ |n| からステップ |n+1| における室 |i| の運転が冷房運転時の場合」とは、
運転モードが「冷房」であり、かつ式(2.15b)を満たす場合をいう。

.. math::
    :nowrap:

    \begin{align*}
        \theta_{upper,target,i,n+1} < \theta_{r,OT,ntr,i,n+1}
        \tag{2.15b}
    \end{align*}

ステップ |n+1| における室 |i| の自然作用温度 :math:`\theta_{r,OT,ntr,i,n+1}`　は式(2.16)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{\theta}_{r,OT,ntr,n+1} = \pmb{f}_{BRM,OT,n+1}^{-1} \cdot \pmb{F}_{BRC,OT,n+1}
        \tag{2.16}
    \end{align*}

係数 :math:`\hat{\pmb{f}}_{BRC,OT,n}` は、式(2.17)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \hat{\pmb{f}}_{BRC,OT,n} = \hat{\pmb{f}}_{BRC,n} + \hat{\pmb{f}}_{BRM,n} \cdot \pmb{f}_{XC,n+1}
        \tag{2.17}
    \end{align*}

係数 :math:`\hat{\pmb{f}}_{BRM,OT,n}` は、式(2.18)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \hat{\pmb{f}}_{BRM,OT,n} = \hat{\pmb{f}}_{BRM,n} \cdot \pmb{f}_{XOT,n+1}
        \tag{2.18}
    \end{align*}

係数 :math:`\pmb{f}_{XC,n}` は、式(2.19)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{f}_{XC,n+1} = \pmb{f}_{XOT,n+1} \cdot \pmb{k}_{r,n+1} \cdot \pmb{f}_{mrt,hum}
        \cdot ( \pmb{f}_{WSC,n+1} + \pmb{f}_{WSV,n+1} )
        \tag{2.19}
    \end{align*}

係数 :math:`\pmb{f}_{XOT,n+1}` は、式(2.20)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{f}_{XOT,n+1} = \left( \pmb{k}_{c,n+1} + \pmb{k}_{r,n+1} \cdot \pmb{f}_{mrt,hum} \cdot \pmb{f}_{WSR} \right)^{-1}
        \tag{2.20}
    \end{align*}

ステップ |n+1| における室 |i| の人体表面の対流熱伝達率が総合熱伝達率に占める割合 :math:`k_{c,i,n+1}` 及び
ステップ |n+1| における室 |i| の人体表面の放射熱伝達率が総合熱伝達率に占める割合　:math:`k_{r,i,n+1}`　は、
式(2.21)及び式(2.22)で表される。

.. math::
    :nowrap:

    \begin{align*}
        k_{c,i,n+1} = \frac{ h_{hum,c,i,n+1} }{ ( h_{hum,c,i,n+1} + h_{hum,r,i,n+1} ) }
        \tag{2.21}
    \end{align*}

    \begin{align*}
        k_{r,i,n+1} = \frac{ h_{hum,r,i,n+1} }{ ( h_{hum,c,i,n+1} + h_{hum,r,i,n+1} ) }
        \tag{2.22}
    \end{align*}

係数 :math:`\hat{\pmb{f}}_{BRM,n}` は、式(2.23)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \begin{split}
            \hat{\pmb{f}}_{BRM,n}
            & = \frac{c_a \cdot \rho_a \cdot \pmb{C}_{rm}}{\Delta t}
            + \pmb{p}_{ij} \cdot \pmb{h}_{s,c} \cdot \pmb{A}_s \cdot (\pmb{p}_{ji} - \pmb{f}_{WSR}) \\
            & + c_a \cdot \rho_a \cdot ( \hat{\pmb{V}}_{vent,out,n} - \hat{\pmb{V}}_{vent,int,n} )
            + \frac{ \pmb{G}_{sh,frt} \cdot \pmb{C}_{sh,frt} }{ ( \pmb{C}_{sh,frt} + \Delta t \cdot \pmb{G}_{sh,frt} ) }
        \end{split}
        \tag{2.23}
    \end{align*}

係数 :math:`\hat{\pmb{f}}_{BRC,n}` は、式(2.24)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \begin{split}
            \hat{\pmb{f}}_{BRC,n}
            & = \frac{c_a \cdot \rho_a \cdot \pmb{V}_{rm} \cdot \pmb{\theta}_{r,n}}{\Delta t}
            + \pmb{p}_{ij} \cdot \pmb{h}_{s,c} \cdot \pmb{A}_s \cdot (\pmb{f}_{WSC,n+1} + \pmb{f}_{WSV,n+1}) \\
            & + c_a \cdot \rho_a \cdot \hat{\pmb{V}}_{vent,out,n} \cdot \pmb{\theta}_{o,n+1} \\
            & + \hat{\pmb{q}}_{gen,n} + \hat{\pmb{q}}_{hum,n} \\
            & + \frac{ \pmb{G}_{sh,frt} \cdot ( \pmb{C}_{sh,frt} \cdot \pmb{\theta}_{frt,n} + \Delta t \cdot \hat{\pmb{q}}_{sol,frt,n} ) }
            { \pmb{C}_{sh,frt} + \Delta t \cdot \pmb{G}_{sh,frt} }
        \end{split}
        \tag{2.24}
    \end{align*}

ステップ |n| からステップ |n+1| における室 |i| の換気・すきま風・自然風の利用による外気の流入量 :math:`V_{vent,out,i,n}` は、式(2.25)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \hat{V}_{vent,out,i,n} = \hat{V}_{leak,i,n} + \hat{V}_{vent,mec,i,n} + \hat{V}_{vent,ntr,i,n}
        \tag{2.25}
    \end{align*}

ステップ |n| からステップ |n+1| における室 |i| の自然風利用による換気量 :math:`\hat{V}_{vent,ntr,i,n}` は、
ステップ |n| からステップ |n+1| における室 |i| の運転モードが「暖房・冷房停止で窓「開」」の場合は、

.. math::
    :nowrap:

    \begin{align*}
        \hat{V}_{vent,ntr,i,n} = \hat{V}_{vent,ntr,set,i}
        \tag{2.26a}
    \end{align*}

とし、それ以外の場合（運転モードが「暖房・冷房停止で窓「開」」でない場合）は、

.. math::
    :nowrap:

    \begin{align*}
        \hat{V}_{vent,ntr,i,n} = 0
        \tag{2.26b}
    \end{align*}

とする。

係数 :math:`\pmb{f}_{WSV,n+1}` は、式(2.27)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{f}_{WSV,n+1} = \pmb{f}_{AX}^{-1} \cdot \pmb{f}_{CVL,n+1}
        \tag{2.27}
    \end{align*}

係数 :math:`f_{CVL,j,n+1}` は、式(2-28)により表される。

.. math::
    :nowrap:

    \begin{align*}
        f_{CVL,j,n+1} = \sum_{m=1}^{M}{\theta'_{s,a,j,m,n+1}} + \sum_{m=1}^{M}{\theta_{s,t,j,m,n+1}}
        \tag{2-28}
    \end{align*}

:math:`M` は項別公比法の指数項の数である。

ステップ |n+1| における境界 |j| の項別公比法の指数項 |m| の吸熱応答の項別成分 :math:`\theta'_{s,a,j,m,n+1}` 及び、
ステップ |n+1| における境界 |j| の項別公比法の指数項 |m| の貫流応答の項別成分 :math:`\theta'_{s,t,j,m,n+1}` は、
式(2.29)及び式(2.30)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \theta'_{s,a,j,m,n+1} = q_{s,j,n} \cdot \phi_{a1,j,m} + r_{j,m} \cdot \theta'_{s,a,j,m,n}
        \tag{2.29}
    \end{align*}

.. math::
    :nowrap:

    \begin{align*}
        \theta'_{s,t,j,m,n+1} = \theta_{rear,j,n} \cdot \phi_{t1,j,m} + r_{j,m} \cdot \theta'_{s,t,j,m,n}
        \tag{2.30}
    \end{align*}

ステップ |n| からステップ |n+1| における室 |i| のすきま風量 :math:`\hat{V}_{leak,i,n}` は、
ステップ |n| における室 |i| の空気温度 :math:`\theta_{r,i,n}` 及びステップ |n| における外気温度 :math:`\theta_{o,n}` に依存して、
??に示す方法により定まる。

ステップ |n| からステップ |n+1| における室 |i| の人体発熱 :math:`\hat{q}_{hum,i,n}` は、式(2.31)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \hat{q}_{hum,i,n} = \hat{q}_{hum,psn,i,n} \cdot \hat{n}_{hum,i,n}
        \tag{2.31}
    \end{align*}

ステップ |n| からステップ |n+1| における室 |i| の1人あたりの人体発熱 :math:`\hat{q}_{hum,psn,i,n}` は、
ステップ |n| における室 |i| の室温 :math:`\theta_{r,i,n}` に応じて??に示す方法により定まる。


ステップ |n| における境界 |j| の裏面温度　:math:`\theta_{rear,j,n}` は、式(2.32)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{\theta}_{rear,n} = \pmb{k}_{ei} \cdot \pmb{\theta}_{ei,n} + \pmb{\theta}_{dstrb,n}
        \tag{2.32}
    \end{align*}

次に示す値、

* ステップ |n| における室 |i| の人体表面の対流熱伝達率 :math:`h_{hum,c,i,n}`
* ステップ |n| における室 |i| の人体表面の放射熱伝達率 :math:`h_{hum,r,i,n}`
* ステップ |n| からステップ |n+1| における運転モード
* ステップ |n+1| における室 |i| の作用温度下限値 :math:`\theta_{lower,target,i,n+1}`
* ステップ |n+1| における室 |i| の作用温度上限値 :math:`\theta_{upper,target,i,n+1}`

は、

* ステップ |n| における室 |i| の温度 :math:`\theta_{r,i,n}`
* ステップ |n| における室 |i| の絶対湿度 :math:`X_{r,i,n}`
* ステップ |n-1| からステップ |n| における運転モード
* ステップ |n| における室 |i| の人体の平均放射温度 :math:`\theta_{mrt,hum,i,n}`
* ステップ |n| から |n+1| における室 |i| の空調需要 :math:`\hat{r}_{ac,demand,i,n}`

に応じて、??に定める方法により計算される。

------------------------------------------------------------------------------------------------------------------------
4 繰り返し計算（地盤）
------------------------------------------------------------------------------------------------------------------------

ステップ |n+1| における境界 |j| の表面熱流（壁体吸熱を正とする） :math:`q_{s,j,n+1}` は、式(3.1)により表される。

.. math::
    :nowrap:

    \begin{align*}
        q_{s,j,n+1} = ( h_{s,c,j} + h_{s,r,j} ) \cdot ( \theta_{o,n+1} - \theta_{s,j,n+1} ) \tag{3.1}
    \end{align*}

ステップ |n+1| における境界 |j| の表面温度 :math:`\theta_{s,j,n+1}` は、式(3.2)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \begin{split}
            \theta_{s,j,n+1}
            &= \left( \phi_{a0,j} \cdot h_{i,j} \cdot \theta_{o,n+1} + \phi_{t0,j} \cdot \theta_{dstrb,j,n+1} \right. \\
            &+ \left. \sum_{m=0}^{M-1}{\theta'_{s,a,j,m,n+1}} + \sum_{m=0}^{M-1}{\theta'_{s,t,j,m,n+1}} \right)
            \cdot \frac{1}{1 + \phi_{a0,j} \cdot (h_{s,c,j} + h_{s,r,j}) }
        \end{split}
        \tag{3.2}
    \end{align*}

ステップ |n+1| における境界 |j| の項別公比法の指数項 |m| の吸熱応答の項別成分 :math:`\theta'_{s,a,j,m,n+1}` 及び、
ステップ |n+1| における境界 |j| の項別公比法の指数項 |m| の貫流応答の項別成分 :math:`\theta'_{s,t,j,m,n+1}` は、
式(3.3)及び式(3.4)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \theta'_{s,a,j,m,n+1} = q_{s,j,n} \cdot \phi_{a1,j,m} + r_{j,m} \cdot \theta'_{s,a,j,m,n}
        \tag{3.3}
    \end{align*}

.. math::
    :nowrap:

    \begin{align*}
        \theta'_{s,t,j,m,n+1} = \theta_{dstrb,j,n} \cdot \phi_{t1,j,m} + r_{j,m} \cdot \theta'_{s,t,j,m,n}
        \tag{3.4}
    \end{align*}

------------------------------------------------------------------------------------------------------------------------
5 事前計算
------------------------------------------------------------------------------------------------------------------------

ステップ |n| における係数 :math:`f_{WSC,j,n}` は、式(4.1)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{f}_{WSC,n} = \pmb{f}_{AX}^{-1} \cdot \pmb{f}_{CRX,n}
        \tag{4.1}
    \end{align*}

係数 :math:`f_{WSR,j,i}` は、式(4.2)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{f}_{WSR} = \pmb{f}_{AX}^{-1} \cdot \pmb{f}_{FIA}
        \tag{4.2}
    \end{align*}

ステップ |n| における係数 :math:`f_{CRX,j,n}` は、式(4.3)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{f}_{CRX,n}
        = \pmb{\phi}_{a0} \cdot \pmb{q}_{s,sol,n}
        + \pmb{\phi}_{t0} \cdot \pmb{k}_{ei} \cdot (\pmb{h}_{c} + \pmb{h}_{r})^{-1} \cdot \pmb{q}_{s,sol,n}
        + \pmb{\phi}_{t0} \cdot \pmb{\theta}_{dstrb,n}
        \tag{4.3}
    \end{align*}

係数 :math:`f_{FIA,j,i}` は、式(4.4)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{f}_{FIA} = (
            \pmb{\phi}_{a0} \cdot \pmb{h}_{s,c}
            + \pmb{\phi}_{t0} \cdot \pmb{k}_{ei} \cdot (\pmb{h}_{s,c} + \pmb{h}_{s,r})^{-1} \cdot \pmb{h}_{s,c}
        ) \cdot \pmb{p}_{ji}
        \tag{4.4}
    \end{align*}

係数 :math:`f_{AX,j,i}` は、式(4.5)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \begin{split}
            \pmb{f}_{AX}
            &= \pmb{I} \\
            &+ \pmb{\phi}_{a0} \cdot (\pmb{h}_{s,c} + \pmb{h}_{s,r}) \\
            &- \pmb{\phi}_{a0} \cdot \pmb{h}_{s,r} \cdot \pmb{p}_{ji} \cdot \pmb{f}_{mrt} \\
            &- \pmb{\phi}_{t0} \cdot (\pmb{h}_{s,c} + \pmb{h}_{s,r})^{-1} \cdot \pmb{h}_{s,r} \cdot \pmb{k}_{ei} \cdot \pmb{p}_{ji} \cdot \pmb{f}_{mrt}
        \end{split}
        \tag{4.5}
    \end{align*}

ステップ |n| の境界 |j| における外気側等価温度の外乱成分 :math:`\theta_{dstrb,j,n}` は、式(4.6)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \theta_{dstrb,j,n} = \theta_{o,eqv,j,n} \cdot k_{eo,j}
        \tag{4.6}
    \end{align*}

ステップ |n| における境界 |j| の透過日射吸収熱量 :math:`q_{s,sol,j,n}` 及び
ステップ |n| からステップ |n+1| における室 |i| に設置された備品等による透過日射吸収熱量時間平均値 :math:`q_{sol,frt,i,n}` は、
室 |i| と境界 |j| の接続に関する係数 :math:`p_{i,j}` 、
境界 |j| の面積 :math:`A_{s,j}` 、
境界 |j| において透過日射を吸収するか否かを表す係数（吸収する場合は :math:`1` とし、吸収しない場合は :math:`0` とする。） :math:`p_{s,sol,abs,j}` 、および
ステップ |n| における室 |i| の透過日射熱量 :math:`q_{trs,sol,i,n}`
に応じて??に示す方法により定まる。

ステップ |n| からステップ |n+1| における室 |i| の機械換気量（全般換気量と局所換気量の合計値） :math:`\hat{v}_{vent,mec,i,n}` は、
式(4.7)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \hat{V}_{vent,mec,i,n} = \hat{V}_{vent,mec,general,i} + \hat{V}_{vent,mec,local,i,n}
        \tag{4.7}
    \end{align*}

室 |i| の微小球に対する境界 |j| の形態係数 :math:`f_{mrt,i,j}` は、
境界 |j| の面積 :math:`A_{s,j}` 、
境界 |j| の室内側放射熱伝達率 :math:`h_{s,r,j}` 、及び
室 |i| と境界 |j| の接続に関する係数 :math:`p_{i,j}` に応じて??に示す方法により定まる。

室 |i| の人体に対する境界 |j| の形態係数 :math:`f_{mrt,hum,i,j}` は、
境界 |j| の面積 :math:`A_{s,j}` 、及び
境界 |j| が床かどうかに応じて?? に示す方法により定まる。

以下の係数は設備の入力情報に応じて??に示す方法により定まる。

- 室 |i| の放射冷房設備の放熱量の放射成分に対する境界 |j| の室内側表面の吸収比率 :math:`f_{flr,c,i,j}`
- 室 |i| の放射暖房設備の放熱量の放射成分に対する境界 |j| の室内側表面の吸収比率 :math:`f_{flr,h,i,j}`
- 室 |i| の放射冷房設備の対流成分比率 :math:`\beta_{c,i}`
- 室 |i| の放射暖房設備の対流成分比率 :math:`\beta_{h,i}`
- 室 |i| に放射冷房設備が設置されているか否か
- 室 |i| に放射暖房設備が設置されているか否か
- 室 |i| の冷房方式として放射空調が設置されている場合の放射冷房最大能力 :math:`q_{rs,c,max,i}`
- 室 |i| の暖房方式として放射空調が設置されている場合の放射暖房最大能力 :math:`q_{rs,h,max,i}`

以下の係数は境界の入力情報に応じて??に示す方法により定まる。

- 室 |i| と境界 |j| の接続に関する係数（境界 |j| が室 |i| に接している場合は :math:`1` とし、それ以外の場合は :math:`0` とする。） :math:`p_{i,j}`
- 境界 |j| が床かどうか
- 境界 |j| が地盤かどうか
- 境界 |j| の裏面温度に境界　|j∗| の等価温度が与える影響 :math:`k_{ei,j,j*}`
- 境界 |j| の温度差係数 :math:`k_{eo,j}`
- 境界 |j| の日射吸収の有無
- 境界 |j| の室内側放射熱伝達率, :math:`h_{s,r,j}`
- 境界 |j| の室内側対流熱伝達率, :math:`h_{s,c,j}`
- 境界 |j| の面積, :math:`A_{s,j}`
- 境界 |j| の吸熱応答係数の初項 :math:`\phi_{a0,j}`
- 境界 |j| の項別公比法の指数項 |m| の吸熱応答係数 :math:`\phi_{a1,j,m}`
- 境界 |j| の貫流応答係数の初項 :math:`\phi_{t0,j}`
- 境界 |j| の項別公比法の指数項 |m| の貫流応答係数 :math:`\phi_{t1,j,m}`
- 境界 |j| の項別公比法の指数項 |m| の公比 :math:`r_{j,m}`
- ステップ |n| における室 |i| の透過日射熱量 :math:`q_{trs,sol,i,n}`
- ステップ |n| における境界 |j| の相当外気温度 :math:`\theta_{o,eqv,j,n}`

