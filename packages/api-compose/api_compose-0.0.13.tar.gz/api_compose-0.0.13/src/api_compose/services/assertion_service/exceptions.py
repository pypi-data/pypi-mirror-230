class JinjaTemplateNotEvaluatedToBooleanException(Exception):
    def __init__(self,
                 template: str
                 ):
        self.template = template

    def __str__(self):
        return f"Template {self.template} is NOT evaluated to a boolean!"
