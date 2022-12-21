from __future__ import print_function
import time
from geojson import Feature, FeatureCollection, loads


"""
Arguments in Python
The * and the ** are designed to supoort functions that take any number of arguments. Both can appear in either function definition
or a function call
"""

## collects all the positional arguments into a new tuple and assigns the variable args to that tuple
def func(*args):
    print(args)


## collects the keyword arguments into a dictionary, it only works for keyword arguments
def funct(**args):
    print(args)
    

## both the normal arguments, the * and the ** can be combined
def functi(a, *pargs,**kwargs):
    print(a,pargs,kwargs)

## keyword-only arguments with defaults are optional, but those without defaults effectively become required keywords for the function
def kwonly(a,*args,b,c='spam'):
    print(a,b,c)
    """
    the kwonly() function needs keyword-only argument b
    """
    
## Ordering Rules
"""
Finally note thaat keyword-only arguments must be specified after a single start not two,
names arguments cannot appear after the **args arbitrary keywords form and a ** can't appear by itself in the argument list
for example def kwonly(a,**kargs,b,c) will generate an error
            def kwonly(a, **, b,c) will also generate an error

When an argument name appears before the *args, it is possibly default positional argument, not keyword-only        
"""
def f(a,*b,c=6,**d):
    print(a,b,c,d)

def test_routes(start,end,*args,suez=False,panama=False,singapore=False):
    var_args = locals()
    print(var_args['suez'],var_args['panama'],var_args['singapore'])

    route_options = Feature(options={'suez':var_args['suez'],'panama':var_args['panama'],'singapore':var_args['singapore']})
    print(route_options)
    if (suez==False) and (panama==False) and (singapore==False):
        print('all false')
        
    if(suez==True) and (panama == True) and (singapore==True):
        print('all true')
        
    if (suez == True) and (panama==False) and (singapore==False):
        print('only suez true')
        
    if (suez == True) and (panama==True) and (singapore==False):
        print('suez and panama true')
        
    if(suez == False) and (panama == False) and (singapore==True):
        print('only singapore true')
        
    if(suez == False) and (panama == True) and (singapore == False):
        print('only panama true')

    if(suez == True) and (panama==False) and (singapore==True):
        print('suez and singapore true')

    if(suez==False) and (panama==True) and (singapore==True):
        print('panama and singapore true')


if __name__=="__main__":
    test_routes(4567,1223,suez=False,panama=True,singapore=True)

        
    
         
    





