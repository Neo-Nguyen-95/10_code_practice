"""You are given two strings word1 and word2. Merge the strings by adding letters in alternating order, starting with word1. If a string is longer than the other, append the additional letters onto the end of the merged string.

Return the merged string.


Example 1:

Input: word1 = "abc", word2 = "pqr"
Output: "apbqcr"
Explanation: The merged string will be merged as so:
word1:  a   b   c
word2:    p   q   r
merged: a p b q c r
Example 2:

Input: word1 = "ab", word2 = "pqrs"
Output: "apbqrs"
Explanation: Notice that as word2 is longer, "rs" is appended to the end.
word1:  a   b 
word2:    p   q   r   s
merged: a p b q   r   s
Example 3:

Input: word1 = "abcd", word2 = "pq"
Output: "apbqcd"
Explanation: Notice that as word1 is longer, "cd" is appended to the end.
word1:  a   b   c   d
word2:    p   q 
merged: a p b q c   d
"""

#%% My solution
word1 = 'abcdef'
word2 = 'pqr'

len_min = min(len(word1), len(word2))
len_max = max(len(word1), len(word2))

merged_word = ''
for i in range(len_max):
    try:
        merged_word += word1[i]
    except:
        pass
    
    try:
        merged_word += word2[i]
    except:
        pass
        
print(merged_word)


#%% Better solution
word1 = 'abcdef'
word2 = 'pqr'

merged_word = []

for w1, w2 in zip(word1, word2):
    merged_word.append(w1 + w2)
    
merged_word.append(word1[len(word2):])
merged_word.append(word2[len(word1):])

result = ''.join(merged_word)

print(result)

