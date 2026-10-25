#%% Q2 THINKING ABOUT IT
"""Example 1:

Input: s = "abacb", k = 2

Output: 4

Explanation:
The valid substrings are:
"aba" (character 'a' appears 2 times).
"abac" (character 'a' appears 2 times).
"abacb" (character 'a' appears 2 times).
"bacb" (character 'b' appears 2 times).
      
Example 2:
Input: s = "abcde", k = 1
Output: 15
"""


from collections import Counter

def numberOfSubstrings(s: str, k: int) -> int:
    n = len(s)
    res = (n + 1) * n // 2
    count = Counter()
    i = 0
    
    for j in range(n):
        # print(count(s[j]))
        count[s[j]] += 1
        
        while count[s[j]] >= k:
            count[s[i]] -= 1
            i += 1
        res -= j - i + 1
    return res



#%% Q1
# https://leetcode.com/problems/count-substrings-with-k-frequency-characters-i/description/

import string

"""
Example 1:
Input: target = "abc"
Output: ["a","aa","ab","aba","abb","abc"]
Princple:
    abc => a, b, c
    a => a
    aa => ab
    aba => abc

Example 2:
Input: target = "he"
Output: ["a","b","c","d","e","f","g","h","ha","hb","hc","hd","he"]
Principle:
    ha => h, e
    a b c d e f g h
    a b d e
"""

target = 'he'


def f(target):
    result = []
    for i in range(len(target)):
        array = ([target[:i] + a for a in string.ascii_lowercase 
                 if target[:i] + a <= target[:i+1]]
                 )
        result.extend(array)
    return result

f(target)
