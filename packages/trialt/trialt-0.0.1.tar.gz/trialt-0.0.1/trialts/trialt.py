def bubble_sort(arr, reverse=False):
    lenl = len(arr)
    flag = False
    for i in range(lenl - 1):
        for j in range(lenl - i - 1):
            if reverse is False:
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    flag = True
            else:
                if arr[j] < arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    flag = True
        if flag is False:
            break
    return arr