.. include:: definition.txt

************************************************************************************************************************
太陽位置
************************************************************************************************************************

========================================================================================================================
I. 評価法
========================================================================================================================

ステップ |n| における太陽方位角 :math:`a_{sun,n}` は、 :math:`-\pi` ～ :math:`0` ～ :math:`\pi` の範囲で定義され、:math:`a_{sun,n}=\pm \pi` を北、 :math:`a_{sun,n}=-\pi/2` を東、 :math:`a_{sun,n}=0` を南、 :math:`a_{sun,n}=\pi/2` を西として、式(1)により計算される。
ただし、太陽の位置が天頂にある場合は定義されない。

.. math::
    :nowrap:

    \begin{align*}
        a_{sun,n} = arctan( \sin{a_{sun,n}},\cos{a_{sun,n}} ) \tag{1}
    \end{align*}

ここで、

:math:`a_{sun,n}`
    | ステップ |n| における太陽方位角, rad
:math:`\sin{a_{sun,n}}`
    | ステップ |n| における太陽方位角の正弦, -
:math:`\cos{a_{sun,n}}`
    | ステップ |n| における太陽方位角の余弦, -

である。また、 :math:`arctan(y, x)` は、 :math:`-\pi/2` ～ :math:`0` ～ :math:`\pi/2` の範囲で定義される通常の逆正接関数とは異なり、座標上で第1引数を :math:`y` , 第2引数を :math:`x` にした際に :math:`x` 軸との角度を求める関数として、 :math:`-\pi \leq arctan(y, x) \leq \pi` の範囲で定義される。すなわち、 :math:`\sin{a_{sun,n}}>0` かつ :math:`\cos{a_{sun,n}}>0` の場合は :math:`0` ～ :math:`\pi/2` の角度を、:math:`\sin{a_{sun,n}}>0` かつ :math:`\cos{a_{sun,n}}<0` の場合は :math:`\pi/2` ～ :math:`\pi` の角度を、 :math:`\sin{a_{sun,n}}<0` かつ :math:`\cos{a_{sun,n}}<0` の場合は :math:`-\pi` ～ :math:`-\pi/2` の角度を、 :math:`\sin{a_{sun,n}}<0` かつ :math:`\cos{a_{sun,n}}>0` の場合は :math:`-\pi/2` ～ :math:`0` の角度を返す関数となる。
 
ステップ |n| における太陽方位角の余弦 :math:`\cos{a_{sun,n}}` は、式(2)により計算される。
ただし、太陽の位置が天頂にある場合は定義されない。

.. math::
    :nowrap:

    \begin{align*}
        \cos{a_{sun,n}} = \dfrac{ \sin{h_{sun,n}} \cdot \sin{\varphi_{loc}} - \sin{\delta_{n}} }{ \cos{h_{sun,n}} \cdot \cos{\varphi_{loc}} } \tag{2}
    \end{align*}

ここで、

:math:`h_{sun,n}`
    | ステップ |n| における太陽高度, rad
:math:`\varphi_{loc}`
    | 緯度, rad
:math:`\delta_{n}`
    | ステップ |n| における赤緯, rad

である。

ステップ |n| における太陽の方位角の正弦 :math:`\sin{a_{sun,n}}` は、式(3)により計算される。
ただし、太陽の位置が天頂にある場合は定義されない。

.. math::
    :nowrap:

    \begin{align*}
        \sin{a_{sun,n}} = \dfrac{ \cos{\delta_{n}} \cdot \sin{\omega_{n}} }{ \cos{h_{sun,n}} } \tag{3}
    \end{align*}

ここで、

:math:`\omega_{n}`
    | ステップ |n| における時角, rad
    
である。

太陽の位置が天頂にある場合とは、太陽高度 :math:`h_{sun,n}` が次式を満たす場合を言う。

.. math::
    :nowrap:

    \begin{align*}
        h_{sun,n} = \frac{ \pi }{ 2 }
    \end{align*}


ステップ |n| における太陽高度 :math:`h_{sun,n}` は、 :math:`-\pi/2 \leq h_{sun,n} \leq \pi/2` の範囲で式(4)により計算される。
    
 .. math::
    :nowrap:

    \begin{align*}
        h_{sun,n} = \arcsin( \sin{\varphi_{loc}} \cdot \sin{\delta_{n}} + \cos{\varphi_{loc}} \cdot \cos{\delta_{n}} \cdot \cos{\omega_{n}} ) \tag{4}
    \end{align*}

なお、 :math:`h_{sun,n} < 0` は、太陽が沈んでいることを意味する。

ステップ |n| における時角 :math:`\omega_{n}` は、式(5)により計算される。
    
.. math::
    :nowrap:

    \begin{align*}
        \omega_{n} = \{ ( t_{m,n} - 12 ) \times 15 \} \times \dfrac{\pi}{180} + ( \lambda_{loc} - \lambda_{loc,mer} ) + e_{t,n} \tag{5}
    \end{align*}   

ここで、

:math:`t_{m,n}`
    | ステップ |n| における標準時, h
:math:`\lambda_{loc}`
    | 経度, rad
:math:`\lambda_{loc,mer}`
    | 標準時の地点の経度, rad
:math:`e_{t,n}`
    | ステップ |n| における均時差, rad
    
である。  

