from docketanalyzer.categories.base_category import Category
from docketanalyzer import Registry


class CategoryRegistry(Registry):
    def find_filter(self, obj):
        return isinstance(obj, type) and issubclass(obj, Category) and obj is not Category


category_registry = CategoryRegistry()
category_registry.find()

category_registry.import_registered()

