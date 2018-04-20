class Node:
    def __init__(self, value, pos, page):
        self.value = value
        self.position = pos
        self.page = page

    def get_position(self):
        """Get position of linebox item, e.g. ((x_upper, y_upper), (x_lower, y_lower))"""
        return self.position

    def get_page(self):
        """Get page number, starts from 0"""
        return self.page

    def get_box_midpoint(self):
        """Get coordinates for middle point of linebox as a tuple, e.g. (x_mid, y_mid)"""
        return ((self.position[0][0]+self.position[1][0])/2, (self.position[0][1]+self.position[1][1])/2)

    def get_value(self):
        """Get string value of linebox item content"""
        return str(self.value)

    def __str__(self):
        return str(self.value)

    def __dir__(self):
        return self.__dict__
