class BayesTheorem:

    #following assumes leftSide is a single value
    #and right side can be multiple values
    def __init__(self):
        self.dummy = True

    def apply(self,leftSide,rightSide):

        denominator = 0
        denominator1 = 1
        denominator2 = 1
        for val in rightSide:
            denominator1 *= float(1-val)
            denominator2 *= float(val)
        if float((1-leftSide)**2) ==0:
            return 0
        else:
            denominator1 /= float((1-leftSide)**2)
        if float(leftSide**(len(rightSide)-1))==0:
            return 0
        else:
            denominator2 /= float(leftSide**(len(rightSide)-1))
        if denominator2 ==0:
            return 0
        else:
            denominator = denominator1/denominator2
        denominator += 1
        return 1/denominator


