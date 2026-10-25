"""
Example 1:
Input: nums = [2,7,11,15], target = 9
Output: [0,1]
Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].

Example 2:
Input: nums = [3,2,4], target = 6
Output: [1,2]

Example 3:
Input: nums = [3,3], target = 6
Output: [0,1]
"""
import sklearn

# nums = [2,7,11,15]
# target = 9

nums = [3,2,4]
target = 6


### WAY 1:
for index_1, element_1 in enumerate(nums):
    for index_2, element_2 in enumerate(nums[index_1+1:]):
        if element_1 + element_2 == target:
            print(element_1, element_2)
            print(index_1, index_2+index_1+1)
            
### WAY 2:
num_to_index = {}
    
for index, num in enumerate(nums):
    complement = target - num
    if complement in num_to_index:
        print(num_to_index[complement], index)
    else:
        num_to_index[num] = index