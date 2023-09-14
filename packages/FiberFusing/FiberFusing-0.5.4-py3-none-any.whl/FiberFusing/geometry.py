#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Third-party imports
import logging
import numpy
from dataclasses import dataclass, field
from scipy.ndimage import gaussian_filter

# MPSPlots imports
from MPSPlots import colormaps
from MPSPlots.Render2D import Scene2D, ColorBar, Axis, Mesh

# FiberFusing imports
from FiberFusing import utils
from FiberFusing.axes import Axes
from FiberFusing.tools import plot_style


@dataclass
class Geometry(object):
    """
    Class represent the refractive index (RI) geometrique profile which
    can be used to retrieve the supermodes.
    """
    background: object
    """ Geometrique object representing the background (usually air). """
    additional_structure_list: list = field(default_factory=list)
    """ List of geometrique object representing the fiber structure. """
    fiber_list: list = field(default_factory=list)
    """ List of fiber structure to add. """
    x_bounds: list = 'auto-centering'
    """ X boundary to render the structure, argument can be either list or a string from ['auto', 'left', 'right', 'centering']. """
    y_bounds: list = 'auto-centering'
    """ Y boundary to render the structure, argument can be either list or a string from ['auto', 'top', 'bottom', 'centering']. """
    resolution: int = 100
    """ Number of point (x and y-direction) to evaluate the rendering. """
    index_scrambling: float = 0
    """ Index scrambling for degeneracy lifting. """
    gaussian_filter: int = None
    """ Standard deviation of the gaussian blurring for the mesh and gradient. """
    boundary_pad_factor: float = 1.3
    """ The factor that multiply the boundary value in order to keep padding between mesh and boundary. """

    def generate_coordinate_system(self) -> None:
        """
        Generates the coordinate system (Axes) for the mesh construction

        :returns:   No returns
        :rtype:     None
        """
        min_x, min_y, max_x, max_y = self.get_boundaries()

        self.coordinate_system = Axes(
            min_x=min_x,
            max_x=max_x,
            min_y=min_y,
            max_y=max_y,
            nx=self.resolution,
            ny=self.resolution
        )

        self.coordinate_system.centering(factor=self.boundary_pad_factor)

        self.interpret_y_boundary()

        self.interpret_x_boundary()

    def add_fiber(self, *fibers):
        """
        Adds a fiber structure to the geometry. The fibers than can be added
        have to be defined with the generic_fiber class in fiber_catalogue.py

        :param      fibers:  The fibers to be added
        :type       fibers:  tuple
        """
        for fiber in fibers:
            self.fiber_list.append(fiber)

    def add_structure(self, *structures):
        """
        Adds a custom structure to the geometry.

        :param      structures:  The fibers to be added
        :type       structures:  tuple
        """
        for structure in structures:
            self.additional_structure_list.append(structure)

    @property
    def structure_list(self) -> list:
        """
        Returns list of all the optical structure to be considered for the mesh construct.

        :returns:   List of the optical structures
        :rtype:     list
        """

        return [self.background, *self.additional_structure_list, *self.fiber_list]

    def interpret_y_boundary(self) -> None:
        """
        Interpret the y_bound parameter.
        If the parameter is in ["top", "bottom", "centering"], it returns
        an auto-evaluated boundary

        :param      y_bound:  The y boundary to be interpreted
        :type       y_bound:  list

        :returns:   The interpreted y boundary
        :rtype:     list
        """
        if isinstance(self.y_bounds, (list, tuple)):
            self.coordinate_system.y_bounds = self.y_bounds

        elif isinstance(self.y_bounds, str):
            arguments = self.y_bounds.split('-')
            if 'centering' in arguments:
                self.coordinate_system.y_centering()
            if 'top' in arguments:
                self.coordinate_system.set_top()
            if 'bottom' in arguments:
                self.coordinate_system.set_bottom()

    def get_boundaries(self) -> tuple:
        """
        Gets the boundaries containing the collection of defined structures.
        The list returns min_x, min_y, max_x, max_y.

        :returns:   The boundaries.
        :rtype:     tuple
        """
        if self.structure_list == []:
            raise ValueError('No internal structure provided for computation of the mesh.')

        min_x, min_y, max_x, max_y = [], [], [], []

        for obj in [*self.additional_structure_list, *self.fiber_list]:
            boundaries = obj.get_structure_max_min_boundaries()

            min_x.append(boundaries[0])
            min_y.append(boundaries[1])
            max_x.append(boundaries[2])
            max_y.append(boundaries[3])

        return (
            numpy.min(min_x),
            numpy.min(min_y),
            numpy.max(max_x),
            numpy.max(max_y)
        )

    def interpret_x_boundary(self) -> None:
        """
        Interpret the x_bound parameter.
        If the parameter is in ["left", "right", "centering"], it returns
        an auto-evaluated boundary

        :param      x_bound:  The y boundary to be interpreted
        :type       x_bound:  list

        :returns:   The interpreted y boundary
        :rtype:     list
        """
        if isinstance(self.x_bounds, (list, tuple)):
            self.coordinate_system.x_bounds = self.x_bounds

        elif isinstance(self.x_bounds, str):
            arguments = self.x_bounds.split('-')

            if 'centering' in arguments:
                self.coordinate_system.x_centering()
            if 'right' in arguments:
                self.coordinate_system.set_right()
            if 'left' in arguments:
                self.coordinate_system.set_left()

    @property
    def max_index(self) -> float:
        return max([obj.index for obj in self.structure_list])[0]

    @property
    def min_index(self) -> float:
        return min([obj.index for obj in self.structure_list])[0]

    def get_index_range(self) -> list:
        """
        Returns the list of all index associated to the element of the geometry.
        """
        return [float(obj.index) for obj in self.structure_list]

    def rotate(self, angle: float) -> None:
        """
        Rotate the full geometry

        :param      angle:  Angle to rotate the geometry, in degrees.
        :type       angle:  float
        """
        for obj in self.structure_list:
            obj = obj.rotate(angle=angle)

    def generate_coordinate_mesh_gradient(self) -> None:
        self.generate_coordinate_system()

        self.generate_mesh()

        self.generate_n2_rho_gradient()

    def randomize_fiber_structures_index(self, random_factor: float) -> None:
        """
        Randomize the refractive index of the fiber structures

        :param      random_factor:  The random factor
        :type       random_factor:  float

        :returns:   No returns
        :rtype:     None
        """
        for fiber in self.fiber_list:
            for structure in fiber.inner_structure:
                structure.index += structure.index * self.index_scrambling * numpy.random.rand()

    def rasterize_polygons(self, coordinates: numpy.ndarray) -> numpy.ndarray:
        """
        Returns the rasterize mesh of the object.

        :param      coordinates:  The coordinates to which evaluate the mesh.
        :type       coordinates:  { type_description }
        :param      n_x:          The number of point in the x direction
        :type       n_x:          int
        :param      n_y:          The number of point in the y direction
        :type       n_y:          int

        :returns:   The rasterized mesh
        :rtype:     numpy.ndarray
        """
        mesh = numpy.zeros(self.coordinate_system.shape)

        self.background.overlay_structures_on_mesh(
            mesh=mesh,
            coordinate_system=self.coordinate_system
        )

        for structure in self.additional_structure_list:
            structure.overlay_structures_on_mesh(
                mesh=mesh,
                coordinate_system=self.coordinate_system
            )

        if self.index_scrambling != 0:
            self.randomize_fiber_structures_index(random_factor=self.index_scrambling)

        for fiber in self.fiber_list:
            fiber.overlay_structures_on_mesh(
                mesh=mesh,
                coordinate_system=self.coordinate_system,
                structures_type='inner_structure'
            )

        return mesh

    def add_background_to_mesh(self, mesh: numpy.ndarray) -> numpy.ndarray:
        raster = self.background.get_rasterized_mesh(coordinate_system=self.coordinate_system)
        mesh[numpy.where(raster != 0)] = 0
        raster *= self.background.index
        mesh += raster

    def generate_mesh(self) -> numpy.ndarray:
        self.coords = numpy.vstack(
            (self.coordinate_system.x_mesh.flatten(), self.coordinate_system.y_mesh.flatten())
        ).T

        self.mesh = self.rasterize_polygons(coordinates=self.coords)

        if self.gaussian_filter is not None:
            self.mesh = gaussian_filter(input=self.mesh, sigma=self.gaussian_filter)

        return self.mesh

    def generate_n2_rho_gradient(self) -> numpy.ndarray:
        self.gradient = utils.get_rho_gradient(
            mesh=self.mesh**2,
            coordinate_system=self.coordinate_system
        )

        return self.gradient

    def render_patch_on_ax(self, ax: Axis) -> None:
        """
        Add the patch representation of the geometry into the give ax.

        :param      ax:   The ax to which append the representation.
        :type       ax:   Axis
        """
        for structure in self.additional_structure_list:
            structure.render_patch_on_ax(ax=ax)

        for fiber in self.fiber_list:
            fiber.render_patch_on_ax(ax=ax)

        ax.set_style(**plot_style.geometry)
        ax.title = 'Coupler index structure'

    def render_gradient_on_ax(self, ax: Axis) -> None:
        """
        Add the rasterized representation of the gradient of the geometrys into the give ax.

        :param      ax:   The ax to which append the representation.
        :type       ax:   Axis
        """
        ax.set_style(**plot_style.geometry)

        colorbar = ColorBar(
            log_norm=True,
            position='right',
            numeric_format='%.1e',
            symmetric=True
        )

        artist = Mesh(
            x=self.coordinate_system.x_vector,
            y=self.coordinate_system.y_vector,
            scalar=self.gradient,
            colormap=colormaps.blue_white_red
        )

        ax.colorbar = colorbar
        ax.title = 'Refractive index gradient'
        ax.add_artist(artist)

    def render_mesh_on_ax(self, ax: Axis) -> None:
        """
        Add the rasterized representation of the geometry into the give ax.

        :param      ax:   The ax to which append the representation.
        :type       ax:   Axis
        """
        ax.set_style(**plot_style.geometry)

        colorbar = ColorBar(
            discreet=False,
            position='right',
            numeric_format='%.4f'
        )

        artist = Mesh(
            x=self.coordinate_system.x_vector,
            y=self.coordinate_system.y_vector,
            scalar=self.mesh,
            colormap='Blues'
        )

        ax.colorbar = colorbar
        ax.title = 'Rasterized mesh'
        ax.add_artist(artist)

    def plot(self, show_patch: bool = True, show_mesh: bool = True, show_gradient: bool = True) -> None:
        """
        Plot the different representations [patch, raster-mesh, raster-gradient]
        of the geometry.
        """
        self.generate_coordinate_mesh_gradient()

        figure = Scene2D(unit_size=(4, 4), tight_layout=True)
        col = 0

        if show_patch:
            ax = Axis(row=0, col=col)
            self.render_patch_on_ax(ax)
            figure.add_axes(ax)
            col += 1

        if show_mesh:
            ax = Axis(row=0, col=col)
            self.render_mesh_on_ax(ax)
            figure.add_axes(ax)
            col += 1

        if show_gradient:
            ax = Axis(row=0, col=col)
            self.render_gradient_on_ax(ax)
            figure.add_axes(ax)
            col += 1

        return figure

# -
