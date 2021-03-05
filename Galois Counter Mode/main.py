import Correc_TP1_AES as AES

#Definition of inputs variable

# You can change value here to test multiple input
P = "Two One Nine Two"
K = "Thats my Kung Fu" # Here dont increase the number of character because AES form tp1 need a 128 bits key. but you can change its value.
A = "This is my Authenticated data" #any number of bits between 0 and 2^64
IV = "This is a value for IV in string for example" #Should be random (must be between 1 and 2^64 bits)
#IV ='asdewazfgdew' # example with 96 bits -> 12 characters


# function int to bits
def binary(int):
    m = '{0:08b}'.format(int)
    if len(m)>64:
        return '{0:0128b}'.format(int)
    return m

#binary(2) return 00000010 in str

# function that take a list of 16 integer to output 128 bits
def bits(liste):
    res = ''
    for element in liste: #each element correspond to a byte
        res += binary(element)
    return res
#Test
# liste = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,120]
# print(bits(liste))
# print(int(binary(liste[-1]),2))

def ToList(binary): #Convert a 128 binary string to a List of 16 integer
    l = []
    for i in range(int(len(binary)/8)):
        l.append(int(binary[i*8:(i+1)*8],2))
    return l

# function that return decimal number corresponding to a list of 16 integer corresponding to 128bits representation for example A_i
def Todecimal(liste):
    return int(bits(liste),2)
# liste = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,120]
# print(Todecimal(liste))


# Padding and 128 bit blocks
def AuthenticatedData(A): # return 128 bits blocks -> each blocks correspond to one A_i / used for cipher and H too(Obviously with H we only take the first element)
    toBlocks = AES.MessageToMatrix(A)
    lastLenght = len(toBlocks[-1])
    nul = [0 for i in range(4)]
    if lastLenght < 4:
        diff = 4 - lastLenght
        for i in range(diff):
            toBlocks[-1].append(0)
    totalLenght = len(toBlocks)

    while totalLenght % 4 != 0:
        toBlocks.append(nul)
        totalLenght += 1

    A_blocks = []
    for i in range(int(totalLenght/4)):
        A_blocks.append(toBlocks[i*4]+toBlocks[i*4+1]+toBlocks[i*4+2]+toBlocks[i*4+3])

    return A_blocks

#print(AuthenticatedData(A)) #tested with different A-values

def matrixToblocks(matrix): # with it we can directly use the AES.MessageToMatrix function to have our blocks of 128 bits
    flat_matrix = [item for sublist in matrix for item in sublist]
    size = len(flat_matrix)
    res = []
    for i in range(int(size/16)):
        res.append(flat_matrix[i*16:(i+1)*16])

    diff = size % 16
    liste = flat_matrix[int(size/16)*16:]

    if diff != 0:
        res.append(liste)
    return res

#Construction of irreductible polynome in binary string:
def irreductiblePoly():
    res=""
    indexs = [0,1,2,7,128]
    for i in range(129):
        if i in indexs:
            res += '1'
        else:
            res += '0'
    return res[::-1]

# print(irreductiblePoly())
# print(int(irreductiblePoly(),2))


def deg(poly):#Return the degree of a polynome
    deg = len(bin(poly)[2:])-1
    return deg

# Polynomial multiplication in GF(2^128), input and output in decimal, irretucdible is the polynome in decimal which define the gallois field
def polyMulti(p1,p2,irretucdible):
    res = 0
    while p1 > 0:
        if p1 & 1:
            res = res^p2

        p1 = p1 >> 1
        p2 = p2 << 1

        if deg(p2) == deg(irretucdible):
            p2 = p2^irretucdible
    return res

#Polynome addition with integer in input
def polyAdd(p1,p2):
    return p1^p2


## test polynomial mult
# print(polyMulti(7,5,int(irreductiblePoly()))) #= 27


