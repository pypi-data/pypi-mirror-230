def count_vowels(text):
    vowels = 'aeiou'
    count = 0

    for char in text:
        if char.lower() in vowels:
            count += 1

    return count