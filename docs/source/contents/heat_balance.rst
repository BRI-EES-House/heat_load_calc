.. |i| replace:: :math:`i`
.. |i*| replace:: :math:`i^*`
.. |j| replace:: :math:`j`
.. |j*| replace:: :math:`j^*`
.. |k| replace:: :math:`k`
.. |m| replace:: :math:`m`
.. |n| replace:: :math:`n`
.. |n+1| replace:: :math:`n+1`
.. |s-1| replace:: s\ :sup:`-1` \
.. |m-1| replace:: m\ :sup:`-1` \
.. |m2| replace:: m\ :sup:`2` \
.. |m-2| replace:: m\ :sup:`-2` \
.. |m3| replace:: m\ :sup:`3` \
.. |m-3| replace:: m\ :sup:`-3` \

************************************************************************************************************************
繰り返し計算（温度と顕熱）
************************************************************************************************************************

========================================================================================================================
I. 評価法
========================================================================================================================

------------------------------------------------------------------------------------------------------------------------
1) 繰り返し計算
------------------------------------------------------------------------------------------------------------------------

繰り返し計算とは、1つ前のステップの状態量から次のステップの状態量を計算することといえる。
ここで、前のステップから次のステップに引き継ぐ状態量は以下の値とする。

:math:`q_{s,j,n}`
    | ステップ |n| における境界 |j| の表面熱流（壁体吸熱を正とする）, W |m-2|
:math:`\theta_{EI,j,n}`
    | ステップ |n| における境界 |j| の等価温度, ℃
:math:`\theta_{mrt,hum,i,n+}`
    | ステップ |n+1| における室 |i| の人体の平均放射温度, ℃


ステップ |n+1| における境界 |j| の表面熱流（壁体吸熱を正とする） :math:`q_{s,j,n+1}` は式(1)により与えられる。

.. math::
    :nowrap:

    \begin{align*}
        q_{s,j,n+1} = ( \theta_{EI,j,n+1} - \theta_{s,j,n+1} ) \cdot ( h_{s,c,j} + h_{s,r,j} ) \tag{1}
    \end{align*}

ここで、

:math:`q_{s,j,n}`
    | ステップ |n| における境界 |j| の表面熱流（壁体吸熱を正とする）, W / |m2|
:math:`\theta_{EI,j,n}`
    | ステップ |n| における境界 |j| の等価温度, ℃
:math:`\theta_{s,j,n}`
    | ステップ |n| における境界 |j| の表面温度, ℃
:math:`h_{s,c,j}`
    | 境界 |j| の室内側対流熱伝達率, W / |m2| K
:math:`h_{s,r,j}`
    | 境界 |j| の室内側放射熱伝達率, W / |m2| K

である。

ステップ |n+1| における境界 |j| の等価温度 :math:`\theta_{EI,j,n}` は式(2)のように表される。

