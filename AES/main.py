import numpy as np
import math
from Sboxes import *

# Take the two additionnal array and reshape it.
Sbox = np.asarray(Sbox)
Sbox = Sbox.reshape(16,16)

Sbox_inv = np.asarray(Sbox_inv)
Sbox_inv = Sbox_inv.reshape(16,16)

# Definition of useful functions
#take two sequence of bits in input and give the xor result between them
def polXor(str1, str2):
    result=""
    for element in zip(str1,str2):
        if element[0]==element[1]:
            result+="0"
        else:
            result+="1"
    return result

# Convert a bits in string to a polynomial with numpy
def bitsTopoly(str1):
    res = [int(element) for element in str1]
    return np.poly1d(res)

# take two sequence of bits in string and output the multiplication of their polynomial representation
def polyMul(str1,str2):
    res = np.polymul(bitsTopoly(str1),bitsTopoly(str2))
    resultat = [] # Modulo 2
    for element in res:
        if element % 2>0:
            resultat.append(1)
        else:
            resultat.append(0)

    longueur = len(resultat)

    #Return product if it is in GF(2^8)
    if longueur<9:
        return np.poly1d(resultat)

    #Compute modulo and return product
    else:
        sampleLen = longueur - 8
        firstTerm = np.poly1d(resultat[sampleLen:longueur]) #The ones that are in GF(2^8)
        secondTerm = np.poly1d(resultat[0:sampleLen]) #The ones that are not in GF(2^8)

        thirdTerm = np.poly1d([1,1,0,1,1]) #Ryjdael finite field
        finalTerm = np.polymul(secondTerm,thirdTerm) # We multiply them
        resultat = [] #And we do the modulo 2
        for element in finalTerm:
            if element % 2 > 0:
                resultat.append(1)
            else:
                resultat.append(0)
        finalTermPoly = np.poly1d(resultat)

        return np.polyadd(finalTermPoly,firstTerm)


#Convert a numpy polynome to his bits representation in strings
def polyTobits(poly):
    res =""
    for i in range(8):
        if poly[i]==1:
            res += "1"
        else:
            res +="0"

    return res[::-1]

# # TEST OF POLY MUL
# p1 = "01011001"
# p2 = "00110110"
# print(polyTobits(polyMul(p1,p2)))

# function to convert string to bits
def tobits(s):
    result = []
    for c in s:
        bits = bin(ord(c))[2:]
        bits = '00000000'[len(bits):] + bits
        result.extend([int(b) for b in bits])
    return result

#function that convert string to bits
def frombits(bits):
    chars = []
    for b in range(len(bits) / 8):
        byte = bits[b*8:(b+1)*8]
        chars.append(chr(int(''.join([str(bit) for bit in byte]), 2)))
    return ''.join(chars)

#Function that separate a list of bits in 128 bits block and do the zero padding (Used to do our 128 bits block)
def slice(listBits):
    blocks = []
    block = []
    longeur = len(listBits)

    if longeur<128: # If smaller than 128
        block = listBits
        paddingLenght = longeur-128
        pad = [0 for i in range(paddingLenght)]
        block += pad #Padding
        blocks.append(block)
        return blocks

    nbrBlocks = math.floor(longeur/128)

    for i in range(0,nbrBlocks): # If the longeur is a multiple no need of pad
        block = listBits[(i*128):((i+1)*128)]
        blocks.append(block)

    if longeur % 128 != 0: # If the length is not multiple of 128 (Need to pad)
        #Last block
        block = listBits[nbrBlocks*128:-1]
        longeurLast = len(block)
        paddingLenght = 128-longeurLast
        padding = [0 for i in range(paddingLenght)]
        block += padding
        blocks.append(block)

    return blocks


# Convert list of integer to string
def listToString(list):
    string_ints = [str(int) for int in list]
    str_of_ints = "".join(string_ints)
    return str_of_ints


