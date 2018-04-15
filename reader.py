import io
import re
import os
from wand.image import Image
from PIL import Image as PI
from PIL import ImageDraw
import pyocr
import pyocr.builders
from graphy import Graph
from node import Node

class Reader():
    def __init__(self):
        self.file = ""
        self.items = []
        self.pages = 0
        self.tool = pyocr.get_available_tools()[0]

    def setup(self, pref_lang, file_path):
        """
        - Reads pdf by using pyocr supported tool such as Tesseract.
        - Builds up boxes from found textfields. Boxes can be changed to i.e. recognizing
            individual letters at 'builder=pyocr.builders.LineBoxBuilder()'
        -
        """
        lang = pref_lang if pref_lang in self.tool.get_available_languages() else "eng"
        print("Will use lang '%s'" % (lang))

        req_image = []

        image_pdf = Image(filename=file_path, resolution=300)
        image_pdf.save(filename=os.path.abspath("./temp-1.png"))
        image_jpeg = image_pdf.convert('jpeg')

        for img in image_jpeg.sequence:
            img_page = Image(image=img)
            req_image.append(img_page.make_blob('jpeg'))

        page = 0
        for img in req_image:
            line = self.tool.image_to_string(
                PI.open(io.BytesIO(img)),
                lang=lang,
                builder=pyocr.builders.LineBoxBuilder()
            )
            for line_item in line:
                item = Node(line_item.content, line_item.position, page)
                self.items.append({page:item})
            page += 1

        return result

    def visualize_result(result_dict):
        for z in range(0,result_dict[len(result_dict)-1]['page']+1):
            im = PI.open(os.path.abspath("./temp-1-" + str(z) + ".png"))
            draw = ImageDraw.Draw(im)
            for x in result_dict:
                if x['page'] == z:
                    draw.rectangle((x['pos']), outline=(255, 0, 0, 255))
            del draw
            im.show()

    def search(result_dict, search_value):
        offset = 85
        for x in result_dict:
            if search_value.lower() in x['text'].lower():
                search_x = (x['pos'][0][0]+x['pos'][1][0])/2
                search_y = (x['pos'][0][1]+x['pos'][1][1])/2
                for x in result_dict:
                    target_x = (x['pos'][0][0]+x['pos'][1][0])/2
                    target_y = (x['pos'][0][1]+x['pos'][1][1])/2
                    if target_x >= search_x-offset and target_x <= search_x+offset and target_y <= search_y+offset and target_y >= search_y-offset and re.match('[0-9]+.*', x['text']):
                        return x['text']

    def table_search(result_dict):
        column_limits = (0, 304, 522, 1130, 1480, 1700, 1980, 3000)
        column_result = {}
        row_limits_page0 = (1180, 3190)
        row_limits_else = (590, 3170)
        for column in range(len(column_limits)-1):
            column_result['column'+str(column)] = []
            for x in result_dict:
                row_limits = row_limits_page0 if x['page'] == 0 else row_limits_else
                if x['pos'][0][0] > column_limits[column] and x['pos'][0][0] < column_limits[column+1] and x['pos'][0][1] > row_limits[0] and x['pos'][0][1] < row_limits[1]:
                    column_result['column'+str(column)].append(x['text'])
        return column_result
