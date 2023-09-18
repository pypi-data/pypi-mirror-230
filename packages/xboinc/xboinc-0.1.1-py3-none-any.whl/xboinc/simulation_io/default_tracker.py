# copyright ############################### #
# This file is part of the Xboinc Package.  #
# Copyright (c) CERN, 2023.                 #
# ######################################### #

import xtrack as xt
import xfields as xf
import xobjects as xo
import xcoll as xc


# ===============================================================================================
# IMPORTANT
# ===============================================================================================
# Only make changes to this file just before a minor version bump (need a separate commit though)
# to avoid having multiple xboinc versions with out-of-sync executables.
# ===============================================================================================

def get_default_tracker():
    """
    Returns a default tracker object.
    """

    # Dummy line containing all supported element types
    default_line = xt.Line(elements=[
        xt.Marker(),
        xt.Drift(),
        xt.Bend(length=1.0),
        xt.Multipole(),
        xt.CombinedFunctionMagnet(length=1.0),
        xt.Quadrupole(length=1.0),
        xt.Sextupole(length=1.0),
        xt.SimpleThinBend(),
        xt.SimpleThinQuadrupole(),
        xt.ReferenceEnergyIncrease(),
        xt.Cavity(),
        xt.Solenoid(length=1.0),
        xt.XYShift(),
        xt.Elens(),
        xt.NonLinearLens(),
        xt.Wire(),
        xt.SRotation(),
        xt.XRotation(),
        xt.YRotation(),
        xt.ZetaShift(),
        xt.RFMultipole(knl=[0], pn=[0]),
#        xt.Fringe(),
#        xt.Wedge(),
        xt.DipoleEdge(),
        xt.Exciter(nsamples=1),
        xt.LineSegmentMap(),
        xt.FirstOrderTaylorMap(),
        xf.BeamBeamBiGaussian2D(
            other_beam_Sigma_11=1.,
            other_beam_Sigma_33=1.,
            other_beam_num_particles=0.,
            other_beam_q0=1.,
            other_beam_beta0=1.,
        ),
#         # Doesn't work because issue with definition of atomicAdd when generating executable
#         xf.BeamBeamBiGaussian3D(
#             slices_other_beam_zeta_center=[0],
#             slices_other_beam_num_particles=[0],
#             phi=0.,
#             alpha=0,
#             other_beam_q0=1.,
#             slices_other_beam_Sigma_11=[1],
#             slices_other_beam_Sigma_12=[0],
#             slices_other_beam_Sigma_22=[0],
#             slices_other_beam_Sigma_33=[1],
#             slices_other_beam_Sigma_34=[0],
#             slices_other_beam_Sigma_44=[0],
#         ),
#         # Doesn't work because fieldmap in different buffer
#         xf.ElectronCloud(fieldmap=xf.TriCubicInterpolatedFieldMap(
#             x_range=(0.,1.), nx=10,
#             y_range=(0.,1.), ny=10,
#             z_range=(0.,1.), nz=10
#         )),
#         # Doesn't work because issue with definition of atomicAdd when generating executable
#         xf.ElectronLensInterpolated(
#             x_range=(0.,1.), nx=10,
#             y_range=(0.,1.), ny=10
#         ),
#         # Doesn't work because issue with definition of atomicAdd when generating executable
#         xf.SpaceCharge3D(
#             x_range=(0.,1.), nx=10,
#             y_range=(0.,1.), ny=10,
#             z_range=(0.,1.), nz=10
#         ),
        xc.BlackAbsorber(length=1),
        xc.EverestCollimator(length=1, material=xc.materials.Silicon),
        xc.EverestCrystal(length=1, material=xc.materials.SiliconCrystal),
        xt.LimitRect(),
        xt.LimitRacetrack(),
        xt.LimitEllipse(),
        xt.LimitPolygon(x_vertices=[0.,1.], y_vertices=[0.,1.]),
        xt.LimitRectEllipse(),
        xt.LongitudinalLimitRect()
    ])

    _context = xo.ContextCpu()
    default_line.build_tracker(_context=_context, compile=True,
                               use_prebuilt_kernels=False)
    default_config_hash = default_line.tracker._hashable_config()
    return default_line.tracker, default_config_hash
