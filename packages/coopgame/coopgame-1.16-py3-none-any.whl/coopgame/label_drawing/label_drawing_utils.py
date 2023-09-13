import pygame
from dataclasses import dataclass, asdict
from cooptools.colors import Color
from coopgame.label_drawing.pyLabel import TextAlignmentType
from cooptools.anchor import Anchor2D, CardinalPosition
import logging
from typing import Tuple, Dict
from coopstructs.geometry import Rectangle
import coopgame.pygamehelpers as help
from coopgame.pointdrawing import point_draw_utils as putils
from coopgame.surfaceManager import SurfaceGroup

logger = logging.getLogger(__name__)

DEFAULT_FONT = pygame.font.Font(None, 20)

@dataclass(frozen=True)
class DrawLabelArgs:
    color: Color = None
    font: pygame.font.Font = None
    alignment: TextAlignmentType = None
    anchor_alignment: CardinalPosition = None
    alpha: float = None
    offset: Tuple[int, int] = None

    def with_(self, **kwargs):
        kw = asdict(self)
        kw.update(kwargs)
        return DrawLabelArgs(**kw)

def get_font_size(
        font: pygame.font.Font,
        text: str
):
    return font.size(text)

def draw_label(hud: pygame.Surface,
               text: str,
               args: DrawLabelArgs,
               pos: Tuple[float, float] = None,
               offset_rect: Rectangle = None,
               deb: bool = False
               ):
    font = args.font
    if font is None:
        font = DEFAULT_FONT

    if pos is None and offset_rect is None:
        raise ValueError(f"At least one of pos and rect cannot be none")

    if offset_rect is None:
        pos = [int(x) for x in pos[:2]]
        if args.offset:
            pos = pos[0] + args.offset[0], pos[1] + args.offset[1]

        anchor_alignment = args.anchor_alignment if args.anchor_alignment is not None else CardinalPosition.TOP_LEFT

        offset_rect = Rectangle(
            anchor=Anchor2D(pt=pos,
                            dims=get_font_size(font, text),
                            cardinality=anchor_alignment,
                            inverted_y=True
                            )
        )

    color=args.color
    if color is None:
        color = Color.BLUE

    alignment = args.alignment
    if alignment is None:
        alignment = TextAlignmentType.TOPLEFT

    rendered_txt = font.render(text, True, color.value)

    alpha = args.alpha
    if alpha:
        rendered_txt.set_alpha(alpha * 100)

    if deb:
        help.draw_box(
            surface=hud,
            rect=offset_rect,
            outline_color=Color.PINK,
            anchor_draw_args=putils.DrawPointArgs(
                color=Color.HOT_PINK,
                radius=4
            ),
            corner_draw_args=putils.DrawPointArgs(
                color=Color.LIGHT_BLUE,
                radius=1
            )
        )

    try:
        rect = rendered_txt.get_rect()
        align_coords = alignment_coords_for_type_rect(alignment, offset_rect)
        setattr(rect, alignment.value, align_coords)
        hud.blit(rendered_txt, rect)
        return rendered_txt
    except Exception as e:
        logger.error(f"{e}")

def alignment_coords_for_type_rect(alignment: TextAlignmentType, rect: Rectangle) -> Tuple[float, float]:
    """
    Note the orientation shift from top to bottom bc of the pygame inversion
    """
    switch = {
        TextAlignmentType.TOPRIGHT:      lambda: rect.TopRight,
        TextAlignmentType.TOPLEFT:       lambda: rect.TopLeft,
        TextAlignmentType.TOPCENTER:     lambda: rect.TopCenter,
        TextAlignmentType.BOTTOMLEFT:    lambda: rect.BottomLeft,
        TextAlignmentType.BOTTOMRIGHT:   lambda: rect.BottomRight,
        TextAlignmentType.RIGHTCENTER:   lambda: rect.RightCenter,
        TextAlignmentType.BOTTOMCENTER:  lambda: rect.BottomCenter,
        TextAlignmentType.LEFTCENTER:    lambda: rect.LeftCenter,
        TextAlignmentType.CENTER:        lambda: rect.Center
    }

    return switch.get(alignment)()

def draw_dict(dict_to_draw: Dict,
              draw_args: DrawLabelArgs,
              surface: pygame.Surface,
              total_game_time_sec: float,
              title: str = None,
              inter_line_buffer: int = 3,
              deb: bool=False):

    tracked_time = [(key, val) for key, val in dict_to_draw.items()]
    tracked_time.sort(key=lambda x: x[1], reverse=True)

    txt_lmbda = lambda key, val: f"{key}: {round(val, 2)} sec ({round(val / total_game_time_sec * 100, 1)}%)"

    rendered_txt = draw_label(
        hud=surface,
        text=title,
        args=draw_args,
        pos=(0, 0),
        deb=deb
    )

    y_off = rendered_txt.get_rect().height + inter_line_buffer
    for key, val in tracked_time:

        rendered_txt = draw_label(
            hud=surface,
            text=txt_lmbda(key, val),
            args=draw_args,
            pos=(0, y_off),
            deb=deb
        )

        y_off += rendered_txt.get_rect().height + inter_line_buffer

    return y_off


def label_surface_group(
        labels: Dict[str, str],
        positions: Dict[str, Tuple[float, float]] = None,
        draw_label_args: DrawLabelArgs | Dict[str, DrawLabelArgs] = None
) -> SurfaceGroup:
    if draw_label_args is None:
        return None

    surf_lookups = {}
    surface_pos = {}
    for id, label in labels.items():
        if type(draw_label_args) == DrawLabelArgs:
            args = draw_label_args
        else:
            args = draw_label_args[id]

        font = args.font
        if font is None:
            font = DEFAULT_FONT

        surf = help.init_surface(get_font_size(font, text=label))

        draw_label(surf,
                  text=label,
                  args=args,
                   pos=(0, 0))
        surf_lookups[id] = surf

        surface_pos[id] = positions.get(id, (0, 0)) if positions is not None else (0, 0)

    return SurfaceGroup(surfaces_lookup=surf_lookups,
                        surface_pos=surface_pos
                        )