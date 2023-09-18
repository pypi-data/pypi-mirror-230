from docketanalyzer.categories.base_category import Category


class CaseStatus(Category):
    open = "Open"
    closed = "Closed"


class CaseType(Category):
    cv = "Civil"
    cr = "Criminal"


class Jurisdiction(Category):
    defendant = "U.S. Government Defendant"
    diversity = "Diversity"
    federal = "Federal Question"
    local = "Local Question"
    plaintiff = "U.S. Government Plaintiff"


class JuryDemand(Category):
    plaintiff = "Plaintiff"
    defendant = "Defendant"
    both = "Both"
    none = "None"

