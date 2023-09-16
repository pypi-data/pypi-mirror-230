from gpaw import GPAW
from gpaw.eigensolvers.rmmdiis import RMMDIIS
from ase import Atoms
from gpaw.test import equal


def test_eigen_keep_htpsit():
    atoms = Atoms('H')
    atoms.center(3.0)

    convergence = {'eigenstates': 1e-2, 'density': 1e-2}
    base_params = dict(
        mode='fd',
        nbands=2,
        convergence=convergence,
        maxiter=20)
    # Keep htpsit
    calc = GPAW(**base_params, eigensolver=RMMDIIS(keep_htpsit=True))
    atoms.calc = calc
    e0 = atoms.get_potential_energy()

    # Do not keep htpsit
    calc = GPAW(**base_params, eigensolver=RMMDIIS(keep_htpsit=False))
    atoms.calc = calc
    e1 = atoms.get_potential_energy()

    equal(e0, e1, 1e-12)
