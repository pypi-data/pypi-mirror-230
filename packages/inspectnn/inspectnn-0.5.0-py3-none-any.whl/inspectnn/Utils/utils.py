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
import numpy as np

def flatten(container):
    for i in container:
        if isinstance(i, (list, tuple)):
            yield from flatten(i)
        else:
            yield i

def grouped(iterable, n):
    return zip(*[iter(iterable)]*n)

def list_partitioning(a_list, num_of_partitions):
    return [list(item) for item in np.array_split(a_list, num_of_partitions)]