##Initial Counter Value
def computeInitialCounter(IV,H):
    size = len(IV)*8
    IV = AuthenticatedData(IV)

    if size == 96:
        # Computation of 32 bits concatenated in case of 96 bits for IV
        concate = ""
        for i in range(31):
            concate += '0'
        concate += '1'

        firstTerm = ''
        for i in range(12): #Take only the first 96 bits
            firstTerm += binary(IV[0][i])
        initialCounter = firstTerm+concate
        return int(initialCounter,2)

    # #Computation of L_IV
    zeros64 = ''
    for i in range(64):
        zeros64 += '0'
    L_IV = zeros64+'{0:0064b}'.format(size)

    IV.append(ToList(L_IV)) # We add L_IV to list containing IV values

    # Compute Initial counter

    #Define irreductible polynome in integer
    irrec = int(irreductiblePoly(),2)

    H = AuthenticatedData(H)[0]

    for i in range(len(IV)-1):
        res = polyMulti(Todecimal(IV[i]),Todecimal(H),irrec)
        res = polyAdd(res,Todecimal(IV[i+1]))
        res = polyMulti(res,Todecimal(H),irrec)

    return res

def stringToInt(string): #Convert a message/cipher of 128 bits to decimal value
    return int(bits(matrixToblocks(AES.MessageToMatrix(string))[0]),2)

def blockToInt(block): #Convert a block of 16 integer to decimal
    return int(bits(block),2)

def counterEncryption(counter): # Make the encryption of a counter easier because integer need some conversion
    matrixCounter = ToList(binary(counter))
    matrixCounter = [[matrixCounter[i * 4], matrixCounter[i * 4 + 1], matrixCounter[i * 4 + 2],matrixCounter[i * 4 + 3]] for i in range(4)]
    counterMessage = AES.MatrixToMessage(matrixCounter)
    C = AES.AES(counterMessage, K, AES.S_box, AES.MixColMatrix)
    return C

def significantBits(counter,nbr): #Fct that return the decimal value with the nbr sigificant bits of a encrypted counter
    res = str(''.join(format(ord(i), 'b') for i in counter))
    res = res[0:nbr]
    return int(res,2)

def decimalToCipher(number):
    cipher=''
    x = '{0:08b}'.format(number)
    while len(x) % 8 != 0: #in case the binary representation is not a multiple of 8 we add 0 until it is
        x = '0'+ x

    for i in range(int(len(x)/8)):
        nb = int(x[i*8:i*8+8],2)

        cipher += chr(nb)

    return cipher

#Authentification with Galois Field
def Authentification(A,H,C_decimals,C_start_decimal):
    #Compute of L using size of A and P
    size_A = len(A)
    size_P = len(P)
    L = int('{0:064b}'.format(size_A) + '{0:064b}'.format(size_P),2)

    #Put in the same format A and H to execute polynomial: liste of 16 integer reprensenting a 128 bits word
    A = AuthenticatedData(A)
    H = AuthenticatedData(H)[0]

    #Define irretuctible polynome in integer
    irrec = int(irreductiblePoly(),2)

    # Authentification
    for i in range(len(A)-1):
        res = polyMulti(Todecimal(A[i]), Todecimal(H), irrec)
        res = polyAdd(res, Todecimal(A[i+1]))
        res = polyMulti(res, Todecimal(H), irrec)
    for i in range(len(C_decimals)):
        res = polyAdd(res, C_decimals[i])
        res = polyMulti(res, Todecimal(H), irrec)

    res = polyAdd(res, L)
    res = polyMulti(res, Todecimal(H), irrec)
    res = polyAdd(res, C_start_decimal)
    return res


