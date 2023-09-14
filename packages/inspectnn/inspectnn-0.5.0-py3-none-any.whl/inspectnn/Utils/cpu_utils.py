"""
Copyright 2022  Salvatore Barone <salvatore.barone@unina.it>
                Filippo Ferrandino <fi.ferrandino@studenti.unina.it>

This is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free
Software Foundation; either version 3 of the License, or any later version.

This is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
RMEncoder; if not, write to the Free Software Foundation, Inc., 51 Franklin
Street, Fifth Floor, Boston, MA 02110-1301, USA.
"""
import itertools
from inspectnn.BaseLayer import *

def mul(a, b, multiplier):
    a = np.array(a)
    b = np.array(b)
    a_shape = np.shape(a)
    b = np.reshape(b, a_shape)
    if multiplier == BaseLayer.default_multiplier:
        return BaseLayer.default_multiplier(a, b)
    return ax_mul(a, b, tuple(a_shape), multiplier)
        
def ax_mul(a, b, shape, multiplier):
    res = np.zeros(shape)
    if len(shape) == 1:
        for i in range(shape[0]):
            res[i] = multiplier.run(int(a[i]),int(b[i]))
    elif len(shape) == 2:
        for i, j in itertools.product(range(shape[0]), range(shape[1])):
            res[i,j] = multiplier.run(int(a[i,j]), int(b[i,j]))
    return res
