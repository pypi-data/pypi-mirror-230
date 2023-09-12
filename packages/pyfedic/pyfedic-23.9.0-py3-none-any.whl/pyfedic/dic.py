#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from scipy import sparse
from scipy.sparse import linalg as splinalg
import platform
import logging
import warnings
from functools import cache

from .tictoc import Tictoc, tictoc
from .cells import Q4, C8, Cell
from .mesh import RegularMesh

try:
    from pyfedic_cython.spfast import spmul
except ModuleNotFoundError:
    def spmul(sp, d):
        return sparse.csc_array((
                sp.data*d[sp.indices],
                sp.indices,
                sp.indptr
            ), sp.shape)

class DIC:
    #
    def __init__(self, imref, mesh):
        self.set_normim_params()
        self.debug_path = None
        self.scale = 0
        self.imref = self.normim(imref)
        self.mesh = mesh
        self.eq_gap = None
        self.tiko = None
        self.median = 0
        self.mean = 0
        self.itermax = 100
        self.normed_dU_min = 0.001
        self.diff_discr_min = 0.001
        self.mask = None
        self.mask_node = None
        self.mask_cell = None
        self.solver = 'cgs'
        self.U_init = np.zeros((self.mesh.Nn, self.imref.ndim), dtype='f4')
        self.gradref = np.array([g[self.mesh.roi.slices].ravel() for g in np.gradient(self.imref)[::-1]])

    def set_normim_params(self, strategy="none", use_mesh=False, use_mask=False):
        self._normim_strategy = strategy
        self._normim_use_mesh = use_mesh
        self._normim_use_mask = use_mask
        self._normim_stats = None

    def normim(self, im):
        if self._normim_strategy == 'none':
            return im.astype('f4')
        if self._normim_stats is not None:
            return ((im-self._normim_stats[0])/self._normim_stats[1]/3+10).astype('f4')
        sel = ~np.isnan(im)
        if self._normim_use_mesh:
            sel[self.mesh.bounding_box.slices] &= True
        if self._normim_use_mask and self.mask is not None:
            sel &= self.mask
        stats = im[sel].mean(), im[sel].std()
        if self._normim_strategy == 'ref':
            self._normim_stats = stats
        return ((im-stats[0])/stats[1]/3+10).astype('f4')

    @tictoc(speak=False)
    def _compute_M_regular(self):
        #
        nelems, zoi = self.mesh.regular
        ndim = self.mesh.ndim

        pix_coords = np.mgrid[(slice(0,zoi),)*ndim].reshape((ndim, zoi**ndim)).T
        coords = ((pix_coords - (zoi-1)/2)*2/zoi)[:,::-1]

        Ne = self.mesh.cell_type.N(coords).astype('f4').reshape((self.mesh.cell_type.n_nodes, zoi**ndim))

        coefs = [np.prod(np.array(nelems)[i+1:]*zoi) for i in range(ndim)]

        data = []
        col = []
        row = []

        for i, zyx in enumerate(self.mesh.iter_Nc()):
            if self.mask is not None and not self.mask[i]:
                continue

            x = np.sum([(pix_coords[:,j] + zyx[j]*zoi)*coefs[j] for j in range(ndim)], axis=0)

            Mes = [g[x]*Ne for g in self.gradref]
            r, c = np.meshgrid(self.mesh.cells[i], self.mesh.cells[i])
            for d in range(len(self.gradref)):
                for e in range(len(self.gradref)):
                    Me = Mes[d] @ Mes[e].T
                    data.append(Me.ravel())
                    row.append(r.ravel()+self.mesh.Nn*d)
                    col.append(c.ravel()+self.mesh.Nn*e)

        self._M = sparse.csc_array((np.hstack(data), (np.hstack(row), np.hstack(col))), (self.mesh.Nn*ndim,self.mesh.Nn*ndim))

        self._M.eliminate_zeros()

        return self._M

    @cache
    @tictoc
    def compute_M(self):
        #
        if isinstance(self.mesh, RegularMesh):
            return self._compute_M_regular()

        if self.mesh.pixN is None:
            self.mesh.compute_pixN()

        M = []
        for g in self.gradref:
            A = spmul(self.mesh.pixN, g)
            M.append(A.T @ A)

        M = sparse.block_diag(M)

        return M.tocsc()

    @tictoc(speak=False)
    def _compute_B_regular(self, diff):
        #
        nelems, zoi = self.mesh.regular
        ndim = self.imref.ndim

        pix_coords = np.mgrid[(slice(0,zoi),)*ndim].reshape((ndim, zoi**ndim)).T
        coords = ((pix_coords - (zoi-1)/2)*2/zoi)[:,::-1]

        Ne = self.mesh.cell_type.N(coords).astype('f4').reshape((self.mesh.cell_type.n_nodes, zoi**ndim))

        coords = (coords.reshape((ndim, zoi**ndim))*zoi/2+(zoi-1)/2).astype(int)

        coefs = [np.prod(np.array(nelems)[i+1:]*zoi) for i in range(ndim)]

        B = np.zeros(self.mesh.Nn*ndim, dtype='f4')

        for i, zyx in enumerate(self.mesh.iter_Nc()):
            if self.mask is not None and not self.mask_cell[i]:
                continue

            x = np.sum([(pix_coords[:,j] + zyx[j]*zoi)*coefs[j] for j in range(ndim)], axis=0)

            for d, g in enumerate(self.gradref):
                B[self.mesh.cells[i]+self.mesh.Nn*d] += (g[x]*Ne) @ diff.flat[x]

        return B

    @tictoc
    def compute_B(self, diff):
        #

        if isinstance(self.mesh, RegularMesh):
            return self._compute_B_regular(diff)

        B = []
        for g in self.gradref:
            A = spmul(self.mesh.pixN, g)
            B.append(A.T @ diff.flat)

        return np.hstack(B)

    def set_tiko(self, reg_size, ddl=None): #TODO
        """

        ddl sould size: mesh.Nn
        with True if used by regularization.

        """
        k = 1/(self.mesh.nodes.max(axis=0) - self.mesh.nodes.min(axis=0))[:self.mesh.ndim].min()
        V = np.cos(2*np.pi*self.mesh.nodes[:,:self.mesh.ndim]*k).T.ravel()[:,None]

        if ddl is not None: # TODO: hum ????
            ddl = np.hstack((ddl, [False]))
            nodes_in_cell = Cell.nn_by_id[self.mesh.cell_types]
            nodes_used_in_cell = ddl[self.mesh.cells].sum(axis=1)
            selection = (nodes_in_cell - nodes_used_in_cell) == 0
        else:
            selection = None

        M = self.compute_M

        N = self.mesh.compute_N(self.mesh.gauss_points())

        print(N.shape, self.mesh)

        print('PLOUUUUUUUUUUUUUUUUUF !')

        NN = N.T.dot(N)

        NN = sparse.block_diag((NN, NN)).tocsr()

        A = (V.T.dot(M.dot(V))/V.T.dot(NN.dot(V))).ravel()[0]
        wm = (reg_size*k)**4
        alpha = wm*A
        Mr = M + alpha*NN
        self.tiko = (Mr, NN, alpha)

    def set_eq_gap(self, reg_size, nu=0.3, ddl=None):
        """

        # FIXME : ddl is not working => TODO
        ddl sould size: mesh.Nn
        with True if used by regularization.

        """
        k = 1/(self.mesh.nodes.max(axis=0) - self.mesh.nodes.min(axis=0))[:self.mesh.ndim].min()
        V = np.cos(2*np.pi*self.mesh.nodes[:,:self.mesh.ndim]*k).T.ravel()[:,None]

        M = self.compute_M()
        K = self.mesh.compute_K(nu)

        KK = K.T @ K
        A = ((V.T @ M @ V) / ( V.T @ KK @ V)).squeeze()
        wm = (reg_size*k)**4
        alpha = wm*A
        Mr = M + alpha*KK

        if ddl is not None:

            ddl = np.tile(ddl, self.mesh.ndim)
            ind = ~(ddl[K.col] & ddl[K.row])
            K.data[ind] *= 0

            KK = K.T @ K
            A = ((V.T @ M @ V) / ( V.T @ KK @ V)).squeeze()
            wm = (reg_size*k)**4
            alpha = wm*A
            Mr = M + alpha*KK

        self.eq_gap = (Mr, KK, alpha)

    def set_median(self, median):
        self.median = median

    def set_mean(self, mean):
        self.mean = mean

    def set_mask(self, mask, mask_threshold): #TODO
        self.mask = mask

        if isinstance(self.mesh, RegularMesh):
            norm = self.mesh.regular[1]**self.mesh.ndim
        elif self.mesh.ndim == 2:
            norm = self.mesh.surf()
        else:
            norm = self.mesh.vol()

        self.mask_cell = self.mesh.split_by_celltype(pixsum_by_cells(mask.astype(int), self.mesh) >= mask_threshold*norm)
        self.mask_node = np.zeros(self.mesh.Nn, dtype='bool')
        nodes = []
        for T, sel in self.mask_cell.items():
            nodes.append(self.mask.cells[T][sel])
        nodes = np.hstack(nodes)
        self.mask_node[np.unique(nodes)] = True
        self.mask_M = np.tile(self.mask_node, (self.imref.ndim, 1)).ravel()

    def set_init(self, U_init, mesh=None, coef=1, mask=None):
        if U_init is None:
            self.U_init = np.zeros((self.mesh.Nn, self.imref.ndim), dtype='f4')
            return
        U_init = U_init[:,:self.imref.ndim].astype('f8')
        if mesh is None:
            self.U_init = U_init
        else:
            if mask is not None:
                self.U_init = mesh.interp_V(U_init, self.mesh, coef, mask_out=self.mask_node, mask_in=mask, out=('mean', 2))
            else:
                self.U_init = mesh.interp_V(U_init, self.mesh, coef)
        if mask is not None:
            self.U_init[~self.mask_node] = np.nan

    def set_convergence_params(self, itermax=None, normed_dU_min=None, diff_discr_min=None):
        if itermax is not None:
            self.itermax = itermax
        if normed_dU_min is not None:
            self.normed_dU_min = normed_dU_min
        if diff_discr_min is not None:
            self.diff_discr_min = diff_discr_min

    def set_solver(self, solver):
        self.solver = solver

    def compute(self, imdef, prompt=""): #TODO
        #

        #imdef = self.normim(imdef)

        if self.imref.ndim == 2:
            norm = self.mesh.surf().sum()
        else:
            norm = self.mesh.vol().sum()

        M = self.compute_M()

        if self.eq_gap is not None:
            M, KK, alpha = self.eq_gap

        if self.tiko is not None:
            M, NN, alpha = self.tiko

        if self.mask is not None:
            M = M[:,self.mask_M].tocsr()[self.mask_M,:].tocsc()
            if self.eq_gap is not None:
                KK = KK[:,self.mask_M].tocsr()[self.mask_M,:].tocsc()
            if self.tiko is not None:
                NN = NN[:,self.mask_M].tocsr()[self.mask_M,:].tocsc()

        if self.mask is not None:
            U = self.U_init[self.mask_node].T.ravel()
        else:
            U = self.U_init.T.ravel()

        dU = np.zeros_like(U)

        if self.debug_path is not None:
            if self.mask is not None:
                cell_values = {'mc': self.mask_cell}
                point_values = {'mn': self.mask_node}
            else:
                cell_values = {}
                point_values = {}
            debug_mesh = self.mesh.copy()
            debug_mesh.nodes *= 2**self.scale

        solver = self.solver

        M = M.astype('f8')
        LU = None

        for c in range(self.itermax):

            def_uv = self.mesh.interp(imdef, U.reshape((self.imref.ndim,self.mesh.Nn)).T)
            diff = self.imref[self.mesh.roi.slices] - def_uv[self.mesh.roi.slices]
            del def_uv

            if self.mask is not None:
                diff_mask = diff[self.mask[self.imref.roi.slices]]
                residual = ((diff_mask[~np.isnan(diff_mask)]**2).sum()/norm)**.5
            else:
                residual = ((diff[~np.isnan(diff)]**2).sum()/norm)**.5

            if c > 0:
                diff_discr = residual - last_residual

                normed_dU = (dU.dot(dU) / (U.dot(U)))**.5

                logging.info(f"{prompt} {c:3d}: |dU| = {normed_dU:9.5f} ddiscr. = {diff_discr:+9.5f} discr. = {residual:9.5f}")

                if self.debug_path is not None:
                    debug_mesh.save(
                        f'{self.debug_path}_i{c:03d}.vtk', U.reshape((self.imref.ndim,self.mesh.Nn)).T*2**self.scale,
                        cell_values=cell_values, point_values=point_values
                    )

                if normed_dU < self.normed_dU_min:
                    break
                if abs(diff_discr) < self.diff_discr_min:
                    break

            last_residual = residual

            B = self.compute_B(diff).astype('f8')

            if self.mask is not None:
                B = B[self.mask_M]

            if self.eq_gap is not None:
                Bm = -KK.dot(U)
                B = B + alpha*Bm.reshape(B.shape)

            if self.tiko is not None:
                Bm = -NN.dot(U)
                B = B + alpha*Bm.reshape(B.shape)

            with Tictoc("solving"):
                if solver == 'cgs':
                    X, _ = splinalg.cgs(M, B, dU, tol=1e-3, atol=0)
                elif solver == 'bicgstab':
                    X, _ = splinalg.bicgstab(M, B, dU, tol=1e-3, atol=0)
                elif solver == 'spsolve':
                    X = splinalg.spsolve(M, B)
                elif solver == 'lsqr':
                    X, _ = splinalg.lsqr(M, B)

            if np.isnan(X).any():
                logging.warning("solver `%s` failed" % solver)
                raise Exception('DIC failed')

            dU[:] = X

            U += dU

            if self.median > 0:
                if self.mask is not None:
                    U.reshape((self.imref.ndim,self.mesh.Nn))[:,~self.mask_node] = np.nan
                U = self.mesh.median_V(U.reshape((self.imref.ndim,self.mesh.Nn)).T, self.median).T.ravel()
                if self.mask is not None:
                    U.reshape((self.imref.ndim,self.mesh.Nn))[:,~self.mask_node] = np.nan

            if self.mean > 0:
                if self.mask is not None:
                    U.reshape((self.imref.ndim,self.mesh.Nn))[:,~self.mask_node] = np.nan
                U = self.mesh.mean_V(U.reshape((self.imref.ndim,self.mesh.Nn)).T, self.mean).T.ravel()
                if self.mask is not None:
                    U.reshape((self.imref.ndim,self.mesh.Nn))[:,~self.mask_node] = np.nan


        return U.reshape((self.imref.ndim,self.mesh.Nn)).T

