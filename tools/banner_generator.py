# GMG Copyright 2022 - Alexandre Díaz
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from flask_babel import _


class BannerGenerator(object):
    # Gradient code by Jens Breit: https://djangosnippets.org/snippets/787/
    def _channel(self, i, c, size, startFill, stopFill):
        """calculate the value of a single color channel for a single pixel"""
        return startFill[c] + int((i * 1.0 / size) * (stopFill[c] - startFill[c]))

    def _color(self, i, size, startFill, stopFill):
        """calculate the RGB value of a single pixel"""
        return tuple([self._channel(i, c, size, startFill, stopFill) for c in range(3)])

    def _gradient(self, startFill, stopFill, runTopBottom=False):
        """Draw a rounded rectangle"""
        width, height = self._image.size
        si = height if runTopBottom else width

        gradient = [self._color(i, si, startFill, stopFill) for i in xrange(si)]

        if runTopBottom:
            modGrad = []
            for i in xrange(height):
                modGrad += [gradient[i]] * width
            self._image.putdata(modGrad)
        else:
            self._image.putdata(gradient * height)

    ##

    def __init__(self, size):
        self.size = size
        self.titleColor = (34, 33, 60)
        self.detailColor = (0, 0, 0)
        self.addressColor = (1, 65, 103)
        self.gradStartColor = (214, 213, 213)
        self.gradEndColor = (166, 165, 165)

        self._fontLarge = ImageFont.truetype(
            'static/fonts/dejavu-2.37/DejaVuSans.ttf', 16
        )
        self._fontLargeBold = ImageFont.truetype(
            'static/fonts/dejavu-2.37/DejaVuSans-Bold.ttf', 16
        )
        self._fontSmall = ImageFont.truetype(
            'static/fonts/dejavu-2.37/DejaVuSans.ttf', 10
        )
        self._image = None

    def generate(self, data, format='png'):
        # Create RGBA Image
        self._image = Image.new('RGBA', self.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(self._image)

        # TODO

        del draw
        # Save Image To Memory
        memory_img = BytesIO()
        self._image.save(memory_img, format=format)
        memory_img.seek(0)
        return memory_img
