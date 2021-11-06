.. include:: definition.txt

************************************************************************************************************************
繰り返し計算（温度と顕熱）
************************************************************************************************************************

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


