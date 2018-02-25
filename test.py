a = '1:3'
def reverse_string_by_word(s):
 lst = s.split(':') # split by blank space by default
 return lst[1]+':' +lst[0]
b = reverse_string_by_word(a)
print b