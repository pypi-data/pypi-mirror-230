class Embed:
    def __init__(self):
        super().__init__()
        self.args = {}
        self.url = "||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​|| _ _ _ _ _ _http://henrymistert.lol/embed"
    def set_title(self, value):
        value = value.replace(" ", "_").replace("\n", "%0A").replace("#", "")
        self.args['title'] = value
    def set_description(self, value):
        value = value.replace(" ", "_").replace("\n", "%0A").replace("#", "")
        self.args['description'] = value
    def set_color(self, value):
        value = value.replace("#", "")
        self.args['color'] = value
    def set_thumbnail(self, value):
        value = value.replace("#", "")
        self.args['image'] = value
    def set_author(self, value):
        value = value.replace(" ", "_").replace("\n", "%0A").replace("#", "")
        self.args['author'] = value
    def set_footer(self, value):
        value = value.replace(" ", "_").replace("\n", "%0A").replace("#", "")
        self.args['footer'] = value
    def generate_text(self):
        cool = "?"
        for arg in self.args:
            name = arg
            value = self.args[arg]
            self.url += f"{cool}{name}={value}"
            cool = "&"
        return self.url