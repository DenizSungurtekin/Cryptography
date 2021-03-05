

S´ecurit´e des Syst`emes d’Information

Mandatory TP 1 - AES

September 23rd, 2020

Surrender on Moodle your Python 3 ﬁle(s) .py, before Tuesday, October

13th, 2020 at 11:59 pm (23h59).

Your code needs to be commented.

Goal

The goal of this TP is simple : you will create an AES block cipher, and use it

to encode plaintexts in diﬀerents block cipher modes (ECB and CBC).

AES Encryption

The AES Box will be used with 128 bits plaintext/ciphertext blocks, and with

keys of either 128, 192 or 256 bits. We have one initial step, and we add 10

rounds for 128 bit keys, 12 rounds for 192 bit keys, or 14 rounds for 256 bit

keys.

Whatever the size of the key, we will create sub-keys of 128 bits and work with

128 bits blocks.

IMPORTANT : All calculations are made considering the 128 bits block as a

4x4 matrix of bytes (8 bits), and each byte is as an element of GF(28), which

is the group of polynomials of degree 7 (0 to 7, that’s eight coeﬃcients) with

elements being either 0 or 1.

For instance, 00110101 represents the polynomial x5 + x4 + x2 + 1.

We will then use addition and multiplication for polynomials. In this case, the

addition becomes a simple xor, since we only work with 0 and 1.

VERY IMPORTANT : When slicing the 128 bit message as a 4x4

matrix, they are ordered column by column :

1













m(1, 8) m(33, 40) m(65, 72) m(97, 104)

m(9, 16) m(41, 48) m(73, 80) m(105, 112)

m(17, 24) m(49, 56) m(81, 88) m(113, 120)

m(25, 32) m(57, 64) m(89, 96) m(121, 128)









Where m(x,y) represents the bits x to y from the message block. Each sub key

is also organised as a matrix in the same order (if you do either row by row,

your results will obviously be wrong in some of the operations).

• Key expansion : First, we need a key expansion system, which will cre-

ate a number of keys equal to the number of rounds plus one (which we

will need for the initial step).

We deﬁne a 32 bits constant (which is created following some rules, but

it’s easier to just give you the table) :

rcon = [rc (00) (00)16 (00) ]

i

i

16

16

Where rci is :

i

1

2

3

4

5

6

7

8

9

10

rci (01)16 (02)16 (04)16 (08)16 (10)16 (20)16 (40)16 (80)16 (1B)16 (36)16

We also deﬁne :

– N as the number of 32-bit words of the key (4,6 or 8 depending if

the key is 128, 192 or 256 bits),

– K , K , ..., K

the 32-bit words of the original key,

0

1

N−1

– R the number of keys needed (11, 13 or 15),

– W ,W ,...,W the 32-bit words of the expanded key (this is the

0

result we’re looking for).

1

4R−1

– Rotation([b ,b ,b ,b ]) = [b ,b ,b ,b ] as a one byte left circular shift,

2

0

1

2

3

1

3

0

– SBox([b ,b ,b ,b ]) = [S(b ),S(b ),S(b ),S(b )] the application of the

3

0

1

2

3

0

1

AES S-Box on each of the four bytes.

2

And we can ﬁnally compute the whole expanded key as :



K ,

if i < N,



i





W

⊕ SBox(Rotation(Wi−1)) ⊕ rcon

i

N

,

if i ≥ N and i ≡ 0 mod N,

≥

if i N, N > 6, and i

otherwise.

i−N

Wi =



⊕

≡

Wi−N

SBox(Wi−1),

4 mod N,





W

⊕ Wi−1,

i−N

So the ﬁrst 4 words (W to W ) are the ﬁrst 128 bit key (for the initial

0

step), then the next four ones (W to W ) are the 128 bit key for the ﬁrst

3

4

7

round, and so on to the last four ones (W4R−4 to W4R−1) for the last

round.

2





• initial step : The initial step is an xor with the ﬁrst sub-key (The W to

0

W in the previous deﬁnition),

3

• Rounds : Now, we will do 10/12/14 rounds as follows :

\1. ByteSub : ByteSub is a non linear permutation, applied byte by

byte, following this given table :

Figure 1: The AES S-Box

The four ﬁrst bits (the bigger ones) of the byte give the row, and the

last four (the weaker ones) give the column. For example, (27)16 is

replaced by (cc)16.

\2. ShiftRow : It is a simple operation in which the elements of each

row of the matrix are shifted.

\- The ﬁrst row is left intact,

\- the second row is shifted one byte on the left,

\- the third row two bytes on the left,

\- and the last one by three bytes on the left.

3





Figure 2: Shift Rows step for AES

\3. MixColumn : Each column of 4 bytes b , b , b , b is considered

0

1

2

3

as a polynomial of degree 3 with coeﬃcients being the bytes, which

means elements of GF(28).

These columns are then multiplied by a ﬁxed polynomial modulo

another ﬁxed polynomial (Details can be found easily on google), but

it is equivalent (proof can be found easily too, even on wikipedia) to

say the new bytes d , d , d and d are equal to :

0

1

2

3













  

d0

d

(02)16 (03)16 (01)16 (01)16

b

0

  

(01)16 (02)16 (03)16 (01)

b

 1



16  1

\=

·

(1)







  

d

d

(01)16 (01)16 (02)16 (03)16

b

b

2

3

2

3

(03)16 (01)16 (01)16 (02)16

Attention : Remember that this matrix multiplication applies to

bytes which are elements in GF(28). Which means all operations are

in GF(28), so addition is a xor, and multiplication is a polynomial

multiplication modulo 2 (we’ll come back on this operation later),

\4. AddRoundKey : And a very easy step to ﬁnish : a simple xor with

the sub-key for the round.

• Warning : The last of the 10/12/14 rounds does not apply the MixCol-

umn step.

4





AES Decryption

Decryption goes through the same process, you have to create the same keys,

just use them in reverse order, and apply each round in reverse order with

inverse operations, which means :

• Creating the keys with the original S-box,

• The ByteSub step is done with the inverted S-box :

Figure 3: AES S-Box Inverse

• Shifting rows right instead of left,

• An inverted MixColumn matrix :







(0E)16 (0B)16 (0D)16 (09)16



(09)16

(0E)16 (0B)16 (0D)



16





(0D)16 (09)16 (0E)16 (0B)16

(0B)16 (0D)16 (09)16 (0E)16

• And the inverse of AddRoundKey is itself, since it’s a xor.

• And of course, you need to reverse the order of operations in each round,

and ﬁnish with the reverse initial step.

5





Reminder : Polynomial Operations

In GF(28), addition is just a bitwise xor.

Multiplication is a more complicated matter though. Let’s say we have p , p two

1

2

polynomials. Their product in GF(28) is computed as their standard product,

modulus the irreducible polynomial used to deﬁne GF(28) (in this case, it is

Rijndael’s ﬁnite ﬁeld, deﬁned by r = x8 + x4 + x3 + x + 1).

So all you have to do is multiply p1 and p2, and then reduce it modulo r

to a polynomial of degree strictly inferior to 8. We can do it by observing

x8 + x4 + x3 + x + 1 ≡ 0 means −x8 ≡ x8 ≡ x4 + x3 + x1 + 1 (the ﬁrst

equivalence is because we work modulo two since we’re in GF(28)). And of

course, you have to remember that we’re working modulo 2. For exemple, let’s

say p = x6 + x4 + x3 + 1 and p = x5 + x4 + x2 + x :

1

2

6

4

3

p · p = x · p + x · p + x · p + p

1

2

2

6

2

2

2

= (x11 +x10 +x +x )+(x +x +x +x )+(x +x +x +x )+(x +x +x +x)

8

7

9

8

5

8

7

5

4

5

4

2

= x11 + x10 + x + x + x + x + x + x

9

8

6

5

2

Now, we still have to apply the modulo :

3

2

1

4

3

6

5

2

= (x + x + x + 1) · (x + x + x + 1) + x + x + x + x

7

4

3

6

5

2

7

6

5

4

3

2

= (x + x + x + 1) + x + x + x + x = x + x + x + x + x + x + x + 1

Which means p = (01011001) and p = (00110110) have the product p =

2

1

2

2

p · p = (11111111) .

1

2

2

TP : Implement AES Encryption and Decryption

You have all the information you need to implement a real version of AES with

Python 3. Note that a ﬁle named ”Sboxes.py” is on Moodle and contains the

S-box and S-box inverse already, as two big tuples (you can obviously modify

them if you prefer to work with another type of structure).

What you need to do for encryption :

• First, take a message, and slice it into 128 bit blocks. If the size of the

message is not a multiple of 128 bits, then you need to pad the last block

with zeros (in order to have only 128 bit blocks).

• Then, encrypt each block separately with AES. For that, you will need to

create the whole AES Box described in this TP, including the possibility

to choose the length of the key (either 128, 192 or 256 bits).

• And then all the encrypted blocks form the ciphertext.

6





For the decryption, slice the cipher into 128 bit blocks. Then, run the AES

decryption (The dedicated section about decryption details how to change the

AES box to decrypt instead of encrypt. It’s mainly about reversing the order

of operations and changing the matrices). Then put the plaintexts together to

get the initial message (normally we should also get rid of the padding, but you

can ignore ths part).

It is strongly advised to cut your work into small pieces, and to start with the

basic instruments needed (notably, how to do an xor and a polynomial multipli-

cation). Remember to test each part to ensure they’re working as intended, as it

will allow you to ﬁnd eventual mistakes much easier at the end. The algorithm

itself is already sliced into diﬀerent sub-functions, so following this and starting

one function at the time is a good idea.

Help : How to debug your box

To debug your AES box, you can use this very useful document : [https:](https://kavaliro.com/wp-content/uploads/2014/03/AES.pdf)

[//kavaliro.com/wp-content/uploads/2014/03/AES.pdf](https://kavaliro.com/wp-content/uploads/2014/03/AES.pdf).

It provides an complete example, with a 128 bit message and a 128 bit key,

what is the ﬁnal ciphertext, and every one of the results after each step of the

calculation.

Try with this message and key to see if the AES box if fully functionnal, and if

not, this document should help in ﬁnding where the mistake is.

7


