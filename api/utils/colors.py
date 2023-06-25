

def nextColor(currentColor=''):
    colors  = ['#fff', '#000','#ccc', '#ddd']
    
    if not currentColor in colors or not currentColor:
        return colors[0] 
    
    index_next_color = colors.index(currentColor) + 1
    return  colors[index_next_color] if index_next_color < len(colors) else colors[0]