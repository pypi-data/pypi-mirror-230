import numpy as np
import cv2

# enum HersheyFonts {
#     FONT_HERSHEY_SIMPLEX        = 0, //!< normal size sans-serif font
# FONT_HERSHEY_PLAIN          = 1, //!< small size sans-serif font
# FONT_HERSHEY_DUPLEX         = 2, //!< normal size sans-serif font (more complex than FONT_HERSHEY_SIMPLEX)
# FONT_HERSHEY_COMPLEX        = 3, //!< normal size serif font
# FONT_HERSHEY_TRIPLEX        = 4, //!< normal size serif font (more complex than FONT_HERSHEY_COMPLEX)
# FONT_HERSHEY_COMPLEX_SMALL  = 5, //!< smaller version of FONT_HERSHEY_COMPLEX
# FONT_HERSHEY_SCRIPT_SIMPLEX = 6, //!< hand-writing style font
# FONT_HERSHEY_SCRIPT_COMPLEX = 7, //!< more complex variant of FONT_HERSHEY_SCRIPT_SIMPLEX
# FONT_ITALIC                 = 16 //!< flag for italic font
# };
DEFAULT_FONT_FACE = cv2.FONT_HERSHEY_TRIPLEX
DEFAULT_FONT_SIZE = 16
DEFAULT_THICKNESS = 1
DEFAULT_TXT_COLOR = (255, 255, 255, 1.0)
DEFAULT_TXT_SHADOW_COLOR = (0, 0, 0, 1.0)


DEFAULT_FONT_SCALE = 0.5


class CustomFont:
    def __init__(self, face=DEFAULT_FONT_FACE,
                 size=None,
                 scale=DEFAULT_FONT_SCALE,
                 thickness=1,
                 color=DEFAULT_TXT_COLOR,
                 shadow_color=DEFAULT_TXT_SHADOW_COLOR):
        self.face = face
        self.thickness = thickness

        if scale is not None:
            self.scale = scale
        elif size is not None:
            self.scale = self.__calc_font_scale_from_size__(size)
        else:
            self.scale = DEFAULT_FONT_SCALE

        self.color = color if color else DEFAULT_TXT_COLOR
        self.shadow_color = shadow_color if shadow_color else DEFAULT_TXT_SHADOW_COLOR

    def __calc_font_scale_from_size__(self, target_size):
        sample_text = "Sample Text for Label - Person: 0.99 %"
        font_face = self.face if self.face else DEFAULT_FONT_FACE
        thickness = self.thickness if self.thickness else DEFAULT_THICKNESS

        min_diff = np.inf
        min_diff_scale = DEFAULT_FONT_SCALE
        for scale in np.arange(0.1, 2.0, 0.1):
            (text_width, text_height) = cv2.getTextSize(text=sample_text,
                                                        fontFace=font_face,
                                                        fontScale=scale,
                                                        thickness=thickness)[0]

            diff = abs(text_height - target_size)
            if min_diff > diff:
                min_diff_scale = scale
                min_diff = diff

        return min_diff_scale

    def set_font_scale_from_size(self, size):
        adjusted_font_scale = self.__calc_font_scale_from_size__(size)

        self.scale = adjusted_font_scale
        return True

    def set_font_thickness(self, thickness):
        if thickness is not None and isinstance(thickness, int):
            self.thickness = thickness
