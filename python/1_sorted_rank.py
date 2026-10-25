arr1 = [40,10,20,30]

arr2 = [100,100,100]

arr3 = [37,12,28,9,100,56,80,5,12]

def way1(arr):
    """
    :type arr: List[int]
    :rtype: List[int]
    """
    num_to_rank = {}
    # Deduplicate and sort arr
    nums = sorted(set(arr))
    rank = 1
    for num in nums:
        print(num)
        num_to_rank[num] = rank
        rank += 1
    
    print(num_to_rank)
    
    for i in range(len(arr)):
        arr[i] = num_to_rank[arr[i]]
    
    return arr
                

way1(arr3)



    
    