from docketanalyzer.categories.base_category import Category


class JudgeRole(Category):
    assigned = "Assigned"
    referred = "Referred"


class JudgeType(Category):
    district = "District Judge"
    magistrate = "Magistrate Judge"

