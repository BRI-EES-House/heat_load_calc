.. include:: definition.txt

************************************************************************************************************************
形態係数から放射熱伝達率
************************************************************************************************************************

========================================================================================================================
I. 評価法
========================================================================================================================

室 |i| に属する面 |j| の表面温度が、室 |i| 内の平均放射温度に寄与する割合 :math:`f_{mrt,i,j}` は、式(1)で表される。

.. math::
    :nowrap:

    \begin{align*}
        f_{mrt,i,j} = \dfrac{h_{r,i,j} A_{j}}{\sum\limits_{j\in{i}} h_{r,i,j} A_{j}} \tag{1}
    \end{align*}

ここで、

:math:`f_{mrt,i,j}`
    | 室 |i| に属する面 |j| の表面温度が室 |i| 内の平均放射温度に寄与する割合, -
:math:`h_{r,i,j}`
    | 室 |i| に属する面 |j| の放射熱伝達率, W/(|m2| K)-
:math:`A_{j}`
    | 面 |j| の面積, |m2| 

である。

室 |i| に属する面 |j| の放射熱伝達率 :math:`h_{r,i,j}` は、式(2)で表される。

.. math::
    :nowrap:

    \begin{align*}
        h_{r,i,j} = \dfrac{ \epsilon_{j} }{ 1 - \epsilon_{j} \cdot f_{i,j}} \cdot 4 \cdot \sigma \cdot (t_{mrt,i} + 273.15 )^{3} \tag{2}
    \end{align*}

ここで、

:math:`\epsilon_{j}`
    | 面 |j| の放射率, -
:math:`f_{i,j}`
    | 室 |i| 内の微小球からみた面 |j| への形態係数, -
:math:`\sigma`
    | ステファン・ボルツマン定数, W/(|m2| K\ :sup:`4`\)
:math:`t_{mrt,i}`
    | 室 |i| 内の平均放射温度, ℃

である。

ステファン・ボルツマン定数 :math:`\sigma` は、 :math:`5.67 \times 10^{-8}` W/(|m2| K\ :sup:`4`\) である。また、平均放射温度 :math:`t_{mrt,i}` は、 :math:`20` ℃ とする。

室 |i| 内の微小球からみた面 |j| への形態係数 :math:`f_{i,j}` は、式(3)で表される。

.. math::
    :nowrap:

    \begin{align*}
        f_{i,j} = \dfrac{A_{j}}{A_{i,k}} f_{i,k}  \tag{3}
    \end{align*}
    
ここで、

:math:`f_{i,k}`
    | 室 |i| 内の微小球から同一方位となる表面のグループ |k| への形態係数, -
:math:`A_{i,k}`
    | 室 |i| 内の同一方位となる表面のグループ |k| の面積, |m2| 
        
である。


室 |i| 内の微小球から同一方位となる表面のグループ |k| への形態係数 :math:`f_{i,k}` は、式(4)で表される。

.. math::
    :nowrap:

    \begin{align*}
        f_{i,k} = \dfrac{1}{2} \Bigl\{ 1 - \mbox{sgn}(\left. 1 - 4 \cdot r_{a,i,k} \middle/ \bar{f_i} \right.) \sqrt{ | \left. 1 - 4 \cdot r_{a,i,k} \middle/ \bar{f_i} \right. | } \Bigr\}  \tag{4}
    \end{align*}

ここで、

:math:`\bar{f_i}`
    | 非線形方程式 :math:`L(\bar{f_i})=0` の解, -
:math:`r_{a,i,k}`
    | 同一方位となる表面のグループ |k| の面積が室 |i| 内の表面積の総和に占める比, -

である。また、 :math:`\mbox{sgn}(x)` は符号関数であり、 :math:`x>0` で  :math:`\mbox{sgn}(x)=1` を、 :math:`x=0` で  :math:`\mbox{sgn}(x)=0` を、 :math:`x<0` で  :math:`\mbox{sgn}(x)=-1` をとる。

:math:`\bar{f_i}` は、式(5)の非線形方程式 :math:`L(\bar{f_i})=0` を解くことで求まる。

.. math::
    :nowrap:

    \begin{align*}
        L(\bar{f_i}) = \sum_{k\in{i}} \dfrac{1}{2} \Bigl\{ 1 - \mbox{sgn}(\left. 1 - 4 \cdot r_{a,i,k} \middle/ \bar{f_i} \right.) \sqrt{ | \left. 1 - 4 \cdot r_{a,i,k} \middle/ \bar{f_i} \right. | } \Bigr\} - 1 = 0 \tag{5}
    \end{align*}

室 |i| 内の同一方位となる表面のグループ |k| の面積の比 :math:`r_{a,i,k}` は、式(6)で表される。

.. math::
    :nowrap:

    \begin{align*}
        r_{a,i,k} =  \dfrac{A_{i,k}}{\sum\limits_{k\in{i}} A_{i,k}} \tag{6}
    \end{align*}

室 |i| 内の同一方位となる表面のグループ |k| の平均放射率 :math:`\epsilon_{i,k}` は、式(7)で表される。

.. math::
    :nowrap:

    \begin{align*}
        \epsilon_{i,k} =  \dfrac{1}{A_{i,k}} \sum\limits_{j\in{k}} \epsilon_{j} A_{j} \tag{7}
    \end{align*}

室 |i| 内の同一方位となる表面のグループ |k| の面積 :math:`a_{i,k}` は、式(8)で表される。

.. math::
    :nowrap:

    \begin{align*}
        A_{i,k} =  \sum\limits_{j\in{k}} A_{j} \tag{8}
    \end{align*}
   
========================================================================================================================
II. 根拠
========================================================================================================================

作成中
