from typing import List

from coopgame.gameTemplate import GameTemplate, BuiltInSurfaceType
from coopgame.spriteHandling.spritePoseHandler import SpritePoseHandler
from coopgame.spriteHandling.spriteFolder import SpriteFolderHandler
from coopgame.spriteHandling.sprites import AnimatedPoseSprite
from cooptools.toggles import IntegerRangeToggleable
from coopstructs.vectors import Vector2
import pygame
import coopgame.pygamehelpers as help

SPRITE_DIRS = [
    r'C:\Users\tburns\Downloads\ninjaadventurenew\png',
    r'C:\Users\tburns\Downloads\freeknight\png',
    r'C:\Users\tburns\Downloads\zombiefiles\png\male',
    r'C:\Users\tburns\Downloads\zombiefiles\png\female',
    r'C:\Users\tburns\Downloads\craftpix-net-786503-free-spaceship-pixel-art-sprite-sheets\Fighter'
]

class SpriteTester(GameTemplate):

    def __init__(self):
        super().__init__()
        self.sprite_handler = SpritePoseHandler.from_spritefolder(
            SpriteFolderHandler(SPRITE_DIRS[4]))

        self.animation_cycle = IntegerRangeToggleable(min=10, max=500, step_size=25)

        self.anim_sprite = AnimatedPoseSprite(
            id='main',
            init_pos=Vector2(0, 0),
            pose_handler=self.sprite_handler,
            animation_cycle_ms=lambda: self.animation_cycle.value,
            width=int(self.screen_width / 3),
            height=int(self.screen_height)
        )

    def initialize_game(self):
        pass

    def draw(self, frames: int, debug_mode: bool = False):
        self.anim_sprite.blit(self.screen)
        current_pose_data = self.anim_sprite.pose_handler.get_current()
        help.draw_text(f"Current Pose: {current_pose_data['pose']}, "
                       f"anim_idx: {current_pose_data['animation_idx']}, "
                       f"anim cycle: {self.animation_cycle.value}"
                       , self.screen)


    def model_updater(self, delta_time_ms: int):
        pass

    def sprite_updater(self, delta_time_ms: int):
        self.anim_sprite.animate(delta_time_ms)

    def on_resize(self):
        pass

    def _increase_animation_cycle(self):
        self.animation_cycle.toggle(loop=False)

    def _decrease_animation_cycle(self):
        self.animation_cycle.toggle(reverse=True, loop=False)

    def register_keys(self):
        self.register_action_to_keys((pygame.K_LEFT,),
                                     lambda key_pressed_args: self.anim_sprite.pose_handler.decrement_pose(),
                                     react_while_holding=False)
        self.register_action_to_keys((pygame.K_RIGHT,),
                                     lambda key_pressed_args: self.anim_sprite.pose_handler.increment_pose(),
                                     react_while_holding=False)
        self.register_action_to_keys((pygame.K_UP,),
                                     lambda key_pressed_args: self._decrease_animation_cycle(),
                                     react_while_holding=False)
        self.register_action_to_keys((pygame.K_DOWN,),
                                     lambda key_pressed_args: self._increase_animation_cycle(),
                                     react_while_holding=False)
    def update_built_in_surfaces(self, surface_types: List[BuiltInSurfaceType]):
        pass

if __name__ == "__main__":
    game = SpriteTester()
    game.main()