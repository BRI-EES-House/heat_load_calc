.. include:: definition.txt

************************************************************************************************************************
太陽位置
************************************************************************************************************************

========================================================================================================================
I. 評価法
========================================================================================================================

ステップ |n| における太陽方位角 :math:`a_{sun,n}` は、 :math:`a_{sun,n}=\pm \pi` を北、 :math:`a_{sun,n}=-\pi/2` を東、 :math:`a_{sun,n}=0` を南、 :math:`a_{sun,n}=\pi/2` を西として、式(1)により計算される。ただし、太陽の位置が天頂にある場合は定義されない。

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

.. math::
    :nowrap:

    \begin{align*}
        \cos{a_{sun,n}} = \dfrac{ \sin{h_{sun,n}} \times \sin{\varphi_{loc}} - \sin{\delta_{n}} }{ \cos{h_{sun,n}} \times \cos{\varphi_{loc}} } \tag{2}
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

.. math::
    :nowrap:

    \begin{align*}
        \sin{a_{sun,n}} = \dfrac{ \cos{\delta_{n}} \times \sin{\omega_{n}} }{ \cos{h_{sun,n}} } \tag{3}
    \end{align*}

ここで、

:math:`\omega_{n}`
    | ステップ |n| における時角, rad
    
である。    
    
ステップ |n| における太陽高度 :math:`h_{sun,n}` は、 :math:`-\pi/2 \leq h_{sun,n} \leq \pi/2` の範囲で式(4)により計算される。
    
 .. math::
    :nowrap:

    \begin{align*}
        h_{sun,n} = \arcsin( \sin{\varphi_{loc}} \times \sin{\delta_{n}} + \cos{\delta_{n}} \times \cos{\omega_{n}} ) \tag{4}
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
    | 均時差, rad
    
である。  


    

========================================================================================================================
II. 根拠
========================================================================================================================

作成中
