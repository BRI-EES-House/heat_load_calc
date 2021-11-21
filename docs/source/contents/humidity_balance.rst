.. |i| replace:: :math:`i`
.. |j| replace:: :math:`j`
.. |k| replace:: :math:`k`
.. |m3| replace:: m\ :sup:`3` \
.. |n| replace:: :math:`n`
.. |n+1| replace:: :math:`n+1`

************************************************************************************************************************
繰り返し計算（湿度と潜熱）
************************************************************************************************************************

========================================================================================================================
I. 評価法
========================================================================================================================

------------------------------------------------------------------------------------------------------------------------
1. 次のステップの絶対湿度と潜熱負荷（絶対湿度を設定する場合（住宅・非住宅用））
------------------------------------------------------------------------------------------------------------------------

ステップ |n| からステップ |n+1| における室 |i| の
潜熱負荷（加湿を正・除湿を負とする） :math:`\hat{L}_{L,i,n}` は、式(1)により計算される。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{\hat{L}}_{L,n} = \pmb{\hat{L}}''_{a,n} \cdot \pmb{X}_{r,n+1} + \pmb{\hat{L}}''_{b,n} \tag{1}
    \end{align*}

ここで、

:math:`\pmb{\hat{L}}_{L,n}`
    | :math:`\hat{L}_{L,i,n}` を要素にもつ :math:`N_{room} \times 1` の縦行列, kg / s
:math:`\pmb{\hat{L}}''_{a,n}`
    | :math:`\hat{L}''_{a,i,j,n}` を要素にもつ :math:`N_{room} \times N_{room}` の正方行列, kg / s(kg/kg(DA))
:math:`\pmb{X}_{r,n+1}`
    | :math:`X_{r,i,n+1}` を要素にもつ :math:`N_{room} \times 1` の縦行列, kg / kg(DA)
:math:`\pmb{\hat{L}}''_{b,n}`
    | :math:`\hat{L}''_{b,i,n}` を要素にもつ :math:`N_{room} \times 1` の縦行列, kg / s

であり、

:math:`\hat{L}_{L,i,n}`
    | ステップ |n| から |n+1| における室 |i| の潜熱負荷（加湿を正・除湿を負とする）, kg / s
:math:`\hat{L}''_{a,i,j,n}`
    | ステップ |n+1| における室 |j| の絶対湿度がステップ |n| から |n+1| における室 |i| の潜熱負荷に与える影響を表す係数, kg / s(kg/kg(DA))
:math:`X_{r,i,n+1}`
    | ステップ |n+1| における室 |i| の絶対湿度, kg / kg(DA)
:math:`\hat{L}''_{b,i,n}`
    | ステップ |n| から |n+1| における室 |i| の潜熱負荷に与える影響を表す係数, kg / s

である。ここで、 :math:`N_{room}` は室の数を表す。

ステップ |n+1| における室 |i| の絶対湿度 :math:`X_{r,i,n+1}` は式(2a)で、
ステップ |n| から |n+1| における係数 :math:`\hat{L}''_{a,i,n}`　は式(2b)で、
ステップ |n| から |n+1| における係数 :math:`\hat{L}''_{b,i,n}`　は式(2c)で表される。

.. math::
    :nowrap:

    \begin{align*}
        X_{r,i,n+1} = \begin{cases}
            k_{i,n} & ( \hat{f}_{set,i,n} = 0, \text{絶対湿度を設定しない場合} ) \\
            X'_{r,set,i,n+1} & ( \hat{f}_{set,i,n} = 1, \text{絶対湿度を設定する場合} )
        \end{cases}
        \tag {2a}
    \end{align*}

.. math::
    :nowrap:

    \begin{align*}
        \hat{L}''_{a,i,j,n} = \hat{L}'_{a,i,j,n} \tag{2b}
    \end{align*}

.. math::
    :nowrap:

    \begin{align*}
        \hat{L}''_{b,i,n} = \begin{cases}
            \hat{L}'_{b,i,n} & ( \hat{f}_{set,i,n} = 0, \text{絶対湿度を設定しない場合} ) \\
		    k_{i,n} & ( \hat{f}_{set,i,n} = 1, \text{絶対湿度を設定する場合} )
        \end{cases}
        \tag{2c}
    \end{align*}

ここで、

:math:`X'_{r,set,i,n+1}`
    | ステップ |n+1| における室 |i| の設定絶対湿度（設定しない場合は0とする）, kg / kg(DA)
:math:`\hat{L}'_{a,i,j,n}`
    | ステップ |n+1| における室 |j| の絶対湿度がステップ |n| から |n+1| における室 |i| の潜熱負荷に与える影響を表す係数, kg / s(kg/kg(DA))
:math:`\hat{L}'_{b,i,n}`
    | ステップ |n| から |n+1| における室 |i| の潜熱負荷に与える影響を表す係数, kg / s
:math:`\hat{f}_{set,i,n}`
    | ステップ |n| から |n+1| における室 |i| の絶対湿度を設定するか否かを表す記号（設定する場合を1とし、設定しない場合を0とする。）

であり、
:math:`k_{i,n}` は、 :math:`\hat{f}_{set,i,n} = 0` の時（絶対湿度を設定しない時）は、
成り行きで求まるステップ |n+1| における室 |i| の絶対湿度を表し、
:math:`\hat{f}_{set,i,n+1} = 1` の時（絶対湿度を設定する時）は、
それに必要なステップ |n| から |n+1| における室 |i| の潜熱負荷を表す。
絶対湿度を設定するか否かに応じて単位が異なることに留意されたい。

係数 :math:`k_{i,n}` は式(3)で表される。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{k}_n　= {\pmb{F}''}_{h,wgt,n}^{-1} \cdot ( - \pmb{F}'_{h,wgt,n} \cdot \pmb{X}'_{r,set,n+1} + \pmb{F}_{h,cst,n} + \pmb{\hat{L}}'_{b,n} )　\tag{3}
    \end{align*}

ここで、

:math:`\pmb{k}_n`
    | :math:`k_{i,n}` を要素にもつ :math:`N_{room} \times 1` の縦行列, kg/kg(DA) または kg / s
:math:`{\pmb{F}''}_{h,wgt,n}`
    | :math:`{F''}_{h,wgt,i,j,n}` を要素にもつ :math:`N_{room} \times N_{room}` の正方行列, kg / s(kg/kg(DA)) または -
:math:`{\pmb{F}'}_{h,wgt,n}`
    | :math:`{F'}_{h,wgt,i,j,n}` を要素にもつ :math:`N_{room} \times N_{room}` の正方行列, kg / s(kg/kg(DA)) または -
:math:`\pmb{X}'_{r,set,n+1}`
    | :math:`X'_{r,set,i,n+1}` を要素にもつ :math:`N_{room} \times 1` の縦行列, kg / kg(DA)
:math:`\pmb{F}_{h,cst,n}`
    | :math:`F_{h,cst,i,n}` を要素にもつ :math:`N_{room} \times 1` の縦行列, kg / s
:math:`\pmb{\hat{L}}'_{b,n}`
    | :math:`\hat{L}'_{b,i,n}` を要素にもつ :math:`N_{room} \times 1` の縦行列, kg / s

である。

係数 :math:`F''_{h,wgt,i,j,n}` は式(4)で表される。

.. math::
    :nowrap:

    \begin{align*}
    	F''_{h,wgt,i,j,n} = \begin{cases}
            F'_{h,wgt,i,j,n} & ( \hat{f}_{set,j,n} = 0 ) \\
            - \delta_{ij} & ( \hat{f}_{set,j,n} = 1 )
        \end{cases}
    	\tag{4}
    \end{align*}

ここで、 :math:`\delta_{ij}` はクロネッカーのデルタである。

係数 :math:`F'_{h,wgt,i,j,n}` は式(5)で表される。

.. math::
    :nowrap:

    \begin{align*}
        F'_{h,wgt,i,j,n} = F_{h,wgt,i,j,n} - \hat{L}'_{a,i,j,n} \tag{5}
    \end{align*}

:math:`X'_{r,set,i,n+1}` はステップ |n+1| における室 |i| の設定絶対湿度（設定しない場合は0とする)を表すため、
絶対湿度を設定する場合は、後述するステップ |n+1| における室 |i| の設定絶対湿度 :math:`X_{r,set,i,n+1} とし、
絶対湿度を設定しない場合は0とする。

:math:`\hat{L}'_{a,i,j,n}` は、
室 |I| において絶対湿度を設定する場合は、

