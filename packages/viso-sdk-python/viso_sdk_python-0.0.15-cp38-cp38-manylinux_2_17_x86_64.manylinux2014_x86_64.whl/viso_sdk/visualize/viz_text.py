import os

from PIL import ImageFont
from viso_sdk.constants import ROOT_DIR
from viso_sdk.logging import get_logger
from viso_sdk.visualize.palette import get_rgba_color


logger = get_logger("vis-font")

DEFAULT_FONT_SIZE = 15
# DEFAULT_THICKNESS = 1
DEFAULT_TXT_COLOR = (255, 255, 255, 1.0)
DEFAULT_SHADOW_COLOR = (0, 0, 0, 1.0)

# print(ASSETS_DIR, os.path.exists(ASSETS_DIR))
FONT_DIR = "../assets/fonts"
# os.path.join(ASSETS_DIR, "fonts")
fonts = [os.path.splitext(fn)[0] for fn in os.listdir(FONT_DIR) if os.path.splitext(fn)[1] == '.ttf']


class VizTextDraw:
    def __init__(self,
                 font: str = None,
                 font_size: int = DEFAULT_FONT_SIZE,
                 # thickness: int = DEFAULT_THICKNESS,
                 font_color=DEFAULT_TXT_COLOR,
                 shadow_color=DEFAULT_SHADOW_COLOR):

        if font_size is None:
            font_size = DEFAULT_FONT_SIZE
        self.font = self.init_font(font_name=font,
                                   font_size=font_size)
        if font_color is None:
            font_color = DEFAULT_TXT_COLOR
        self.default_txt_color = get_rgba_color(font_color)

        if shadow_color is None:
            shadow_color = DEFAULT_SHADOW_COLOR
        self.default_shadow_color = get_rgba_color(shadow_color)

    @staticmethod
    def init_font(font_name, font_size):
        if font_name is None:
            logger.warning(f"font_name is not specified, use default {fonts[0]}")
            font_name = fonts[0]
        elif os.path.isabs(font_name) and os.path.exists(font_name):
            pass
        elif font_name not in fonts:
            logger.warning(f"can not fine such font file {font_name}, use default {fonts[0]}")
            font_name = fonts[0]
        else:
            logger.info(f"load font {font_name}")

        font_file = os.path.join(FONT_DIR, f"{font_name}.ttf")
        show_font = ImageFont.truetype(font_file, font_size)
        return show_font

    def draw_texts(
            self,
            draw,
            text,
            txt_color=None,
            pos=(50, 50),
            large_padding=False,
            fill_rectangle=False, fill_rectangle_color=None,
            show_shadow=False, shadow_color=None):

        # calculate area to put text
        text_width, text_height = draw.textsize(text, self.font)

        padding = max(int(text_height // 4), 2)
        padding_left = padding
        if large_padding:
            padding_top = padding * 2
        else:
            padding_top = padding // 2

        x, y = pos
        if fill_rectangle:
            # put filled text rectangle
            draw.rectangle([(x, y), (x + text_width + padding_left * 2, y - text_height - padding_top)],
                           fill=fill_rectangle_color)

        # shadow effect
        if show_shadow:
            if shadow_color is None:
                shadow_color = self.default_shadow_color
            draw.multiline_text((x + padding + 1, y - text_height - padding_top + 1),
                                font=self.font, text=text, fill=shadow_color)

        # put text above rectangle
        if txt_color is None:
            txt_color = self.default_txt_color
        draw.multiline_text((x + padding, y - text_height - padding_top),
                            font=self.font, text=text, fill=txt_color)

        return draw

    # def draw_
    # if label is not None and isinstance(label, str) and len(label) > 0:
    #     (x0, y0) = label_pos
    #     self.label_drawer.draw_texts(
    #         draw=draw,
    #         text=label, pos=(x0, y0),
    #         large_padding=True,
    #         txt_color=label_color,
    #         show_shadow=True, shadow_color=None,
    #         fill_rectangle=False)


if __name__ == '__main__':
    # from . import Image
    VizTextDraw().draw_texts()
