class Kali:
        def GetTools():
                modules = [
                            "git clone https://github.com/htr-tech/zphisher.git",
                            "git clone https://github.com/th3unkn0n/osi.ig.git",
                        ##    "git clone https://github.com/thelinuxchoice/inshackle",
                            "git clone https://github.com/htr-tech/nexphisher.git",
                            "git clone https://github.com/xHak9x/SocialPhish.git",
                            "git clone https://github.com/suljot/shellphish.git",
                            "git clone https://github.com/iinc0gnit0/BlackPhish",
                            "git clone https://github.com/jaykali/maskphish",
                            "git clone https://github.com/htr-tech/unfollow-plus.git",
                        ##    "git clone https://github.com/thelinuxchoice/blackeye",
                        ##    "git clone https://github.com/DarkSecDevelopers/HiddenEye-Legacy.git",
                            "git clone https://github.com/sherlock-project/sherlock.git",
                            "git clone https://github.com/capture0x/XCTR-Hacking-Tools/",
                            "git clone https://github.com/AdrMXR/KitHack.git",
                            "git clone https://github.com/rajkumardusad/IP-Tracer.git",
                            "git clone https://github.com/xadhrit/terra.git",
                            "git clone https://github.com/jaygreig86/dmitry.git",
                            "git clone https://github.com/lanmaster53/recon-ng.git",
                            "git clone https://github.com/m4ll0k/Infoga.git",
                            "git clone https://github.com/Ultrasecurity/DarkSide",
                            "git clone https://github.com/CybernetiX-S3C/InfoSploit",
                            "git clone https://github.com/Z4nzu/hackingtool.git",
                            "git clone https://github.com/m3n0sd0n4ld/uDork",
                            "git clone https://github.com/jackind424/onex.git",
                            "git clone https://github.com/opsdisk/pagodo.git",
                            "git clone https://github.com/jseidl/GoldenEye.git",
                            "git clone https://github.com/ultrasecurity/Storm-Breaker",
                            "git clone https://github.com/abhisharma404/vault.git",
                            "git clone https://github.com/rezasp/joomscan.git",
                            "git clone https://github.com/m8r0wn/crosslinked",
                        ##    "git clone https://github.com/GitHackTools/BillCipher",
                            "git clone https://github.com/pwn0sec/PwnXSS",
                            "git clone https://github.com/commixproject/commix.git"
                ]

                import os
                for module in modules:
                    os.system(module)

class Int:
        @staticmethod
        def chkprime(number):
            if number > 1:
                for i in range(2, number):
                    if (number % i) == 0:
                        return False
                else:
                    return True
            else:
                return False

        @staticmethod
        def factorial(number):
            fact = 1
            for i in range(1, number + 1):
                fact = fact * i
            return fact

        @staticmethod
        def palindrome(number):
            temp = number
            rev = 0
            while number > 0:
                dig = number % 10
                rev = rev * 10 + dig
                number = number // 10
            if temp == rev:
                retur True
            else:
                return False

        @staticmethod
        def findprimes(start, stop):
            primes = []
            for num in range(start, stop + 1):
                if num > 1:
                    for i in range(2, num):
                        if (num % i) == 0:
                            break
                    else:
                        primes.append(num)
            return primes

        @staticmethod
        def reverse(number):
            rn = 0
            while number != 0:
                digit = number % 10
                rn = rn * 10 + digit
                number //= 10
            return rn

        @staticmethod
        def sumdigits(number):
            sum = 0
            temp = number
            while number != 0:
                digit = number % 10
                sum = sum + digit
                number //= 10
            return sum

class Str:
        @staticmethod
        def palindrome(string):
            rev = ""
            for i in string:
                rev = i + rev
            if rev == string:
                return True
            else:
                return False

        @staticmethod
        def analyse(string):
            a = 0  # Initial Assign
            u = 0  # Initial Assign
            l = 0  # Initial Assign
            d = 0  # Initial Assign
            al = 0  # Initial Assign
            o = 0  # Initial Assign
            for i in string:
                if i.isupper():  # Check for Upper
                    u += 1
                    al += 1
                elif i.islower():  # Check for Lower
                    l += 1
                    al += 1
                elif i.isdigit():  # Check for Digits
                    d += 1
                else:  # Other Symbols
                    o += 1
            a = len(string)
            return {"Total": a, "UpperCase": u, "LowerCase": l, "Digits": d, "Alphabets": al, "Others": o}

        @staticmethod
        def occurrence(string, word):
            ct = 0
            for i in range(len(string)):
                if string[i] == word[0]:
                    if string[i:i + len(word)] == word:
                        ct += 1
            return ct

        @staticmethod
        def longest(string):
            mx = ""
            ln = 0
            m = 0
            a = string.split()
            l = len(a)
            for i in range(l):
                ln = len(a[i])
                if ln > m:
                    m = ln
                    mx = a[i]
            return mx

class List:
    @staticmethod
    def frequency(list):
        freq = 0
        lst = [ ]
        result = {}
        for i in list:
            while i not in lst:
                freq = list.count(i)
                lst.append(i)
                if freq > 1:
                    result[i] = f"{freq} times"
                elif freq == 1:
                    result[i] = f"{freq} times"
        return result
    
    @staticmethod
    def maxminrange(list, start, stop):
        mn = 0
        mx = 0
        lst = [ ]
        lst = list[start:stop+1]

        for i in lst:
            if i > mx:
                mx = i
        for j in lst:
            if mn == 0:
                mn = j
            elif j < mn:
                mn = j
        return {"Max":mx, "Min":mn}
    
    @staticmethod
    def removedups(list):
        lst = [ ]

        for i in list:
            while i not in lst:
                lst.append(i)
        return lst

class Tuple:
    @staticmethod
    def frequency(tuple):
        freq = 0
        tup = ()
        result = {}
        for i in tuple:
            while i not in tup:
                freq = tuple.count(i)
                tup += (i,)
                if freq > 1:
                    result[i] = f"{freq} times"
                elif freq == 1:
                    result[i] = f"{freq} times"
        return result
    
    @staticmethod
    def removedups(tuple):
        tup = ()

        for i in tuple:
            while i not in tup:
                tup += (i,)
        return tup

def binary_search(item, array):
    array.sort()
    first=0
    last=len(array)-1
    mid = (first+last)//2
    found = False
    while( first<=last and not found):
        mid = (first + last)//2
        if array[mid] == item :
             return mid
             found= True
        else:
            if item < array[mid]:
                last = mid - 1
            else:
                first = mid + 1 
       
    if found == False:
        return
