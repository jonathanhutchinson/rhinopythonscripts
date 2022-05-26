#Colours in Python

import rhinoscriptsyntax as rs

def TweenValue( list_length, start_colour, end_colour ):
    """Takes 3 integers"""
    list_of_colours = []
    
    if start_colour == end_colour:
        list_of_colours = [ start_colour ] * list_length
    else:
        step = ( start_colour - end_colour) * -1 #if st-en is -ve we need to increment, flip sign >> is st-en is +ve, we need to decrement, flip sign
        index_range = range ( 1 , list_length ) # intervals
        factor = step / list_length
        
        list_of_colours.append(start_colour)
        
        tweened = [ int ( round( start_colour + ( index * factor ) ) ) for index in index_range ]
        list_of_colours.extend( tweened )
        list_of_colours.append( end_colour )
        
    return list_of_colours

def TweenColour( starting_colour, goal_colour, objects_to_colour ):
    
    r = TweenValue ( len(objects_to_colour), starting_colour [0] , goal_colour [0] )
    g = TweenValue ( len(objects_to_colour), starting_colour [1] , goal_colour [1] )
    b = TweenValue ( len(objects_to_colour), starting_colour [2] , goal_colour [2] )
    
    rgb_values = zip( r,g,b )
    
    return rgb_values

starting_colour = [ 225,200,0 ]
goal_colour = [10,150,255]

length = 55
x_range = range(3,75)
guids = []

rs.EnableRedraw(False)
for x in x_range:
    guid = rs.AddLine(  [x,0,0], [x,length,0] )
    guids.append(guid)

colours = TweenColour( starting_colour, goal_colour, guids )

object_and_colour = zip(guids, colours)
for i in object_and_colour:
    rs.ObjectColor(i [0], i [1])

rs.EnableRedraw(True)

"""
starting_colour = [ 43,240,23 ]
goal_colour = [50,50,50]
step_R = int ( ( 256 - starting_colour [0] ) / number )
step_G = int ( ( 256 - starting_colour [1] ) / number )
step_B = int ( ( 256 - starting_colour [2] ) / number )

steps = [step_R, step_G, step_B]

for index, step in enumerate(steps):
    if step == 0:
        steps [index] += 1

values_R = range(starting_colour [0] , 256, int( steps [0] ) )
values_G = range(starting_colour [1], 256, int( steps [1] ) )
values_B =range(starting_colour [2], 256, int( steps [2] ) )
# colors = [ rs.CreateColor ( values_R, values_G, values_B ) for value in values ] # only 11 colours
#With high numbers, not returning enough values
#suddenly to black - bad division

length = 50
number = 25
number_range = range(0,26)

colors = zip( values_R, values_G, values_B )
guids = []

rs.EnableRedraw(False)
for num in number_range:
    guid = rs.AddLine(  [num,0,0], [0,length,0] )
    guids.append(guid)

object_and_colour = zip(guids, colors)
for i in object_and_colour:
    rs.ObjectColor(i [0], i [1])

rs.EnableRedraw(True)

# create_colour_divisions = len(objects)
#basic colour tween #Interpolate through a range?
"""