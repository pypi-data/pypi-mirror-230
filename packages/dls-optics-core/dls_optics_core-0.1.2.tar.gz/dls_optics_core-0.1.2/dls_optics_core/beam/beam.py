from math import tan
from optics.beam.image import Image

class Beam:
    def __init__(self, source_image):
        self.source = source_image
        self.final_width = source_image.width
        self.final_height = source_image.height

    @classmethod
    def from_initial_dimensions(cls, width, height, h_div, v_div):
        return cls(Image(width, height, h_div, v_div))

    @property
    def initial_width(self):
        return self.source.width

    @property
    def initial_height(self):
        return self.source.height

    @property
    def initial_h_div(self):
        return self.source.h_div

    @property
    def initial_v_div(self):
        return self.source.v_div

    @property
    def h_crossing(self):
        return self.final_width < 0

    @property
    def v_crossing(self):
        return self.final_height < 0

    def propogate(self, distance):
        self.final_width = self.initial_width + 2*tan(self.initial_h_div/2)*distance
        self.final_height = self.initial_height + 2*tan(self.initial_v_div/2)*distance

        image_width = -self.final_width if self.h_crossing else self.final_width
        image_height = -self.final_height if self.v_crossing else self.final_height

        image_h_div = -self.initial_h_div if self.h_crossing else self.initial_h_div
        image_v_div = -self.initial_v_div if self.v_crossing else self.initial_v_div

        return Image(image_width, image_height, image_h_div, image_v_div)
