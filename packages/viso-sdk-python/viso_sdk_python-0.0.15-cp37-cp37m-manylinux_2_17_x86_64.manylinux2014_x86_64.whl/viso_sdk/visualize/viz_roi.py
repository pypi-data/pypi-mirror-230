import numpy as np
import cv2
from PIL import ImageDraw, Image

from viso_sdk.visualize.viz_text import VizTextDraw
from viso_sdk.visualize.palette import get_rgba_color

# from viso_sdk.logging import get_logger
# logger = get_logger("vis-roi")


DEFAULT_ROI_COLOR = (255, 150, 113, 0.4)
DEFAULT_ROI_OUTLINE_COLOR = (70, 70, 70, 1.0)
DEFAULT_ROI_OUTLINE_THICKNESS = 1
DEFAULT_LABEL_COLOR = (255, 255, 255, 0.4)
DEFAULT_LABEL_SIZE = 20


class VizPolygonDraw:
    def __init__(self,
                 roi_color=DEFAULT_ROI_COLOR,
                 outline_color=DEFAULT_ROI_COLOR,
                 outline_thickness=DEFAULT_ROI_OUTLINE_THICKNESS,
                 show_label=False,
                 label_size=DEFAULT_LABEL_COLOR,
                 label_color=DEFAULT_LABEL_SIZE
                 ):

        self.label_drawer = VizTextDraw(
            font_size=label_size,
            font_color=get_rgba_color(label_color)
        )

        if roi_color is None:
            roi_color = DEFAULT_ROI_COLOR
        self.default_roi_color = get_rgba_color(roi_color)

        if outline_color is None:
            if roi_color is not None:
                outline_color = [roi_color[0] + 10, roi_color[1] + 10, roi_color[2] + 10, roi_color[3]]
            else:
                outline_color = DEFAULT_ROI_OUTLINE_COLOR
        self.default_outline_color = get_rgba_color(outline_color)

        # if outline_thickness is None:
        #     outline_thickness = DEFAULT_ROI_OUTLINE_THICKNESS
        # self.default_outline_thickness = int(outline_thickness)

    def _draw_polygon_(
            self,
            draw: ImageDraw.Draw,
            polygon,
            outline_color=None,
            # outline_thickness=None,
            fill=True,
            fill_color=None
    ):
        if fill:
            if fill_color is None:
                fill_color = self.default_roi_color
        else:
            fill_color = None

        if outline_color is None:
            outline_color = self.default_outline_color

        # if outline_thickness is None:
        #     outline_thickness = self.default_outline_thickness

        draw.polygon(xy=polygon,
                     fill=fill_color,
                     outline=outline_color)

        return draw

    def draw_polygon_rois(
            self,
            img,
            rois,
            fill_color=None,
            outline_color=None
    ):
        img_h, img_w = img.shape[:2]

        # Convert the image to RGB (OpenCV uses BGR)
        cv_im_rgba = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2RGBA)

        # Pass the image to PIL
        pil_base_im = Image.fromarray(cv_im_rgba, "RGBA")

        pil_viz_im = Image.new("RGBA", pil_base_im.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(pil_viz_im, "RGBA")

        if fill_color is None:
            fill_color = self.default_roi_color
        if outline_color is None:
            outline_color = self.default_outline_color

        for roi in rois:
            if np.max(roi['polygon']) < 1.0:
                polygon = (roi['polygon'] * np.array([img_w, img_h])).astype(np.int).reshape(-1).tolist()
                x0, y0 = np.average((roi['polygon'] * np.array([img_w, img_h])), axis=0)
            else:
                polygon = (roi['polygon']).astype(np.int).reshape(-1).tolist()
                x0, y0 = np.average(np.array(roi['polygon']), axis=0)

            label = roi.get('roi_name', '')

            self._draw_polygon_(
                draw=draw,
                polygon=polygon,
                fill_color=fill_color,
                outline_color=outline_color
            )

            self.label_drawer.draw_texts(
                draw=draw, pos=(int(x0), int(y0)),
                large_padding=True,
                text=label,
                show_shadow=True,
                fill_rectangle=False
            )

        pil_out = Image.alpha_composite(pil_base_im, pil_viz_im)
        cv_im_processed = cv2.cvtColor(np.array(pil_out), cv2.COLOR_RGBA2BGR)
        return cv_im_processed

    def draw_line_rois(self):
        pass