.. math::
    :nowrap:

    \begin{align*}
        {{\hat{L}'_{a,i,j,n}} \vert}_{i=I} = 0
    \end{align*}

絶対湿度を設定しない場合は、

.. math::
    :nowrap:

    \begin{align*}
        {{\hat{L}'_{a,i,j,n}} \vert}_{i \neq I} = \hat{L}_{a,i,j,n}
    \end{align*}

であり、
:math:`\hat{L}'_{b,i,n}` は、
室 |I| において絶対湿度を設定する場合は、

.. math::
    :nowrap:

    \begin{align*}
        \hat{L}'_{b,i,n} = 0
    \end{align*}

絶対湿度を設定しない場合は、

.. math::
    :nowrap:

    \begin{align*}
        \hat{L}'_{b,i,n} = \hat{L}_{b,i,n}
    \end{align*}

である。

ここで、

:math:`\hat{L}_{a,i,j,n}`
    | ステップ |n+1| における室 |j| の絶対湿度がステップ |n| から |n+1| における室 |i| の潜熱負荷に与える影響を表す係数, kg / s(kg/kg(DA))
:math:`\hat{L}_{b,i,n}`
    | ステップ |n| から |n+1| における室 |i| の潜熱負荷に与える影響を表す係数, kg / s

であり、後述する、ステップ |n+1| における室 |i| の加湿・除湿を行わない場合の絶対湿度 :math:`X_{r,ntr,i,n+1}` に応じて定まり、
その決定方法は、付録Aに示す。

------------------------------------------------------------------------------------------------------------------------
2. 次のステップの絶対湿度と潜熱負荷（絶対湿度を設定しない場合（住宅用））
------------------------------------------------------------------------------------------------------------------------

ステップ |n| からステップ |n+1| における室 |i| の
潜熱負荷（加湿を正・除湿を負とする） :math:`\hat{L}_{L,i,n}` は、式(6)により計算される。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{\hat{L}}_{L,n} = \pmb{\hat{L}}_{a,n} \cdot \pmb{X}_{r,n+1} + \pmb{\hat{L}}_{b,n} \tag{6}
    \end{align*}

ここで、

:math:`\pmb{\hat{L}}_{L,n}`
    | :math:`\hat{L}_{L,i,n}` を要素にもつ :math:`N_{room} \times 1` の縦行列, kg / s
:math:`\pmb{\hat{L}}_{a,n}`
    | :math:`\hat{L}_{a,i,j,n}` を要素にもつ :math:`N_{room} \times N_{room}` の正方行列, kg / s(kg/kg(DA))
:math:`\pmb{X}_{r,n+1}`
    | :math:`X_{r,i,n+1}` を要素にもつ :math:`N_{room} \times 1` の縦行列, kg / kg(DA)
:math:`\pmb{\hat{L}}_{b,n}`
    | :math:`\hat{L}_{b,i,n}` を要素にもつ :math:`N_{room} \times 1` の縦行列, kg / s

であり、

:math:`\hat{L}_{L,i,n}`
    | ステップ |n| から |n+1| における室 |i| の潜熱負荷（加湿を正・除湿を負とする）, kg / s
:math:`\hat{L}_{a,i,j,n}`
    | ステップ |n+1| における室 |j| の絶対湿度がステップ |n| から |n+1| における室 |i| の潜熱負荷に与える影響を表す係数, kg / s(kg/kg(DA))
:math:`X_{r,i,n+1}`
    | ステップ |n+1| における室 |i| の絶対湿度, kg / kg(DA)
:math:`\hat{L}_{b,i,n}`
    | ステップ |n| から |n+1| における室 |i| の潜熱負荷に与える影響を表す係数, kg / s

である。ここで、 :math:`N_{room}` は室の数を表す。


ステップ |n+1| における絶対湿度 :math:`\pmb{X}_{r,n+1}` は式(7)で表される。

.. math::
    :nowrap:

    \begin{align*}
        \pmb{X}_{r,n+1}　= {\pmb{F}'}_{h,wgt,n}^{-1} \cdot ( \pmb{F}_{h,cst,n} + \pmb{\hat{L}}_{b,n} )　\tag{7}
    \end{align*}

ここで、

:math:`{\pmb{F}'}_{h,wgt,n}`
    | :math:`{F'}_{h,wgt,i,j,n}` を要素にもつ :math:`N_{room} \times N_{room}` の正方行列, kg / s(kg/kg(DA)) または -
:math:`\pmb{F}_{h,cst,n}`
    | :math:`F_{h,cst,i,n}` を要素にもつ :math:`N_{room} \times 1` の縦行列, kg / s
:math:`\pmb{\hat{L}}_{b,n}`
    | :math:`\hat{L}_{b,n}` を要素にもつ :math:`N_{room} \times 1` の縦行列, kg / s

である。

係数 :math:`F'_{h,wgt,i,j,n}` は式(8)で表される。

.. math::
    :nowrap:

    \begin{align*}
        F'_{h,wgt,i,j,n} = F_{h,wgt,i,j,n} - \hat{L}_{a,i,j,n} \tag{8}
    \end{align*}

:math:`\hat{L}_{a,i,j,n}` 及び :math:`\pmb{\hat{L}}_{b,n}` は、
後述する、ステップ |n+1| における室 |i| の加湿・除湿を行わない場合の絶対湿度 :math:`X_{r,ntr,i,n+1}` に応じて定まり、
その決定方法は、付録Aに示す。

------------------------------------------------------------------------------------------------------------------------
3. 加湿・除湿を行わない場合の次のステップの絶対湿度
------------------------------------------------------------------------------------------------------------------------

加湿・除湿を行わない場合のステップ |n+1| における室 |i| の絶対湿度 :math:`X_{r,ntr,i,n+1}` は式(9)で表される。

.. math::
    :nowrap:

    \begin{align*}
    	\pmb{X}_{r,ntr,n+1}　= \pmb{F}_{h,wgt,n}^{-1} \cdot \pmb{F}_{h,cst,n}　\tag{9}
    \end{align*}

ここで、

:math:`\pmb{X}_{r,ntr,n+1}`
    | :math:`X_{r,ntr,i,n+1}` を要素にもつ :math:`I \times 1` の縦行列, kg / kg(DA)

であり、

:math:`X_{r,ntr,i,n+1}`
    | ステップ |n+1| における室 |i| の加湿・除湿を行わない場合の絶対湿度, kg / kg(DA)

である。

------------------------------------------------------------------------------------------------------------------------
4. 係数 :math:`F_{h,wgt}` ・係数 :math:`F_{h,cst}`
------------------------------------------------------------------------------------------------------------------------

ステップ |n| における係数 :math:`F_{h,wgt,i,j,n}` は式(10)で表される。

.. math::
    :nowrap:

    \begin{align*}
    	F_{h,wgt,i,j,n}
	    &= \left( \rho_a \cdot \left( \frac{ V_{room,i} }{ \Delta t } + \hat{V}_{out,vent,i,n} \right) + \frac{ G_{lh,frt,i} \cdot C_{lh,frt,i} }{ C_{lh,frt,i} + \Delta t \cdot G_{lh,frt,i} } \right) \cdot \delta_{ij} \\
    	&- \rho_a \cdot \left( \hat{V}_{int,vent,i,j,n} - \delta_{ij} \cdot \sum_{k=0}^{N_{room}-1}{\hat{V}_{int,vent,i,k,n}} \right)
    	\tag{10}
    \end{align*}

ここで、

:math:`\rho_a`
    | 空気の密度, kg / |m3| 
:math:`V_{room,i}`
    | 室 |i| の容積, |m3| 
:math:`\Delta t`
    | 1ステップの時間間隔, s 
:math:`\hat{V}_{out,vent,i,n}`
    | ステップ |n| から |n+1| における室 |i| の外気との換気量, |m3| / s
:math:`G_{lh,frt,i}`
    | 室 |i| の備品等と空気間の湿気コンダクタンス, kg / (s kg/kg(DA))
:math:`C_{lh,frt,i}`
    | 室 |i| の備品等の湿気容量, kg / (kg/kg(DA))
:math:`\hat{V}_{int,vent,i,j,n}`
    | 室 |j| から室 |i| への室間の機械換気量, |m3| / s
:math:`\hat{V}_{int,vent,i,k,n}`
    | 室 |k| から室 |i| への室間の機械換気量, |m3| / s

である。

ステップ |n| における室の湿度に関する係数 :math:`F_{h,cst,i,n}` は式(11)で表される。

.. math::
    :nowrap:

    \begin{align*}
    	F_{h,cst,i,n}
        &= \rho_a \cdot \frac{ V_{room,i} }{ \Delta t } \cdot X_{r,i,n}
    	+ \rho_a \cdot \hat{V}_{out,vent,i,n} \cdot X_{o,n+1} \\
	    &+ \frac{G_{lh,frt,i} \cdot C_{lh,frt,i} }{ C_{lh,frt,i} + \Delta t \cdot G_{lh,frt,i} } \cdot X_{frt,i,n}
    	+ \hat{X}_{gen,i,n} + \hat{X}_{hum,i,n}
        \tag{11}
    \end{align*}

ここで、

:math:`X_{o,n}`
    | ステップ |n| における外気絶対湿度, kg/kg(DA)
:math:`X_{frt,i,n}`
    | ステップ |n| における室 |i| の備品等の絶対湿度, kg/kg(DA)
:math:`\hat{X}_{gen,i,n}`
    | ステップ |n| における室 |i| の人体発湿を除く内部発湿, kg/s
:math:`\hat{X}_{hum,i,n}`
    | ステップ |n| における室 |i| の人体発湿, kg/s

である。

------------------------------------------------------------------------------------------------------------------------
付録A 係数 :math:`\hat{L}_a` ・係数 :math:`\hat{L}_b`
------------------------------------------------------------------------------------------------------------------------

係数 :math:`\hat{L}_{a,n}` 及び :math:`\hat{L}_{b,n}` の定め方について、設備の種類ごとに記述する。

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
A.1. 除湿・加湿を行わない場合
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ステップ |n| から |n+1| における室 |i| において除湿・加湿を行わない場合は以下のように定める。

.. math::
    :nowrap:

    \begin{align*}
        \hat{L}_{a,i,j,n} = 0 \tag{A.1a}
    \end{align*}

.. math::
    :nowrap:

    \begin{align*}
        \hat{L}_{b,i,n} = 0 \tag{A.1b}
    \end{align*}

ここで、 :math:`j = 0 \ldots N_{room} - 1` である。


^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
A.2. 一定量の除湿・加湿を行う場合
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ステップ |n| から |n+1| における室 |i| において一定量の除湿・加湿を行う場合は以下のように定める。

.. math::
    :nowrap:

    \begin{align*}
        \hat{L}_{a,i,j,n} = 0 \tag{A.2a}
    \end{align*}

.. math::
    :nowrap:

    \begin{align*}
        \hat{L}_{b,i,n} = \hat{q}_{X,i,n} \tag{A.2b}
    \end{align*}

ここで、

:math:`\hat{q}_{X,i,n}`
    | ステップ |n| から |n+1| における室 |i| の加湿・除湿量（加湿を正・除湿を負とする）, kg / s

である。
また、 :math:`j = 0 \ldots N_{room} - 1` である。

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
A.3.　絶対湿度に応じて一定量の除湿を行う場合（ルームエアコンディショナー）
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ルームエアコンディショナーを設置する室の集合を :math:`\pmb{k}` とする。
ステップ |n| から |n+1| における室 |i| において、
ステップ |n+1| における室 |i| の絶対湿度に応じて一定量の除湿を行う場合は以下のように定める。

.. math::
    :nowrap:

    \begin{align*}
        \left. \hat{L}_{a,i,j,n} \right|_{i \in \pmb{k}} = \begin{cases}
            - \hat{V}_{rac,i,n} \cdot \rho_a \cdot ( 1 - BF_{rac,i} ) \cdot \delta_{ij} & \begin{pmatrix} X_{r,ntr,i,n+1} > X_{rac,ex-srf,i,n+1} \\ \text{and} \\ \hat{q}_{s,i,n} > 0 \end{pmatrix} \\
            0 & \left( \text{その他の場合} \right)
        \end{cases}
        \tag{A.3a}
    \end{align*}

.. math::
    :nowrap:

    \begin{align*}
        \left. \hat{L}_{b,i,n} \right|_{i \in \pmb{k}} = \begin{cases}
            \hat{V}_{rac,i,n} \cdot \rho_a \cdot ( 1 - BF_{rac,i} ) \cdot X_{rac,ex-srf,i,n+1} & \begin{pmatrix} X_{r,ntr,i,n+1} > X_{rac,ex-srf,i,n+1} \\ \text{and} \\ \hat{q}_{s,i,n} > 0 \end{pmatrix} \\
            0 & \left( \text{その他の場合} \right)
        \end{cases}
        \tag{A.3b}
    \end{align*}

ここで、

:math:`\hat{V}_{rac,i,n}`
    | ステップ |n| から |n+1| における室 |i| に設置されたルームエアコンディショナーの吹き出し風量, |m3| / s
:math:`\rho_a`
    空気の密度, kg / |m3| 
:math:`BF_{rac,i}`
    室 |i| に設置されたルームエアコンディショナーの室内機の熱交換器のバイパスファクター, -
:math:`X_{rac,ex-srf,i,n+1}`
    ステップ |n+1| における室 |i| に設置されたルームエアコンディショナーの室内機の熱交換器表面絶対湿度, kg/kg(DA)

である。

ステップ |n+1| における室 |i| に設置されたルームエアコンディショナーの室内機の熱交換器表面絶対湿度 :math:`X_{rac,ex-srf,i,n+1}` は式(A.4)で表される。

.. math::
    :nowrap:

    \begin{align*}
        X_{rac,ex-srf,i,n+1} = f_x \left( f_{p,vs} \left( \theta_{rac,ex-srf,i,n+1} \right) \right) \tag{A.4}
    \end{align*}

:math:`\theta_{rac,ex-srf,i,n+1}`
    | ステップ :math:`n+1` における室 :math:`i` に設置されたルームエアコンディショナーの室内機の熱交換器表面温度, ℃

また、関数 :math:`f_x` は、飽和水蒸気圧を飽和絶対湿度に変換する関数、関数 :math:`f_{p,vs}` は温度を飽和水蒸気圧に変換する関数である。

ステップ |n+1| における室 |i| に設置されたルームエアコンディショナーの室内機の熱交換器表面温度　:math:`\theta_{rac,ex-srf,i,n+1}` は式(A.5)で表される。

.. math::
    :nowrap:

    \begin{align*}
        \theta_{rac,ex-srf,i,n+1} = \theta_{r,i,n+1} - \frac{ \hat{q}_{s,i,n} }{ c_a \cdot \rho_a \cdot \hat{V}_{rac,i,n} \cdot (1 - BF_{rac,i}) } \tag{A.5}
    \end{align*}

ここで、

:math:`\theta_{r,i,n+1}`
    | ステップ |n+1| における室 |i| の温度, ℃
:math:`\hat{q}_{s,i,n}`
    | ステップ |n| から |n+1| における室 |i| の顕熱負荷, W
:math:`c_a`
    | 空気の比熱, J / kg K

である。

室 |i| に設置されたルームエアコンディショナーの室内機の熱交換器のバイパスファクター :math:`BF_{rac,i}` は 0.2 とする。

ステップ |n| から |n+1| における室 |i| に設置されたルームエアコンディショナーの吹き出し風量 :math:`\hat{V}_{rac,i,n}` は式(A.6)により表される。
ただし、計算された :math:`\hat{V}_{rac,i,n}` が :math:`V_{rac,min,i}` を下回る場合は :math:`V_{rac,min,i}` に等しいとし、
:math:`V_{rac,max,i}` を上回る場合は :math:`V_{rac,max,i}` に等しいとする。

.. math::
    :nowrap:

    \begin{align*}
        \hat{V}_{rac,i,n}
        = V_{rac,min,i} \cdot \frac{ q_{rac,max,i} - q_{s,i,n} }{ q_{rac,max,i} - q_{rac,min,i} }
        + V_{rac,max,i} \cdot \frac{ q_{rac,min,i} - q_{s,i,n} }{ q_{rac,min,i} - q_{rac,max,i} }
        \tag{A.6}
    \end{align*}

ここで、

:math:`V_{rac,min,i}`
    | 室 |i| に設置されたルームエアコンディショナーの最小能力時における風量, |m3| / s
:math:`V_{rac,max,i}`
    | 室 |i| に設置されたルームエアコンディショナーの最大能力時における風量, |m3| / s
:math:`q_{rac,min,i}`
    | 室 |i| に設置されたルームエアコンディショナーの最小能力, W
:math:`q_{rac,max,i}`
    | 室 |i| に設置されたルームエアコンディショナーの最大能力, W

である。

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
A.3.　絶対湿度に応じて一定量の除湿を行う場合（ダクト式セントラル空調）
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. math::
    :nowrap:

    \begin{align*}
        \hat{L}_{a,i,j,n} = - \hat{V}_{RAC,i,n} \cdot \rho_a \cdot ( 1 - BF_{RAC,i} ) \tag{A.7a}
    \end{align*}

.. math::
    :nowrap:

    \begin{align*}
    	\hat{L}_{b,i,n} = \hat{V}_{RAC,i,n} \cdot \rho_a \cdot ( 1 - BF_{RAC,i} ) \cdot X_{RAC,ex-srf,i} \tag{A.7b}
    \end{align*}

ここで、

:math:`\hat{V}_{RAC,i,n}`
    | ステップ |n| から |n+1| における室 |i| に設置されたルームエアコンディショナーの吹き出し風量, |m3| / s
:math:`\rho_a`
    | 空気の密度, kg / |m3| 
:math:`BF_{RAC,i}`
    | 室 |i| に設置されたルームエアコンディショナーの室内機の熱交換器のバイパスファクター, -
:math:`X_{RAC,ex-srf,i}`
    室 |i| に設置されたルームエアコンディショナーの室内機の熱交換器表面の絶対湿度, kg/kg(DA)

である。


========================================================================================================================
II. 根拠
========================================================================================================================

------------------------------------------------------------------------------------------------------------------------
１） 室全体の水分収支
------------------------------------------------------------------------------------------------------------------------

室 |i| の空気の水分収支は式(b1)で表される。

.. math::
    :nowrap:

    \begin{align*}
        \rho_a \cdot V_{room,i} \cdot \frac{dX_{r,i}}{dt}
        &= \rho_a \cdot V_{out,vent,i} \cdot ( X_o - X_{r,i} ) + G_{lh,frt,i} \cdot ( X_{frt,i} - X_{r,i} ) \\
        &+ \rho_a \cdot \sum_{j=0}^{J-1}{V_{int,vent,i,j} \cdot (X_{r,j} - X_{r,i})} + X_{gen,i} + X_{hum,i} + L_{L,i}
        \tag{b1}
    \end{align*}

ここで、

:math:`\rho_a`
    | 空気の密度, kg / |m3| 
:math:`V_{room,i}`
    | 室 |i| の容積, |m3| 
:math:`X_{r,i}`
    | 室 |i| の絶対湿度, kg / kg(DA)
:math:`X_{r,j}`
    | 室 |j| の絶対湿度, kg / kg(DA)
:math:`t`
    | 時間, s
:math:`V_{out,vent,i}`
    | 室 |i| の外気との換気量, |m3| /s
:math:`X_o`
    | 外気絶対湿度, kg/kg(DA)
:math:`G_{lh,frt,i}`
    | 室 |i| の備品等と空気間の湿気コンダクタンス, kg / (s kg/kg(DA))
:math:`X_{frt,i}`
    | 室 |i| の備品等の絶対湿度, kg / kg(DA)
:math:`V_{int,vent,i,j}`
    | 室 |j| から室 |i| への機械換気量, |m3| / s
:math:`X_{gen,i}`
    | 室 |i| の人体発湿を除く内部発湿, kg / s
:math:`X_{hum,i}`
    | 室 |i| の人体発湿, kg / s
:math:`L_{L,i}`
    | 室 |i| の潜熱負荷（加湿を正・除湿を負とする）, kg / s

である。

空調による除湿・加湿の方法として以下のパターンを想定する。

- 除湿・加湿を行わない場合
- （加湿器の使用など）固定値で除湿・加湿を行う場合
- 目標絶対湿度を満たすように除湿・加湿を行う場合（従来の負荷計算方法）
- 室内の絶対湿度に応じて除湿量が定まる場合（放射パネルやエアコンなど除湿量を完全には制御しない方式）

これらを踏まえて、一般的に室 |i| の潜熱負荷 :math:`L_{L,i}` を以下の式で表す。

.. math::
    :nowrap:

    \begin{align*}
        L_{L,i} = L_{a,i} \cdot X_{r,i} + L_{b,i} \tag{b2}
    \end{align*}

除湿・加湿を行わない場合、 :math:`L_{a,i} = 0` 及び :math:`L_{b,i} = 0` とすればよい。

ある一定値で除加湿を行う場合、 :math:`L_{a,i} = 0` とし、与えたい除湿・加湿量を  :math:`L_{b,i}`  に与えれば良い。

目標絶対湿度を満たすように除湿・加湿を行う場合、 :math:`L_{a,i} = 0` とし、 :math:`X_{r,i}` を目標絶対湿度としたうえで、
:math:`L_{b,i}` を未知数として除湿・加湿量を求めれば良い。

室内の絶対湿度に応じて除湿を行う方法の場合、室内の絶対湿度と除湿を行う表面の飽和絶対湿度との差によって除湿量が決定される場合が多い。
その場合、以下のような式で表される。

.. math::
    :nowrap:

    \begin{align*}
        L_{L,i} = \begin{cases}
            -k_{l,i} \cdot (X_{r,i} - X_{srf,ex,i}) & ( X_{r,i} \gt X_{srf,ex,i} ) \\
            0 & ( X_{srf,ex,i} \le X_{r,i} )
        \end{cases}
        \tag{b3}
    \end{align*}

ここで、

:math:`X_{srf,ex,i}`
    | 室 |i| に設置された設備の熱交換器表面の飽和絶対湿度, kg/kg(DA)
:math:`k_{l,i}`
    | 室 |i| に設置された設備の熱交換器表面の湿気コンダクタンス, kg/(s kg/kg(DA))

である。このように、絶対湿度と熱交換器表面における飽和絶対湿度との大小関係によって除湿の有無が決定されるため、
数値計算においては、一旦、除湿を行わない場合の絶対湿度 :math:`X_{r,ndh}` を求め、
その湿度と熱交換器表面における飽和絶対湿度 :math:`X_{srf,ex,i}` の大小を比較して除湿の有無を決定することになる。
なお、 :math:`L_{a,i}` 及び :math:`L_{b,i}` の決定方法は後述する。

備品等の水分収支式は室空気との物質移動だけを考慮すればよいため、次式で表すことができる。

.. math::
    :nowrap:

    \begin{align*}
    	C_{lh,frt,i} \cdot \frac{dX_{frt,i}}{dt} = G_{lh,frt,i} \cdot ( X_{r,i} - X_{frt,i} ) \tag{b4}
    \end{align*}

ここで、

:math:`C_{lh,frt,i}`
    | 室 |i| の備品等の湿気容量, kg/(kg/kg(DA))

である。

式(b2)を式(b1)に代入して後退差分で離散化すると次式となる。

.. math::
    :nowrap:

    \begin{align*}
    	\rho_a \cdot V_{room,i} \cdot \frac{ X_{r,i,n+1} - X_{r,i,n} }{ \Delta t }
	    &= \rho_a \cdot \hat{V}_{out,vent,i,n} \cdot ( X_{o,n+1} - X_{r,i,n+1} ) \\
    	&+ G_{lh,frt,i} \cdot ( X_{frt,i,n+1} - X_{r,i,n+1} ) \\
	    &+ \rho_a \cdot \sum_{j=0}^{J-1}{\hat{V}_{int,vent,i,j,n} \cdot ( X_{r,j,n+1} - X_{r,i,n+1} ) } \\
    	&+ \hat{X}_{gen,i,n} + \hat{X}_{hum,i,n} + \hat{L}_{a,i,n} \cdot X_{r,i,n+1} + \hat{L}_{b,i,n}
    	\tag{b5}
    \end{align*}

ここで、

:math:`\Delta t`
    | 1ステップの時間間隔, s
:math:`X_{r,i,n}`
    | ステップ |n| における室 |i| の絶対湿度, kg/kg(DA)
:math:`X_{r,j,n}`
    | ステップ |n| における |j| の絶対湿度, kg/kg(DA)
:math:`\hat{V}_{out,vent,i,n}`
    | ステップ |n| からステップ |n+1| における室 |i| の外気との換気量, |m3| /s
:math:`X_{o,n}`
    | ステップ |n| における外気絶対湿度, kg/kg(DA)
:math:`X_{frt,i,n}`
    | ステップ |n| における室 |i| の備品等の絶対湿度, kg/kg(DA)
:math:`\hat{V}_{int,vent,i,j,n}`
    | ステップ |n| からステップ |n+1| における室 |j| から室 |i| への機械換気量, |m3| /s
:math:`\hat{X}_{gen,i,n}`
    | ステップ |n| における室 |i| の人体発湿を除く内部発湿, kg/s
:math:`\hat{X}_{hum,i,n}`
    | ステップ |n| における室 |i| の人体発湿, kg/s
:math:`\hat{L}_{a,i,n}`
    | ステップ |n| からステップ |n+1| における潜熱負荷に関する係数, kg/(s kg/kg(DA))
:math:`\hat{L}_{b,i,n}`
    | ステップ |n| からステップ |n+1| における潜熱負荷に関する係数, kg/s

である。
記号の上につく :math: `\hat{ }` （ハット）は、ステップ |n| から |n+1| の期間における積算値または平均値を表す。

式(b4)も同様に後退差分で離散化すると次式となる。

.. math::
    :nowrap:

    \begin{align*}
    	C_{lh,frt,i} \cdot \frac{ X_{frt,i,n+1} - X_{frt,i,n} }{ \Delta t } = G_{lh,frt,i} \cdot ( X_{r,i,n+1} - X_{frt,i,n+1} ) \tag{b6}
    \end{align*}

式(b6)をステップ |n+1| における室 |i| の備品等の絶対湿度 :math:`X_{frt,i,n+1}` について解くと、

.. math::
    :nowrap:

    \begin{align*}
    	X_{frt,i,n+1} = \frac{ C_{lh,frt,i} \cdot X_{frt,i,n} + \Delta t \cdot G_{lh,frt,i} \cdot X_{r,i,n+1} }{ C_{lh,frt,i} + \Delta t \cdot G_{lh,frt,i} } \tag{b7}
    \end{align*}

となる。これを式(b5)に代入すると、

.. math::
    :nowrap:

    \begin{align*}
    	\rho_a \cdot V_{room,i} \cdot \frac{ X_{r,i,n+1} - X_{r,i,n} }{ \Delta t }
	    &= \rho_a \cdot \hat{V}_{out,vent,i,n} \cdot ( X_{o,n+1} - X_{r,i,n+1} ) \\
    	&+ G_{lh,frt,i} \cdot C_{lh,frt,i} \cdot \frac{ X_{frt,i,n} - X_{r,i,n+1} }{ C_{lh,frt,i} + \Delta t \cdot G_{lh,frt,i} } \\
	    &+ \rho_a \cdot \sum_{j=0}^{J-1}{ \hat{V}_{int,vent,i,j,n} \cdot ( X_{r,j,n+1} - X_{r,i,n+1} ) } \\
    	&+ \hat{X}_{gen,i,n} + \hat{X}_{hum,i,n} + \hat{L}_{a,i,n} \cdot X_{r,i,n+1} + \hat{L}_{b,i,n}
    	\tag{b8}
    \end{align*}

となる。ステップ |n+1| における室 |i| および室 |j| の絶対湿度に解くと、

.. math::
    :nowrap:

    \begin{align*}
    	& \left( \rho_a \cdot \left( \frac{ V_{room,i} }{ \Delta t } + \hat{V}_{out,vent,i,n} \right)
	    + \frac{G_{lh,frt,i} \cdot C_{lh,frt,i} }{ C_{lh,frt,i} + \Delta t \cdot G_{lh,frt,i} } - \hat{L}_{a,i,n} \right) \cdot X_{r,i,n+1} \\
    	&- \rho_a \sum_{j=0}^{J-1}{ \hat{V}_{int,vent,i,j,n} \cdot ( X_{r,j,n+1} - X_{r,i,n+1} ) } \\
	    &= \rho_a \cdot \frac{ V_{room,i} }{ \Delta t } \cdot X_{r,i,n} + \rho_a \cdot \hat{V}_{out,vent,i,n} \cdot X_{o,n+1} \\
    	&+ \frac{ G_{lh,frt,i} \cdot C_{lh,frt,i} }{ C_{lh,frt,i} + \Delta t \cdot G_{lh,frt,i} } \cdot X_{frt,i,n} \\
	    &+ \hat{X}_{gen,i,n} + \hat{X}_{hum,i,n} + \hat{L}_{b,i,n}
    	\tag{b9}
    \end{align*}

となる。式(b9)は左辺に室 |i| の絶対湿度と室 |j| の絶対湿度がでてくる連立方程式であり、行列式で表すと

.. math::
    :nowrap:

    \begin{align*}
    	( \pmb{F}_{h,wgt,n} - \pmb{ \hat{L} }_{a,n} ) \cdot \pmb{X}_{r,n+1} = \pmb{F}_{h,cst,n} + \pmb{\hat{L}}_{b,n} \tag{b10}
    \end{align*}

となる。

:math:`\pmb{F}_{h,wgt,n}` は、 :math:`I \times I` の正方行列で、次式で表される。

.. math::
    :nowrap:

    \begin{align*}
    	\pmb{F}_{h,wgt,n} &= diag \left( \rho_a \left( \frac{V_{room,i} }{ \Delta t } + \hat{V}_{out,vent,i,n} \right) + \frac{ G_{lh,frt,i} \cdot C_{lh,frt,i} }{ C_{lh,frt,i} + \Delta t \cdot G_{lh,frt,i} } \right) \\
	    &- \rho_a \cdot \pmb{\hat{V}}_{int,vent,n}
    	\tag{b11}
    \end{align*}

:math:`diag` は室の数を :math:`I` とすると、室 :math:`0` から :math:`I-1` の対角行列を表す。

:math:`\pmb{F}_{h,cst,n}` は :math:`I \times 1` の行列であり、その要素を :math:`F_{h,cst,i,n}` とすると、

.. math::
    :nowrap:

    \begin{align*}
    	F_{h,cst,i,n} &= \rho_a \cdot \frac{ V_{room,i} }{ \Delta t } \cdot X_{r,i,n}
	    + \rho_a \cdot \hat{V}_{out,vent,i,n} \cdot X_{o,n+1} \\
    	&+ \frac{G_{lh,frt,i} \cdot C_{lh,frt,i} }{ C_{lh,frt,i} + \Delta t \cdot G_{lh,frt,i} } \cdot X_{frt,i,n}
	    + \hat{X}_{gen,i,n} + \hat{X}_{hum,i,n}
    	\tag{b12}
    \end{align*}

:math:`\pmb{\hat{L}}_{a,n}` は :math:`I \times I` の対角化行列であり、以下で定義される。

.. math::
    :nowrap:

    \begin{align*}
    	\pmb{\hat{L}}_{a,n} = diag( \hat{L}_{a,i,n} )
    \end{align*}

:math:`\pmb{\hat{L}}_{b,n}` は :math:`I \times 1` の縦行列であり、その要素は :math:`\hat{L}_{b,i,n}` である。

:math:`\pmb{\hat{V}}_{int,vent,n}` は室間換気を表す :math:`I \times I` の行列であり、例えば、室総数が3の場合で室1から室0へ60　|m3| / s の換気量がある場合は、

.. math::
    :nowrap:

    \begin{align*}
    	\pmb{\hat{V}}_{int,vent,n}
	    = \begin{pmatrix}
      	-60 & 60 & 0 \\
  	    0   & 0  & 0 \\
  	    0   & 0  & 0
		    \end{pmatrix}
    \end{align*}

となり、室総数が3の場合で室1から室0へ 60 |m3| / s の換気量かつ室2から室0へ 30 |m3|/s の換気量がある場合は、

.. math::
    :nowrap:

    \begin{align*}
    	\pmb{\hat{V}}_{int,vent,n}
	    = \begin{pmatrix}
      	-90 & 60 & 30 \\
  	    0   & 0  &  0 \\
      	0   & 0  &  0
	    	\end{pmatrix}
    \end{align*}

となる。これを式で表すと、

.. math::
    :nowrap:

    \begin{align*}
    	\pmb{\hat{V}}_{int,vent,n}
	    &= - diag \left (
    	\sum_{j=0}^{J-1}{\hat{V}_{int,vent,0,j,n}} \  \cdots \  \sum_{j=0}^{J-1}{\hat{V}_{int,vent,i,j,n}} \  \dots \  \sum_{j=0}^{J-1}{\hat{V}_{int,vent,I-1,j,n}}
	    \right ) \\
    	&+ \begin{pmatrix}
	    0 & \cdots & \hat{V}_{int,vent,0,j,n} & \cdots & \hat{V}_{int,vent,0,J-1,n} \\
    	\vdots & \ddots & \vdots & & \vdots \\
	    \hat{V}_{int,vent,i,0,n} & \cdots & 0 & \cdots & \hat{V}_{int,vent,i,J-1,n} \\
    	\vdots & & \vdots & \ddots & \vdots \\
	    \hat{V}_{int,vent,I-1,0,n} & \cdots & \hat{V}_{int,vent,I-1,j,n} & \cdots & 0 \\
    	\end{pmatrix}
		\tag{b13}
    \end{align*}

となる。

------------------------------------------------------------------------------------------------------------------------
2） 目標絶対湿度を設定する場合と設定しない場合が混在している場合の解法
------------------------------------------------------------------------------------------------------------------------

ここで、 目標とする絶対湿度を設定する場合としない場合で式(b10)における未知数が異なる。
この式について、変数を指定する項目と指定しない項目とに分離すると、

.. math::
    :nowrap:

    \begin{align*}
    	( \pmb{F}_{h,wgt,n} - \pmb{\hat{L}}'_{a,n} ) \cdot ( \pmb{X}'_{r,n+1} + \pmb{X}'_{r,set,n+1} )
        = \pmb{F}_{h,cst,n} + \pmb{\hat{L}}'_{b,n} + \pmb{\hat{L}}'_{b,set,n}
    	\tag{b14}
    \end{align*}

となる。ここで、室 |i| に目標とする絶対湿度を設定する場合は、定義から :math:`\pmb{\hat{L}}'_{a,n}` の |i| 成分が0になり、 :math:`\pmb{\hat{L}}'_{b,set,n}` のみが未知数となる。
ここで、 :math:`\pmb{\hat{L}}'_{b,set,n}` は絶対湿度を設定(=set)した場合の未知数としての負荷成分であることに留意されたい。未知数を左辺に既知数を右辺に整理する。

.. math::
    :nowrap:

    \begin{align*}
    	& ( \pmb{F}_{h,wgt,n} - \pmb{\hat{L}}'_{a,n} ) \cdot \pmb{X}'_{r,n+1} - \pmb{\hat{L}}'_{b,set,n} \\
	    &= - ( \pmb{F}_{h,wgt,n} - \pmb{\hat{L}}'_{a,n} ) \cdot \pmb{X}'_{r,set,n+1} + \pmb{F}_{h,cst,n} + \pmb{\hat{L}}'_{b,n}
    	\tag{b15}
    \end{align*}

ここで、

.. math::
    :nowrap:

    \begin{align*}
    	\pmb{X}'_{r,n+1} = {\begin{pmatrix} X'_{r,0,n+1} & \cdots & X'_{r,i,n+1} & \cdots & X'_{r,I-1,n+1} \end{pmatrix}}^T
    \end{align*}

.. math::
    :nowrap:

    \begin{align*}
    	\pmb{\hat{L}}'_{a,n} = diag( \hat{L}'_{a,i,n} )
    \end{align*} 

.. math::
    :nowrap:

    \begin{align*}
    	\pmb{\hat{L}}'_{b,n} = {\begin{pmatrix} \hat{L}'_{b,0,n} & \cdots & \hat{L}'_{b,i,n} & \cdots & \hat{L}'_{b,I-1,n} \end{pmatrix}}^T
    \end{align*}

.. math::
    :nowrap:

    \begin{align*}
    	\pmb{X}'_{r,set,n+1} = {\begin{pmatrix} X'_{r,set,0,n+1} & \cdots & X'_{r,set,i,n+1} & \cdots & X'_{r,set,I-1,n+1} \end{pmatrix}}^T
    \end{align*}

.. math::
    :nowrap:

    \begin{align*}
    	\pmb{\hat{L}}'_{b,set,n} = {\begin{pmatrix} \hat{L}'_{b,set,0,n} & \cdots & \hat{L}'_{b,set,i,n} & \cdots & \hat{L}'_{b,set,I-1,n} \end{pmatrix}}^T
    \end{align*}

であり、

:math:`X'_{r,i,n+1}`
    | ステップ |n+1| における室iの絶対湿度（ただし、室 |i| の設定絶対湿度を定める場合は0とする）, kg/kg(DA)
:math:`\hat{L}'_{b,i,n}`
    | ステップ |n| からステップ |n+1| における室 |i| の設定潜熱負荷（加湿を正・除湿を負とする）（ただし、室 |i| の設定絶対湿度を定める場合は0とする）, kg/s
:math:`X'_{r,set,i,n+1}`
    | ステップ |n+1| における室 |i| の設定絶対湿度（ただし、室 |i| の設定絶対湿度を定めない場合は0とする）, kg/kg(DA)
:math:`\hat{L}'_{b,set,i,n}`
    | ステップ |n| からステップ |n+1| における室 |i| の潜熱負荷（加湿を正・除湿を負とする）（ただし、室 |i| の設定絶対湿度を定めない場合は0とする）, kg/s

である。ここで、 :math:`X'_{r,i,n+1}` と :math:`\hat{L}'_{b,set,i,n}` のどちらか一方は必ず0となる。
同様に、:math:`X'_{r,set,i,n+1}` と :math:`\hat{L}'_{b,i,n}` のどちらか一方は必ず0となる。

ここで、

.. math::
    :nowrap:

    \begin{align*}
        \pmb{F}'_{h,wgt,n} = \pmb{F}_{h,wgt,n} - \pmb{\hat{L}}'_{a,n}
    \end{align*}

とおくと、式(b15)は、

.. math::
    :nowrap:

    \begin{align*}
    	\pmb{F}'_{h,wgt,n} \cdot \pmb{X}'_{r,n+1} - \pmb{\hat{L}}'_{b,set,n} = - \pmb{F}'_{h,wgt,n} \cdot \pmb{X}'_{r,set,n+1} + \pmb{F}_{h,cst,n} + \pmb{\hat{L}}'_{b,n} \tag{b16}
    \end{align*}

となる。

:math:`X'_{r,i,n+1}` と :math:`\hat{L}'_{b,set,i,n}` のどちらか一方は必ず0となることを利用し、 :math:`\pmb{F}''_{h,wgt,n}` を :math:`I \times J` の行列とし、
その要素を次式で表される :math:`F''_{h,wgt,i,j,n}` とすると、

.. math::
    :nowrap:

    \begin{align*}
    	F''_{h,wgt,i,j,n} = \begin{cases}
            F'_{h,wgt,i,j,n} & ( \hat{f}_{set,j,n} = 0 ) \\
            - \delta_{i,j} & ( \hat{f}_{set,j,n} = 1 )
        \end{cases}
    	\tag{b17}
    \end{align*}

とおくと、

.. math::
    :nowrap:

    \begin{align*}
    	& \pmb{F}''_{h,wgt,n} \cdot ( \pmb{X}'_{r,n+1} + \pmb{\hat{L}}'_{b,set,n} ) \\
	    &= - \pmb{F}'_{h,wgt,n} \cdot \pmb{X}'_{r,set,n+1} + \pmb{F}_{h,cst,n} + \pmb{\hat{L}}'_{b,n}
    	\tag{b18}
    \end{align*}

となり、

.. math::
    :nowrap:

    \begin{align*}
    	\pmb{k}_n
        &= \pmb{X}'_{r,n+1} + \pmb{\hat{L}}'_{b,set,n} \\
        &= {\pmb{F}''}_{h,wgt,n}^{-1} \cdot ( - \pmb{F}'_{h,wgt,n} \cdot \pmb{X}'_{r,set,n+1} + \pmb{F}_{h,cst,n} + \pmb{\hat{L}}'_{b,n} )
    	\tag{b19}
    \end{align*}

を解けばよい。ここで、:math:`\hat{f}_{set,j,n}` は、室 |j| において、
絶対湿度を指定する場合（加湿・除湿量は指定された室の絶対湿度を満たすように成り行きで定まる場合）を1、
室の絶対湿度を指定せず成り行きの絶対湿度とする場合（加湿・除湿を行わない又は加湿・除湿を室の絶対湿度に依らず定められた量行う場合）を0とする。

また、

.. math::
    :nowrap:

    \begin{align*}
    	\pmb{k}_n = \pmb{X}'_{r,n+1} + \pmb{\hat{L}}'_{b,set,n}
    \end{align*}

における、室 |i| の要素 :math:`X'_{r,i,n+1}` または :math:`\hat{L}'_{b,set,i,n}` について、どちらかは必ずゼロになるため、前述の :math:`\hat{f}_{set,i,n}` （添字は |i| とした）を用いて、

.. math::
    :nowrap:

    \begin{align*}
    	X_{r,i,n+1} = \begin{cases}
	    	k_{i,n} & ( \hat{f}_{set,i,n} = 0 ) \\
		    X'_{r,set,i,n+1} & ( \hat{f}_{set,i,n} = 1 )
    	\end{cases}
    	\tag{b20-1}
    \end{align*}

.. math::
    :nowrap:

    \begin{align*}
    	\hat{L}_{b,i,n} = \begin{cases}
	    	\hat{L}'_{b,i,n} & ( \hat{f}_{set,i,n} = 0 ) \\
		    k_{i,n} & ( \hat{f}_{set,i,n} = 1 )
    	\end{cases}
    	\tag{b20-2}
    \end{align*}

と表すことができる。

この際、潜熱負荷は、

.. math::
    :nowrap:

    \begin{align*}
        \pmb{\hat{L}}_{L,n} = \pmb{\hat{L}}_{a,n} \cdot \pmb{X}_{r,n+1} + \pmb{\hat{L}}_{b,n} \tag{b21}
    \end{align*}

で表される。

------------------------------------------------------------------------------------------------------------------------
3） 加湿・除湿に係る係数の定め方
------------------------------------------------------------------------------------------------------------------------

係数 :math:`\pmb{\hat{L}}_{a,n}` ・ :math:`\pmb{\hat{L}}_{b,n}` の決定方法を記す。

これらの係数は、すべての要素が0である行列として、以下の場合に基づいて各要素に値を加算していく。

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ア） 除湿・加湿を行わない場合
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

係数 :math:`\pmb{\hat{L}}_{a,n}` ・ :math:`\pmb{\hat{L}}_{b,n}` に対する加算は行わない。


^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
イ） 一定量の除湿・加湿を行う場合
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

係数 :math:`\pmb{\hat{L}}_{a,n}` に対する加算は行わない。

係数 :math:`\pmb{\hat{L}}_{b,n}` の要素 :math:`\hat{L}_{b,i,n}` に対して、　:math:`\hat{L}_{L,const,i,n}` を加算する。
ここで、

:math:`\hat{L}_{L,const,i,n}`
    | ステップ |n| からステップ |n+1| における室 |i| の潜熱負荷（加湿を正・除湿を負とする）, kg/s

である。

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ウ）室の絶対湿度に応じて一定量の除湿を行う場合
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

室の絶対湿度に応じて加湿量が決まる機構をもつ設備は存在しないため、本パターンにおいては、除湿のみを考える。

係数 :math:`\hat{L}_{a,n}` ・ :math:`\hat{L}_{b,n}` の決め方は設備固有のものである。

多くの場合、この方法は除湿を行う場合に採用される。
熱交換器表面の飽和絶対湿度よりも室の絶対湿度が上回っている場合は除湿を行うが、下回っている場合は除湿が行われない。
この場合、まず空調していない場合の絶対湿度を計算し、機器の熱交換器表面の飽和絶対湿度をそれが下回っている場合に除湿が行われるとし、
上回っている場合は「ア） 除湿・加湿を行わない場合」と同じ考え方で特に加算は行わない。
なお、本評価は室間換気を考慮した全室の連成計算のため、厳密に言えば他の部屋で加湿を行っている場合は、対象とする室がその影響を受けて除湿が行われるということがありうる。
しかし、これを考慮すると、収束計算等が必要となるため、本評価ではこれを考慮しない。
（その結果、厳密には、室の絶対湿度が熱交換器表面の飽和絶対湿度より大きい場合であっても、潜熱負荷が生じないということがありうる。）

次に、係数 :math:`\hat{L}_{a,n}` ・ :math:`\hat{L}_{b,n}` の決め方を対流型の空調と放射型の空調の場合に分けて記す。

i) 対流型の空調の場合

機器の吹き出し絶対湿度 :math:`X_{eq,out}` は吸い込み湿度 :math:`X_{eq,in}` と熱交換器表面の飽和絶対湿度 :math:`X_{eq,srf,ex}` を用いて次のように表される。

.. math::
    :nowrap:

    \begin{align*}
    	X_{eq,out} = BF \cdot X_{eq,in} + ( 1 - BF ) \cdot X_{eq,srf,ex} \tag{b22}
    \end{align*}

ここで、

:math:`X_{eq,out}`
    | 機器の室内機の吹き出し絶対湿度, kg / kg(DA)
:math:`X_{eq,in}`
    | 機器の室内機の吸い込み絶対湿度, kg / kg(DA)
:math:`X_{eq,srf,ex}`
    | 機器の室内機の熱交換器表面の絶対湿度, kg / kg(DA)
:math:`BF`
    | 機器のバイパスファクター

である。機器の室内機の吹き出し風量を :math:`V_{eq}` とすると、除湿量は、

.. math::
    :nowrap:

    \begin{align*}
    	L_{L} = - V_{eq} \cdot \rho_a \cdot ( X_{eq,in} - X_{eq,out} ) \tag{b23}
    \end{align*}

と表される。ここで、

:math:`L_L`
    | 機器の除湿量, kg / s
:math:`V_{eq}`
    | 機器の室内機の吹き出し風量, |m3| / s

である。

機器の室内機の吸い込み絶対湿度 :math:`X_{eq,in}` は室の絶対湿度 :math:`X_r` に等しいとし、式(b23)に式(b22)を代入すると、

.. math::
    :nowrap:

    \begin{align*}
    	L_L &= - V_{eq} \cdot \rho_a \cdot ( X_{eq,in} - X_{eq,out} ) \\
            &= - V_{eq} \cdot \rho_a \cdot ( X_{eq,in} - (BF \cdot X_{eq,in} + ( 1 - BF ) \cdot X_{eq,srf,ex} )) \\
            &= - V_{eq} \cdot \rho_a \cdot ( 1 - BF ) \cdot ( X_r - X_{eq,srf,ex} )
    	\tag{b24}
    \end{align*}

ここで、潜熱負荷 :math:`L_L` を

.. math::
    :nowrap:

    \begin{align*}
    	L_L = L_a \cdot X_r + L_b
    \end{align*}

と表したとすると、

.. math::
    :nowrap:

    \begin{align*}
    	L_a = - V_{eq} \cdot \rho_a \cdot ( 1 - BF ) \tag{b25}
    \end{align*}

.. math::
    :nowrap:

    \begin{align*}
    	L_b = V_{eq} \cdot \rho_a \cdot ( 1 - BF ) \cdot X_{RAC,eq,ex} \tag{b26}
    \end{align*}

となる。

次に、ルームエアコンディショナーのように各室に対応して設置し、吸い込みと吹き出しが同じ室で行われる個別空調の場合と、
ダクト式セントラル空調のように吸い込みと吹き出しが別の室（例えば非居室から吸い込み、各居室に吹き出す）で行われる居室間空調の場合とで分けて考える。

i-1) 個別空調の場合（ルームエアコンディショナー）

室 |i| に設置するルームエアコンディショナー等の個別空調（以下、単に機器という）の
