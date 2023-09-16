DEFAULT_OPACITY = 100


def get_adjust_font_size(img_sz):
    img_h, img_w = img_sz
    # use a truetype font

    font_sz = int(1.0 * (img_h + img_w) / 100)
    font_sz = min(max(20, font_sz), 30)
    return font_sz


def get_adjust_bbox_thick(img_sz):
    img_h, img_w = img_sz
    bbox_thick = int(0.5 * (img_h + img_w) / 1000)
    if bbox_thick < 2:
        bbox_thick = 2

    return bbox_thick
