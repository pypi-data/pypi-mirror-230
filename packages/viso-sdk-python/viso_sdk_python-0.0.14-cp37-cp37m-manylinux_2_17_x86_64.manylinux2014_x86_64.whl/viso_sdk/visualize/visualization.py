import cv2
import numpy as np


from viso_sdk.visualize.custom_font import CustomFont
from viso_sdk.visualize.palette import get_rgba_color, get_rgba_color_with_palette_id


# DEFAULT_LINE_COLOR = (255, 0, 0, 0.8)
DEFAULT_ROI_COLOR = (255, 150, 113, 0.4)


class BaseVisualization:
    def __init__(self, img_sz=None, txt_color=None, line_color=None, roi_color=DEFAULT_ROI_COLOR):
        self.txt_color = get_rgba_color(color=txt_color)
        self.line_color = get_rgba_color(color=line_color)
        self.roi_color = get_rgba_color(color=roi_color)

        self.bbox_thickness = None
        self.font_size = None

        self.font = CustomFont(color=self.txt_color,
                               shadow_color=None)

        if img_sz is not None:
            self.bbox_thickness = self.__get_adjust_bbox_thick__(img_sz)
            self.font_size = self.__get_adjust_font_size__(img_sz)

            self.font.set_font_scale_from_size(self.font_size)
            self.font.set_font_thickness(self.bbox_thickness)

    def __init_vis_img__(self, img_sz=None, img=None):

        if img is not None:
            img_sz = img.shape[:2]

        if img_sz is not None:
            if self.bbox_thickness is None:
                self.bbox_thickness = self.__get_adjust_bbox_thick__(img_sz)

            if self.font_size is None:
                self.font_size = self.__get_adjust_font_size__(img_sz)

                self.font.set_font_scale_from_size(self.font_size)
                self.font.set_font_thickness(self.bbox_thickness // 2)

    @staticmethod
    def __get_adjust_font_size__(img_sz):
        img_h, img_w = img_sz
        # use a truetype font

        min_font_sz = 10  # 480 p
        max_font_sz = 15  # 1080 p
        font_sz = abs(int((max_font_sz - min_font_sz) / (1080 - 480) * (img_h - 480)) + min_font_sz)
        font_sz = min(max(min_font_sz, font_sz), 25)
        return font_sz

    @staticmethod
    def __get_adjust_bbox_thick__(img_sz):
        img_h, img_w = img_sz
        bbox_thick = int(0.5 * (img_h + img_w) / 1000)
        if bbox_thick < 2:
            bbox_thick = 2

        return bbox_thick

    @staticmethod
    def get_rgba_color_with_palette_id(palette_id):
        return get_rgba_color_with_palette_id(palette_id)

    def __get_text_area_size__(self, texts):
        face = self.font.face
        scale = self.font.scale
        thickness = self.font.thickness

        text_widths, text_heights = [], []
        for line in texts:
            line_text_width, line_text_height = cv2.getTextSize(
                line,
                fontFace=face,
                fontScale=scale,
                thickness=thickness)[0]

            text_widths.append(line_text_width)
            text_heights.append(line_text_height)

        return max(text_widths), max(text_heights)

    def draw_text(self, img, text, org, padding=0, shadow=False, shadow_color=None):
        # shadow effect
        x, y = org
        if shadow and shadow_color is not None:
            img = cv2.putText(
                img=img,
                text=text,
                org=(x + padding, y),
                fontFace=self.font.face,
                fontScale=self.font.scale,
                color=self.font.shadow_color,
                thickness=self.font.thickness,
                lineType=cv2.LINE_AA
            )

        img = cv2.putText(
            img=img,
            text=text,
            org=(x + padding + 1, y + 1),
            fontFace=self.font.face,
            fontScale=self.font.scale,
            color=self.font.color,
            thickness=self.font.thickness,
            lineType=cv2.LINE_AA
        )
        return img

    def draw_label(self, img, text, pos,
                   large_padding=False,
                   fill_rectangle=False,
                   fill_rectangle_color=None,
                   txt_shadow=False,
                   txt_shadow_color=None):

        if self.font_size is None:
            img_h, img_w, = img.shape[:2]
            self.__init_vis_img__((img_w, img_h), None)

        overlay = img.copy()

        if isinstance(text, str):
            texts = text.split("\n")
        elif isinstance(text, list):
            texts = text
        else:
            texts = []

        # get text size
        line_width, line_height = self.__get_text_area_size__(texts)

        padding = max(int(line_height // 4), 2)
        padding_left = padding
        if large_padding:
            padding_top = padding * 2
        else:
            padding_top = padding // 2

        line_height += padding_top
        x0, y0 = pos
        if fill_rectangle:
            # put filled text rectangle
            overlay = cv2.rectangle(
                img=overlay,
                pt1=(int(x0), int(y0)),
                # pt2=(x0 + text_width + padding_left * 2, y0 + text_height + 2 * padding_top),
                pt2=(int(x0 + line_width + padding_left), int(y0 + len(texts) * line_height + 2 * padding_top)),
                thickness=-1,
                color=fill_rectangle_color
            )
            alpha = fill_rectangle_color[-1]
            if alpha > 1.0:
                alpha /= 255

            img = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)

        # put text above rectangle
        for line_no, line in enumerate(texts):
            y = int(y0 + line_height * (line_no + 1))

            img = self.draw_text(
                img=img,
                text=line,
                org=(x0, y),
                padding=padding,
                shadow_color=txt_shadow_color,
                shadow=txt_shadow
            )

        return img

    def draw_polygons(self, img, rois):
        img_h, img_w, = img.shape[:2]
        if self.font_size is None:
            self.__init_vis_img__(None, img)

        fill_color = self.roi_color
        outline_color = (fill_color[0] + 10, fill_color[1] + 10, fill_color[2] + 10, fill_color[3])

        overlay = img.copy()

        for roi in rois:
            pts = (roi['polygon'] * np.asarray([img_w, img_h])).astype(int).reshape(-1, 2)
            # pts = (roi['polygon'] * np.asarray([img_w, img_h])).astype(int).reshape(-1, 1, 2)

            # fill out
            cv2.fillPoly(img=overlay, color=fill_color, pts=[pts])

            # polygon border
            cv2.polylines(img=overlay, isClosed=True, thickness=self.bbox_thickness, color=outline_color, pts=[pts])

            # get text label
            label = roi.get('roi_name', '')
            x0, y0 = int(roi['polygon'][0][0] * img_w), int(roi['polygon'][0][1] * img_h)
            img = self.draw_label(
                img=img,
                pos=(x0, y0),
                text=label,
                large_padding=True,
                txt_shadow=True,
                fill_rectangle=False,
                fill_rectangle_color=fill_color)

        alpha = fill_color[-1]
        if alpha > 1.0:
            alpha /= 255

        img = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)
        return img

    @staticmethod
    def draw_bounding_box(img, rect, bbox_color, thickness, fill_out=False):
        overlay = img.copy()

        x, y, w, h = rect

        pt1 = (x, y)
        pt2 = (x + w, y + h)

        if fill_out:
            thickness = -1

        cv2.rectangle(
            img=overlay,
            pt1=pt1, pt2=pt2,
            color=bbox_color,
            thickness=thickness,
            lineType=None,
        )

        alpha = bbox_color[-1]
        if alpha > 1.0:
            alpha /= 255

        return cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)
