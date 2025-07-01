from .interfaces import StyleType

class Style(StyleType):
    def __init__(self, style_dict: dict = None):
        self.tags: dict[str, dict] = {}
        self.ids: dict[str, dict] = {}
        self.classes: dict[str, dict] = {}
        self.universal: dict = {}
        if style_dict:
            self.apply(style_dict)

    def apply(self, style_dict: dict):
        for selector, props in style_dict.items():
            if selector == "*":
                self.universal.update(props)
            elif selector.startswith("#"):
                self.ids[selector[1:]] = props
            elif selector.startswith("."):
                self.classes[selector[1:]] = props
            else:
                self.tags[selector] = props

    def get(self, node) -> dict:
        result = {}
        id = node.id or node.properties.id
        if self.universal:
            result.update(self.universal)
        if node.element_type in self.tags:
            result.update(self.tags[node.element_type])
        if id and id in self.ids:
            result.update(self.ids[id])
        if node.properties.class_name and node.properties.class_name in self.classes:
            result.update(self.classes[node.properties.class_name])
        return result