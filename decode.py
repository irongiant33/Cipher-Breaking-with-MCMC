#import libraries
import random
import sys
import math
import numpy

#define global variables
symbolProbability={}
transitionProbability={}

#build the dictionary of symbol probabilities. Should be a dictionary of 28 values with 
#each key corresponding to a letter of the alphabet and each value corresponding to the 
#probability of that letter.
#input:
#   -input_fileName: string .CSV file name of the CSV file containing symbol probabilities
def buildSymbolProbability(input_fileName):
    global symbolProbability
    input_file=open(input_fileName,'r')
    temp=input_file.readline()
    input_file.close()
    probabilities=temp[0:len(temp)-1].split(',') #ignore \n at EOL
    alphabet=list('abcdefghijklmnopqrstuvwxyz .')
    for index in range(0,len(alphabet)):
        symbolProbability[alphabet[index]]=float(probabilities[index])

#build the dictionary of transition probabilities. Should be a dictionary of 28x28 values with
#each key corresponding to the tuple of transitions where the first value of the tuple is the 
#current letter and the second value of the tuple is the previous letter. Each key's value
#corresponds to the probability of transitioning from the previous letter to the current letter.
#input:
#   -input_fileName: string .CSV file name of the CSV file containing transition probabilities
def buildTransitionProbability(input_fileName):
    global transitionProbability
    input_file=open(input_fileName,'r')
    matrix=input_file.readlines()
    input_file.close()
    alphabet=list('abcdefghijklmnopqrstuvwxyz .')
    for rowIndex in range(0,len(alphabet)):
        row=matrix[rowIndex]
        rowProbabilities=row[0:len(row)-1].split(',') #ignore \n at EOL
        for colIndex in range(0,len(alphabet)):
            transition=(alphabet[rowIndex],alphabet[colIndex])
            probability=float(rowProbabilities[colIndex])
            
            #a probability of 0 would yield infinity for log, so instead, just set
            #the value to be a very small number
            if(probability==0):
                probability=math.exp(-20)
            transitionProbability[transition]=probability

#returns the string of the unique characters that comprise of the input.
#input:
#   -ciphertext: string value
#output
#   -uniqueChars: string of the unique characters in the order in which they 
#                 occurred in the input string.
def findUniqueChars(ciphertext):
    uniqueChars=''
    for char in ciphertext:
        if(uniqueChars.find(char)<0):
            uniqueChars=uniqueChars+char
    return uniqueChars


#checks to make sure the unique characters in the ciphertext are members of the
#expected characters. Otherwise, throw an error and stop the program.
#input:
#   -uniqueChars: string of the unique characters of the ciphertext. No particular
#                 order is necessary
def checkUniqueChars(uniqueChars):
    expectedChars='abcdefghijklmnopqrstuvwxyz .'
    flag=1
    for char in expectedChars:
        if(uniqueChars.find(char)>-1):
            uniqueChars=uniqueChars.replace(char,'')
    if(len(uniqueChars)!=0):
        flag=-1
    if(flag<0):
        print('ERROR: There was a mismatch in the expected unique characters \
               and the unique characters in your ciphertext. Double check your \
               ciphertext to make sure you are only including the appropriate \
               characters {a-z, ,.}')


#returns an arbitrary cipher function.
#output:
#   -cipherFunction: list of length 28 that maps the letter in the alphabet at
#                    each index to the letter in the cipherFunction at that index
def chooseCipherFunction():
    alphabet='abcdefghijklmnopqrstuvwxyz .'
    cipherFunction=''
    while(len(alphabet)>0):
        randomIndex=random.randint(0,len(alphabet)-1)
        #print(str(randomIndex)+' '+str(len(alphabet)))
        cipherFunction=cipherFunction+alphabet[randomIndex]
        alphabet=alphabet[0:randomIndex]+alphabet[randomIndex+1:len(alphabet)]
    return cipherFunction
    #return 'gscpbediowknzr.uma xhtfvlqyj'

#returns a cipher function that differs in 2 symbols from the input cipher function
#input:
#   -cipherFunction: original cipher function
#output:
#   -newCipherFunction: cipher function that differs in 2 random symbols
def cipherFunctionTransition(cipherFunction):
    switchIndex1=random.randint(0,27)
    switchIndex2=random.randint(0,27)
    newCipherFunction=cipherFunction
    while(switchIndex2==switchIndex1):
        switchIndex2=random.randint(0,27)
    temp=newCipherFunction[switchIndex1]
    newCipherFunction=newCipherFunction[0:switchIndex1]+newCipherFunction[switchIndex2]+newCipherFunction[switchIndex1+1:len(newCipherFunction)]
    newCipherFunction=newCipherFunction[0:switchIndex2]+temp+newCipherFunction[switchIndex2+1:len(newCipherFunction)]
    return newCipherFunction