# Put the blocks into matrix ordered by column
def blocksTomatrix(blocks):
    #Rearange to have byte in each element
    matrix =[]
    for element in blocks:
        block = np.asarray(element)
        blockByte = np.resize(block,(16,8))
        matrix.append(blockByte)
    matrix = np.asarray(matrix)

    #Store each matrix 4 by 4 in matrices
    matrices=[]
    for k in range(len(matrix)):
        m = np.zeros((4, 4))
        m = m.astype('str')
        c = 0
        for i in range(4):
            for j in range(4):
                m[i][j]=listToString(matrix[k][c])
                c += 1
        matrices.append(m)

    # Taking the transpose to order by column
    for i in range(len(matrices)):
        matrices[i] = matrices[i].transpose()

    return matrices

#Return an int in it's binary form
def intTo8bits(int):
    return '{0:08b}'.format(int)

#Circular shift of one bits so argument must be equal to 8 for one byte
def Rotation(str,left,right):
    res = (str * 3)[len(str) + left - right:
                         2 * len(str) + left - right]
    return res

#Transformation for 4 bytes (Bytesub) (Used to generate W)
def boxTransformation(bytes,box):
    # Stores each four bits in string format
    Strings=[]
    for i in range(8):
        String = bytes[i*4:i*4+4]
        Strings.append(String)

    #Convert each 4 bits to integer
    Integers = []
    for element in Strings:

        Integers.append(int(element,2))

    #Take the value for each byte inside the Sbox
    firstByte = intTo8bits(box[Integers[0]][Integers[1]])
    secondByte = intTo8bits(box[Integers[2]][Integers[3]])
    thirdByte = intTo8bits(box[Integers[4]][Integers[5]])
    fourthByte = intTo8bits(box[Integers[6]][Integers[7]])

    # Return the concatenation in strings of 32 bits
    return firstByte + secondByte + thirdByte + fourthByte

## Transformation test
#print(boxTransformation("00000000000000010001000100010000"))

#Same for one byte (Used for compute all member of our new matrix
def boxTransformationOneByte(byte,box):

    Strings=[]
    for i in range(2):
        String = byte[i*4:i*4+4]
        Strings.append(String)

    #Convert each 4 bits to integer
    Integers = []
    for element in Strings:
        Integers.append(int(element,2))

    #Take the value of the byte
    firstByte = intTo8bits(box[Integers[0]][Integers[1]])

    return firstByte

# Compute all the 32 bits part of our keys
def Wcompute(R,N,K,rc):
    constante = '{0:024b}'.format(0)
    longeur = 4*R
    W=[0 for i in range(longeur)] #Doit contenir 4 mot de 32 bits en string
    for i in range(longeur):
        if i<N:
            W[i] = K[i]
        else:
            if ((i>=N) and (i % N == 0)):
                rcon = intTo8bits(rc[int(i / N)-1])
                rcon += constante

                a = Rotation(W[i-1],8,0)
                S = boxTransformation(a,Sbox)
                W[i] = polXor(polXor(S,W[i-N]),rcon)
            else:
                if ((i>N and N>6) and (i%N==4)):

                    W[i] = polXor(W[i-N],boxTransformation(W[i-1]),Sbox)
                else:
                    W[i] = polXor(W[i-N],W[i-1])

    return W

# Compute the part of the key by calling Wcompute()
def keyExpansion(cle):
    rc = [0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1B,0x36]
    longueur = len(cle)
    N = int(len(cle)/32)
    K = [0 for i in range(N)]
    for i in range(N):
        K[i] = cle[i*32:i*32+32]

    if longueur == 128:
        R = 11
    else:
        if longueur == 192:
            R = 13
        else:
            if longueur == 256:
                R = 15
            else: print("Mauvaise taille de clé")
    W = Wcompute(R,N,K,rc)
    return W

# Convert a string into a liste (Used to simplify to put the blocks in the right format to obtain the fulls keys of 128 bits)
def Convert(string):
    list1=[]
    list1[:0]=string
    return list1