def Encryption(P,IV,K,A):
    # Computation of Hash subkey
    nullMatrix = [[0 for i in range(4)] for j in range(4)]
    nullMessage = AES.MatrixToMessage(nullMatrix)
    H = AES.AES(nullMessage, K, AES.S_box, AES.MixColMatrix)

    # Encryption of initial counter
    initialCounter = computeInitialCounter(IV, H)  # Result in integer
    C_start_decimal = initialCounter
    C_start = counterEncryption(initialCounter)  # Used later but in decimal thats why we do not use this variable

    Ciphers = []
    CiphersDecimal = [] # store decimals value for authentification
    P_blocks = matrixToblocks(AES.MessageToMatrix(P))
    for i in range(len(P_blocks)):
        if i == len(P_blocks)-1: # Last case when the last block is not necessary of size 128 bits
            initialCounter += 1
            C = counterEncryption(initialCounter)
            size = len(P_blocks[-1])
            nbrBits = size*8
            pValue = blockToInt(P_blocks[i])
            cValue = significantBits(C,nbrBits)
            res = polyAdd(cValue,pValue)

            cipher = decimalToCipher(res)
            Ciphers.append(cipher)
            CiphersDecimal.append(res)
            break

        initialCounter += 1 # increment counter
        C = counterEncryption(initialCounter)
        pValue = blockToInt(P_blocks[i]) # Value in decimal of 128 bits block
        cValue = stringToInt(C) # Value in decimal of encrypted cipher
        res = polyAdd(cValue,pValue) # Xor operation
        cipher = decimalToCipher(res)
        Ciphers.append(cipher)
        CiphersDecimal.append(res)

    Tag = Authentification(A, H, CiphersDecimal,C_start_decimal)
    finalCipher =''
    for element in Ciphers:
        finalCipher += element
    return finalCipher,Tag #Return Ciphers in string too to see it if we want



#DEcryption
def Decryption(C,T,K,A,IV):

    # Computation of Hash subkey
    nullMatrix = [[0 for i in range(4)] for j in range(4)]
    nullMessage = AES.MatrixToMessage(nullMatrix)
    H = AES.AES(nullMessage, K, AES.S_box, AES.MixColMatrix)
    initialCounter = computeInitialCounter(IV, H)

    C_blocks = matrixToblocks(AES.MessageToMatrix(C)) # Obtain blocks of 16 integer for ciphertext and convert it to decimal
    C_decimals = [blockToInt(element) for element in C_blocks]

    Tag = Authentification(A, H, C_decimals,initialCounter) #Compute tag value associated to the cipher
    if Tag == T:
        Plains = []
        Plains_decimals = []

        for i in range(len(C_decimals)):
            if i == len(C_decimals) - 1:  # Last case when the last block is not necessary of size 128 bits
                initialCounter += 1
                C = counterEncryption(initialCounter)
                size = len('{0:08b}'.format(C_decimals[-1]))
                while size % 8 != 0: # in case size is not a multiple of 8
                    size += 1
                nbrBits = size
                cipherValue = C_decimals[i]
                cValue = significantBits(C, nbrBits)
                res = polyAdd(cValue, cipherValue)

                plain = decimalToCipher(res)
                Plains.append(plain)
                Plains_decimals.append(res)
                break

            initialCounter += 1  # increment counter
            C = counterEncryption(initialCounter)
            pValue = C_decimals[i]
            cValue = stringToInt(C)  # Value in decimal of encrypted cipher
            res = polyAdd(cValue, pValue)  # Xor operation
            plain = decimalToCipher(res)
            Plains.append(plain)
            Plains_decimals.append(res)
        final_plain = ''
        for element in Plains:
            final_plain += element
        return final_plain
    else:
        return "FAIL: WRONG TAG"


#ENCRYPTION
C,Tag = Encryption(P,IV,K,A) ## ATENTION les ciphers (C) peuvent s'afficher avec un point d'interogation dans ce cas il est possible d'utiliser la methode .encode('utf8)
#DECRYPTION
plain = Decryption(C,Tag,K,A,IV)


print("Original plaintext: ",P)
print("Decrypted plaintext: ",plain)

# The code seems to work correctly, i tested it with multiple A,P or IV value. Please tell me if you find something that was wrong or misunderstood, thank you.