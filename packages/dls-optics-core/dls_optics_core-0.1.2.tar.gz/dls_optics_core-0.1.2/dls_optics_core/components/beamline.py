class Beamline():
    def __init__(self):
        self.elements = []
        self.beam = []

    def beam_at_distance(self, distance):
        pass
        # current = 0

        # for element in self.elements:
        #     if current + element.r1 > distance:
        #         index = self.elements.index(element)
        #         source = beam.initial_beam