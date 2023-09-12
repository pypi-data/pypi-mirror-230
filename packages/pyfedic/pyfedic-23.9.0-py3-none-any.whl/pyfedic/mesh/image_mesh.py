#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from scipy import ndimage
from scipy import sparse

from .regular_mesh import RegularBaseMesh
from ..tictoc import tictoc

class Roi:
    """

    """

    def __init__(self, offset=None, shape=None):
        self.offset = tuple(offset)
        self.shape = tuple(shape)
        self.ndim = len(self.offset)

    def __repr__(self):
        return "Roi with origin at %s and shape %s." % (str(self.offset), str(self.shape))

    @property
    def slices(self):
        return tuple([slice(o, s+o) for o, s in zip(self.offset[:self.ndim], self.shape[:self.ndim])])

    @classmethod
    def from_mesh(cls, mesh):
        ndim = mesh.ndim
        offset = np.floor(mesh.nodes[:,ndim-1::-1].min(axis=0)+0.5).astype(int)
        shape = np.ceil(mesh.nodes[:,ndim-1::-1].max(axis=0)+0.5).astype(int)-offset
        return cls(offset, shape)

    def from_coords(xn, yn, zn=None):
        ndim = 2 if zn is None else 3
        if xn.ndim == 1:
            nodes = np.vstack((xn, yn, zn)).T
            offset = np.floor(nodes[:,ndim-1::-1].min(axis=0)+0.5).astype(int)
            shape = np.ceil(nodes[:,ndim-1::-1].max(axis=0)+0.5).astype(int)-offset
            return Roi(offset, shape)
        else: # xn.shape = (nbr of cell, nbr to bounding) -> (Np, Nc) -> (Nc, 3, Np)
            # (Np*3, Nc) -> (Nc, Np*3)
            nodes = np.vstack((xn, yn, zn)).T.reshape((xn.shape[1], 3, xn.shape[0]))
            offset = np.floor(nodes[:,:,ndim-1::-1].min(axis=0)+0.5).astype(int)
            shape = np.ceil(nodes[:,:,ndim-1::-1].max(axis=0)+0.5).astype(int)
            return [Roi(offset[i,:], shape[i,:]) for i in range(offset.shape[0])]

    def copy(self):
        return Roi(tuple(self.offset), tuple(self.shape))