.. math::
    :nowrap:

    \begin{align*}
        \begin{split}
            \theta_{EI,j,n+1}
            &= \frac{ 1 }{ h_{s,c,j} + h_{s,r,j} } \cdot \\
            & \left( h_{s,c,j} \sum_{i=0}^{I-1}{ ( p_{i,j} \cdot \theta_{r,i,n+1} ) }
            + h_{s,r,j} \cdot \sum_{j*=0}^{J-1}{ ( f'_{mrt,j,j*} \cdot \theta_{s,j*,n+1} ) } \right. \\
            & \left. + q_{sol,j,n+1} + \frac{ \sum_{i=0}^{I-1}{ ( \hat{f}_{flr,i,j,n} \cdot \hat{L}_{SR,i,n} \cdot (1 - \hat{\beta}_{i,n}) ) } }{ A_{s,j} } \right)
        \end{split}
        \tag{2}
    \end{align*}

ここで、

:math:`\theta_{r,i,n}`
    | ステップ |n| における室 |i| の室温, ℃
:math:`f'_{mrt,j*,j}`
    | 平均放射温度計算時の境界 |j*| の表面温度が境界 |j| に与える重み
:math:`q_{sol,j,n+1}`
    | ステップ |n+1| における境界 |j| の透過日射吸収熱量, W / |m2|
:math:`\hat{f}_{flr,i,j,n}`
    | ステップ |n| からステップ |n+1| における室 |i| に設置された放射暖冷房の放熱量のうち放射成分に対する境界 |j| の室内側表面の吸収比率, -
:math:`\hat{L}_{SR,i,n}`
    | ステップ |n| からステップ |n+1| における室 |i| に設置された放射空調の吸放熱量, W
:math:`\hat{\beta}_{i,n}`
    | ステップ |n| からステップ |n+1| における室 |i| に設置された放射暖冷房の対流成分比率, -
:math:`A_{s,j}`
    | 境界 |j| の面積, |m2|
:math:`p_{i,j}`
    | 室 |i| と境界 |j| の接続に関する係数。　境界 |j| が室 |i| に接している場合は :math:`1` とし、それ以外の場合は :math:`0` とする。

である。
なお、式中では、境界 |j*| と境界 |j| で添字を書き分けているが、意味するところは同じであり、例えば表面温度の場合、

.. math::
    :nowrap:

    \begin{align*}
        \theta_{s,j,n} = \theta_{s,j*,n}
    \end{align*}

である。

ステップ |n+1| における室 |i| の人体の平均放射温度 :math:`\theta_{mrt,hum,i,n+1}` は式(3)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \theta_{mrt,hum,i,n+1} = f_{mrt,hum,i,j} \cdot \theta_{s,j,n+1} \tag{3}
    \end{align*}

ここで、

:math:`\theta_{mrt,hum,i,n+1}`
    | ステップ |n+1| における室 |i| の人体の平均放射温度, ℃
:math:`f_{mrt,hum,i,j}`
    | 境界 |j| から室 |i| の人体に対する形態係数, -

である。

ステップ |n+1| における室 |i| の家具の温度 :math:`\theta_{frt,i,n+1}` は式(4)で表される。

.. math::
    :nowrap:

    \begin{align*}
        \theta_{frt,i,n+1} = \frac{
            C_{sh,frt,i} \cdot \theta_{frt,i,n} + \Delta t \cdot G_{sh,frt,i} \cdot \theta_{r,i,n+1}
            + \Delta t \cdot \hat{q}_{sol,frt,n+1}
        }{ C_{sh,frt,i} + \Delta t \cdot G_{sh,frt,i} }
        \tag{4}
    \end{align*}

ここで、

:math:`\theta_{frt,i,n}`
    | ステップ |n| における室 |i| に設置された家具の温度, ℃
:math:`C_{sh,frt,i}`
    | 室 |i| に設置された家具の熱容量, J / K
:math:`G_{sh,frt,i}`
    | 室 |i| における家具と空気間の熱コンダクタンス, W/K
:math:`\Delta t`
    | 時間ステップの間隔, s
:math:`\hat{q}_{sol,frt,i,n}`
    | ステップ |n| からステップ |n+1| における室 |i| に設置された家具による透過日射吸収熱量時間平均値, W

である。


ステップ |n+1| における境界 |j| の表面温度 :math:`\theta_{s,j,n+1}` は式(5)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{\theta}_{s,n+1}
        = \pmb{F}_{WSR} \cdot \pmb{\theta}_{r,n+1} + \pmb{F}_{WSC,n+1} + \pmb{F}_{WSB} \cdot \hat{\pmb{L}}_{SR,n} + \pmb{F}_{WSV,n+1}
        \tag{5}
    \end{align*}

ここで、

:math:`\pmb{\theta}_{s,n}`
    | :math:`\theta_{s,i,n}` を要素にもつ :math:`I \times 1` の縦行列, ℃
:math:`\pmb{\theta}_{r,n}`
    | :math:`\theta_{r,i,n}` を要素にもつ :math:`I \times 1` の縦行列, ℃
:math:`\hat{\pmb{L}}_{SR,n}`
    | :math:`\hat{L}_{SR,i,n}` を要素にもつ :math:`I \times 1` の縦行列, W
:math:`\pmb{F}_{WSR}`
    | :math:`F_{WSR,j,i}` を要素にもつ :math:`J \times I` で表される行列, -
:math:`\pmb{F}_{WSC,n}`
    | :math:`F_{WSC,j,n}` を要素にもつ :math:`J \times 1` で表される縦行列, ℃
:math:`\pmb{F}_{WSB,n}`
    | :math:`F_{WSB,j,i,n}` を要素にもつ :math:`J \times I` で表される行列, K / W
:math:`\pmb{F}_{WSV,n}`
    | :math:`F_{WSV,j,n}` を要素にもつ :math:`J \times 1` で表される縦行列, ℃

である。


ステップ |n+1| における室 |i| の室温 :math:`\theta_{r,i,n+1}` は式(6)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{\theta}_{r,n+1}
        = \pmb{F}_{XOT,n+1} \cdot \pmb{\theta}_{OT,n+1} - \pmb{F}_{XLR,n+1} \cdot \hat{\pmb{L}}_{SR,n} - \pmb{F}_{XC,n+1}
        \tag{6}
    \end{align*}

ここで、

:math:`\pmb{\theta}_{OT,n}`
    | :math:`\theta_{OT,i,n}` を要素にもつ :math:`I \times 1` で表される縦行列, -
:math:`\pmb{F}_{XOT,n}`
    | :math:`F_{XOT,i,i,n}` を要素にもつ :math:`I \times I` で表される行列, -
:math:`\pmb{F}_{XLR,n}`
    | :math:`F_{XLR,i,i,n}` を要素にもつ :math:`I \times I` で表される行列, K / W
:math:`\pmb{F}_{XC,n}`
    | :math:`F_{XC,i,n}` を要素にもつ :math:`I \times 1` で表される縦行列, ℃

であり、

:math:`\theta_{OT,i,n}`
    | ステップ |n| における室 |i| の作用温度, ℃

である。

ステップ |n+1| における室の作用温度　:math:`\pmb{\theta}_{OT,i,n+1}` は式(7)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{F}_{BRM,OT,n+1} \cdot \pmb{\theta}_{OT,n+1} = \hat{\pmb{L}}_{SC,n}
        + \pmb{F}_{BRL,OT,n+1} \cdot \hat{\pmb{L}}_{SR,n}
        + \pmb{F}_{BRC,OT,n+1}
        \tag{7}
    \end{align*}

ここで、

:math:`\hat{\pmb{L}}_{SC,n}`
    | :math:`\hat{L}_{SC,i,n}` を要素にもつ :math:`I \times 1` で表される縦行列, W
:math:`\pmb{F}_{BRM,OT,n}`
    | :math:`F_{BRM,OT,i,i,n}` を要素にもつ :math:`I \times I` で表される行列, W / K
:math:`\pmb{F}_{BRL,OT,n}`
    | :math:`F_{BRL,OT,i,i,n}` を要素にもつ :math:`I \times I` で表される縦行列, -
:math:`\pmb{F}_{BRC,OT,n}`
    | :math:`F_{BRC,OT,i,i,n}` を要素にもつ :math:`I \times I` で表される行列, W

であり、

:math:`\hat{L}_{SC,i,n}`
    | ステップ |n| からステップ |n+1| における室 |i| に設置された対流空調の吸放熱量, W

である。

作用温度（左辺の :math:`\theta_{OT,i,n+1}` ）を与えて
負荷（右辺の :math:`\hat{L}_{SC,i,n}` 及び :math:`\hat{L}_{SR,i,n}` ）を未知数として計算する場合（いわゆる負荷計算）と、
負荷（右辺の :math:`\hat{L}_{SC,i,n}` 及び :math:`\hat{L}_{SR,i,n}` を与えて
作用温度（左辺の :math:`\theta_{OT,i,n+1}` ）を未知数として計算する場合（いわゆる成り行き温度）があり、
どちらの計算を行うのかは各室 :math:`i` ごとに定められる運転スケジュールにより決定される。

また、運転スケジュールから空調を行う場合でも、自然室温（空調しない場合の室温）が設定温度以上（暖房時）または設定温度以下（冷房時）の場合は、
自然室温計算を行うことになる。

負荷の :math:`\hat{L}_{SC,i,n}` 及び :math:`\hat{L}_{SR,i,n}` の内訳は、
対流暖冷房設備・放射暖冷房設備の設置の有無及びそれらの最大能力等に依存する。

負荷計算を行うか、成り行き温度計算を行うかの如何に関わらず、
作用温度 :math:`\theta_{OT,i,n+1}`　及び負荷 :math:`\hat{L}_{SC,i,n}` 及び :math:`\hat{L}_{SR,i,n}` を計算することになる。

まとめると、この計算は、

入力値

* 係数 :math:`\pmb{F}_{BRM,OT,n+1}` , W / K
* 係数 :math:`\pmb{F}_{BRL,OT,n+1}` , -
* 係数 :math:`\pmb{F}_{BRC,OT,n+1}` , W
* ステップ |n| から |n+1| における室 |i| の運転モード（暖房・冷房・暖房・冷房停止で窓「開」・暖房・冷房停止で窓「閉」）
* ステップ |n+1| における室 |i| の目標作用温度（冷房用） :math:`\theta_{OT,upper,target,i,n+1}`
* ステップ |n+1| における室 |i| の目標作用温度（暖房用） :math:`\theta_{OT,lower,target,i,n+1}`
* ステップ |n| から |n+1| における室 |i| の空調需要 :math:`\hat{r}_{ac,demand,i,n}`
* 室 |i| の放射暖房の有無
* 室 |i| の放射冷房の有無
* 室 |i| の放射暖房の最大放熱量（放熱を正値とする） :math:`q_{SR,h,max,i}`, W
* 室 |i| の放射冷房の最大吸熱量（吸熱を負値とする） :math:`q_{SR,c,max,i}`, W
* ステップ |n+1| における室 |i| の自然作用温度 :math:`\theta_{r,OT,ntr,i,n+1}`, ℃

出力値

* ステップ |n+1| における室 |i| の作用温度 :math:`\theta_{OT,i,n+1}` , ℃
* ステップ |n| からステップ |n+1| における室 |i| に設置された対流空調の吸放熱量 :math:`\hat{L}_{SC,i,n}` , W
* ステップ |n| からステップ |n+1| における室 |i| に設置された放射空調の吸放熱量 :math:`\hat{L}_{SR,i,n}` , W

である。これらの計算方法は、付録・・・に示す。

係数 :math:`\pmb{F}_{BRL,OT,n+1}` は、式(8)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{F}_{BRL,OT,n+1} = \pmb{F}_{BRL,n+1} + \pmb{F}_{BRM,n+1} \cdot \pmb{F}_{XLR,n+1} \tag{8}
    \end{align*}

ここで、

:math:`\pmb{F}_{BRL,n}`
    | :math:`F_{BRL,i,i,n}` を要素にもつ :math:`I \times I` で表される行列, -
:math:`\pmb{F}_{BRM,n}`
    | :math:`F_{BRM,i,i,n}` を要素にもつ :math:`I \times I` で表される行列, W / K

である。

係数 :math:`\pmb{F}_{XLR,n+1}` は、式(9)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{F}_{XLR,n+1} = \pmb{F}_{XOT,n+1} \cdot \pmb{k}_{r,n+1} \cdot \pmb{F}_{mrt,hum} \cdot \pmb{F}_{WSB,n+1} \tag{9}
    \end{align*}

ここで、

:math:`\pmb{k}_{r,n+1}`
    | :math:`k_{r,i,n+1}` を要素にもつ :math:`I \times I` の対角化行列

であり、

:math:`k_{r,i,n}`
    | ステップ |n| における室 |i| の人体表面の放射熱伝達率が総合熱伝達率に占める割合, -

である。

係数 :math:`\pmb{F}_{BRL,n}` は、式(10)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{F}_{BRL,n} = \pmb{p}_{ij} \cdot \pmb{h}_{s,c} \cdot \pmb{A}_{s} \cdot \pmb{F}_{WSB,n+1} + \hat{\pmb{\beta}}_{n}
        \tag{10}
    \end{align*}

ここで、

:math:`\pmb{h}_{s,c}`
    | :math:`h_{s,c,j}` を要素にもつ :math:`J \times J` の対角化行列
:math:`\pmb{A}_{s}`
    | :math:`A_{s,j}` を要素にもつ :math:`J \times J` の対角化行列
:math:`\hat{\pmb{\beta}}_{n}`
    | :math:`\hat{\beta}_{i,n}` を要素にもつ :math:`I \times I` の対角化行列

であり、

:math:`h_{s,c,j}`
    | 境界 |j| の室内側対流熱伝達率, W / |m2| K
:math:`A_{s,j}`
    | 境界 |j| の面積, |m2|

とする。また、 :math:`\pmb{p}_{ij}` は :math:`p_{i,j}` を要素にもつ、室 |i| と境界 |j| との関係を表す行列であり、

:math:`\pmb{p}_{ij}`
    | :math:`p_{i,j}` を要素にもつ :math:`I \times J` の対角化行列

とし、この転置行列を :math:`\pmb{p}_{ji}` と表記する。つまり、

.. math::
    :nowrap:

    \begin{align*}
        \pmb{p}_{ij} = \pmb{p}_{ji}^{T}
    \end{align*}

と定義する。

:math:`\pmb{F}_{WSB,n+1}` は、式(11)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{F}_{WSB,n+1} = \pmb{F}_{AX}^{-1} \cdot \pmb{F}_{FLB,n+1} \tag{11}
    \end{align*}

ここで、

:math:`\pmb{F}_{AX}`
    | :math:`F_{AX,j,j*}` を要素にもつ、:math:`J \times J` の行列, -
:math:`\pmb{F}_{FLB,n}`
    | :math:`F_{FLB,j，i,n}` を要素にもつ、:math:`J \times I` の行列, K/W

である。

:math:`F_{FLB,j,i,n+1}` は、式(12)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \begin{split}
            F_{FLB,j,i,n+1}
            &= \frac{ \phi_{A0,j} \cdot ( 1 - \hat{\beta}_{i,n} ) \cdot f_{flr,i,j,n+1} }{ A_{s,j} } \\
            &+ \phi_{T0,j} \cdot \sum_{j*=0}^{J-1}{
            \frac{ k'_{EI,j,j*}  \cdot ( 1 - \hat{\beta}_{i,n} ) \cdot f_{flr,i,j*,n+1} }{ A_{s,j*} \cdot ( h_{s,c,j*} + h_{s,r,j*} ) }
            }
        \end{split}
        \tag{12}
    \end{align*}

ここで、

:math:`\phi_{A0,j}`
    | 境界 |j| の吸熱応答係数の初項, |m2| K / W
:math:`\phi_{T0,j}`
    | 境界 |j| の貫流応答係数の初項, -
:math:`k'_{EI,j,j*}`
    | 境界 |j| の裏面温度に境界　|j*| の等価温度が与える影響
:math:`h_{s,r,j}`
    | 境界 |j| の室内側放射熱伝達率, W / |m2| K

である。

ステップ |n| からステップ |n+1| における室 |i| に設置された放射暖冷房の対流成分比率 :math:`\hat{\beta}_{i,n}` および、
ステップ |n| からステップ |n+1| における室 |i| に設置された放射暖房の放熱量のうち放射成分に対する境界 |j| の室内側表面の吸収比率 :math:`{\hat{f}_{flr,i,j,n}}` は、

ステップ |n| からステップ |n+1| における室 |i| の運転が暖房運転時の場合

.. math::
    :nowrap:

    \begin{align*}
        \hat{\beta}_{i,n} = \beta_{h,i} \tag{13a}
    \end{align*}

    \begin{align*}
        \hat{f}_{flr,i,j,n} = f_{flr,h,i,j} \tag{14a}
    \end{align*}

ステップ |n| からステップ |n+1| における室 |i| の運転が冷房運転時の場合

.. math::
    :nowrap:

    \begin{align*}
        \hat{\beta}_{i,n} = \beta_{c,i} \tag{13b}
    \end{align*}

    \begin{align*}
        \hat{f}_{flr,i,j,n} = f_{flr,c,i,j} \tag{14b}
    \end{align*}

それ以外の場合

.. math::
    :nowrap:

    \begin{align*}
        \hat{\beta}_{i,n} = 0 \tag{13c}
    \end{align*}

    \begin{align*}
        \hat{f}_{flr,i,j,n} = 0 \tag{14c}
    \end{align*}

とする。

ここで、

:math:`\beta_{h,i}`
    | 室 |i| に設置された放射暖房の対流成分比率
:math:`\beta_{c,i}`
    | 室 |i| に設置された放射冷房の対流成分比率
:math:`f_{flr,h,i,j}`
    室 |i| に設置された放射暖房の放熱量のうち放射成分に対する境界 |j| の室内側表面の吸収比率
:math:`f_{flr,c,i,j}`
    室 |i| に設置された放射暖房の放熱量のうち放射成分に対する境界 |j| の室内側表面の吸収比率

である。

「ステップ |n| からステップ |n+1| における室 |i| の運転が暖房運転時の場合」とは、
運転モードが「暖房」であり、かつ式(15a)を満たす場合をいう。

.. math::
    :nowrap:

    \begin{align*}
        \theta_{r,OT,ntr,i,n+1} < \theta_{lower,target,i,n+1} \tag{15a}
    \end{align*}

「ステップ |n| からステップ |n+1| における室 |i| の運転が冷房運転時の場合」とは、
運転モードが「冷房」であり、かつ式(15b)を満たす場合をいう。

.. math::
    :nowrap:

    \begin{align*}
        \theta_{upper,target,i,n+1} < \theta_{r,OT,ntr,i,n+1} \tag{15b}
    \end{align*}

ここで、

:math:`\theta_{r,OT,ntr,i,n+1}`
    | ステップ |n+1| における室 |i| の自然作用温度 , ℃
:math:`\theta_{lower,target,i,n+1}`
    | ステップ |n+1| における室 |i| の作用温度下限値 , ℃
:math:`\theta_{upper,target,i,n+1}`
    | ステップ |n+1| における室 |i| の作用温度上限値 , ℃

である。

ステップ |n+1| における室 |i| の自然作用温度 :math:`\theta_{r,OT,ntr,i,n+1}`　は式(16)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{\theta}_{r,OT,ntr,n+1} = \pmb{f}_{BRM,OT,n+1}^{-1} \cdot \pmb{F}_{BRC,OT,n+1} \tag{16}
    \end{align*}

係数 :math:`\pmb{F}_{BRC,OT,n+1}` は、式(17)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{F}_{BRC,OT,n+1} = \pmb{F}_{BRC,n} + \pmb{F}_{BRM,n} \cdot \pmb{F}_{XC,n+1} \tag{17}
    \end{align*}

ここで、

:math:`\pmb{F}_{BRC,n}`
    | :math:`I \times 1` で表される縦行列, W

である。

係数 :math:`\pmb{F}_{BRM,OT,n+1}` は、式(18)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{F}_{BRM,OT,n+1} = \pmb{F}_{BRM,n} \cdot \pmb{F}_{XOT,n+1} \tag{18}
    \end{align*}

係数 :math:`\pmb{F}_{XC,n}` は、式(19)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{F}_{XC,n+1} = \pmb{F}_{XOT,n+1} \cdot \pmb{kr}_{n+1} \cdot \pmb{F}_{mrt,hum}
        \cdot ( \pmb{F}_{WSC,n+1} + \pmb{F}_{WSV,n+1} )
        \tag{19}
    \end{align*}

係数 :math:`\pmb{F}_{XOT,n+1}` は、式(20)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{F}_{XOT,n+1} = \left( \pmb{kc}_{n+1} + \pmb{kr}_{n+1} \cdot \pmb{F}_{mrt,hum} \cdot \pmb{F}_{WSR} \right)^{-1}
        \tag{20}
    \end{align*}

ここで、

:math:`\pmb{kc}_{n+1}`
    | :math:`kc_{i,n+1}` を要素にもつ :math:`I \times I` の対角化行列

であり、

:math:`kc_{i,n+1}`
    | ステップ |n+1| における室 |i| の人体表面の対流熱伝達率が総合熱伝達率に占める割合, -

である。

ステップ |n+1| における室 |i| の人体表面の対流熱伝達率が総合熱伝達率に占める割合 :math:`kc_{i,n+1}` 及び
ステップ |n+1| における室 |i| の人体表面の放射熱伝達率が総合熱伝達率に占める割合　:math:`kr_{i,n+1}`　は、
式(21)及び式(22)で表される。

.. math::
    :nowrap:

    \begin{align*}
        kc_{i,n} = \frac{ h_{hum,c,i,n} }{ ( h_{hum,c,i,n} + h_{hum,r,i,n} ) } \tag{21}
    \end{align*}

    \begin{align*}
        kr_{i,n} = \frac{ h_{hum,r,i,n} }{ ( h_{hum,c,i,n} + h_{hum,r,i,n} ) } \tag{22}
    \end{align*}

ここで、

:math:`h_{hum,c,i,n}`
    | ステップ |n| における室 |i| の人体表面の対流熱伝達率, W / |m2| K
:math:`h_{hum,r,i,n}`
    | ステップ |n| における室 |i| の人体表面の放射熱伝達率, W / |m2| K

である。

係数 :math:`\pmb{F}_{BRM,n}` は、式(23)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \begin{split}
            \pmb{F}_{BRM,n}
            & = \frac{\pmb{C}_{rm}}{\Delta t}
            + \pmb{p}_{ij} \cdot \pmb{h}_{s,c} \cdot \pmb{A}_s \cdot (\pmb{p}_{ji} - \pmb{F}_{WSR}) \\
            & + c_a \cdot \rho_a \cdot ( \hat{\pmb{V}}_{vent,out,n} - \hat{\pmb{V}}_{vent,int,n} )
            + \frac{ \pmb{G}_{sh,frt} \cdot \pmb{C}_{sh,frt} }{ ( \pmb{C}_{sh,frt} + \Delta t \cdot \pmb{G}_{sh,frt} ) }
        \end{split}
        \tag{23}
    \end{align*}

係数 :math:`\pmb{F}_{BRC,n}` は、式(24)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \begin{split}
            \pmb{F}_{BRC,n}
            & = \frac{ \pmb{C}_{rm} \cdot \pmb{\theta}_{r,n} }{\Delta t}
            + \pmb{p}_{ij} \cdot \pmb{h}_{s,c} \cdot \pmb{A}_s \cdot (\pmb{F}_{WSC,n+1} + \pmb{F}_{WSV,n+1}) \\
            & + c_a \cdot \rho_a \cdot \hat{\pmb{V}}_{vent,out,n} \cdot \pmb{\theta}_{o,n+1} \\
            & + \hat{\pmb{q}}_{gen,n} + \hat{\pmb{q}}_{hum,n} \\
            & + \frac{ \pmb{G}_{sh,frt} \cdot ( \pmb{C}_{sh,frt} \cdot \pmb{\theta}_{frt,n} + \Delta t \cdot \hat{\pmb{q}}_{sol,frt,n} ) }
            { \pmb{C}_{sh,frt} + \Delta t \cdot \pmb{G}_{sh,frt} }
        \end{split}
        \tag{24}
    \end{align*}

ここで、

:math:`\pmb{C}_{rm}`
    | :math:`C_{rm,i}` を要素にもつ :math:`I \times I` の対角化行列, J / K
:math:`\pmb{h}_c`
    | :math:`h_{c,j}` を要素にもつ :math:`J \times J` の対角化行列, W / |m2| K
:math:`\hat{\pmb{V}}_n`
    | :math:`V_{i,n}` を要素にもつ :math:`I \times I` の対角化行列, |m3| |s-1|
:math:`\hat{\pmb{V}}_{vent,out,n}`
    | :math:`\hat{V}_{vent,out,i,n}` を要素にもつ :math:`I \times 1` の縦行列, |m3| |s-1|
:math:`\hat{\pmb{V}}_{vent,int,n}`
    | :math:`\hat{V}_{vent,int,i,i*,n}` を要素にもつ :math:`I \times I` の行列, |m3| |s-1|
:math:`\pmb{G}_{frt}`
    | :math:`G_{frt,i}` を要素にもつ :math:`I \times I` の対角化行列, W / K
:math:`\pmb{C}_{frt}`
    | :math:`C_{frt,i}` を要素にもつ :math:`I \times I` の対角化行列, J / K
:math:`\pmb{\theta}_{o,n}`
    | :math:`I \times 1` の縦行列であり、 :math:`\theta_{o,i,n} = \theta_{o,n}` , ℃
:math:`\hat{\pmb{H}}_n`
    | :math:`H_{i,n}` を要素にもつ :math:`I \times 1` の縦行列, W
:math:`\hat{\pmb{q}}_{gen,n}`
    | :math:`\hat{q}_{gen,i,n}` を要素にもつ :math:`I \times 1` の縦行列, W
:math:`\hat{\pmb{q}}_{hum,n}`
    | :math:`\hat{q}_{hum,i,n}` を要素にもつ :math:`I \times 1` の縦行列, W
:math:`\pmb{\theta}_{frt,n}`
    | :math:`\theta_{frt,i,n}` を要素にもつ :math:`I \times 1` の縦行列, ℃

であり、

:math:`C_{rm,i}`
    | 室 |i| の空気の熱容量, J / K
:math:`h_{c,j}`
    | 境界 |j| の室内側対流熱伝達率, W / |m2| K
:math:`c_a`
    | 空気の比熱, J / kg K
:math:`\rho_a`
    | 空気の密度, kg / |m3|
:math:`\hat{V}_{vent,out,i,n}`
    | ステップ |n| からステップ |n+1| における室 |i| の換気・すきま風・自然風の利用による外気の流入量, |m3| |s-1|
:math:`\hat{V}_{vent,int,i,i*,n}`
    | ステップ |n| からステップ |n+1| における室 |i*| から室 |i| への室間の空気移動量, |m3| |s-1|
:math:`G_{frt,i}`
    | 室 |i| における家具と空気間の熱コンダクタンス, W / K
:math:`C_{frt,i}`
    | 室 |i| に設置された家具の熱容量, J / K
:math:`\theta_{o,n}`
    | ステップ |n| における外気温度, ℃
:math:`\hat{q}_{gen,i,n}`
    | ステップ |n| からステップ |n+1| における室 |i| の人体発熱を除く内部発熱, W
:math:`\hat{q}_{hum,i,n}`
    | ステップ |n| からステップ |n+1| における室 |i| の人体発熱, W
:math:`\theta_{frt,i,n}`
    | ステップ |n| における室 |i| に設置された家具の温度, ℃

である。


ステップ |n| からステップ |n+1| における室 |i| の換気・すきま風・自然風の利用による外気の流入量 :math:`V_{vent,out,i,n}` は、式(25)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \hat{V}_{vent,out,i,n} = \hat{V}_{leak,i,n} + \hat{V}_{vent,mec,i,n} + \hat{V}_{vent,ntr,i,n}
        \tag{25}
    \end{align*}

ここで、

:math:`\hat{V}_{leak,i,n}`
    | ステップ |n| からステップ |n+1| における室 |i| のすきま風量, |m3| |s-1|
:math:`\hat{V}_{vent,mec,i,n}`
    | ステップ |n| からステップ |n+1| における室 |i| の機械換気量（全般換気量と局所換気量の合計値）, |m3| |s-1|
:math:`\hat{V}_{vent,ntr,i,n}`
    | ステップ |n| からステップ |n+1| における室 |i| の自然風利用による換気量, |m3| |s-1|

である。

ステップ |n| からステップ |n+1| における室 |i| の自然風利用による換気量 :math:`\hat{V}_{vent,ntr,i,n}` は、
ステップ |n| からステップ |n+1| における室 |i| の運転モードが「暖房・冷房停止で窓「開」」の場合は、

.. math::
    :nowrap:

    \begin{align*}
        \hat{V}_{vent,ntr,i,n} = \hat{V}_{vent,ntr,set,i} \tag {26a}
    \end{align*}

とし、それ以外の場合（運転モードが「暖房・冷房停止で窓「開」」でない場合）は、

.. math::
    :nowrap:

    \begin{align*}
        \hat{V}_{vent,ntr,i,n} = 0 \tag {26b}
    \end{align*}

とする。
ここで、

:math:`\hat{V}_{vent,ntr,set,i}`
    | 室 |i| の自然風利用時の換気量, |m3| |s-1|

である。

係数 \pmb{F}_{WSV,n+1} は、式(27)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{f}_{WSV,n+1} = \pmb{f}_{AX}^{-1} \cdot \pmb{f}_{CVL,n+1} \tag {27}
    \end{align*}

:math:`\pmb{f}_{CVL,n}`
    | :math:`f_{CVL,j,n}` を要素にもつ :math:`J \times 1` で表される縦行列, ℃


    # ステップn+1の境界jにおける係数WSV, degree C, [j, 1]
    wsv_js_n_pls = np.dot(ss.ivs_ax_js_js, cvl_js_n_pls)
    # ステップn+1の境界jにおける係数WSV, degree C, [j, 1]
    f_wsv_js_n_pls = np.dot(ss.ivs_f_ax_js_js, f_cvl_js_n_pls)

    # ステップn+1の境界jにおける係数CVL, degree C, [j, 1]
    cvl_js_n_pls = np.sum(theta_dsh_srf_t_js_ms_n_pls + theta_dsh_srf_a_js_ms_n_pls, axis=1, keepdims=True)

    # ステップn+1の境界jにおける項別公比法の指数項mの貫流応答の項別成分, degree C, [j, m] (m=12)
    theta_dsh_srf_t_js_ms_n_pls = ss.phi_t1_js_ms * theta_rear_js_n + ss.r_js_ms * c_n.theta_dsh_srf_t_js_ms_n

    # ステップn+1の境界jにおける項別公比法の指数項mの吸熱応答の項別成分, degree C, [j, m] (m=12)
    theta_dsh_srf_a_js_ms_n_pls = ss.phi_a1_js_ms * c_n.q_srf_js_n + ss.r_js_ms * c_n.theta_dsh_srf_a_js_ms_n

    # ステップnの室iにおけるすきま風量, m3/s, [i, 1]
    v_leak_is_n = ss.get_infiltration(theta_r_is_n=c_n.theta_r_is_n, theta_o_n=ss.theta_o_ns[n])

    # ステップnの室iにおける人体発湿, kg/s, [i, 1]
    x_hum_is_n = x_hum_psn_is_n * n_hum_is_n

    # ステップnの室iにおける1人あたりの人体発湿, kg/s, [i, 1]
    x_hum_psn_is_n = occupants.get_x_hum_psn_is_n(theta_r_is_n=c_n.theta_r_is_n)

    # ステップnの室iにおける人体発熱, W, [i, 1]
    q_hum_is_n = q_hum_psn_is_n * n_hum_is_n

    # ステップnの室iにおける1人あたりの人体発熱, W, [i, 1]
    q_hum_psn_is_n = occupants.get_q_hum_psn_is_n(theta_r_is_n=c_n.theta_r_is_n)

    # ステップnの境界jにおける裏面温度, degree C, [j, 1]
    theta_rear_js_n = np.dot(ss.k_ei_js_js, c_n.theta_ei_js_n) + theta_dstrb_js_n

    # ステップnにおける室iの状況（在室者周りの総合熱伝達率・運転状態・Clo値・目標とする作用温度）を取得する
    #     ステップnにおける室iの在室者周りの対流熱伝達率, W / m2K, [i, 1]
    #     ステップnにおける室iの在室者周りの放射熱伝達率, W / m2K, [i, 1]
    #     ステップnの室iにおける運転モード, [i, 1]
    #     ステップnの室iにおける目標作用温度下限値, [i, 1]
    #     ステップnの室iにおける目標作用温度上限値, [i, 1]
    #     ステップnの室iの在室者周りの風速, m/s, [i, 1]
    #     ステップnの室iにおけるClo値, [i, 1]
    #     ステップnの室iにおける目標作用温度, degree C, [i, 1]
    h_hum_c_is_n, h_hum_r_is_n, operation_mode_is_n, theta_lower_target_is_n_pls, theta_upper_target_is_n_pls, remarks_is_n \
        = ss.get_ot_target_and_h_hum(
            x_r_is_n=c_n.x_r_is_n,
            operation_mode_is_n_mns=c_n.operation_mode_is_n,
            theta_r_is_n=c_n.theta_r_is_n,
            theta_mrt_hum_is_n=c_n.theta_mrt_hum_is_n,

            ac_demand_is_n=ac_demand_is_n
        )

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2) 繰り返し計算の前処理
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    # BRM(換気なし), W/K, [i, i]
    brm_non_vent_is_is = np.diag(c_rm_is.flatten() / delta_t)\
        + np.dot(p_is_js, (p_js_is - wsr_js_is) * a_srf_js * h_c_js)\
        + np.diag((c_sh_frt_is * g_sh_frt_is / (c_sh_frt_is + g_sh_frt_is * delta_t)).flatten())

    # BRL, [i, i]
    brl_is_is = np.dot(p_is_js, wsb_js_is * h_c_js * a_srf_js) + np.diag(beta_is.flatten())

    # WSC, degree C, [j, n]
    wsc_js_ns = np.dot(ivs_ax_js_js, crx_js_ns)

    # WSR, [j, i]
    wsr_js_is = np.dot(ivs_ax_js_js, fia_js_is)

    # CRX, degree C, [j, n]
    crx_js_ns = phi_a0_js * q_sol_js_ns\
        + phi_t0_js / h_i_js * np.dot(k_ei_js_js, q_sol_js_ns)\
        + phi_t0_js * theta_dstrb_js_ns

    # FIA, [j, i]
    fia_js_is = phi_a0_js * h_c_js * p_js_is\
        + np.dot(k_ei_js_js, p_js_is) * phi_t0_js * h_c_js / h_i_js

    # AX^-1, [j, j]
    ivs_ax_js_js = np.linalg.inv(ax_js_js)

    # AX, [j, j]
    ax_js_js = np.diag(1.0 + (phi_a0_js * h_i_js).flatten())\
        - np.dot(p_js_is, f_mrt_is_js) * h_r_js * phi_a0_js\
        - np.dot(k_ei_js_js, np.dot(p_js_is, f_mrt_is_js)) * h_r_js * phi_t0_js / h_i_js

    # ステップnの境界jにおける外気側等価温度の外乱成分, ℃, [j, n]
    theta_dstrb_js_ns = theta_o_sol_js_ns * k_eo_js

    # ステップnの境界jにおける透過日射吸収熱量, W/m2, [j, n]
    # TODO: 日射の吸収割合を入力値にした方がよいのではないか？
    q_sol_js_ns = np.dot(p_js_is, q_trs_sol_is_ns / a_srf_abs_is)\
        * is_solar_abs_js * (1.0 - r_sol_fnt)

    # 室iにおける日射が吸収される境界の面積の合計, m2, [i, 1]
    a_srf_abs_is = np.dot(p_is_js, a_srf_js * is_solar_abs_js)

    # ステップnの室iにおける家具の吸収日射量, W, [i, n]
    q_sol_frnt_is_ns = q_trs_sol_is_ns * r_sol_fnt

    # 室内侵入日射のうち家具に吸収される割合
    # TODO: これは入力値にした方がよいのではないか？
    r_sol_fnt = 0.5

    # ステップnの室iにおける機械換気量（全般換気量+局所換気量）, m3/s, [i, n]
    v_mec_vent_is_ns = v_vent_ex_is[:, np.newaxis] + v_mec_vent_local_is_ns

    # 境界jの室内側表面総合熱伝達率, W/m2K, [j, 1]
    h_i_js = h_c_js + h_r_js

    # 平均放射温度計算時の各部位表面温度の重み, [i, j]
    f_mrt_is_js = shape_factor.get_f_mrt_is_js(a_srf_js=a_srf_js, h_r_js=h_r_js, p_is_js=p_is_js)

室 |i| の空気の熱容量 :math:`C_{rm,i}` は式(x)により表される。

.. math::
    :nowrap:

    \begin{align*}
        C_{rm,i} = V_{rm,i} \cdot \rho_{air} \cdot c_{air} \tag{x}
    \end{align*}

ここで、

:math:`C_{rm,i}`
    | 室 |i| の空気の熱容量, J / K
:math:`V_{rm,i}`
    | 室 |i| の容積, |m3|
:math:`\rho_{air}`
    | 空気の密度, kg / |m3|
:math:`c_{air}`
    | 空気の比熱, J / kg K

である。ここで、 :math:`\rho_{air}` は :math:`1.2` kg / |m3| 、 :math:`c_{air}` は :math:`1005.0` J / kg K とする。

========================================================================================================================
II. 根拠
========================================================================================================================

------------------------------------------------------------------------------------------------------------------------
1. 境界表面における熱収支
------------------------------------------------------------------------------------------------------------------------

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
1) 表面温度
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ステップ |n+1| における境界 |j| の表面温度 :math:`\theta_{s,j,n+1}` は式(b1)～(b3)により表される。

.. math::
    :nowrap:

    \begin{align*}
        \theta_{s,j,n+1}
        = \phi_{A0,j} \cdot q_{j,n+1} + \sum_{m=1}^{M}{\theta'_{S,A,j,m,n+1}}
        + \phi_{T0,j} \cdot \theta_{rear,j,n+1} + \sum_{m=1}^{M}{\theta'_{S,T,j,m,n+1}}
        \tag{b1}
    \end{align*}

.. math::
    :nowrap:

    \begin{align*}
        \theta'_{S,A,j,m,n+1} = q_{j,n} \cdot \phi_{A1,j,m} + r_{j,m} \cdot \theta'_{S,A,j,m,n}
        \tag{b2}
    \end{align*}

.. math::
    :nowrap:

    \begin{align*}
        \theta'_{S,T,j,m,n+1} = \theta_{rear,j,n} \cdot \phi_{T1,j,m} + r_{j,m} \cdot \theta'_{S,T,j,m,n}
        \tag{b3}
    \end{align*}

ここで、

:math:`\theta_{s,j,n}`
    | ステップ |n| における境界 |j| の表面温度, ℃
:math:`\phi_{A0,j}`
    | 境界 |j| の吸熱応答係数の初項, |m2| K / W
:math:`\phi_{T0,j}`
    | 境界 |j| の貫流応答係数の初項, -
:math:`q_{j,n}`
    | ステップ |n| における境界 |j| の表面熱流（壁体吸熱を正とする）, W / |m2|
:math:`\theta_{rear,j,n}`
    | ステップ |n| における境界 |j| の裏面温度, ℃
:math:`\theta'_{S,A,j,m,n}`
    | ステップ |n| における境界 |j| の項別公比法の指数項 |m| の吸熱応答の項別成分, ℃
:math:`\theta'_{S,T,j,m,n}`
    | ステップ |n| における境界 |j| の項別公比法の指数項 |m| の貫流応答の項別成分, ℃
:math:`\phi_{A1,j,m}`
    | 境界 |j| の項別公比法の指数項 |m| の吸熱応答係数, |m2| K / W
:math:`\phi_{T1,j,m}`
    | 境界 |j| の項別公比法の指数項 |m| の貫流応答係数, -
:math:`r_{j,m}`
    | 境界 |j| の項別公比法の指数項 |m| の公比, -

である。 :math:`M` は項別公比法の指数項の数である。

これらの式を境界 :math:`0` ～ :math:`J-1` でベクトル表記をすると、式(b4)～(b6)となる。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{\theta}_{s,n+1} = \pmb{\phi}_{A0} \cdot \pmb{q}_{n+1} + \sum_{m=1}^{M}{\pmb{\theta}'_{S,A,m,n+1}}
        + \pmb{\phi}_{T0} \cdot \pmb{\theta}_{rear,n+1} + \sum_{m=1}^{M}{\pmb{\theta}'_{S,T,m,n+1}}
        \tag{b4}
    \end{align*}

.. math::
    :nowrap:

    \begin{align*}
        \pmb{\theta}'_{S,A,m,n+1} = \pmb{\phi}_{A1,m} \cdot \pmb{q}_{n} + \pmb{r}_{m} \cdot \pmb{\theta}'_{S,A,m,n}
        \tag{b5}
    \end{align*}

.. math::
    :nowrap:

    \begin{align*}
        \pmb{\theta}'_{S,T,m,n+1}
        = \pmb{\phi}_{T1,m} \cdot \pmb{\theta}_{rear,n} + \pmb{r}_{m} \cdot \pmb{\theta}'_{S,T,m,n}
        \tag{b6}
    \end{align*}

ここで、

:math:`\pmb{\theta}_{s,n}`
    | :math:`\theta_{s,j,n}` を要素にもつ :math:`J \times 1` の縦行列, ℃
:math:`\pmb{\phi}_{A0}`
    | :math:`\phi_{A0,j}` を要素にもつ :math:`J \times J` の対角化行列, |m2| K / W
:math:`\pmb{\phi}_{T0}`
    | :math:`\phi_{T0,j}` を要素にもつ :math:`J \times J` の対角化行列, -
:math:`\pmb{q}_{n}`
    | :math:`q_{j,n}` を要素にもつ :math:`J \times 1` の縦行列, W / |m2|
:math:`\pmb{\theta}_{rear,n}`
    | :math:`\theta_{rear,j,n}` を要素にもつ :math:`J \times 1` の縦行列, ℃
:math:`\pmb{\theta}'_{S,A,m,n}`
    | :math:`\theta'_{S,A,j,m,n}` を要素にもつ :math:`J \times 1` の縦行列, ℃
:math:`\pmb{\theta}'_{S,T,m,n}`
    | :math:`\theta'_{S,T,j,m,n}` を要素にもつ :math:`J \times 1` の縦行列, ℃
:math:`\pmb{\phi}_{A1,m}`
    | :math:`\phi_{A1,j,m}` を要素にもつ :math:`J \times J` の対角化行列, |m2| K / W
:math:`\pmb{\phi}_{T1,m}`
    | :math:`\phi_{T1,j,m}` を要素にもつ :math:`J \times J` の対角化行列, -
:math:`\pmb{r}_{m}`
    | :math:`r_{j,m}` を要素にもつ :math:`J \times J` の対角化行列, -

である。

なお、境界の吸熱応答係数の初項 :math:`\pmb{\phi}_{A0}` など、室温や熱流にかける変数については、
本来であれば :math:`J \times 1` の1次元のベクトルであるが、
後のベクトル計算の記述性・操作性を考え、予め対角化した行列として表現している。
なお、室温や日射量等の状態量を表す変数は、対角化せずに、 :math:`J \times 1` の行列で表す。

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2) 表面熱流
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ステップ |n| における境界 |j| の表面熱流 :math:`q_{j,n}` は式(b7)により表される。

.. math::
    :nowrap:

    \begin{align*}
        q_{j,n} = h_{i,j} \cdot ( \theta_{EI,j,n} - \theta_{S,j,n} )
        \tag{b7}
    \end{align*}

ここで、

:math:`h_{i,j}`
    | 境界 |j| の室内側総合熱伝達率, W / |m2| K
:math:`\theta_{EI,j,n}`
    | ステップ |n| における境界 |j| の等価温度, ℃

である。

これらの式を境界 :math:`0` ～ :math:`J-1` でベクトル表記をすると、式(b8)となる。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{q}_{n} = \pmb{h}_{i} \cdot ( \pmb{\theta}_{EI,n} - \pmb{\theta}_{S,n} )
        \tag{b8}
    \end{align*}

ここで、

:math:`\pmb{h}_{i}`
    | :math:`h_{i,j}` を要素にもつ :math:`J \times J` の対角化行列, W / |m2| K
:math:`\pmb{\theta}_{EI,n}`
    | :math:`\theta_{EI,j,m}` を要素にもつ :math:`J \times 1` の縦行列, ℃

である。

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
3) 等価温度
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

境界の表面における熱流を対流・放射・日射熱取得・放射暖房からの熱取得に分けて記述すると次式となる。

.. math::
    :nowrap:

    \begin{align*}
        \begin{split}
            q_{j,n}
            &= h_{c,j} \cdot (\theta_{r,j,n} - \theta_{S,j,n})
            + h_{r,j} \cdot (MRT_{j,n} - \theta_{S,j,n}) \\
            &+ RS_{j,n}
            + \frac{ flr_{j,i} \cdot Lr_{i,n} \cdot (1 - \beta_i) }{A_j}
        \end{split}
        \tag{b9}
    \end{align*}

ここで、

:math:`h_{c,j}`
    | 境界 |j| の室内側対流熱伝達率, W / |m2| K
:math:`h_{r,j}`
    | 境界 |j| の室内側放射熱伝達率, W / |m2| K
:math:`\theta_{r,j,n}`
    | ステップ |n| における境界 |j| が接する室の空気温度, ℃
:math:`MRT_{j,n}`
    | ステップ |n| における境界 |j| の平均放射温度, ℃
:math:`RS_{j,n}`
    | ステップ |n| における境界 |j| の透過日射吸収熱量, W / |m2|
:math:`flr_{j,i}`
    | 室 |i| に設置された放射暖房の放熱量のうち放射成分に対する境界 |j| の室内側表面の吸収比率, -
:math:`Lr_{i,n}`
    | ステップ |n| における室 |i| に設置された放射暖房の放熱量, W
:math:`\beta_{i}`
    | 室 |i| に設置された放射暖房の対流成分比率, -
:math:`A_{j}`
    | 境界 |j| の面積, |m2|

である。この境界表面における熱流は式(b7)（再掲）のように表されるため、

.. math::
    :nowrap:

    \begin{align*}
        q_{j,n} = h_{i,j} \cdot ( \theta_{EI,j,n} - \theta_{S,j,n} )
        \tag{b7}
    \end{align*}

ステップ |n| における境界 |j| の等価温度 :math:`\theta_{EI,j,n}` は式(b10)のように表される。

.. math::
    :nowrap:

    \begin{align*}
        \theta_{EI,j,n}
        = \frac{h_{c,j}}{h_{i,j}} \cdot \theta_{r,j,n}
        + \frac{h_{r,j}}{h_{i,j}} \cdot MRT_{j,n}
        + \frac{RS_{j,n}}{h_{i,j}}
        + \frac{flr_{j,i} \cdot Lr_{i,n} \cdot (1 - \beta_i) }{A_j \cdot h_{i,j}}
        \tag{b10}
    \end{align*}

これらの式を境界 :math:`0` ～ :math:`J-1` でベクトル表記をすると、式(b11)となる。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{\theta}_{EI,n} = \pmb{h}_{i}^{-1} \cdot
        ( \pmb{h}_{c} \cdot \pmb{p} \cdot \pmb{\theta}_{r,n} + \pmb{h}_{r} \cdot \pmb{MRT}_{n}
        + \pmb{RS}_{n} + \pmb{A}^{-1} \cdot \pmb{flr} \cdot (\pmb{I} - \pmb{\beta}) \cdot \pmb{Lr}_{n} )
        \tag{b11}
    \end{align*}

ここで、

:math:`\pmb{h}_{c}`
    | :math:`h_{c,j}` を要素にもつ :math:`J \times J` の対角化行列, W / |m2| K
:math:`\pmb{h}_{r}`
    | :math:`h_{r,j}` を要素にもつ :math:`J \times J` の対角化行列, W / |m2| K
:math:`\pmb{p}`
    | :math:`p_{j,i}` を要素にもつ :math:`J \times I` の行列
:math:`\pmb{\theta}_{r,n}`
    | :math:`\theta'_{r,i}` を要素にもつ :math:`I \times 1` の縦行列, ℃
:math:`\pmb{MRT}_{n}`
    | :math:`MRT_{j}` を要素にもつ :math:`J \times 1` の縦行列, ℃
:math:`\pmb{RS}_{n}`
    | :math:`RS_{j}` を要素にもつ :math:`J \times 1` の縦行列, W / |m2|
:math:`\pmb{flr}`
    | :math:`flr_{j,i}` を要素にもつ :math:`J \times I` の行列, -
:math:`\pmb{Lr}_{n}`
    | :math:`Lr_{i}` を要素にもつ :math:`I \times 1` の縦行列, W
:math:`\pmb{\beta}`
    | :math:`\beta_{i}` を要素にもつ :math:`I \times I` の対角化行列, -
:math:`\pmb{A}`
    | :math:`A_{i}` を要素にもつ :math:`I \times I` の対角化行列, |m2|

である。
ここで、ステップ |n| における境界 |j| が接する室の空気温度は、

.. math::
    :nowrap:

    \begin{align*}
        \begin{pmatrix}
        \theta_{r,0,n} \\
        \vdots \\
        \theta_{r,J-1,n}
        \end{pmatrix} =
        \begin{pmatrix}
        p_{0,0} & \ldots & p_{0,I-1} \\
        \vdots & \ddots & \vdots \\
        p_{J-1,0} & \ldots & p_{J-1,I-1}
        \end{pmatrix} \cdot
        \begin{pmatrix}
        \theta_{r,0} \\
        \vdots \\
        \theta_{r,I-1}
        \end{pmatrix} =
        \pmb{p} \cdot \pmb{\theta}_r
    \end{align*}

の関係を用いて、 :math:`I \times 1` の要素を :math:`J \times 1` の要素に変換している。

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
4) 裏面温度
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

裏面温度とは、境界の種類によって、

- 外気温度の場合
- 外気温度と室内温度を按分する場合（温度差係数が1ではない場合）
- 隣室の温度の場合

が考えられるため、一般化して式(b12)のように定義する。

.. math::
    :nowrap:

    \begin{align*}
        \theta_{rear,j,n} =
        \begin{pmatrix}
        k'_{EI,j,0} & \ldots & k'_{EI,j,J-1}
        \end{pmatrix} \cdot
        \begin{pmatrix}
        \theta_{EI,0,n} \\
        \vdots \\
        \theta_{EI,J-1,n}
        \end{pmatrix} +
        k_{EO,j} \cdot \theta_{EO,n}
        \tag{b12}
    \end{align*}

ここで、

:math:`k'_{EI,j,j^*}`
    | 境界 |j| の裏面温度に境界　|j*| の等価温度が与える影響
:math:`k_{EO,j}`
    | 境界 |j| の裏面温度に屋外側等価温度が与える影響
:math:`\theta_{EO,n}`
    | ステップ |n| における屋外側等価温度, ℃

である。

例えば、外気温度の場合、
:math:`k'_{EI,j,0}` ～ :math:`k'_{EI,j,J-1}` は :math:`0.0`、 :math:`k_{EO,j}` は :math:`1.0` である。

外気温度と室内温度を按分する場合の例として例えば床下の場合は温度差係数 :math:`0.7` が採用されるが、
その場合の床下に面する境界の裏面（床下側）温度に等価温度として与える境界を |j*| とすると、
:math:`k'_{EI,j,j^*}` は :math:`0.3` 、 :math:`k'_{EO,j}` は :math:`0.7` である。

間仕切り等、裏面が室の場合、
:math:`k'_{EI,j,0}` ～ :math:`k'_{EI,j,J-1}` のどれかが :math:`1.0`, :math:`k_{EO,j}` は :math:`0.0` である。

これらの式を境界 :math:`0` ～ :math:`J-1` でベクトル表記をすると、次式となる。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{\theta}_{rear,n} = \pmb{k}'_{EI} \cdot \pmb{\theta}_{EI,n} + \pmb{k}_{EO} \cdot \theta_{EO,n}
        \tag{b13}
    \end{align*}

ここで、

:math:`\pmb{k}'_{EI,j,j^*}`
    | :math:`k'_{EI,j,j^*}` を要素にもつ :math:`J \times J` の行列
:math:`\pmb{k}_{EO}`
    | :math:`k_{EO,j}` を要素にもつ :math:`J \times 1` の縦行列

である。

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
5) 平均放射温度と放射熱伝達率
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ステップ |n| における境界 |j| の等価温度 :math:`\theta_{EI,j,n}` を求めるにあたり、放射のやりとりは、

.. math::
    :nowrap:

    \begin{align*}
        h_{r,j} \cdot MRT_{j,n}
    \end{align*}

で表されるが、ここで、 :math:`MRT_{j,n}` を室 |i| の微小球の温度で代表させると、平均放射温度 :math:`MRT` は室 |i| ごとに定められ、

.. math::
    :nowrap:

    \begin{align*}
        MRT_{i,n} = \sum_{j=0}^{J-1}{F_{mrt,i,j}} \cdot \theta_{S,j,n}
        \tag{b14}
    \end{align*}

となる。ここで、

:math:`F_{mrt,i,j}`
    | 境界 |j| の室 |i| の微小球に対する形態係数

である。放射熱伝達率についても微小球に対するものとして再定義される。この放射のやりとりをベクトル表記すると、

.. math::
    :nowrap:

    \begin{align*}
        \pmb{h}_r \cdot \pmb{p} \cdot \pmb{F}_{mrt} \cdot \pmb{\theta}_{S,n}
    \end{align*}

となる。ここで、

:math:`\pmb{F}_{mrt}`
    | :math:`F_{mrt,i,j}` を要素にもつ :math:`I \times J` の行列

である。
この関係を式(b11)に代入すると、

.. math::
    :nowrap:

    \begin{align*}
        \begin{split}
            \pmb{\theta}_{EI,n}
            &= \pmb{h}_{i}^{-1} \cdot
            ( \pmb{h}_{c} \cdot \pmb{p} \cdot \pmb{\theta}_{r,n}
            + \pmb{h}_{r} \cdot \pmb{p} \cdot \pmb{F}_{mrt} \cdot \pmb{\theta}_{S,n} \\
            &+ \pmb{RS}_{n}
            + \pmb{A}^{-1} \cdot \pmb{flr} \cdot (\pmb{I} - \pmb{\beta}) \cdot \pmb{Lr}_{n}
            )
        \end{split}
        \tag{b15}
    \end{align*}

となる。

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
6) 表面温度の関係式の整理
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

