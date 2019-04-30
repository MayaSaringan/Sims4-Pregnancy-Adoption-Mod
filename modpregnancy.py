from sims.sim_info_types import Age, Species
from probabilities import BayesTheorem
import random
class BabyTracker:
    def __init__(self,parent):
        self.owner  = parent #SimInfo object
        self.pr_base_want_child = 0.45
        self.pr_want_child = self.get_pr_want_child()
        self.pr_wrt_spouse_does_want_child = 0.3

    @property
    def pr_wrt_age(self):
        if (self.owner.age == Age.YOUNGADULT):
            return 0.75
        elif (self.owner.age == Age.ADULT):
            return 0.70
        elif (self.owner.age == Age.ELDER):
            return 0.2
        else:
            return 0

    @property
    def prt_wrt_income(self):
        if (self.owner.weeklyIncome < 1000):
            return 0.1
        elif (self.owner.weeklyIncome >= 1000 and self.owner.weeklyIncome < 3000):
            return 0.15
        elif (self.owner.weeklyIncome >= 3000 and self.owner.weeklyIncome < 5000):
            return 0.85
        elif (self.owner.weeklyIncome >= 5000 and self.owner.weeklyIncome < 10000):
            return 0.9
        else:
            return 0.98

    @property
    def prt_wrt_funds(self):
        if (self.owner.funds < 1000):
            return 0.5
        elif (self.owner.funds >= 1000 and self.owner.funds < 5000):
            return 0.1
        elif (self.owner.funds >= 5000 and self.owner.funds < 20000):
            return 0.3
        else:
            return 0.95

    @property
    def prt_wrt_traits(self):
        if ('trait_FamilyOriented' in self.owner.traits.personality):
            return 0.99
        elif ('trait_HatesChildren' in self.owner.traits.personality):
            return 0.03
        else:
            return 0

    @property
    def prt_wrt_aspirations(self):
        if ('Track_Family_A' == self.owner.aspiration.name):
            return 0.97
        elif ('Track_Family_B' == self.owner.aspiration.name):
            return 0.99
        else:
            return 0

    @property
    def prt_wrt_num_child(self):
        if (len(self.owner.family.children) == 0):
            return 0.8
        elif (len(self.owner.family.children) == 1):
            return 0.65
        elif (len(self.owner.family.children) == 2):
            return 0.1
        else:
            return 0.05

    @property
    def can_have_child(self):
        if self.can_bear or self.can_seed:
            return True
        return False

    @property
    def can_bear(self):

        impregnableStr = "trait_GenderOptions_Pregnancy_CanBeImpregnated"
        if  impregnableStr in self.owner.traits.genderOptions:
            return True
        return False

    @property
    def can_seed(self):
        canImpregnateStr  = "trait_GenderOptions_Pregnancy_CanImpregnate"
        if canImpregnateStr in self.owner.traits.genderOptions:
            return True
        return False
    @property
    def want_child(self):

        r =  random.random()
        if r < self.pr_want_child:
            return True
        return False


    def get_pr_want_child(self):
        if self.can_have_child:

            br = BayesTheorem()
            pr_asp = self.prt_wrt_aspirations
            pr_trait = self.prt_wrt_traits
            if pr_asp ==0 and pr_trait==0:
                arr = [
                    self.pr_wrt_age,
                    self.prt_wrt_income,
                    self.prt_wrt_num_child,
                    self.prt_wrt_funds
                ]

                return br.apply(self.pr_base_want_child,
                                arr
                                )
            elif pr_asp ==0:
                arr = [
                    self.pr_wrt_age,
                    self.prt_wrt_income,
                    self.prt_wrt_num_child,
                    self.prt_wrt_funds,
                    pr_trait
                ]

                return br.apply(self.pr_base_want_child,
                                arr
                                )
            elif pr_trait == 0:
                arr = [
                    self.pr_wrt_age,
                    self.prt_wrt_income,
                    self.prt_wrt_num_child,
                    self.prt_wrt_funds,
                    pr_asp
                ]

                return br.apply(self.pr_base_want_child,
                                arr
                                )


            else:
                arr = [
                    self.pr_wrt_age,
                    self.prt_wrt_income,
                    self.prt_wrt_num_child,
                    self.prt_wrt_funds,
                    pr_asp,pr_trait
                ]

                return br.apply(self.pr_base_want_child,
                                arr
                                )
        return  0

    def __str__(self):
        returnStr=  ""
        if self.can_have_child:
            if self.want_child:
                returnStr+="Wants child. "
            else:
                returnStr+="Does not want child.  "
            if self.can_bear:
                returnStr+="Can bear. "
            if self.can_seed:
                returnStr+="Can  seed. "
            returnStr+="Pr: "+str(self.pr_want_child)
        else:
            returnStr+= "Can't have child"
        return returnStr