ステップ |n| における標準時 :math:`t_{m,n}` は、時間間隔により次表のように定義される。

.. csv-table:: 時間間隔が1時間の場合

     ステップ |n| , 0, 1, 2, …, 8760
     標準時 , 0, 1, 2, …, 8760

.. csv-table:: 時間間隔が30分の場合

     ステップ |n| , 0, 1, 2, 3, 4, …, 17519, 17520
     標準時 , 0, 0.5, 1, 1.5, 2, …, 8759.5, 8760

.. csv-table:: 時間間隔が15分の場合

     ステップ |n| , 0, 1, 2, 3, 4, 5, 6, …, 35039, 35040
     標準時 , 0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, …, 8759.75, 8760

ステップ |n| における赤緯 :math:`\delta_{n}` は、 :math:`-\pi/2 \leq \delta_{n} \leq \pi/2` の範囲で式(6)により計算される。

.. math::
    :nowrap:

    \begin{align*}
        \delta_{n} = \arcsin \{ \cos ( \nu_n + \epsilon_n ) \cdot \sin \delta_0 \} \tag{6}
    \end{align*}  

ここで、

:math:`\nu_n`
    | ステップ |n| における真近点離角, rad
:math:`\epsilon_n`
    | ステップ |n| における近日点と冬至点の角度, rad
:math:`\delta_0`
    | 北半球の冬至の日赤緯, rad

である。北半球の冬至の日赤緯 :math:`\delta_0` は、 :math:`-23.4393 \times \pi/180` radを用いる。

ステップ |n| における均時差 :math:`e_{t,n}` は、式(7)により計算される。

.. math::
    :nowrap:

    \begin{align*}
        e_{t,n} = ( m_n - \nu_n ) - \arctan \dfrac{ 0.043 \sin \{ 2 ( \nu_n + \epsilon_n ) \} }{ 1 - 0.043 \cos \{ 2 ( \nu_n + \epsilon_n ) \} } \tag{7}
    \end{align*}  

ここで、

:math:`m_n`
    | ステップ |n| における平均近点離角, rad

である。

ステップ |n| における真近点離角 :math:`\nu_n` は、式(8)により計算される。

.. math::
    :nowrap:

    \begin{align*}
        \nu_n = m_n + ( 1.914 \sin m_n + 0.02 \sin 2m_n ) \times \dfrac{\pi}{180} \tag{8}
    \end{align*}

ステップ |n| における近日点と冬至点の角度 :math:`\epsilon_n` は、式(9)により計算される。

.. math::
    :nowrap:

    \begin{align*}
        \epsilon_n = \Bigl\{ 12.3901 + 0.0172 \Bigl( N + \dfrac{ m_n }{ 2 \pi } \Bigr) \Bigr\} \times \dfrac{\pi}{180}  \tag{9}
    \end{align*}  

ここで、

:math:`N`
    | 1968年との年差, 年

である。

ステップ |n| における平均近点離角 :math:`m_n` は、式(10)により計算される。

.. math::
    :nowrap:

    \begin{align*}
        m_n = 2 \pi ( d_n - d_0 ) / d_{ay}  \tag{10}
    \end{align*}  

ここで、

:math:`d_n`
    | ステップ |n| における年通算日( :math:`1` 月 :math:`1` 日を :math:`1` とする), day
:math:`d_0`
    | 平均軌道上の近日点通過日(暦表時による :math:`1968` 年 :math:`1` 月 :math:`1` 日正午基準の日差), day
:math:`d_{ay}`
    | 近点年(近日点基準の公転周期日数), day
    
である。本計算では、近点年(近日点基準の公転周期日数) :math:`d_{ay}` は :math:`365.2596` とする。

ステップ |n| における平均軌道上の近日点通過日(暦表時による :math:`1968` 年 :math:`1` 月 :math:`1` 日正午基準の日差) :math:`d_0` は、式(11)により計算される。

.. math::
    :nowrap:

    \begin{align*}
        d_0 = 3.71 + 0.2596 N - \biggl\lfloor \dfrac{ N + 3 }{ 4 } \biggr\rfloor  \tag{11}
    \end{align*}  

なお :math:`\lfloor x \rfloor` は、 :math:`x` の小数点以下を切り捨てた値とする。
	
1968年との年差 :math:`N` は、式(12)により計算される。

.. math::
    :nowrap:

    \begin{align*}
        N = y - 1968  \tag{12}
    \end{align*}  

ここで、

:math:`y`
    | 計算するする年(西暦), 年
    
である。本計算では、計算するする年は西暦1989年とする。
	
:math:`1` 月 :math:`1` 日を :math:`1` とする、ステップ |n| における年通算日 :math:`d_n` は、式(13)により計算される。

.. math::
    :nowrap:

    \begin{align*}
        d_n = \biggl\lfloor \dfrac{ n }{ 24 n_h } \biggr\rfloor + 1  \tag{13}
    \end{align*} 

なお :math:`\lfloor x \rfloor` は、 :math:`x` の小数点以下を切り捨てた値とする。

標準時の地点の経度 :math:`\lambda_{loc,mer}` は、式(14)により計算される。

.. math::
    :nowrap:

    \begin{align*}
        \lambda_{loc,mer} = 135 \times \dfrac{\pi}{180} \tag{14}
    \end{align*} 

========================================================================================================================
II. 根拠
========================================================================================================================

作成中