#Put the keys together to have 128 bits key
def keysToBlock(keys):
    blocks = []
    for i in range(int(len(keys)/4)):
        block = []
        block.append(keys[i*4]+keys[i*4+1]+keys[i*4+2]+keys[i*4+3])
        blocks.append(list(map(int,Convert(block[0]))))
    return blocks


# Initial step Or addroundkey step depending of the parameter step which define the key used
def initialStep(matricesPlains, matricesKeys,step):
    matricesInitials = []
    for elements in matricesPlains:
        m = np.zeros((4, 4))
        m = m.astype('str')
        for i in range(4):
            for j in range(4):
                m[i][j] = polXor(elements[i][j], matricesKeys[step][i][j])

        matricesInitials.append(m)
    return matricesInitials

#Function that regroup a row to make the shift (Used to simplify the shiftRow)
def regroup(matrices,matriceIndex,rowIndex):
    group=""
    for element in matrices[matriceIndex][rowIndex]:
        group+=element
    return group

#Function that separate a 32 bits into 4 part of byte (In a list) (Used to simplify the shiftRow)
def separate(str):
    part = [0,8,16,24]
    part.append(len(str))
    return [str[i: j] for i, j in zip(part, part[1:])]

# Do the shiftRowLeft transformation
def shiftRowLeft(matrices):
    matricesRes = []
    for k in range(len(matrices)):
        m = np.zeros((4, 4))
        m = m.astype('str')
        for i in range(4):
            for j in range(4):
                if i == 0:
                    m[i][j] = matrices[k][i][j]
                else:
                    list = separate(Rotation(regroup(matrices,k,i),i*8,0))
                    m[i][j]=list[j]

        matricesRes.append(m)

    return matricesRes

# Do the shiftRowRight transformation
def shiftRowRight(matrices):
    matricesRes = []
    for k in range(len(matrices)):
        m = np.zeros((4, 4))
        m = m.astype('str')
        for i in range(4):
            for j in range(4):
                if i == 0:
                    m[i][j] = matrices[k][i][j]
                else:
                    list = separate(Rotation(regroup(matrices,k,i),0,i*8))
                    m[i][j]=list[j]

        matricesRes.append(m)

    return matricesRes

# Do the mixColumn Transformation
def MixColumn(matrices,mixColumnMatrix):
    matricesRes = []
    for k in range(len(matrices)):
        m = np.zeros((4, 4))
        m = m.astype('str')
        for i in range(4):
            for j in range(4):
                row = mixColumnMatrix[i]
                column = matrices[k][:,j]
                m[i][j] = polXor(polXor(polyTobits(polyMul(row[0],column[0])),polyTobits(polyMul(row[1],column[1]))),polXor(polyTobits(polyMul(row[2],column[2])),polyTobits(polyMul(row[3],column[3]))))
                # Product and sum of row of mixMatric and column of Plain/Cipher
        matricesRes.append(m)

    return matricesRes

#Definition of constant mix Matrix and putting it in adequate format for my code
mixColumnMatrixDirect = np.matrix([[2,3,1,1],[1,2,3,1],[1,1,2,3],[3,1,1,2]])
mixColumnMatrixDirect = mixColumnMatrixDirect.astype('str')
#Convert element to binary
for i in range(4):
    for j in range(4):
        mixColumnMatrixDirect[i,j] = intTo8bits(int(mixColumnMatrixDirect[i,j]))

#Same for indirect matrix
mixColumnMatrixInDirect = np.matrix('14 11 13 9;9 14 11 13;13 9 14 11;11 13 9 14')
mixColumnMatrixInDirect = mixColumnMatrixInDirect.astype('str')

for i in range(4):
    for j in range(4):
        mixColumnMatrixInDirect[i,j] = intTo8bits(int(mixColumnMatrixInDirect[i,j]))

