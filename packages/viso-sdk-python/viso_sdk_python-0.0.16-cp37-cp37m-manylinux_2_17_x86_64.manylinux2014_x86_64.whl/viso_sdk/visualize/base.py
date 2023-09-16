from viso_sdk.visualize.viz_text import VizTextDraw
from viso_sdk.visualize.viz_roi import VizPolygonDraw
from viso_sdk.visualize.viz_object import VizObjectDraw
from viso_sdk.visualize.palette import get_rgba_color_with_palette_id


class BaseVisualization:
    def __init__(self,
                 text_vis_params,
                 object_vis_params,
                 roi_vis_params
                 ):
        self.text_drawer = VizTextDraw(
            font_size=text_vis_params.get('text_size', None),
            font_color=text_vis_params.get('text_color', None)
        )

        self.object_drawer = VizObjectDraw(
            bbox_color=object_vis_params.get('bbox_color', None),
            bbox_thickness=object_vis_params.get('bbox_thickness', None),
            text_size=object_vis_params.get('text_size', None),
            text_color=object_vis_params.get('text_color', None)
        )

        self.roi_drawer = VizPolygonDraw(
            roi_color=roi_vis_params.get('roi_color', None),
            outline_color=roi_vis_params.get('outline_color', None),
            outline_thickness=roi_vis_params.get('outline_thickness', None),
            show_label=roi_vis_params.get('show_label', True),
            label_size=roi_vis_params.get('label_size', None),
            label_color=roi_vis_params.get('label_color', None)
        )

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

    def draw_detections(self, img, detections, show_label, show_confidence):
        show = self.object_drawer.draw_detections(
            img=img,
            detections=detections,
            show_label=show_label,
            show_confidence=show_confidence
        )
        return show

    def draw_rois(self, img, rois: list, roi_type: str = 'polygon'):
        if roi_type == 'polygon':
            show = self.roi_drawer.draw_polygon_rois(
                img=img,
                rois=rois
            )
            return show

        elif roi_type == 'line':
            show = self.roi_drawer.draw_line_rois()
            return show
        else:
            return img
