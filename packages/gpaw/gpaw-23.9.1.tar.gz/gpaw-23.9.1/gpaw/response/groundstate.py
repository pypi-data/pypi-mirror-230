from pathlib import Path
from types import SimpleNamespace

import numpy as np

from ase.units import Ha, Bohr
from ase.utils import lazyproperty

import gpaw.mpi as mpi
from gpaw.ibz2bz import IBZ2BZMaps


class ResponseGroundStateAdapter:
    def __init__(self, calc):
        wfs = calc.wfs

        self.atoms = calc.atoms
        self.kd = wfs.kd
        self.world = calc.world
        self.gd = wfs.gd
        self.finegd = calc.density.finegd
        self.bd = wfs.bd
        self.nspins = wfs.nspins
        self.dtype = wfs.dtype

        self.spos_ac = calc.spos_ac

        self.kpt_u = wfs.kpt_u
        self.kpt_qs = wfs.kpt_qs

        self.fermi_level = wfs.fermi_level
        self.atoms = calc.atoms
        self.pawdatasets = [ResponsePAWDataset(setup) for setup in calc.setups]

        self.pbc = self.atoms.pbc
        self.volume = self.gd.volume

        self.nvalence = wfs.nvalence

        self.ibz2bz = IBZ2BZMaps.from_calculator(calc)

        self._wfs = wfs
        self._density = calc.density
        self._hamiltonian = calc.hamiltonian
        self._calc = calc

    @classmethod
    def from_gpw_file(cls, gpw, context):
        """Initiate the ground state adapter directly from a .gpw file."""
        from gpaw import GPAW, disable_dry_run
        assert Path(gpw).is_file()

        context.print('Reading ground state calculation:\n  %s' % gpw)

        with context.timer('Read ground state'):
            with disable_dry_run():
                calc = GPAW(gpw, txt=None, communicator=mpi.serial_comm)

        return cls(calc)

    @property
    def pd(self):
        # This is an attribute error in FD/LCAO mode.
        # We need to abstract away "calc" in all places used by response
        # code, and that includes places that are also compatible with FD.
        return self._wfs.pd

    @lazyproperty
    def global_pd(self):
        """Get a PWDescriptor that includes all k-points.

        In particular, this is necessary to allow all cores to be able to work
        on all k-points in the case where calc is parallelized over k-points,
        see gpaw.response.kspair
        """
        from gpaw.pw.descriptor import PWDescriptor

        assert self.gd.comm.size == 1
        kd = self.kd.copy()  # global KPointDescriptor without a comm
        return PWDescriptor(self.pd.ecut, self.gd,
                            dtype=self.pd.dtype,
                            kd=kd, fftwflags=self.pd.fftwflags,
                            gammacentered=self.pd.gammacentered)

    def get_occupations_width(self):
        # Ugly hack only used by pair.intraband_pair_density I think.
        # Actually: was copy-pasted in chi0 also.
        # More duplication can probably be eliminated around those.

        # Only works with Fermi-Dirac distribution
        occs = self._wfs.occupations
        assert occs.name in {'fermi-dirac', 'zero-width'}

        # No carriers when T=0
        width = getattr(occs, '_width', 0.0) / Ha
        return width

    def nonpbc_cell_product(self):
        """Volume, area, or length, taken in all non-periodic directions."""
        nonpbc = ~self.pbc
        cell_cv = self.gd.cell_cv
        return abs(np.linalg.det(cell_cv[nonpbc][:, nonpbc]))

    @property
    def nt_sR(self):
        # Used by localft and fxc_kernels
        return self._density.nt_sG

    @property
    def nt_sr(self):
        # Used by localft
        if self._density.nt_sg is None:
            self._density.interpolate_pseudo_density()
        return self._density.nt_sg

    @property
    def D_asp(self):
        # Used by fxc_kernels
        return self._density.D_asp

    def get_pseudo_density(self, gridrefinement=2):
        # Used by localft
        if gridrefinement == 1:
            return self.nt_sR, self.gd
        elif gridrefinement == 2:
            return self.nt_sr, self.finegd
        else:
            raise ValueError(f'Invalid gridrefinement {gridrefinement}')

    def get_all_electron_density(self, gridrefinement=2):
        # Used by fxc, fxc_kernels and localft
        return self._density.get_all_electron_density(
            atoms=self.atoms, gridrefinement=gridrefinement)

    # Things used by EXX.  This is getting pretty involved.
    #
    # EXX naughtily accesses the density object in order to
    # interpolate_pseudo_density() which is in principle mutable.

    def hacky_all_electron_density(self, **kwargs):
        # fxc likes to get all electron densities.  It calls
        # calc.get_all_electron_density() and so we wrap that here.
        # But it also collects to serial (bad), and it also zeropads
        # nonperiodic directions (probably WRONG!).
        #
        # Also this one returns in user units, whereas the calling
        # code actually wants internal units.  Very silly then.
        #
        # ALso, the calling code often wants the gd, which is not
        # returned, so it is redundantly reconstructed in multiple
        # places by refining the "right" number of times.
        n_g = self._calc.get_all_electron_density(**kwargs)
        n_g *= Bohr**3
        return n_g

    # Used by EXX.
    @property
    def hamiltonian(self):
        return self._hamiltonian

    # Used by EXX.
    @property
    def density(self):
        return self._density

    # Ugh SOC
    def soc_eigenstates(self, **kwargs):
        from gpaw.spinorbit import soc_eigenstates
        return soc_eigenstates(self._calc, **kwargs)

    @property
    def xcname(self):
        return self.hamiltonian.xc.name

    def get_xc_difference(self, xc):
        # XXX used by gpaw/xc/tools.py
        return self._calc.get_xc_difference(xc)

    def get_wave_function_array(self, u, n):
        # XXX used by gpaw/xc/tools.py in a hacky way
        return self._wfs._get_wave_function_array(
            u, n, realspace=True)

    def pair_density_paw_corrections(self, qpd):
        from gpaw.response.paw import get_pair_density_paw_corrections
        return get_pair_density_paw_corrections(
            pawdatasets=self.pawdatasets, qpd=qpd, spos_ac=self.spos_ac,
            atomrotations=self.atomrotations)

    def get_pos_av(self):
        # gd.cell_cv must always be the same as pd.gd.cell_cv, right??
        return np.dot(self.spos_ac, self.gd.cell_cv)

    def count_occupied_bands(self, ftol=1e-6):
        """Count the number of filled and non-empty bands.

        ftol : float
            Threshold determining whether a band is completely filled
            (f > 1 - ftol) or completely empty (f < ftol).
        """
        nocc1 = 9999999
        nocc2 = 0
        for kpt in self.kpt_u:
            f_n = kpt.f_n / kpt.weight
            nocc1 = min((f_n > 1 - ftol).sum(), nocc1)
            nocc2 = max((f_n > ftol).sum(), nocc2)
        return nocc1, nocc2

    @property
    def ibzq_qc(self):
        # For G0W0Kernel
        kd = self.kd
        bzq_qc = kd.get_bz_q_points(first=True)
        U_scc = kd.symmetry.op_scc
        ibzq_qc = kd.get_ibz_q_points(bzq_qc, U_scc)[0]

        return ibzq_qc

    def get_ibz_vertices(self):
        # For the tetrahedron method in Chi0
        from gpaw.bztools import get_bz
        # NB: We are ignoring the pbc_c keyword to get_bz() in order to mimic
        # find_high_symmetry_monkhorst_pack() in gpaw.bztools. XXX
        _, ibz_vertices_kc = get_bz(self._calc)
        return ibz_vertices_kc

    def get_aug_radii(self):
        return np.array([max(pawdata.rcut_j) for pawdata in self.pawdatasets])

    @property
    def atomrotations(self):
        return self._wfs.setups.atomrotations


# Contains all the relevant information
# from Setups class for response calculators
class ResponsePAWDataset:
    def __init__(self, setup):
        self.ni = setup.ni
        self.rgd = setup.rgd
        self.rcut_j = setup.rcut_j
        self.l_j = setup.l_j
        self.lq = setup.lq
        self.nabla_iiv = setup.nabla_iiv
        self.data = SimpleNamespace(phi_jg=setup.data.phi_jg,
                                    phit_jg=setup.data.phit_jg)
        self.xc_correction = SimpleNamespace(
            rgd=setup.xc_correction.rgd, Y_nL=setup.xc_correction.Y_nL,
            n_qg=setup.xc_correction.n_qg, nt_qg=setup.xc_correction.nt_qg,
            nc_g=setup.xc_correction.nc_g, nct_g=setup.xc_correction.nct_g,
            nc_corehole_g=setup.xc_correction.nc_corehole_g,
            B_pqL=setup.xc_correction.B_pqL, e_xc0=setup.xc_correction.e_xc0)
        self.hubbard_u = setup.hubbard_u