mixColumnMatrixDirect = np.asarray(mixColumnMatrixDirect)
mixColumnMatrixInDirect = np.asarray(mixColumnMatrixDirect)


### ENCRYPTION
message = "deniz est le boss et c'est tout"
listeBits = tobits(message) #Transforme the message to binary
blocks = slice(listeBits) #take the list of binary to put them in blocks of 128 bits
matricesPlains = blocksTomatrix(blocks) #Obtain matrix of size 4x4

cle = "Thats my Kung Fu"
key128 = listToString(tobits(cle)) #Convert in 128 bits key
keys = keyExpansion(key128)# Compute W and put them in the correct format
matricesKeys = blocksTomatrix(keysToBlock(keys)) #Put the keys in matrix form


def Encryption(matricesPlains,matricesKeys):

    matricesPlains = initialStep(matricesPlains,matricesKeys,0) #Initial step

    for i in range(len(matricesKeys)-2): # All transformation in order

        for k in range(len(matricesPlains)):  # ByteSub
            for i in range(4):
                for i in range(4):
                    matricesPlains[k][i][j] = boxTransformationOneByte(matricesPlains[k][i][j],Sbox)

        matricesPlains = shiftRowLeft(matricesPlains) #ShiftRow Left
        matricesPlains = MixColumn(matricesPlains,mixColumnMatrixDirect) # Mix column
        matricesPlains = initialStep(matricesPlains,matricesKeys,i+1) # addRoundKey

  ## Last iteration without mixColumns
    for k in range(len(matricesPlains)):  # ByteSub
        for i in range(4):
            for i in range(4):
                matricesPlains[k][i][j] = boxTransformationOneByte(matricesPlains[k][i][j], Sbox)

    matricesPlains = shiftRowLeft(matricesPlains)  # ShiftRow Left
    matricesPlains = initialStep(matricesPlains,matricesKeys,len(matricesKeys)-1)#Last addRoundKey


    return matricesPlains

#Inverse order of key
cipherkeys = keys[::-1]
matricesCipherkeys = blocksTomatrix(keysToBlock(cipherkeys))

def Decryption(matricesCipher,matricesCipherKeys):

    # First iteration reverse transformation
    matricesCipher = initialStep(matricesCipher,matricesCipherKeys,0)
    matricesCipher = shiftRowRight(matricesCipher)  # ShiftRow Right
    for k in range(len(matricesCipher)):  # ByteSub
        for i in range(4):
            for i in range(4):
                matricesCipher[k][i][j] = boxTransformationOneByte(matricesCipher[k][i][j], Sbox_inv)

    #Next iteration
    for i in range(len(matricesCipherKeys)-2):

        matricesCipher = initialStep(matricesCipher, matricesCipherKeys, i + 1)  # addRoundKey
        matricesCipher = MixColumn(matricesCipher, mixColumnMatrixInDirect)  # Mix column
        matricesCipher = shiftRowRight(matricesCipher) #ShiftRow Right

        for k in range(len(matricesCipher)):  # ByteSub
            for i in range(4):
                for i in range(4):
                    matricesCipher[k][i][j] = boxTransformationOneByte(matricesCipher[k][i][j],Sbox_inv)

     #Initial step reverse
    matricesCipher = initialStep(matricesCipher,matricesCipherKeys,len(matricesCipherKeys)-1)#Last addRoundKey

    return matricesCipher

#Call both function to verify
matriceCipher = Encryption(matricesPlains,matricesKeys)
matricesPlains2 = Decryption(matriceCipher,matricesCipherkeys)


# Unfortunately we can see that the bytes in the plains matrix are not equivalent
# In fact i do not know where the error can be, all my transform and my reverse transform seems to be in the good order,
# Furthermore i tried to test the best i can all my function by printing their return value but i cannot see errors.
# Sorry for the trouble, please tell me if you can find it.
print(matricesPlains[0])
print(" ")
print(matricesPlains2[0])





























