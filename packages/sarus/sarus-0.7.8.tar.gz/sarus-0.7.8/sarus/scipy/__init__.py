# flake8: noqa
import scipy

from sarus.dataspec_wrapper import DataSpecWrapper
from sarus.utils import init_wrapped, register_ops


@init_wrapped
class bsr_array(DataSpecWrapper[scipy.sparse.bsr_array]):
    ...


@init_wrapped
class coo_array(DataSpecWrapper[scipy.sparse.coo_array]):
    ...


@init_wrapped
class csc_array(DataSpecWrapper[scipy.sparse.csc_array]):
    ...


@init_wrapped
class csr_array(DataSpecWrapper[scipy.sparse.csr_array]):
    ...


@init_wrapped
class dia_array(DataSpecWrapper[scipy.sparse.dia_array]):
    ...


@init_wrapped
class dok_array(DataSpecWrapper[scipy.sparse.dok_array]):
    ...


@init_wrapped
class lil_array(DataSpecWrapper[scipy.sparse.lil_array]):
    ...


@init_wrapped
class bsr_matrix(DataSpecWrapper[scipy.sparse.bsr_matrix]):
    ...


@init_wrapped
class coo_matrix(DataSpecWrapper[scipy.sparse.coo_matrix]):
    ...


@init_wrapped
class csc_matrix(DataSpecWrapper[scipy.sparse.csc_matrix]):
    ...


@init_wrapped
class csr_matrix(DataSpecWrapper[scipy.sparse.csr_matrix]):
    ...


@init_wrapped
class dia_matrix(DataSpecWrapper[scipy.sparse.dia_matrix]):
    ...


@init_wrapped
class dok_matrix(DataSpecWrapper[scipy.sparse.dok_matrix]):
    ...


@init_wrapped
class lil_matrix(DataSpecWrapper[scipy.sparse.lil_matrix]):
    ...


@init_wrapped
class spmatrix(DataSpecWrapper[scipy.sparse.spmatrix]):
    ...


register_ops()
