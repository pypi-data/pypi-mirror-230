"""
Frads is an open-source library providing high-level
abstraction of Radiance matrix-based simulation workflows.

Frads automates setup of these simulations by providing
end users with an open-source, high-level abstraction of
the Radiance command-line workflow (Unix toolbox model),
helping to reduce the steep learning curve and associated
user errors. frads also provides the necessary infrastructure
needed for seamless integration of Radiance and other
modeling tools, such as EnergyPlus.

## Intended audience

1. Developers who are interested in incorporating multi-phase
matrix methods into their software and are seeking examples
and guidance; i.e., LBNL-suggested default parameters and settings; and,
2. Engineering firms, researchers, and students who are comfortable
working in the command-line or Python scripting environment and
tasked with a project that cannot be completed with existing tools.

## Why matrix-based methods?

Matrix algebraic methods reduce the time needed to perform accurate,
ray-tracing based, annual daylight simulations by several orders of
magnitude.

## Why frads?

A good deal of expertise is needed to set up the simulations
properly to achieve the desired level of accuracy.
frads provides users with tools (e.g., `mrad`) that automatically
determine which matrix-based method to use then sets the associated
simulation parameters, helping beginners learn the different matrix
methods by observing the tools’ behavior. The user is still required
to understand basic concepts underlying matrix-based simulation methods
(see [tutorials](https://www.radiance-online.org/learning/tutorials)).

Matrix-based methods also enable accurate, ray-tracing generated,
irradiance, illuminance, and luminance data to be available for
run-time data exchange and co-simulations. frads provides users with
tools that generate the appropriate Radiance-generated
data then interfaces with the “actuator” EMS module in EnergyPlus or
within the Spawn-of-EnergyPlus and Modelica co-simulation environment.
This enables end users to evaluate the performance of buildings with
manual- and automatically-controlled shading and daylighting systems
or other site and building features that can change parametrically
or on a time-step basis.
"""

import logging

from .epjson2rad import epjson_to_rad

from .eprad import EnergyPlusModel, EnergyPlusSetup, ep_datetime_parser

from .matrix import (
    load_matrix,
    load_binary_matrix,
    matrix_multiply_rgb,
    Matrix,
    SunMatrix,
    SensorSender,
    SurfaceSender,
    SkyReceiver,
    SurfaceReceiver,
    ViewSender,
    SunReceiver,
    surfaces_view_factor,
)

from .methods import WorkflowConfig, TwoPhaseMethod, ThreePhaseMethod, FivePhaseMethod

from .sky import (
    gen_perez_sky,
    genskymtx,
    parse_epw,
    parse_wea,
    WeaData,
    WeaMetaData,
)

from .utils import gen_grid, unpack_primitives

from .window import GlazingSystem, AIR, ARGON, KRYPTON, XENON

__version__ = "1.0.1"

logger: logging.Logger = logging.getLogger(__name__)


__all__ = [
    "AIR",
    "ARGON",
    "EnergyPlusModel",
    "EnergyPlusSetup",
    "FivePhaseMethod",
    "GlazingSystem",
    "KRYPTON",
    "Matrix",
    "SensorSender",
    "SkyReceiver",
    "SunMatrix",
    "SunReceiver",
    "SurfaceReceiver",
    "SurfaceSender",
    "ThreePhaseMethod",
    "TwoPhaseMethod",
    "ViewSender",
    "WeaData",
    "WeaMetaData",
    "WorkflowConfig",
    "XENON",
    "ep_datetime_parser",
    "epjson2rad",
    "epjson_to_rad",
    "gen_grid",
    "gen_perez_sky",
    "genskymtx",
    "load_binary_matrix",
    "load_matrix",
    "matrix_multiply_rgb",
    "parse_epw",
    "parse_wea",
    "surfaces_view_factor",
    "unpack_primitives",
]
