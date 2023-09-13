import pygame
from coopstructs.geometry import Rectangle
from coopgame.colors import Color
from coopstructs.geometry.vectors.vectorN import Vector2, VectorN
import numpy as np
from typing import List, Dict, Tuple
import logging
from coopgame.label_drawing.pyLabel import TextAlignmentType
import cooptools.geometry_utils.vector_utils as vec
import cooptools.geometry_utils.circle_utils as circ
import math
from cooptools.anchor import Anchor2D, CardinalPosition
from cooptools.matrixManipulation import point_transform_3d
from coopgame.pointdrawing.point_draw_utils import draw_points, DrawPointArgs
import cooptools.matrixManipulation as mm

def mouse_pos() -> vec.FloatVec:
    return pygame.mouse.get_pos()

def mouse_pos_as_vector() -> Vector2:
    """ Get the global coords of the mouse position and convert them to a Vector2 object"""
    return Vector2(*mouse_pos())

def draw_box(surface: pygame.Surface,
             rect: Rectangle,
             color: Color = None,
             width: int = 0,
             outline_color: Color = None,
             anchor_draw_args: DrawPointArgs=None,
             corner_draw_args: DrawPointArgs=None,
             vec_transform: vec.VecTransformer = None
             ):

    if color:
        pygame.draw.rect(surface, color.value, (rect.TopLeft[0], rect.TopLeft[1], rect.width, rect.height), width)
    if outline_color:
        pygame.draw.rect(surface, outline_color.value, (rect.TopLeft[0], rect.TopLeft[1], rect.width, rect.height), 1)
    if anchor_draw_args:
        draw_points(
            surface=surface,
            points={rect.anchor.pos(): anchor_draw_args},
            vec_transformer=vec_transform
        )
    if corner_draw_args:
        draw_points(
            surface=surface,
            points={x: corner_draw_args for x in rect.corner_generator()},
            vec_transformer=vec_transform
        )

def draw_polygon(surface: pygame.Surface,
                 points,
                 color: Color,
                 width: int = 0,
                 alpha: int = 255,
                 vec_transform: vec.VecTransformer = None):
    if type(points[0]) in [VectorN, Vector2]:
        points = [point.as_tuple() for point in points]

    scaled = vec.resolve_vec_transformed_points(
        points=points,
        vec_transformer=vec_transform
    )

    # TODO: this is slower, but may support alpha. It needs to be evaluated further
    # minx = min(point[0] for point in points)
    # maxx = max(point[0] for point in points)
    # miny = min(point[1] for point in points)
    # maxy = max(point[1] for point in points)
    #
    # points = [(point[0] - minx, point[1] - miny) for point in points]
    # s = pygame.Surface((int(maxx - minx), int(maxy - miny)), pygame.SRCALPHA)
    # c_with_alpha = (color.value[0], color.value[1], color.value[2], alpha)
    # pygame.draw.polygon(s, c_with_alpha, points, width)
    # surface.blit(s, (minx, miny))

    c_with_alpha = (color.value[0], color.value[1], color.value[2], alpha)
    points = [x[:2] for x in scaled]
    pygame.draw.polygon(surface, c_with_alpha, points, width)

def draw_arrow(surface: pygame.Surface,
               start: vec.FloatVec,
               end: vec.FloatVec,
               color: Color,
               arrow_height: int = 5,
               leader_line_width: int = 1,
               leader_line: bool = False,
               arrow_width: int = 5):
    if leader_line:
        pygame.draw.line(surface, color.value, start, end, width=leader_line_width)

    if start == end:
        return

    arrow_points = [end, (end[0] - arrow_width / 2, end[1] - arrow_height), (end[0] + arrow_width / 2, (end[1] - arrow_height))]

    unit_backwards = vec.unit_vector(vec.vector_between(end, start))
    unit_backwards = (unit_backwards[0], -unit_backwards[1])  # negative to account for the pygame inverse Y-orientation
    unit_angle = circ.rads_between(unit_backwards)
    adjustment = - math.pi / 2
    rotation_angle = -(unit_angle + adjustment)  # negative to account for the pygame inverse Y-orientation

    rotated_points = []
    for point in arrow_points:
        rotated_points.append(circ.rotated_point(point, (end), rotation_angle))

    pygame.draw.polygon(surface, color.value, rotated_points)

