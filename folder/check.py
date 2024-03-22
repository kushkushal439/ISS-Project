list =  ['images/img55.jpg', 'images/img1.jpg', 'images/img2.jpg', 'images/img3.jpg']
numbers = []
for string in list:
    parts = string.split('/')
    last_part = parts[-1]    
    number_str = last_part.replace('.jpg', '')   
    number_str1 = number_str.replace('img', ''); 
    numbers.append(int(number_str1))
    rmdir1 = "static/" + 'selected/'  + last_part
    print(rmdir1)
print(numbers)