これまで整理した式、

.. math::
    :nowrap:

    \begin{align*}
        \pmb{\theta}_{s,n+1} = \pmb{\phi}_{A0} \cdot \pmb{q}_{n+1} + \sum_{m=1}^{M}{\pmb{\theta}'_{S,A,m,n+1}}
        + \pmb{\phi}_{T0} \cdot \pmb{\theta}_{rear,n+1} + \sum_{m=1}^{M}{\pmb{\theta}'_{S,T,m,n+1}}
        \tag{b4}
    \end{align*}

.. math::
    :nowrap:

    \begin{align*}
        \pmb{q}_{n} = \pmb{h}_{i} \cdot ( \pmb{\theta}_{EI,n} - \pmb{\theta}_{S,n} )
        \tag{b8}
    \end{align*}

.. math::
    :nowrap:

    \begin{align*}
        \pmb{\theta}_{rear,n} = \pmb{k}'_{EI} \cdot \pmb{\theta}_{EI,n} + \pmb{k}_{EO} \cdot \theta_{EO,n}
        \tag{b13}
    \end{align*}

.. math::
    :nowrap:

    \begin{align*}
        \begin{split}
            \pmb{\theta}_{EI,n}
            &= \pmb{h}_{i}^{-1} \cdot
            ( \pmb{h}_{c} \cdot \pmb{p} \cdot \pmb{\theta}_{r,n}
            + \pmb{h}_{r} \cdot \pmb{p} \cdot \pmb{F}_{mrt} \cdot \pmb{\theta}_{S,n} \\
            &+ \pmb{RS}_{n}
            + \pmb{A}^{-1} \cdot \pmb{flr} \cdot (\pmb{I} - \pmb{\beta}) \cdot \pmb{Lr}_{n}
            )
        \end{split}
        \tag{b15}
    \end{align*}

について、順次代入すると、

.. math::
    :nowrap:

    \begin{align*}
        \begin{split}
            \pmb{\theta}_{s,n+1}
            &= \pmb{\phi}_{A0} \cdot \pmb{q}_{n+1}
            + \sum_{m=1}^{M}{\pmb{\theta}'_{S,A,m,n+1}}
            + \pmb{\phi}_{T0} \cdot \pmb{\theta}_{rear,n+1}
            + \sum_{m=1}^{M}{\pmb{\theta}'_{S,T,m,n+1}} \\

            &= \pmb{\phi}_{A0} \cdot \pmb{h}_{i} \cdot ( \pmb{\theta}_{EI,n+1} - \pmb{\theta}_{S,n+1} ) \\
            &+ \pmb{\phi}_{T0} \cdot (\pmb{k'}_{EI} \cdot \pmb{\theta}_{EI,n+1} + \pmb{k}_{EO} \cdot \theta_{EO,n+1}) \\
            &+ \sum_{m=1}^{M}{\pmb{\theta}'_{S,A,m,n+1}} + \sum_{m=1}^{M}{\pmb{\theta}'_{S,T,m,n+1}} \\

            &= \pmb{\phi}_{A0} \cdot \pmb{h}_{i} \cdot \pmb{h}_{i}^{-1} \cdot (\pmb{h}_{c} \cdot \pmb{p} \cdot \pmb{\theta}_{r,n+1} + \pmb{h}_{r} \cdot \pmb{p} \cdot \pmb{F}_{mrt} \cdot \pmb{\theta}_{S,n+1} \\
            &+ \pmb{RS}_{n+1} + \pmb{A}^{-1} \cdot \pmb{flr} \cdot (\pmb{I} - \pmb{\beta}) \cdot \pmb{Lr}_{n+1}) \\
            &- \pmb{\phi}_{A0} \cdot \pmb{h}_{i} \cdot \pmb{\theta}_{S,n+1} \\
            &+ \pmb{\phi}_{T0} \cdot \pmb{k}'_{EI} \cdot \pmb{h}_{i}^{-1} \cdot (\pmb{h}_{c} \cdot \pmb{p} \cdot \pmb{\theta}_{r,n+1} + \pmb{h}_{r} \cdot \pmb{p} \cdot \pmb{F}_{mrt} \cdot \pmb{\theta}_{S,n+1} \\
            &+ \pmb{RS}_{n+1} + \pmb{A}^{-1} \cdot \pmb{flr} \cdot (\pmb{I} - \pmb{\beta}) \cdot \pmb{Lr}_{n+1}) \\
            &+ \pmb{\phi}_{T0} \cdot \pmb{k}_{EO} \cdot \theta_{EO,n+1} \\
            &+ \sum_{m=1}^{M}{\pmb{\theta}'_{S,A,m,n+1}} + \sum_{m=1}^{M}{\pmb{\theta}'_{S,T,m,n+1}} \\

            &= \pmb{\phi}_{A0} \cdot \pmb{h}_{c} \cdot \pmb{p} \cdot \pmb{\theta}_{r,n+1} \\
            &+ \pmb{\phi}_{A0} \cdot \pmb{h}_{r} \cdot \pmb{p} \cdot \pmb{F}_{mrt} \cdot \pmb{\theta}_{S,n+1} \\
            &+ \pmb{\phi}_{A0} \cdot \pmb{RS}_{n+1} \\
            &+ \pmb{\phi}_{A0} \cdot \pmb{A}^{-1} \cdot \pmb{flr} \cdot (\pmb{I} - \pmb{\beta}) \cdot \pmb{Lr}_{n+1} \\
            &- \pmb{\phi}_{A0} \cdot \pmb{h}_{i} \cdot \pmb{\theta}_{S,n+1} \\
            &+ \pmb{\phi}_{T0} \cdot \pmb{k}'_{EI} \cdot \pmb{h}_{i}^{-1} \cdot \pmb{h}_{c} \cdot \pmb{p} \cdot \pmb{\theta}_{r,n+1} \\
            &+ \pmb{\phi}_{T0} \cdot \pmb{k}'_{EI} \cdot \pmb{h}_{i}^{-1} \cdot \pmb{h}_{r} \cdot \pmb{p} \cdot \pmb{F}_{mrt} \cdot \pmb{\theta}_{S,n+1} \\
            &+ \pmb{\phi}_{T0} \cdot \pmb{k}'_{EI} \cdot \pmb{h}_{i}^{-1} \cdot \pmb{RS}_{n+1} \\
            &+ \pmb{\phi}_{T0} \cdot \pmb{k}'_{EI} \cdot \pmb{h}_{i}^{-1} \cdot \pmb{A}^{-1} \cdot \pmb{flr} \cdot (\pmb{I} - \pmb{\beta}) \cdot \pmb{Lr}_{n+1} \\
            &+ \pmb{\phi}_{T0} \cdot \pmb{k}_{EO} \cdot \theta_{EO,n+1} \\
            &+ \sum_{m=1}^{M}{\pmb{\theta}'_{S,A,m,n+1}} + \sum_{m=1}^{M}{\pmb{\theta}'_{S,T,m,n+1}} \\
        \end{split}
        \tag{b16}
    \end{align*}

となる。 :math:`\pmb{\theta}_{S,n+1}` に関係する項を左辺に移動させると、

.. math::
    :nowrap:

    \begin{align*}
        \begin{split}
            &\pmb{\theta}_{s,n+1} - \pmb{\phi}_{A0} \cdot \pmb{h}_{r} \cdot \pmb{p} \cdot \pmb{F}_{mrt} \cdot \pmb{\theta}_{S,n+1} \\
            &+ \pmb{\phi}_{A0} \cdot \pmb{h}_{i} \cdot \pmb{\theta}_{S,n+1}
            - \pmb{\phi}_{T0} \cdot \pmb{k}'_{EI} \cdot \pmb{h}_{i}^{-1} \cdot \pmb{h}_{r} \cdot \pmb{p} \cdot \pmb{F}_{mrt} \cdot \pmb{\theta}_{S,n+1}\\
            &= (\pmb{I} - \pmb{\phi}_{A0} \cdot \pmb{h}_{r} \cdot \pmb{p} \cdot \pmb{F}_{mrt}
            + \pmb{\phi}_{A0} \cdot \pmb{h}_{i} - \pmb{\phi}_{T0} \cdot \pmb{h}_{i}^{-1} \cdot \pmb{h}_{r} \cdot \pmb{k}'_{EI} \cdot \pmb{p} \cdot \pmb{F}_{mrt} ) \cdot \pmb{\theta}_{S,n+1} \\
            &= \pmb{\phi}_{A0} \cdot \pmb{h}_{c} \cdot \pmb{p} \cdot \pmb{\theta}_{r,n+1}
            + \pmb{\phi}_{T0} \cdot \pmb{k}'_{EI} \cdot \pmb{h}_{i}^{-1} \cdot \pmb{h}_{c} \cdot \pmb{p} \cdot \pmb{\theta}_{r,n+1} \\
            &+ \pmb{\phi}_{A0} \cdot \pmb{RS}_{n+1}
            + \pmb{\phi}_{T0} \cdot \pmb{k}'_{EI} \cdot \pmb{h}_{i}^{-1} \cdot \pmb{RS}_{n+1}
            + \pmb{\phi}_{T0} \cdot \pmb{k}_{EO} \cdot \theta_{EO,n+1} \\
            &+ \pmb{\phi}_{A0} \cdot \pmb{A}^{-1} \cdot \pmb{flr} \cdot (\pmb{I} - \pmb{\beta}) \cdot \pmb{Lr}_{n+1} \\
            &+ \pmb{\phi}_{T0} \cdot \pmb{k}'_{EI} \cdot \pmb{A}^{-1} \cdot \pmb{h}_{i}^{-1} \cdot (\pmb{I} - \pmb{\beta}) \cdot \pmb{flr} \cdot \pmb{Lr}_{n+1} \\
            &+ \sum_{m=1}^{M}{\pmb{\theta}'_{S,A,m,n+1}} + \sum_{m=1}^{M}{\pmb{\theta}'_{S,T,m,n+1}} \\
        \end{split}
        \tag{b17}
    \end{align*}

となる。

ここで、

.. math::
    :nowrap:

    \begin{align*}
        \pmb{AX}
        = \pmb{I}
        + \pmb{\phi}_{A0} \cdot \pmb{h}_{i}
        - \pmb{\phi}_{A0} \cdot \pmb{h}_{r} \cdot \pmb{p} \cdot \pmb{F}_{mrt}
        - \pmb{\phi}_{T0} \cdot \pmb{h}_{i}^{-1} \cdot \pmb{h}_{r} \cdot \pmb{k}'_{EI} \cdot \pmb{p} \cdot \pmb{F}_{mrt}
        \tag{b18}
    \end{align*}

.. math::
    :nowrap:

    \begin{align*}
        \pmb{FIA} = (\pmb{\phi}_{A0} \cdot \pmb{h}_{c}
        + \pmb{\phi}_{T0} \cdot \pmb{k}'_{EI} \cdot \pmb{h}_{i}^{-1} \cdot \pmb{h}_{c}) \cdot \pmb{p}
        \tag{b19}
    \end{align*}

.. math::
    :nowrap:

    \begin{align*}
        \pmb{CRX}_{n+1}
        = \pmb{\phi}_{A0} \cdot \pmb{RS}_{n+1}
        + \pmb{\phi}_{T0} \cdot \pmb{k}'_{EI} \cdot \pmb{h}_{i}^{-1} \cdot \pmb{RS}_{n+1}
        + \pmb{\phi}_{T0} \cdot \pmb{k}_{EO} \cdot \theta_{EO,n+1}
        \tag{b20}
    \end{align*}

.. math::
    :nowrap:

    \begin{align*}
        \pmb{FLB} = (
        \pmb{\phi}_{A0} \cdot \pmb{A}^{-1}
        + \pmb{\phi}_{T0} \cdot \pmb{k}'_{EI} \cdot \pmb{A}^{-1} \cdot \pmb{h}_{i}^{-1}
        ) \cdot (\pmb{I} - \pmb{\beta}) \cdot \pmb{flr}
        \tag{b21}
    \end{align*}

.. math::
    :nowrap:

    \begin{align*}
        \pmb{CVL}_{n+1} = \sum_{m=1}^{M}{\pmb{\theta}'_{S,A,m,n+1}} + \sum_{m=1}^{M}{\pmb{\theta}'_{S,T,m,n+1}}
        \tag{b22}
    \end{align*}

とおくと、式(b17)は次式のように表すことができる。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{AX} \cdot \pmb{\theta}_{S,n+1}
        = \pmb{FIA} \cdot \pmb{\theta}_{r,n+1} + \pmb{CRX}_{n+1} + \pmb{FLB} \cdot \pmb{LR}_{n+1} + \pmb{CVL}_{n+1}
        \tag{b23}
    \end{align*}

この式の各項に左から :math:`\pmb{AX}` の逆行列をかけて、次のように式変形する。

.. math::
    :nowrap:

    \begin{align*}
        \begin{split}
            \pmb{\theta}_{S,n+1}
            &= \pmb{AX}^{-1} \cdot (
            \pmb{FIA} \cdot \pmb{\theta}_{r,n+1} + \pmb{CRX}_{n+1}
            + \pmb{FLB} \cdot \pmb{LR}_{n+1} + \pmb{CVL}_{n+1} ) \\
            &= \pmb{WSR} \cdot \pmb{\theta}_{r,n+1}
            + \pmb{WSC}_{n+1}
            + \pmb{WSB} \cdot \pmb{LR}_{n+1}
            + \pmb{WSV}_{n+1}
        \end{split}
        \tag{b24}
    \end{align*}

ここで、

.. math::
    :nowrap:

    \begin{align*}
        \pmb{WSR} = \pmb{AX}^{-1} \cdot \pmb{FIA}
        \tag{b25}
    \end{align*}

.. math::
    :nowrap:

    \begin{align*}
        \pmb{WSC}_{n+1} = \pmb{AX}^{-1} \cdot \pmb{CRX}_{n+1}
        \tag{b26}
    \end{align*}

.. math::
    :nowrap:

    \begin{align*}
        \pmb{WSB} = \pmb{AX}^{-1} \cdot \pmb{FLB}
        \tag{b27}
    \end{align*}

.. math::
    :nowrap:

    \begin{align*}
        \pmb{WSV}_{n+1} = \pmb{AX}^{-1} \cdot \pmb{CVL}_{n+1}
        \tag{b28}
    \end{align*}

とした。

------------------------------------------------------------------------------------------------------------------------
2. 室の熱収支
------------------------------------------------------------------------------------------------------------------------

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
1) 室の熱収支
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

室の熱収支は次のように表される。

.. math::
    :nowrap:

    \begin{align*}
        \begin{split}
            C_{rm,i} \cdot \frac{d \theta_{r,i,n}}{d t}
            &= \sum_{j \in \pmb{J}_i}{h_{c,j} \cdot A_j \cdot ( \theta_{s,j,n} - \theta_{r,j,n} )} \\
            &+ C_a \cdot \rho_a \cdot V_{i,n} \cdot ( \theta_{o,n} - \theta_{r,i,n} ) \\
            &+ C_a \cdot \rho_a \cdot \sum_{i^*}^{I}{V_{nxt,i,i^*} \cdot \theta_{i^*}} \\
            &+ H_{i,n} \\
            &+ (L_{C,i,n} + \beta_i \cdot L_{r,i,n}) \\
            &+ G_{frt,i} \cdot ( \theta_{frt,i,n} - \theta_{r,i,n} ) \\
        \end{split}
        \tag{b29}
    \end{align*}

ここで、

:math:`C_{rm,i}`
    | 室 |i| の空気の熱容量, J / K
:math:`t`
    | 時刻, s
:math:`c_a`
    | 空気の比熱, J / kg K
:math:`\rho_a`
    | 空気の密度, kg / |m3|
:math:`V_{i,n}`
    | ステップ |n| における室 |i| の換気・すきま風・自然風の利用による外気の流入量, |m3| / s
:math:`V_{nxt,i,i^*}`
    | ステップ |n| における室 |i*| から室 |i| への室間の空気移動量, |m3| / s
:math:`H_{i,n}`
    | ステップ |n| における室 |i| の室内発熱, W
:math:`Lc_{i,n}`
    | ステップ |n| における室 |i| に設置された対流暖房の放熱量, W
:math:`G_{frt,i}`
    | 室 |i| における家具と空気間の熱コンダクタンス, W/K
:math:`\theta_{fun,i,n}`
    | ステップ |n| における室 |i| に設置された家具の温度, ℃

ここで、 |i| は流入先の室番号を表し、 |i*| は流出元の室番号を表す。

なお、変数 :math:`V_{nxt,i,i^*}` について、
例えば、 :math:`V_{nxt,2,0}` は室 :math:`2` から室 :math:`0` への空気流入量を表すとともに、
:math:`V_{nxt,0,0}` は室 :math:`0` から他室への空気流出量を表すこととする。
流入する空気の合計と流出する空気の合計は一致することから、

.. math::
    :nowrap:

        \begin{align*}
            V_{nxt,i,i} = - \sum_{i^*, i^* \ne i}{V_{nxt,i,i^*}}
        \end{align*}

が成り立つ。

式(b29)を室 :math:`0` ～ :math:`I−1` でベクトル表記をすると、式(b30)となる。

.. math::
    :nowrap:

    \begin{align*}
        \begin{split}
            \pmb{C}_{rm} \cdot \frac{d \pmb{\theta}_{r,n}}{d t}
            & = \pmb{p}^{T} \cdot \pmb{h}_c \cdot \pmb{A} \cdot (\pmb{\theta}_{S,n} - \pmb{p} \cdot \pmb{\theta}_{r,n}) \\
            & + c_a \cdot \rho_a \cdot \pmb{V}_n \cdot (\pmb{\theta}_{o,n} - \pmb{\theta}_{r,n})
            + c_a \cdot \rho_a \cdot \pmb{V}_{nxt,n} \cdot \pmb{\theta}_{r,n} \\
            & + \pmb{H}_n
            + (\pmb{Lc}_n + \pmb{\beta} \cdot \pmb{Lr}_n)
            + \pmb{G}_{frt} \cdot (\pmb{\theta}_{frt,n} - \pmb{\theta}_{r,n})
        \end{split}
        \tag{b30}
    \end{align*}

ここで、

:math:`\pmb{C}_{rm}`
    | :math:`C_{rm,i}` を要素にもつ :math:`I \times I` の対角化行列, J / K
:math:`\pmb{V_n}`
    | :math:`V_{i,n}` を要素にもつ :math:`I \times I` の対角化行列, |m3| / s
:math:`\pmb{V_{nxt,n}}`
    | :math:`V_{nxt,i,i^*}` を要素にもつ :math:`I \times I` の行列, |m3| / s
:math:`\pmb{H}_n`
    | :math:`H_{i,n}` を要素にもつ :math:`I \times 1` の縦行列, W
:math:`\pmb{Lc}_n`
    | :math:`Lc_{i,n}` を要素にもつ :math:`I \times 1` の縦行列, W
:math:`\pmb{G}_{frt}`
    | :math:`G_{frt,i}` を要素にもつ :math:`I \times I` の対角化行列, W/K
:math:`\pmb{\theta}_{fun,n}`
    | :math:`\theta_{fun,i,n}` を要素にもつ :math:`I \times 1` の縦行列, ℃

である。ここで、室 |i| が接する境界表面の熱流を仮に :math:`q_{s,bdr,j}` とし、それらの室 |i| における合計を :math:`q_{s,rm,i}` とすると、

.. math::
    :nowrap:

    \begin{align*}
        \pmb{q}_{s,rm} =
        \begin{pmatrix}
        q_{s,rm,0} \\
        \vdots \\
        q_{s,rm,I-1}
        \end{pmatrix} =
        \begin{pmatrix}
        p_{0,0} & \ldots & p_{0,J-1} \\
        \vdots & \ddots & \vdots \\
        p_{I-1,0} & \ldots & p_{I-1,J-1}
        \end{pmatrix} \cdot
        \begin{pmatrix}
        q_{s,bdr,0} \\
        \vdots \\
        q_{s,bdr,J-1}
        \end{pmatrix} =
        \pmb{p}^T \cdot \pmb{q}_{s,bdr}
    \end{align*}

の関係を用いて、 :math:`J \times 1` の要素を :math:`I \times 1` の要素に変換している。


両辺をステップ |n| から |n+1| まで積分すると左辺は、

.. math::
    :nowrap:

    \begin{align*}
        \left. \frac{d \pmb{\theta}_r}{dt} \right|_n
        = \frac{\pmb{\theta}_{r,n} - \pmb{\theta}_{r,n-1}}{\Delta t}
    \end{align*}

のようになり、右辺は　|n| から |n+1| までの平均値（本来であれば積算値であるが、
全体を :math:`\Delta n` で除しているので平均値）となるが、
平均値が計算できない温度の項についてはステップ |n+1| の瞬時値で代表させる（後退差分）こととする。
換気量・放熱量については |n| から |n+1| までの平均値として定義し、
瞬時値と区別するために以後の式展開では記号の上側にハットを付すこととする。

室の熱収支は式(b31)となる。

.. math::
    :nowrap:

    \begin{align*}
        \begin{split}
            &\pmb{C}_{rm} \frac{\pmb{\theta}_{r,n+1} - \pmb{\theta}_{r,n}}{\Delta t} \\
            & = \pmb{p}^{T} \cdot \pmb{h}_c \cdot \pmb{A} \cdot (\pmb{\theta}_{S,n+1} - \pmb{p} \cdot \pmb{\theta}_{r,n+1}) \\
            & + c_a \cdot \rho_a \cdot \hat{\pmb{V}}_n \cdot (\pmb{\theta}_{o,n+1} - \pmb{\theta}_{r,n+1})
            + c_a \cdot \rho_a \cdot \hat{\pmb{V}}_{nxt,n} \cdot \pmb{\theta}_{r,n+1} \\
            & + \hat{\pmb{H}}_n
            + ( \hat{\pmb{Lc}}_n + \pmb{\beta} \cdot \hat{\pmb{Lr}}_n )
            + \pmb{G}_{frt} \cdot (\pmb{\theta}_{frt,n+1} - \pmb{\theta}_{r,n+1})
        \end{split}
        \tag{b31}
    \end{align*}

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2) 室の家具と空間との熱収支
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

家具の熱収支は次式で表される。

.. math::
    :nowrap:

    \begin{align*}
        C_{frt,i} \cdot \frac{d \theta_{frt,i,n}}{d t}
        = G_{frt,i} \cdot (\theta_{r,i,n} - \theta_{frt,i,n}) + Q_{sol,frt,i,n}
        \tag{b32}
    \end{align*}

ここで、

:math:`C_{frt,i}`
    | 室 |i| に設置された家具の熱容量, J / K
:math:`Q_{sol,frt,i,n}`
    | ステップ |n| における室 |i| に設置された家具による透過日射吸収熱量, W

である。

式(b32)を室 :math:`0` ～ :math:`I−1` でベクトル表記をすると、式(b33)となる。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{C}_{frt} \cdot \frac{d \pmb{\theta}_{frt,n}}{d t}
        = \pmb{G}_{frt} \cdot (\pmb{\theta}_{r,n} - \pmb{\theta}_{frt,n}) + \pmb{Q}_{sol,frt,n}
        \tag{b33}
    \end{align*}

ここで、

:math:`\pmb{C}_{frt}`
    | :math:`C_{frt,i}` を要素にもつ :math:`I \times I` の対角化行列, J / K
:math:`\pmb{Q}_{sol,frt,n}`
    | :math:`Q_{sol,frt,i}` を要素にもつ :math:`I \times 1` の縦行列, W

である。

この式を差分で表すと次式となる。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{C}_{frt} \cdot \frac{\pmb{\theta}_{frt,n+1} - \pmb{\theta}_{frt,n}}{\Delta t}
        = \pmb{G}_{frt} \cdot (\pmb{\theta}_{r,n+1} - \pmb{\theta}_{frt,n+1})　+ \hat{\pmb{Q}}_{sol,frt,n}
        \tag{b34}
    \end{align*}

この式を :math:`\pmb{\theta}_{frt,n+1}` について解くと、

.. math::
    :nowrap:

    \begin{align*}
        \begin{split}
            &\pmb{\theta}_{frt,n+1} \\
            &= (\pmb{C}_{frt} + \Delta t \cdot \pmb{G}_{frt})^{-1}
            \cdot
            (
            \pmb{C}_{frt} \cdot \pmb{\theta}_{frt,n}
            + \Delta t \cdot \pmb{G}_{frt} \cdot \pmb{\theta}_{r,n+1}
            + \Delta t \cdot \hat{\pmb{Q}}_{sol,frt,n+1}
            )
        \end{split}
        \tag{b35}
    \end{align*}

となる。

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
3) 関係式の整理
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

式(b35)と表面温度に関する関係式(b24)を、式(b31)に代入すると、

.. math::
    :nowrap:

    \begin{align*}
        \begin{split}
            &\pmb{C}_{rm} \frac{\pmb{\theta}_{r,n+1} - \pmb{\theta}_{r,n}}{\Delta t} \\
            &= \pmb{p}^{T} \cdot \pmb{h}_c \cdot \pmb{A} \cdot
            (
            \pmb{WSR} \cdot \pmb{\theta}_{r,n+1}
            + \pmb{WSC}_{n+1}
            + \pmb{WSB} \cdot \pmb{Lr}_{n+1} \\
            &+ \pmb{WSV}_{n+1}
            - \pmb{p} \cdot \pmb{\theta}_{r,n+1}
            ) \\
            &+ c_a \cdot \rho_a \cdot \hat{\pmb{V}}_n \cdot (\pmb{\theta}_{o,n+1} - \pmb{\theta}_{r,n+1}) \\
            &+ c_a \cdot \rho_a \cdot \hat{\pmb{V}}_{nxt,n} \cdot \pmb{\theta}_{r,n+1} \\
            &+ \hat{\pmb{H}}_n + ( \hat{\pmb{Lc}}_n + \pmb{\beta} \cdot \hat{\pmb{Lr}}_n ) \\
            &+ \pmb{G}_{frt} \cdot ( (\pmb{C}_{frt} + \Delta t \cdot \pmb{G}_{frt})^{-1} \\
            &\cdot
            (
            \pmb{C}_{frt} \cdot \pmb{\theta}_{frt,n}
            + \Delta t \cdot \pmb{G}_{frt} \cdot \pmb{\theta}_{r,n+1}
            + \Delta t \cdot \hat{\pmb{Q}}_{sol,frt,n+1}
            ) - \pmb{\theta}_{r,n+1})
        \end{split}
        \tag{b36}
    \end{align*}

となる。

表面温度は応答係数方を用いて計算しているため、　:math:`\pmb{Lr}_{n+1}` はステップ |n+1| における瞬時値である。
一方で、設備による放熱量等の値はステップ |n| からステップ |n+1| までの積算値である。
ここでは、 :math:`\pmb{Lr}_{n+1}` を :math:`\hat{\pmb{Lr}}_{n}` で代表させ、
:math:`\pmb{\theta}_{n+1}` を左辺に移動させると、
右辺は、:math:`\hat{\pmb{Lr}}_n` 及び :math:`\hat{\pmb{Lc}}_n` でまとめると、

.. math::
    :nowrap:

    \begin{align*}
        \begin{split}
            & \pmb{C}_{rm} \cdot \frac{1}{\Delta t} \cdot \pmb{\theta}_{r,n+1} \\
            &+ \pmb{p}^{T} \cdot \pmb{h}_c \cdot \pmb{A} \cdot (\pmb{p} - \pmb{WSR}) \cdot \pmb{\theta}_{r,n+1} \\
            & + c_a \cdot \rho_a \cdot \hat{\pmb{V}}_n \cdot \pmb{\theta}_{r,n+1} \\
            & - c_a \cdot \rho_a \cdot \hat{\pmb{V}}_{nxt,n} \cdot \pmb{\theta}_{r,n+1} \\
            &+ \pmb{G}_{frt} \cdot (
            (\pmb{C}_{frt} + \Delta t \cdot \pmb{G}_{frt})^{-1}
            \cdot \pmb{C}_{frt} \cdot \pmb{\theta}_{r,n+1} \\
            & = \pmb{C}_{rm} \cdot \frac{1}{\Delta t} \cdot \pmb{\theta}_{r,n} \\
            & + \pmb{p}^{T} \cdot \pmb{h}_c \cdot \pmb{A} \cdot (\pmb{WSC}_{n+1} + \pmb{WSV}_{n+1}) \\
            & + c_a \cdot \rho_a \cdot \hat{\pmb{V}}_n \cdot \pmb{\theta}_{o,n+1} \\
            & + \hat{\pmb{H}}_n \\
            & + \pmb{G}_{frt} \cdot (\pmb{C}_{frt} + \Delta t \cdot \pmb{G}_{frt})^{-1}
            \cdot ( \pmb{C}_{frt} \cdot \pmb{\theta}_{frt,n} + \Delta t \cdot \hat{\pmb{Q}}_{sol,frt,n+1} ) \\
            & + \hat{\pmb{Lc}}_n \\
            & + \pmb{p}^{T} \cdot \pmb{h}_c \cdot \pmb{A} \cdot \pmb{WSB} \cdot \hat{\pmb{Lr}}_n + \pmb{\beta} \cdot \hat{\pmb{Lr}}_n \\
        \end{split}
        \tag{b37}
    \end{align*}

となる。

ここで、

.. math::
    :nowrap:

    \begin{align*}
        \begin{split}
            \pmb{BRM}_n
            & = \pmb{C}_{rm} \cdot \frac{1}{\Delta t}
            + \pmb{p}^{T} \cdot \pmb{h}_c \cdot \pmb{A} \cdot (\pmb{p} - \pmb{WSR}) \\
            & + c_a \cdot \rho_a \cdot \hat{\pmb{V}}_n
            - c_a \cdot \rho_a \cdot \hat{\pmb{V}}_{nxt,n}
            + \pmb{G}_{frt} \cdot (\pmb{C}_{frt} + \Delta t \cdot \pmb{G}_{frt})^{-1} \cdot \pmb{C}_{frt}
        \end{split}
        \tag{b38}
    \end{align*}

.. math::
    :nowrap:

    \begin{align*}
        \begin{split}
            \pmb{BRC}_n
            & = \pmb{C}_{rm} \cdot \frac{1}{\Delta t} \cdot \pmb{\theta}_{r,n}
            + \pmb{p}^{T} \cdot \pmb{h}_c \cdot \pmb{A} \cdot (\pmb{WSC}_{n+1} + \pmb{WSV}_{n+1}) \\
            & + c_a \cdot \rho_a \cdot \hat{\pmb{V}}_n \cdot \pmb{\theta}_{o,n+1} + \hat{\pmb{H}}_n \\
            & + \pmb{G}_{frt} \cdot (\pmb{C}_{frt} + \Delta t \cdot \pmb{G}_{frt})^{-1}
            \cdot ( \pmb{C}_{frt} \cdot \pmb{\theta}_{frt,n} + \Delta t \cdot \hat{\pmb{Q}}_{sol,frt,n+1} )
        \end{split}
        \tag{b39}
    \end{align*}

.. math::
    :nowrap:

    \begin{align*}
        \pmb{BRL} = \pmb{p}^{T} \cdot \pmb{h}_c \cdot \pmb{A} \cdot \pmb{WSB} + \pmb{\beta}
        \tag{b40}
    \end{align*}

とすると、式(b37)は、

.. math::
    :nowrap:

    \begin{align*}
        \pmb{BRM}_n \cdot \pmb{\theta}_{r,n+1}
        = \pmb{BRC}_n + \hat{\pmb{Lc}}_n + \pmb{BRL} \cdot \hat{\pmb{Lr}}_n
        \tag{b41}
    \end{align*}

のように表される。

------------------------------------------------------------------------------------------------------------------------
3. 作用温度と室温
------------------------------------------------------------------------------------------------------------------------

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
1) 作用温度
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

作用温度は次式で表される。

.. math::
    :nowrap:

    \begin{align*}
        \theta_{OT,i,n+1}
        = kc_{i,n+1} \cdot \theta_{r,i,n+1}　+ kr_{i,n+1} \cdot \theta_{MRT,hum,i,n+1}
        \tag{b42}
    \end{align*}

ここで、

:math:`\theta_{OT,i,n+1}`
    | ステップ |n+1| における室 |i| の作用温度, ℃
:math:`\theta_{MRT,hum,i,n+1}`
    | ステップ |n+1| における室 |i| に居る人体に対する平均放射温度, ℃
:math:`kc_{i,n+1}`
    | ステップ |n+1| における室 |i| の人体表面の対流熱伝達率が総合熱伝達率に占める割合
:math:`kr_{i,n+1}`
    | ステップ |n+1| における室 |i| の人体表面の放射熱伝達率が総合熱伝達率に占める割合

である。

式(b42)を室 :math:`0` ～ :math:`I−1` でベクトル表記をすると、式(b43)となる。


.. math::
    :nowrap:

    \begin{align*}
        \pmb{\theta}_{OT,n+1}
        = \pmb{kc}_{n+1} \cdot \pmb{\theta}_{r,n+1}　+ \pmb{kr}_{n+1} \cdot \pmb{\theta}_{MRT,hum,n+1}
        \tag{b43}
    \end{align*}

ここで、

:math:`\pmb{\theta}_{OT,n+1}`
    | :math:`\theta_{OT,i,n+1}` を要素にもつ :math:`I \times 1` の縦行列, ℃
:math:`\pmb{\theta}_{MRT,hum,n+1}`
    | :math:`\theta_{MRT,hum,i,n+1}` を要素にもつ :math:`I \times 1` の縦行列, ℃
:math:`\pmb{kc}_{n+1}`
    | :math:`kc_{i,n+1}` を要素にもつ :math:`I \times I` の対角化行列
:math:`\pmb{kr}_{n+1}`
    | :math:`kr_{i,n+1}` を要素にもつ :math:`I \times I` の対角化行列

である。

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2) 平均放射温度
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ステップ |n+1| における室 |i| に居る人体に対する平均放射温度は式(b44)で表される。

.. math::
    :nowrap:

    \begin{align*}
        \theta_{MRT,hum,i,n+1} = \sum_j{F_{mrt,hum,i,j} \cdot \theta_{S,j,n+1}}
        \tag{b44}
    \end{align*}

ここで、

:math:`F_{mrt,hum,i,j}`
    | 境界 |j| の表面温度が室 |i| に居る人体に与える放射の影響

である。

式(b44)を室 :math:`0` ～ :math:`I−1` でベクトル表記をすると、式(b45)となる。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{\theta}_{MRT,hum,n+1} = \pmb{F}_{mrt,hum} \cdot \pmb{\theta}_{S,n+1}
        \tag{b45}
    \end{align*}

ここで、

:math:`\pmb{F}_{mrt,hum}`
    | :math:`F_{mrt,hum,i,j}` を要素にもつ :math:`I \times J` の行列

である。

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
3) 室温と作用温度との関係式の整理
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

式(b43)に式(b45)及び式(b24)を代入する。

.. math::
    :nowrap:

    \begin{align*}
        \begin{split}
            \pmb{\theta}_{OT,n+1}
            & = \pmb{kc}_{n+1} \cdot \pmb{\theta}_{r,n+1} + \pmb{kr}_{n+1} \cdot \pmb{\theta}_{MRT,hum,n+1} \\
            & = \pmb{kc}_{n+1} \cdot \pmb{\theta}_{r,n+1} \\
            & + \pmb{kr}_{n+1} \cdot \pmb{F}_{mrt,hum} \\
            & \cdot ( \pmb{WSR} \cdot \pmb{\theta}_{r,n+1} + \pmb{WSC}_{n+1} + \pmb{WSB} \cdot \pmb{Lr}_{n+1} + \pmb{WSV}_{n+1} )
        \end{split}
        \tag{b46}
    \end{align*}

この式を :math:`\pmb{\theta}_{r,n+1}` について解くと、

.. math::
    :nowrap:

    \begin{align*}
        \begin{split}
            &( \pmb{kc}_{n+1} + \pmb{kr}_{n+1} \cdot \pmb{F}_{mrt,hum} \cdot \pmb{WSR} ) \cdot \pmb{\theta}_{r,n+1} \\
            & = \pmb{\theta}_{OT,n+1} \\
            &- \pmb{kr}_{n+1} \cdot \pmb{F}_{mrt,hum} \cdot \pmb{WSB} \cdot \hat{\pmb{Lr}}_{n} \\
            &- \pmb{kr}_{n+1} \cdot \pmb{F}_{mrt,hum} \cdot ( \pmb{WSC}_{n+1} + \pmb{WSV}_{n+1} )
        \end{split}
        \tag{b47}
    \end{align*}

となる。

なお、式(b37)における式変形と同様に、　:math:`\pmb{Lr}_{n+1}` を :math:`\hat{\pmb{Lr}}_{n}` で代表させている。


ここで、

.. math::
    :nowrap:

    \begin{align*}
        \pmb{XOT}_{n+1} = ( \pmb{kc}_{n+1} + \pmb{kr}_{n+1} \cdot \pmb{F}_{mrt,hum} \cdot \pmb{WSR} ) ^ {-1}
        \tag{b48}
    \end{align*}

.. math::
    :nowrap:

    \begin{align*}
        \pmb{XLR}_{n+1} = - \pmb{XOT}_{n+1} \cdot \pmb{kr}_{n+1} \cdot \pmb{F}_{mrt,hum} \cdot \pmb{WSB}
        \tag{b49}
    \end{align*}

.. math::
    :nowrap:

    \begin{align*}
        \pmb{XC}_{n+1}
        = - \pmb{XOT}_{n+1} \cdot \pmb{kr}_{n+1} \cdot \pmb{F}_{mrt,hum} \cdot (\pmb{WSC}_{n+1} + \pmb{WSV}_{n+1})
        \tag{b50}
    \end{align*}

とおくと、式(b47)は、

.. math::
    :nowrap:

    \begin{align*}
        \pmb{\theta}_{r,n+1}
        = \pmb{XOT}_{n+1} \cdot \pmb{\theta}_{OT,n+1} + \pmb{XLR}_{n+1} \cdot \hat{\pmb{Lr}}_{n} + \pmb{XC}_{n+1}
        \tag{b51}
    \end{align*}

となる。

------------------------------------------------------------------------------------------------------------------------
4. 作用温度と負荷
------------------------------------------------------------------------------------------------------------------------

式(b41)に式(b51)を代入すると次式となる。

.. math::
    :nowrap:

    \begin{align*}
        \begin{split}
            & \pmb{BRM}_n \cdot (
            \pmb{XOT}_{n+1} \cdot \pmb{\theta}_{OT,n+1} + \pmb{XLR}_{n+1} \cdot \hat{\pmb{Lr}}_{n} + \pmb{XC}_{n+1}
            ) \\
            & = \pmb{BRC}_n + \hat{\pmb{Lc}}_n + \pmb{BRL} \cdot \hat{\pmb{Lr}}_n
        \end{split}
        \tag{b52}
    \end{align*}

この式を、 :math:`\pmb{\theta}_{OT,n+1}` について解くと、

.. math::
    :nowrap:

    \begin{align*}
        \begin{split}
            \pmb{\theta}_{OT,n+1}
            & = (\pmb{BRM}_n \cdot \pmb{XOT}_{n+1})^{-1} \cdot \hat{\pmb{LC}}_n \\
            & + (\pmb{BRM}_n \cdot \pmb{XOT}_{n+1})^{-1}
            \cdot ( \pmb{BRL} - \pmb{BRM}_n \cdot \pmb{XLR}_{n+1} )
            \cdot \hat{\pmb{Lr}}_{n} \\
            & + (\pmb{BRM}_n \cdot \pmb{XOT}_{n+1})^{-1}
            \cdot ( \pmb{BRC}_n - \pmb{BRM}_n \cdot \pmb{XC}_{n+1} )
        \end{split}
        \tag{b53}
    \end{align*}

------------------------------------------------------------------------------------------------------------------------
5. 具体的な解法の手順
------------------------------------------------------------------------------------------------------------------------

これまで定式化した数式における記号は以下の3種類に分類される。

イ） 時刻によって変動しない値（形態係数など）

ロ） 時刻によって変動するが他の時刻の影響を受けない値（日射量など）

ハ） 時刻によって変動し、かつ、前の時刻の状態に影響を受ける値（室温など）

今回の計算のほとんどの部分は、ハ）の値を算出するために最初のステップ（ :math:`n = 0` ）から逐次ステップ数をインクリメントして計算していく部分である。

今後の説明において、イ）とロ）は既知のものとして扱い、特に断りの無い限り、その計算方法は別の箇所で記述する。
ステップ |n+1| の状態を計算するのに必要なステップ |n| の状態を表す最低限のパラメータは以下のとおりである。
なお、ここで引き渡す値については特にこれでないといけないという決まりはない。
（例えば :math:`\pmb{q}_n` の代わりに :math:`\pmb{\theta}_{EI,n+1}` を引き渡しても良い。）
計算の前後関係から、なるべく引き渡すパラメータの数が少なくなるように配慮して選定した。

また、以下に示すパラメータについては、暖冷房の運転状態やPMV等の何らかのステップ |n| における状態から決定される値とした。
なお、ここで挙げるパラメータの決め方については、記述を省略する。

:math:`\overline{\pmb{V}_n}`

:math:`\overline{\pmb{V}_{nxt,n}}`

:math:`\pmb{kr}_{n+1}`

:math:`\pmb{kc}_{n+1}`

関係図を以下に示す。
各パラメータの関係は非常に複雑なため、作用温度を求めるまでの計算と作用温度を求めてからの各種温度計算（ポスト処理）とに分けて記述する。

変数種類イ）については以下のフローにより計算する。

.. image:: ../_static/images/heat_load_balance_1.png
    :scale: 30%

図1　変数種類イ）の計算フロー

負荷または自然室温を計算するフローを以下に示す。

.. image:: ../_static/images/heat_load_balance_2.png
    :scale: 30%

図2　負荷または自然室温の計算フロー

負荷および自然室温を計算した後のフローを以下に示す。

.. image:: ../_static/images/heat_load_balance_3.png
    :scale: 30%

図3　負荷および自然室温計算後の計算フロー


