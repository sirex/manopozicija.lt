import logging

from PIL import Image, ImageColor
from sorl.thumbnail.engines.pil_engine import Engine

logger = logging.getLogger(__file__)


class Engine(Engine):
    """Sorl Thumbnail Engine that accepts background color

    Created on Sunday, February 2012 by Yuji Tomita

    https://yuji.wordpress.com/2012/02/26/sorl-thumbnail-convert-png-to-jpeg-with-background-color/
    """
    def create(self, image, geometry, options):
        ALPHA = 3  # 3 is the alpha of an RGBA image.
        thumb = super(Engine, self).create(image, geometry, options)
        background = options.get('background')
        if background:
            try:
                bgthumb = Image.new('RGB', thumb.size, ImageColor.getcolor(background, 'RGB'))
                bgthumb.paste(thumb, mask=thumb.split()[ALPHA])
                return bgthumb
            except Exception:
                logger.exception('error while creating %r thumbnail with parameter: %r, %r', image, geometry, options)
                return thumb
        return thumb
