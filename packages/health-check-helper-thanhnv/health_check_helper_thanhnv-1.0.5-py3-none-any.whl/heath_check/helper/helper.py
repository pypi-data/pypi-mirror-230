def combine_list_number(list_number):

    if(len(list_number)==0):
        return list_number
    start = list_number[0]
    end = start
    new_list = []
    for number in list_number[1:-1]:
        if number == end+1:
            end = number
        elif start == end:
            new_list.append(str(end))
            start = number
            end = number
        else:
            new_list.append(f"{start}-{end}")
            start = number
            end = number

    if list_number[-1] == end + 1:
        new_list.append(f"{start}-{list_number[-1]}")
    elif start!= list_number[-1]:
        new_list.append(str(start))
        new_list.append(str(list_number[-1]))
    else:
        new_list.append(str(list_number[-1]))
    return new_list
