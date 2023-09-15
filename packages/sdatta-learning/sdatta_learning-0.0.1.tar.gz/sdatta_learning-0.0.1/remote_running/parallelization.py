def split_list(n, data, column_name_split_by):
    lst = data[column_name_split_by].unique().tolist()
    size = len(lst) // n
    leftovers = len(lst) % n
    result = []
    for i in range(n):
        start = i * size + min(i, leftovers)
        end = (i + 1) * size + min(i + 1, leftovers)
        result.append(lst[start:end])
    result = [list(map(int, x)) for x in result]

    return result


# TODO: add parts for parallelization


