import io
from wand.image import Image
from PIL import Image as PI, ImageDraw
import pyocr
import pyocr.builders
from node import Node

class Reader():
    def __init__(self):
        self.file = ""
        self.result = []
        self.pages = 0
        self.req_image = []
        self.tool = pyocr.get_available_tools()[0]
        self.pref_lang = "eng"

    def __enter__(self):
        return self

    def set_pref_lang(self, value):
        """Setter method for preffered language"""
        if str(value) in self.tool.get_available_languages():
            self.pref_lang = str(value)
            return True
        return False

    def get_pref_lang(self):
        return self.pref_lang

    def set_file(self, file):
        #TODO: Filetype check, return statement
        self.file = file

    def get_result(self):
        #TODO: return results in with a suitable type e.g. JSON
        pass

    def setup(self):
        """
        - Reads pdf by using pyocr supported tool such as Tesseract.
        - Builds up boxes from found textfields. Boxes can be changed to i.e. recognizing
            individual letters at 'builder=pyocr.builders.LineBoxBuilder()'
        """
        #TODO: Create graph from nodes and implement a smarter search function
        image_pdf = Image(filename=self.file, resolution=300)
        image_jpeg = image_pdf.convert('jpeg')

        for img in image_jpeg.sequence:
            img_page = Image(image=img)
            self.req_image.append(img_page.make_blob('jpeg'))

        for img in self.req_image:
            line = self.tool.image_to_string(
                PI.open(io.BytesIO(img)),
                lang=self.pref_lang,
                builder=pyocr.builders.LineBoxBuilder()
            )
            for line_item in line:
                item = Node(line_item.content, line_item.position, self.pages)
                self.result.append(item)
            self.pages += 1

    def visualize_result(self, page):
        if page > 0 and page <= self.pages:
            sample_image = PI.open(io.BytesIO(self.req_image[page-1]))
            draw = ImageDraw.Draw(sample_image)
            for item in self.result:
                if item.get_page() is page:
                    draw.rectangle((item.get_position()), outline=(255, 0, 0, 255))
            del draw
            sample_image.show()

    def search(self, search_value):
        #TODO: Create method for searching values from self.result with regex/etc.
        for search_iter in self.result:
            if search_value.lower() in search_iter.get_value().lower():
                pass

    def table_search(self, column_separators, crop_box):
        #TODO: Create method for searching values from a table
        column_result = {}
        row_limits = (crop_box['y'], crop_box['y']+crop_box['height'])
        for column in range(len(column_separators)-1):
            column_result['column_'+str(column)] = []
            for x in self.result:
                if x['pos'][0][0] > column_separators[column] and x['pos'][0][0] < column_separators[column+1] and x['pos'][0][1] > row_limits[0] and x['pos'][0][1] < row_limits[1]:
                    column_result['column'+str(column)].append(x['text'])
        return column_result

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