class ImageMesh:
    ""

    def __init__(self):
        self._roi = Roi.from_mesh(self)
        self._pixN = None
        self._pixmask = None
        self._pixelt = None

    @property
    def roi(self):
        """Bounding box of the mesh. TODO: update this !

        :Exemple:

        >>> mesh = gen_mesh([5, 10], [3, 7.5], zoi=2)
        >>> mesh
        Mesh with 4 cells and 9 nodes of type Q4.
        >>> mesh.xn
        array([ 5.5,  7.5,  9.5,  5.5,  7.5,  9.5,  5.5,  7.5,  9.5])
        >>> mesh.roi.slices
        (slice(3, 9, None), slice(5, 11, None))

        Returns
        -------
        out : tuple of slice
            a slice is returned for each dimension in zyx convention.

        """
        return self._roi

    @property
    def pixN(self):
        """

        Returns
        =======
        out: ndarray

        """

        return self._pixN

    @property
    def pixmask(self):
        """
        Mask for all pixels/voxels inside the mesh.

        Returns
        =======
        out: ndarray
            binary mask.

        """

        return self._pixmask

    @property
    def pixelt(self):
        """

        Returns
        =======
        out: ndarray

        """

        return self._pixelt

    def _pixsum_by_cells_regular(self, image):
        """
        see pixsum_by_cells.
        """

        nelems, zoi = self.regular
        ndim = self.ndim

        pix_coords = np.mgrid[(slice(0,zoi),)*ndim].reshape((ndim, zoi**ndim)).T
        coefs = [np.prod(np.array(nelems)[i+1:]*zoi) for i in range(ndim)]

        result = np.zeros(self.Nc)
        for i, zyx in enumerate(self.iter_Nc()):
            x = np.sum([(pix_coords[:,j] + zyx[j]*zoi)*coefs[j] for j in range(ndim)], axis=0)
            result[i] = image[self.roi.slices].flat[x].sum()

        return result

    @tictoc
    def pixsum_by_cells(self, image):
        """
        Sum all pixel values included in each cells of the mesh.

        Returns
        -------
        result: array_like
            pixel sum for each cells.

        """
        if isinstance(self, RegularBaseMesh):
            return self._pixsum_by_cells_regular(image)

        im = image[self.roi.slices].flat
        result = np.zeros(self.Nc)

        if self.pixelt is None:
            self.compute_pixN()

        for c in range(self.Nc):
            result[c] = im[self.pixelt.indices[self.pixelt.indptr[c]:self.pixelt.indptr[c+1]]].sum()

        return result

    def _compute_pixN_get_sizes(self):
        Np = np.prod(self.roi.shape)
        cs = (Np/self.Nc)**(1/self.ndim)
        Nt = int((np.array(self.roi.shape)/cs*(cs+1)).prod()*2**self.ndim)
        return Np, Nt

    def _compute_pixN_get_pix(self, pp):
        xx, yy, zz = pp.T

        zpix, ypix, xpix = np.meshgrid(
            np.arange(np.floor(zz.min()+0.5), np.ceil(zz.max()+0.5)),
            np.arange(np.floor(yy.min()+0.5), np.ceil(yy.max()+0.5)),
            np.arange(np.floor(xx.min()+0.5), np.ceil(xx.max()+0.5)),
            indexing='ij'
        )

        if self.ndim == 3:
            ipix = (zpix-self.roi.offset[0])*self.roi.shape[1]*self.roi.shape[2] + \
                    (ypix-self.roi.offset[1])*self.roi.shape[2]+xpix-self.roi.offset[2]
        else:
            ipix = (ypix-self.roi.offset[0])*self.roi.shape[1]+xpix-self.roi.offset[1]

        ipix = ipix.astype('i').ravel()
        xpix = xpix.astype('f8').ravel()
        ypix = ypix.astype('f8').ravel()
        zpix = zpix.astype('f8').ravel()

        return ipix, np.vstack((xpix, ypix, zpix)).T

    def _compute_pixN_regular(self, method=1):
        ""

        nelems, zoi = self.regular
        ndim = self.ndim
        nelems = np.array(nelems)

        nnn = np.prod(nelems+1)

        pix_coords = np.mgrid[(slice(0,zoi),)*ndim].reshape((ndim, zoi**ndim)).T
        coords = ((pix_coords - (zoi-1)/2)*2/zoi)[:,::-1]

        Ne = self.cell_type.N(coords).astype('f4').reshape((self.cell_type.n_nodes, zoi**ndim))

        coefs = [np.prod(nelems[i+1:]*zoi) for i in range(ndim)]

        match method:
            case 0:

                XYZ = np.sum([(X[None,:]+Xc.ravel()[:,None])*coefs[i] for i, X, Xc in zip(range(ndim), pix_coords.T, np.mgrid[[slice(0,x) for x in nelems]]*zoi)], axis=0)

                row = np.tile(XYZ, (1, self.cell_type.n_nodes)).flat
                col = np.repeat(self.cells, zoi**ndim)
                data = np.tile(Ne.ravel(), np.prod(nelems))

            case 1:

                dimNe = Ne.size

                data = np.zeros(dimNe*np.prod(nelems), dtype='f4')
                col = np.zeros(dimNe*np.prod(nelems), dtype=int)
                row = np.zeros(dimNe*np.prod(nelems), dtype=int)

                i = 0

                for zyx in self.iter_Nc():
                    x = np.sum([(pix_coords[:, j] + zyx[j]*zoi)*coefs[j] for j in range(ndim)], axis=0)

                    data[dimNe*i:dimNe*(i+1)] = Ne.ravel()
                    row[dimNe*i:dimNe*(i+1)] = np.tile(x, self.cell_type.n_nodes)
                    col[dimNe*i:dimNe*(i+1)] = np.repeat(self.cells[i], zoi**ndim)

                    i += 1

        N = sparse.csc_matrix((data, (row, col)), (np.prod(nelems*zoi), nnn))

        N.eliminate_zeros()

        self._pixN = N
        self._pixmask = np.ones(np.prod(nelems*zoi), dtype='bool')
        self._pixelt = np.repeat(np.arange(np.prod(nelems)), zoi**ndim)

    @tictoc
    def compute_pixN(self):
        ""
        if isinstance(self, RegularBaseMesh):
            return self._compute_pixN_regular()

        self._pixN, done = self.compute_N(points=self, raw=True)
        Np = self._pixN.shape[0]

        pixelt_row = np.arange(Np)[done>0]
        pixelt_col = done[done>0]-1
        pixelt_val = np.ones(pixelt_col.shape, dtype='bool')

        self._pixmask = done.astype('bool')
        self._pixelt = sparse.csc_array((pixelt_val, (pixelt_row, pixelt_col)), shape=(Np, self.Nc))

    def _interp_regular(self, image, U, order=1, out=np.nan):
        """
        see interp
        """
        U = U[:,:image.ndim].copy()
        U[np.isnan(U)] = 0

        nelems, zoi = self.regular
        ndim = self.ndim

        pix_coords = np.mgrid[(slice(0,zoi),)*ndim].reshape((ndim, zoi**ndim)).T
        coords = ((pix_coords - (zoi-1)/2)*2/zoi)[:,::-1]

        Ne = self.cell_type.N(coords).astype('f4').reshape((self.cell_type.n_nodes, zoi**ndim)).T

        coefs = [np.prod(np.array(nelems)[i+1:]*zoi) for i in range(ndim)]

        im_output = np.full_like(image, out, dtype='f4')

        for i, zyx in enumerate(self.iter_Nc()):
            x = np.sum([(pix_coords[:,j] + zyx[j]*zoi)*coefs[j] for j in range(ndim)], axis=0)

            new_coords = np.vstack([pix_coords[:,j] + zyx[j]*zoi + self.roi.offset[j] + Ne @ U.T[::-1][j][self.cells[i]] for j in range(ndim)])

            res = ndimage.map_coordinates(image, new_coords, cval=out, order=order)

            im_output[self.roi.slices].flat[x] = res

        return im_output

    @tictoc
    def interp(self, image, U, order=1, out=np.nan):
        """
        Interpolate the image as it was located on the mesh after
        the displacement field `U` was applied.

        Parameters
        ----------
        U : array_like
            displacement field of size (self.mesh.Nn, self.ndim).
        order : int, optional
            order of the interpolation (default value 1 means linear).
        out : float, optional
            value to set for pixels out of the self.mesh.

        Returns
        -------
        im_output: array_like
            deformed image of the same size as input image according the
            displacement field.

        """
        if isinstance(self, RegularBaseMesh):
            return self._interp_regular(image, U, order, out)

        U = U[:,:image.ndim].copy()
        U[np.isnan(U)] = 0

        im_output = np.full_like(image, out, dtype='f4')

        if self.pixN is None:
            self.compute_pixN()
        N = self.pixN

        new_coords = np.vstack([x.ravel() + N.dot(u) for x, u in zip(np.mgrid[self.roi.slices], U.T[::-1])])

        slices = tuple(slice(max(0,s.start), min(d,s.stop)) for s, d in zip(self.roi.slices, image.shape))
        crop = tuple(slice(y.start - x.start, y.stop - x.start) for x, y in  zip(self.roi.slices, slices))

        pixmask = np.zeros(self.roi.shape, dtype=bool)
        pixmask[crop] = self.pixmask.reshape(self.roi.shape)[crop]

        #im_output[slices].flat[self.pixmask] = ndimage.map_coordinates(image, new_coords[:,self.pixmask], cval=out, order=order)[crop]
        im_output[slices].flat[pixmask[crop].ravel()] = ndimage.map_coordinates(image, new_coords[:,pixmask.flat], cval=out, order=order)
        return im_output

    @tictoc
    def transform(self, image, U, order=1, out=np.nan):
        """
        transform the image using the displacement field `U` holded by
        the mesh.

        In a manner, this function do the opposite to what the
        :func:`pyFEDIC.image.Image.interp` does.

        Parameters
        ----------
        U : array_like
            displacement field of size (self.mesh.Nn, self.ndim).
        order : int, optional
            order of the interpolation (default value 1 means linear).
        out : float, optional
            value to set for pixels out of the self.mesh.

        Returns
        -------
        im_output: array_like
            transformed image of the same size as input image according the
            displacement field.

        """
        mesh = self.copy()
        if U.shape[1] == 2:
            U = np.hstack((U, np.zeros((mesh.Nn,1))))
        mesh.nodes += U
        return ImageMesh(mesh).interp(image, -U)

