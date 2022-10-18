"""
This file will assist in converting the float urls
in the path function
"""

class FloatUrlParameterConverter:
    regex = '[-+]?\d+(\.\d+)'
    
    def to_python(self,value):
        return float(value)

    def to_url(self,value):
        return str(value)    