#given the cipherFunction, decodes the ciphertext via substitution.
#input:
#   -ciphertext: text on which to apply the cipherFunction
#   -cipherFunction: the mapping of alphabet characters
#output:
#   -decoded_text: the text that was generated as a result of applying the cipherFunction
#                  to the ciphertext
def decoded(ciphertext,cipherFunction):
    decoded_text=''
    alphabet='abcdefghijklmnopqrstuvwxyz .'
    for char in ciphertext:
        charIndex=cipherFunction.find(char)
        decoded_text=decoded_text+alphabet[charIndex]
    return decoded_text


#returns the likelihood that the decoded text is correct. Does so based on the probability
#of transitioning from letter to letter. A higher likelihood is associated with a better 
#cipherFunction.
#input:
#   -decoded_text: text to assess the likelihood of
#output:
#   -likelihood: probability that the decoded text is accurate
def calcLogLikelihood(decoded_text,base):
    global symbolProbability
    global transitionProbability
    logLikelihood=0
    #logLikelihood+=math.log(symbolProbability[decoded_text[0]])
    for textIndex in range(1,len(decoded_text)):
        transition=transitionProbability[(decoded_text[textIndex],decoded_text[textIndex-1])]
        logLikelihood+=math.log(transition,base)
    return logLikelihood


#returns the position of the breakpoint in the ciphertext, should there be one. 
#input: 
#   -decoded_text: text to find the breakpoint in
#output:
#   -breakpoint: index of the breakpoint in the ciphertext
def findBreakpoint(decoded_text):
    global transitionProbability
    transition=[]
    average=[]
    derivative=[]
    threshold=round(0.02*len(decoded_text))
    for textIndex in range(1,len(decoded_text)):
        transition.append(transitionProbability[(decoded_text[textIndex],decoded_text[textIndex-1])])
        if(textIndex>threshold):
            average.append(numpy.average(transition[textIndex-threshold-1:textIndex-1]))
        if(textIndex>2*threshold):
            derivative.append((average[textIndex-threshold-1]-average[textIndex-2*threshold-1])/threshold)

    minVal=10000
    minIndex=0
    maxVal=-10000
    maxIndex=0
    for i in range(0,len(derivative)):
        if(derivative[i]<minVal):
            minVal=derivative[i]
            minIndex=i
        if(derivative[i]>maxVal):
            maxVal=derivative[i]
            maxIndex=i
    print([minIndex,maxIndex,threshold,minVal,maxVal])
    if(abs(minVal)>abs(maxVal)):
        return minIndex+threshold
    else:
        return maxIndex+threshold


#returns the fraction of characters that are identical between the decoded text and
#the real text.
#input:
#   -decoded_text: text to compare with real text
#   -realtext: baseline standard
#output:
#   -fraction of times that the decoded_text and realtext matched.
def compare_text(decoded_text,realtext):
    similarity_count=0
    for i in range(0,len(decoded_text)):
        if(decoded_text[i]==realtext[i]):
            similarity_count+=1
    return similarity_count/len(decoded_text)


#calculates the entropy of the input text based on the symbol probability
#input:
#   -input_text: text from which to calculate the entropy
#output:
#   -entropy: entropy defined as the summation of the probabiltiy of each symbol multiplied
#             by the log of the probability of that symbol
def calcEntropy(input_text,base):
    entropy=0
    for i in range(0,len(input_text)):
        p=symbolProbability[input_text[i]]
        entropy+=p*math.log(p,base)
    return entropy