def game_area_coords_from_parent_coords(parent_coords: Vector2, game_area_surface_rectangle: Rectangle) -> Vector2:
    """Converts Global Coords into coords on the game area"""
    return Vector2(parent_coords.x - game_area_surface_rectangle.x, parent_coords.y - game_area_surface_rectangle.y)


def scaled_points_of_a_rect(rect,
                            vec_transformer: vec.VecTransformer) -> List[Vector2]:
    ''' get the rectangle object representing the grid position that was input'''
    return scaled_points(rect.Corners,
                         vec_transformer=vec_transformer)

def scaled_points(points: List[Vector2],
                  vec_transformer: vec.VecTransformer=None) -> List[Vector2]:

    if vec_transformer is None:
        return points

    points = vec.resolve_vec_transformed_points(
        points=[x.as_tuple() for x in points],
        vec_transformer=vec_transformer
    )

    return [Vector2.from_tuple(point) for point in points]


def viewport_point_on_plane(viewport_point: Vector2,
                            game_area_rect,
                            vec_transformer:vec.VecTransformer=None) -> vec.FloatVec:
    points_on_plane = scaled_points_of_a_rect(game_area_rect,
                                              vec_transformer=vec_transformer)

    projected = vec.points_projected_to_plane(
        [viewport_point.as_tuple()],
        plane_points=points_on_plane
    )[0]

    return projected

def scaled_points_to_normal_points(points: List[Vector2], draw_scale_matrix=None):
    translated_points = [(point.x, point.y, 0, 1) for point in points]
    normal_array = scaled_array_to_normal_array(scaled_array=translated_points, draw_scale_matrix=draw_scale_matrix)
    normal_points = [Vector2(point[0], point[1]) for point in normal_array]

    return normal_points


def scaled_array_to_normal_array(scaled_array, draw_scale_matrix=None):
    if draw_scale_matrix is None:
        draw_scale_matrix = np.identity(4)

    draw_scale_matrix_inv = np.linalg.inv(draw_scale_matrix)
    normal_points = draw_scale_matrix_inv.dot(np.transpose(scaled_array))

    normal_points = np.reshape(normal_points, (-1, 2))

    return normal_points


def normal_points_to_scaled_points(points: List[Vector2], draw_scale_matrix=None):
    return scaled_points(points, draw_scale_matrix)


def mouse_in_plane_point(game_area_rect: Rectangle, draw_scale_matrix=None):
    # test = draw_scale_matrix_inv.dot(draw_scale_matrix)
    """Gets the mouse position and converts it to a grid position"""
    mouse_game_area_coord = game_area_coords_from_parent_coords(parent_coords=mouse_pos_as_vector(),
                                                                game_area_surface_rectangle=game_area_rect)
    mouse_plane_point = viewport_point_on_plane(mouse_game_area_coord, game_area_rect, draw_scale_matrix)

    return mouse_plane_point


def normal_mouse_position(game_area_rect: Rectangle, draw_scale_matrix=None) -> Vector2:
    # test = draw_scale_matrix_inv.dot(draw_scale_matrix)
    """Gets the mouse position and converts it to a grid position"""
    # mouse_game_area_coord = game_area_coords_from_parent_coords(parent_coords=mouse_pos_as_vector(), game_area_surface_rectangle=game_area_rect)
    mouse_plane_point = mouse_in_plane_point(game_area_rect, draw_scale_matrix)
    points = np.array([mouse_plane_point[0], mouse_plane_point[1], mouse_plane_point[2], 1])

    normal_array = scaled_array_to_normal_array(points, draw_scale_matrix)

    return Vector2(normal_array[0][0], normal_array[0][1])

def calculate_fps(frame_times: List):
    avg_sec_per_frame = sum(frame_times) / len(frame_times) / 1000.0
    fps = 1 / avg_sec_per_frame if avg_sec_per_frame > 0 else 0
    return fps

def init_surface(dims):
    surface = pygame.Surface(dims).convert()
    surface.set_colorkey(Color.BLACK.value)
    return surface

def draw_mouse_pos(args: DrawPointArgs,
                   screen: pygame.Surface):
    draw_points(
        {tuple(int(x) for x in mouse_pos()): args},
        surface=screen,
    )
