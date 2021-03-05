import SHAConstants as SHA


def convertMessageToByte(message): #Convert a message to bits in string (ASCII)
    byteListe = [ord(char) for char in message]
    m =""
    for byte in byteListe:
        m += "{0:b}".format(byte)
    return m

# Compute K, do the 0 padding and add L as a 64 bits integer
def padding(message):
    message = convertMessageToByte(message)
    L = len(message)
    message = message + "1"
    Lmod = L%512 #In case L > 512
    K = 512 - (Lmod + 1 + 64)
    for i in range(K):
        message += "0"
    L_bits = "{0:064b}".format(L)
    message += L_bits
    return message


#Slice the message into 512-bit blocks with 16 32bits words (The message is in bits and the result in decimal)
def slice(message):
    length = len(message)
    nbrBlocks = int(length/512)
    blocks=[]
    for i in range(nbrBlocks):
        word = message[i*512:(i+1)*512]

        block = []
        for j in range(16):
            block.append(word[j*32:(j+1)*32])
        blocks.append(block)


    #convert to integer
    blocks = [[int(bina,2) for bina in block] for block in blocks]
    return blocks

# Rightrotate and righshift
def rightShift(int,offset):
    return int >> offset

#For 32 bits
def rightRotate(int, offset):
    return (int >> offset) | (int << (32 - offset)) & 0xFFFFFFFF


def compute64words(block):#add word 17 to 64 in a block of 16 word of 32 bits
    for i in range(17,65):
        s_0 = rightRotate(block[i-15],7) ^ rightRotate(block[i-15],18) ^ rightShift(block[i-15],3)
        s_1 = rightRotate(block[i - 2], 17) ^ rightRotate(block[i - 2], 19) ^ rightShift(block[i - 2], 10)
        w = (block[i-16] + s_0 + block[i-7] + s_1) % 2**32
        block.append(w)
    return block


# Compression function, exactly how it is described in the course
def compression(words,IV):

    a = IV[0]
    b = IV[1]
    c = IV[2]
    d = IV[3]
    e = IV[4]
    f = IV[5]
    g = IV[6]
    h = IV[7]

    for i in range(64):
        X_1 = rightRotate(e,6) ^ rightRotate(e,11) ^ rightRotate(e,25)
        CH = (e & f) ^ ((~e) & g)
        X_2 = rightRotate(a,2) ^ rightRotate(a,13) ^ rightRotate(a,22)
        MAJ = (a & b) ^ (a & c) ^ (b & c)
        temp1 = (h + X_1 + CH + SHA.K[i] + words[i]) % 2**32
        temp2 = (X_2 + MAJ) % 2**32
        h = g
        g = f
        f = e
        e = (d + temp1) % 2**32
        d = c
        c = b
        b = a
        a = (temp1 + temp2) % 2**32
    return [a,b,c,d,e,f,g,h]

#The SHA-256 one-way compression function
def SHA256(block,IV):
    a = IV[0]
    b = IV[1]
    c = IV[2]
    d = IV[3]
    e = IV[4]
    f = IV[5]
    g = IV[6]
    h = IV[7]
    words = compute64words(block)
    new = compression(words,IV)
    newh0 = (new[0] + a) % 2**32
    newh1 = (new[1] + b) % 2**32
    newh2 = (new[2] + c) % 2**32
    newh3 = (new[3] + d) % 2**32
    newh4 = (new[4] + e) % 2**32
    newh5 = (new[5] + f) % 2**32
    newh6 = (new[6] + g) % 2**32
    newh7 = (new[7] + h) % 2**32
    return [newh0,newh1,newh2,newh3,newh4,newh5,newh6,newh7]



## You can comment and uncomment to test each message
message = ""
# message = "Welcome to Wrestlemania!"
# message = "Fight for your dreams, and your dreams will fight for you!"

print("This is the initial message: ",message)
padedMessage = padding(message)
L = len(padedMessage)
print("This is the padded Message of size:",L," ",padedMessage)
blocks = slice(padedMessage)
print("This is our blocks of 16 integers of 32 bits : ",blocks)
h = SHA.IV


#Appliying SHA256 for each block
for block in blocks:
    # h is initially IV and the become the next cipher
    h = SHA256(block,h)

print("This is the final h values in Integer: ",h)

#Joining all value from h in bits
final = ''
for element in h:
    final += "{0:032b}".format(element)

#Print the result in hexadecimal
print("This is the final cipher: ",hex(int(final,2)))

# Obviously, seeing the final cipher, my implementation is wrong. However, after verification, i really don't see the error(s),
# I tested all the bitwise operation and all my functions and they semms to work correcly.
# Furthermore, i think my understanding of the SHA256 is right, all my function are doing exactly what the course is explaining
# I am sorry for the trouble but I really do not see my error, so if you see something wrong please tell me
# I think my error has big chance to be in the "compression" function or in the "compute64words" function but it didnt seems that my formula are wrongly copied from the course

# Again i am sorry for the trouble but after multiple verification of the course and my code I can't see any error, so I suppose there is a detail that
# I am not understanding or seeing in the course.













