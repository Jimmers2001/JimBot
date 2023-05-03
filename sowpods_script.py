#this script keeps only the 5 letter words from sowpods.txt
with open('sowpods.txt', 'r') as file:
    lines = file.readlines()

lines = [line.strip() for line in lines]  # remove any leading/trailing whitespace

new_lines = [line for line in lines if len(line) == 5]  # keep only words that are 5 letters long

with open('new_sowpods.txt', 'w') as file:
    file.write('\n'.join(new_lines))  # write the filtered words back to the file, separated by newlines
