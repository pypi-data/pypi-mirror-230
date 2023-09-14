from time import ctime

import numpy as np
from ase.units import Ha

from gpaw.response.integrators import Integrand, HilbertTetrahedron, Intraband
from gpaw.response.chi0 import Chi0Calculator
from gpaw.response.pair_functions import SingleQPWDescriptor
from gpaw.response.chi0_data import Chi0DrudeData
from gpaw.response.frequencies import FrequencyGridDescriptor


class Chi0DrudeCalculator(Chi0Calculator):
    """Class for calculating the plasma frequency contribution to Chi0,
    that is, the contribution from intraband transitions inside of metallic
    bands. This corresponds directly to the dielectric function in the Drude
    model."""

    def __init__(self, *args, **kwargs):
        self.base_ini(*args, **kwargs)
        self.task, self.wd = self.construct_integral_task_and_wd()

    @property
    def nblocks(self):
        # The plasma frequencies aren't distributed in memory
        # NB: There can be a mismatch with self.pair.nblocks, which seems
        # dangerous XXX
        return 1

    def calculate(self, wd, rate, spin='all'):
        """Calculate the Drude dielectric response.

        Parameters
        ----------
        wd : FrequencyDescriptor
            Frequencies to evaluate the reponse function at.
        rate : float
            Plasma frequency decay rate (in eV), corresponding to the
            imaginary part of the complex frequency.
        spin : str or int
            If 'all' then include all spins.
            If 0 or 1, only include this specific spin.
        """
        self.print_info(wd, rate)

        # Parse the spin input
        spins = self.get_spins(spin)

        chi0_drude = Chi0DrudeData.from_frequency_descriptor(wd, rate)
        self._calculate(chi0_drude, spins)

        return chi0_drude

    def _calculate(self, chi0_drude: Chi0DrudeData, spins):
        """In-place calculation of the Drude dielectric response function,
        based on the free-space plasma frequency of the intraband transitions.
        """
        # Create a dummy plane-wave descriptor. We need this for the symmetry
        # analysis -> see discussion in gpaw.response.jdos
        qpd = SingleQPWDescriptor.from_q([0., 0., 0.],
                                         ecut=1e-3, gd=self.gs.gd)
        domain, analyzer, prefactor = self.get_integration_domain(qpd, spins)

        # The plasma frequency integral is special in the way that only
        # the spectral part is needed
        integrand = PlasmaFrequencyIntegrand(self, qpd, analyzer)

        # Integrate using temporary array
        tmp_plasmafreq_wvv = np.zeros((1,) + chi0_drude.vv_shape, complex)
        self.integrator.integrate(task=self.task,
                                  domain=domain,  # Integration domain
                                  integrand=integrand,
                                  wd=self.wd,
                                  out_wxx=tmp_plasmafreq_wvv)  # Output array
        tmp_plasmafreq_wvv *= prefactor

        # Store the plasma frequency itself and print it for anyone to use
        plasmafreq_vv = tmp_plasmafreq_wvv[0].copy()
        analyzer.symmetrize_wvv(plasmafreq_vv[np.newaxis])
        chi0_drude.plasmafreq_vv += 4 * np.pi * plasmafreq_vv
        self.context.print('Plasma frequency:', flush=False)
        self.context.print((chi0_drude.plasmafreq_vv**0.5 * Ha).round(2))

        # Calculate the Drude dielectric response function from the
        # free-space plasma frequency
        # χ_D(ω+iη) = ω_p^2 / (ω+iη)^2
        assert chi0_drude.zd.upper_half_plane
        chi0_drude.chi_Zvv += plasmafreq_vv[np.newaxis] \
            / chi0_drude.zd.hz_z[:, np.newaxis, np.newaxis]**2

    def construct_integral_task_and_wd(self):
        if self.integrationmode == 'tetrahedron integration':
            # Calculate intraband transitions at T=0
            fermi_level = self.gs.fermi_level
            wd = FrequencyGridDescriptor([-fermi_level])
            task = HilbertTetrahedron(self.integrator.blockcomm)
        else:
            task = Intraband()

            # We want to pass None for frequency descriptor, but
            # if that goes wrong we'll get TypeError which is unhelpful.
            # This dummy class will give us error messages that allow finding
            # this spot in the code.
            class NotAFrequencyDescriptor:
                pass

            wd = NotAFrequencyDescriptor()
        return task, wd

    def print_info(self, wd, rate):
        isl = ['',
               f'{ctime()}',
               'Calculating drude chi0 with:',
               f'    Number of frequency points:{len(wd)}',
               f'    Plasma frequency decay rate: {rate} eV',
               '',
               self.get_gs_info_string(tab='    ')]
        self.context.print('\n'.join(isl))


class PlasmaFrequencyIntegrand(Integrand):
    def __init__(self, chi0drudecalc, qpd, analyzer):
        self._drude = chi0drudecalc
        self.qpd = qpd
        self.analyzer = analyzer

    def _band_summation(self):
        # Intraband response needs only integrate partially unoccupied bands.
        return self._drude.nocc1, self._drude.nocc2

    def matrix_element(self, k_v, s):
        """NB: In dire need of documentation! XXX."""
        n1, n2 = self._band_summation()
        k_c = np.dot(self.qpd.gd.cell_cv, k_v) / (2 * np.pi)
        kptpair_factory = self._drude.kptpair_factory
        kpt1 = kptpair_factory.get_k_point(s, k_c, n1, n2)
        n_n = range(n1, n2)

        vel_nv = kptpair_factory.pair_calculator().intraband_pair_density(
            kpt1, n_n)

        if self._drude.integrationmode is None:
            f_n = kpt1.f_n
            width = self._drude.gs.get_occupations_width()
            if width > 1e-15:
                dfde_n = - 1. / width * (f_n - f_n**2.0)
            else:
                dfde_n = np.zeros_like(f_n)
            vel_nv *= np.sqrt(-dfde_n[:, np.newaxis])
            weight = np.sqrt(self.analyzer.get_kpoint_weight(k_c) /
                             self.analyzer.how_many_symmetries())
            vel_nv *= weight

        return vel_nv

    def eigenvalues(self, k_v, s):
        """A function that can return the intraband eigenvalues.

        A method describing the integrand of
        the response function which gives an output that
        is compatible with the gpaw k-point integration
        routines."""
        n1, n2 = self._band_summation()
        gs = self._drude.gs
        kd = gs.kd
        k_c = np.dot(self.qpd.gd.cell_cv, k_v) / (2 * np.pi)
        K1 = self._drude.kptpair_factory.find_kpoint(k_c)
        ik = kd.bz2ibz_k[K1]
        kpt1 = gs.kpt_qs[ik][s]
        assert gs.kd.comm.size == 1

        return kpt1.eps_n[n1:n2]