#returns the plaintext from ciphertext after running the Monte Carlo Markov Chain (MCMC) 
#simulation. 
#input:
#   -ciphertext: text to be decrypted.
#   -has_breakpoint: 0 if the ciphertext does not have a breakpoint
#                    1 if the ciphertext has a breakpoint
#output:
#   -plaintext: decrypted ciphertext
def mcmc(ciphertext, has_breakpoint):
    troubleshoot=0
    base=math.exp(1) #set the base with which to take the logarithm

    if(troubleshoot==1):
        metafile=open('metadata.csv','w')
        realtextfile=open('data/plaintext_paradiselost.txt','r')
        realtext=(realtextfile.readlines())[0]
        realtext=realtext.replace('\n','')
        realtextfile.close()

    plaintext=ciphertext
    decoded_message=plaintext
    bestLikelihood=-999999999
    for tries in range(0,10):
        cipherFunction1=chooseCipherFunction()
        logLikelihood1=0
        stationary=0
        iterationCount=0
        acceptanceCount=0
        while(stationary<1000 and iterationCount<10000):
            iterationCount+=1
            decoded_text1=decoded(ciphertext,cipherFunction1)
            logLikelihood1=calcLogLikelihood(decoded_text1,base)
            cipherFunction2=cipherFunctionTransition(cipherFunction1)
            decoded_text2=decoded(ciphertext,cipherFunction2)
            logLikelihood2=calcLogLikelihood(decoded_text2,base)

            coinFlip=random.uniform(0,1)
            acceptanceProbability=logLikelihood2-logLikelihood1
        
            acceptanceProbability=math.pow(base,min(acceptanceProbability,0))
            if(coinFlip<acceptanceProbability):
                acceptanceCount+=1
                stationary=0
                cipherFunction1=cipherFunction2
            else: 
                stationary=stationary+1
                plaintext=decoded_text1

            cycles=10
            if(iterationCount%cycles==0 and troubleshoot==1):
                print('Iteration Count: '+str(iterationCount))
                print('Log Likelihood: '+str(logLikelihood1))
                print('Acceptance Rate: '+str(acceptanceCount/cycles))
                print(plaintext[0:20])
                print()
                accuracy=compare_text(plaintext,realtext)
                metafile.write(str(iterationCount)+','+str(logLikelihood1)+','+str(acceptanceCount/cycles)+','+str(accuracy)+'\n')
                acceptanceCount=0
        if(logLikelihood1>bestLikelihood):
            bestLikelihood=logLikelihood1
            decoded_message=plaintext

    breakpoint=-1
    if(has_breakpoint==1):
        breakpoint=findBreakpoint(decoded_message)

    if(troubleshoot==1):
        metafile.close()

    return [decoded_message[0:len(ciphertext)],breakpoint]

#this is the function that test.py calls in order to test my code. 
#this function is effectively the same as if __name__=="__main__"
#except that it gives less debug information because it is the function
#run by the test script.
#input:
#   -ciphertext: string of ciphertext to decrypt
#   -has_breakpoint: boolean variable that determines whether or not a breakpoint exists.
#output:
#   -plaintext: decrypted ciphertext
def decode(ciphertext,has_breakpoint):

    #build the symbolProbability and transitionProbability dictionaries
    buildSymbolProbability('data/letter_probabilities.csv')
    buildTransitionProbability('data/letter_transition_matrix.csv')
    
    if(has_breakpoint):
        [jumbledtext,breakpoint]=mcmc(ciphertext,1)
        [part1,point1]=mcmc(ciphertext[0:breakpoint],0)
        [part2,point2]=mcmc(ciphertext[breakpoint:len(ciphertext)],0)
        plaintext=part1+part2
        return plaintext
    else:
        [plaintext,breakpoint]=mcmc(ciphertext,0)
        return plaintext

if __name__=="__main__":
    #check user input
    if(len(sys.argv)!=3):
            print("Usage: decode.py ciphertext.txt {0,1}\n")
            print("{false,true} specifies a breakpoint in the cipher.\n")
            print("\tfalse means there is not a breakpoint\n")
            print("\ttrue means there is a breakpoint\n")
    fileName=sys.argv[1]
    try:
        cipherFile=open(fileName,"r")
    except:
        print('ERROR: There was a problem reading in your file.\n \
                Did you spell it correctly? Is it in this directory?')
        sys.exit(0)

    #open and parse the input ciphertext file
    ciphertext=(cipherFile.readlines())[0]
    cipherFile.close()
    ciphertext=ciphertext.replace('\n','')
    uniqueChars=findUniqueChars(ciphertext)
    checkUniqueChars(uniqueChars)

    #build the symbolProbability and transitionProbability dictionaries
    buildSymbolProbability('data/letter_probabilities.csv')
    buildTransitionProbability('data/letter_transition_matrix.csv')

    #get realtext for accuracy check
    realtextfile=open('test_plaintext.txt','r')
    realtext=(realtextfile.readlines())[0]
    realtext=realtext.replace('\n','')
    realtextfile.close()

    #execute MCMC
    decodedtext=''
    if((sys.argv[2]).lower()=='true'):
        [jumbledtext,breakpoint]=mcmc(ciphertext,1)
        [part1,point1]=mcmc(ciphertext[0:breakpoint],0)
        [part2,point2]=mcmc(ciphertext[breakpoint:len(ciphertext)],0)
        decodedtext=part1+part2
    
    [decodedtext2,point]=mcmc(ciphertext,0)
    print("Accuracy without accounting for Breakpoint: "+str(compare_text(decodedtext2,realtext)))
    print("Accuracy accounting for Breakpoint: "+str(compare_text(decodedtext,realtext)))
    print("Breakpoint of paradise lost: 4739 out of 5000")
    print("Breakpoint of war and peace: 25809 out of 85491")
    print("Breakpoint of paradise lost2: 424 out of 5000")

    #write output of MCMC to file
    outFile=open("decoded_text.txt","w")
    for char in decodedtext:
        outFile.write(char)
    outFile.write('\n')
    outFile.close()
