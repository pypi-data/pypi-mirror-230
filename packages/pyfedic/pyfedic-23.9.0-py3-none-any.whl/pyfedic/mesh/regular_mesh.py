import numpy as np

from ..cells import Q4, C8
from .base_mesh import BaseMesh

class RegularBaseMesh(BaseMesh):
    """

    """

    def __init__(self, xlims, ylims, zlims=None, zoi=16):
        ""

        if zlims is None:
            nex, ney = int(np.diff(xlims) // zoi), int(np.diff(ylims) // zoi)
            nnx, nny = nex+1, ney+1
            c00 = np.array([0, 1, nnx+1, nnx])
            c0 = np.arange(nex).repeat(4).reshape(nex,4) + c00.reshape(1,4).repeat(nex, axis=0)
            cell_type = Q4
            cells = np.arange(ney).repeat(4*nex).reshape(nex*ney,4)*nnx + np.tile(c0, (ney, 1))
        else:
            nex, ney, nez = int(np.diff(xlims) // zoi), int(np.diff(ylims) // zoi), int(np.diff(zlims) // zoi)
            nnx, nny, nnz = nex+1, ney+1, nez+1
            c000 = np.array([0, 1, nnx+1, nnx, nnx*nny, nnx*nny+1, nnx*nny+nnx+1, nnx*nny+nnx])
            c00 = np.arange(nex).repeat(8).reshape(nex,8) + c000.reshape(1,8).repeat(nex, axis=0)
            c0 = np.arange(ney).repeat(8*nex).reshape(nex*ney,8)*nnx + np.tile(c00, (ney, 1))
            cell_type = C8
            cells = np.arange(nez).repeat(8*nex*ney).reshape(nex*ney*nez,8)*nnx*nny + np.tile(c0, (nez, 1))

        xn = np.round(np.arange(nnx)*zoi+xlims[0]+((xlims[1]-xlims[0]) % zoi)/2)-0.5
        yn = np.round(np.arange(nny)*zoi+ylims[0]+((ylims[1]-ylims[0]) % zoi)/2)-0.5
        if zlims is None:
            zn = [0]
            regular = (ney, nex), zoi
        else:
            zn = np.round(np.arange(nnz)*zoi+zlims[0]+((zlims[1]-zlims[0]) % zoi)/2)-0.5
            regular = (nez, ney, nex), zoi

        zn, yn, xn = np.meshgrid(zn, yn, xn, indexing='ij')
        nodes = np.vstack((xn.flat, yn.flat, zn.flat)).T

        super().__init__(nodes, cells, cell_type)
        self.regular = regular

    def iter_Nc(self):
        nelems, zoi = self.regular
        n = len(nelems)
        mv = nelems[::-1]
        ks = [0]*n
        while True:
            if ks[n-1] >= mv[n-1]:
                break
            yield ks[::-1]
            ks[0] += 1
            for i in range(n-1):
                if ks[i] >= mv[i]:
                    ks[i] = 0
                    ks[i+1] += 1
