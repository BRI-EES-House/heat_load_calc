************************************************************************************************************************
注意事項
************************************************************************************************************************

I. 本評価における行列表記について
========================================================================================================================

本評価では、何箇所かで2次元の行列を計算を行っている。行列は太字で :math:`\pmb{a}` のように表す。
:math:`\pmb{a}` の要素は :math:`a_{i,j}` であり、要素数 :math:`I \times J` の場合、

.. math::

    \pmb{a} = \begin{pmatrix}
        a_{0,0}   & \cdots & a_{0,j}   & \cdots & a_{0,J-1} \\
        \vdots    & \ddots & \vdots    &        & \vdots \\
        a_{i,0}   & \cdots & a_{i,j}   & \cdots & a_{i,J-1} \\
        \vdots    &        & \vdots    & \ddots & \vdots \\
        a_{I-1,0} & \cdots & a_{I-1,j} & \cdots & a_{I-1,J-1}
    \end{pmatrix}

で定義される。

行方向（縦方向）を :math:`i` とし、列方向（横方向）を :math:`j` とし、その配列数をそれぞれ、
:math:`I` 及び :math:`J` だとすると、これを要素数 :math:`I \times J` の行列と呼び、要素を :math:`a_{i,j}` と記す。

多くの場合、室の数などを上限（ :math:`I` とする）とする正方行列の場合が多く、その場合
:math:`I \times I` の行列と呼ぶこともあるが、あくまで要素は、:math:`a_{i,j}` であることに留意されたい。

また、縦方向に :math:`I` 横方向に1の縦行列の場合も多く、その場合、

.. math::

    \pmb{a} = \begin{pmatrix}
        a_{0} \\
        \vdots \\
        a_{i} \\
        \vdots \\
        a_{I-1}
    \end{pmatrix}

であり、これを要素数 :math:`I \times 1` の行列と呼び、要素を :math:`a_i` と記す。 

記号説明をする場合において、以下のようなベクトルがあった場合に、

.. math::
    :nowrap:

    \begin{align*}
        \pmb{a} = \begin{pmatrix}
            a_{0} \\
            \vdots \\
            a_{i} \\
            \vdots \\
            a_{I-1}
        \end{pmatrix}
    \end{align*}

    \begin{align*}
        \pmb{b}
        = \begin{pmatrix}
            b_{0} & \cdots & 0 & \cdots & 0 \\
            \vdots & \ddots & \vdots & & \vdots \\
            0 & \cdots & b_{i} & \cdots & 0 \\
            \vdots & & \vdots & \ddots & \vdots \\
            0 & \cdots & 0 & \cdots & b_{I-1}
        \end{pmatrix}
    \end{align*}

    \begin{align*}
    \pmb{c} = \begin{pmatrix}
            c_{0,0}   & \cdots & c_{0,j}   & \cdots & c_{0,J-1} \\
            \vdots    & \ddots & \vdots    &        & \vdots \\
            c_{i,0}   & \cdots & c_{i,j}   & \cdots & c_{i,J-1} \\
            \vdots    &        & \vdots    & \ddots & \vdots \\
            c_{I-1,0} & \cdots & c_{I-1,j} & \cdots & c_{I-1,J-1}
        \end{pmatrix}
    \end{align*}

表記を簡単にするためにそれぞれ、

:math:`\pmb{a}`
    | :math:`a_i` を要素にもつ :math:`I \times 1` の縦行列
:math:`\pmb{b}`
    | :math:`b_i` を要素にもつ :math:`I \times I` の対角化行列
:math:`\pmb{c}`
    | :math:`c_{i,j}` を要素にもつ :math:`I \times J` の行列

と記す。