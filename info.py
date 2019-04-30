import services
from tunable_time import Days as tdays
from relationships.relationship_bit import RelationshipBitCollectionUid
from modpregnancy import *
from sims.sim_info_types import Age
from traits.traits import TraitType
from probabilities import BayesTheorem
from sims.pregnancy.pregnancy_tracker import PregnancyTracker
import random
Days = [tdays.SUNDAY,
        tdays.MONDAY,
        tdays.TUESDAY,
        tdays.WEDNESDAY,
        tdays.THURSDAY,
        tdays.FRIDAY,
        tdays.SATURDAY]
class CoupleInfo:
    def __init__(self,sim1,sim2):
        #check if sim1 is valid for a couple

        self.sim1 = sim1
        self.sim2 = sim2
        self.pr_poa_wrt_pregnant = 0.6
        self.pr_poa_wrt_adopt= 0.8
        self.bearer,self.seeder=  self.get_bearer_seeder()


    @property
    def pr_pregnant_over_adopt(self):
        br = BayesTheorem()
        return br.apply(0.5,[self.pr_poa_wrt_pregnant,self.pr_poa_wrt_adopt])
    def get_bearer_seeder(self):

        if (self.sim1.baby_tracker.can_bear
            and self.sim2.baby_tracker.can_bear
            and self.sim1.baby_tracker.can_seed
            and self.sim2.baby_tracker.can_seed):

            r = random.random()
            if r<0.5:
                return self.sim1,self.sim2
            else:
                return self.sim2,self.sim1
        elif (self.sim1.baby_tracker.can_bear
            and self.sim2.baby_tracker.can_seed):

            return  self.sim1, self.sim2
        elif (self.sim2.baby_tracker.can_bear
            and self.sim1.baby_tracker.can_seed):
            return self.sim2, self.sim1
        else:
            return None

    @property
    def want_child(self):
        r =  random.random()
        if  r < self.pr_want_child:
            return True
        return False



    def have_baby(self):
        if self.want_child  and self.can_have_baby:
            pr_pregnant= 0

            if (self.bearer.age == Age.YOUNGADULT):
                pr_pregnant = 0.75
            elif (self.bearer.age == Age.ADULT):
                pr_pregnant = 0.65
            elif (self.bearer.age == Age.ELDER):
                pr_pregnant = 0.03
            r = random.random()
            if r < pr_pregnant:
                self.bearer.impregnate(self.seeder)
                self.bearer.household_count +=1
                return True



        elif self.can_have_baby:# does not want child
            pr_pregnant = 0

            if (self.bearer.age == Age.YOUNGADULT):
                pr_pregnant = 0.05
            elif (self.bearer.age == Age.ADULT):
                pr_pregnant = 0.03
            elif (self.bearer.age == Age.ELDER):
                pr_pregnant = 0.001
            r = random.random()
            if r < pr_pregnant:
                self.bearer.impregnate(self.seeder)
                self.bearer.household_count += 1


                return True
        return None

    @property
    def pr_want_child(self):
        return float(self.sim1.baby_tracker.pr_want_child * self.sim1.baby_tracker.pr_wrt_spouse_does_want_child)
    @property
    def can_have_baby(self):
        if self.bearer is None or self.seeder is None:
            return False
        if self.bearer.raw_info.pregnancy_tracker.is_pregnant:
            return False
        if self.bearer.household_count<8:
            return True
        return  True


    def __str__(self):
        return "====Couple====\n"+"Couple Pr to want child: "+str(self.pr_want_child)+"\nBearer: "+self.bearer.fullName+". Seeder:  "+self.seeder.fullName+"\n"+str(self.sim1) + ".\n"+ str(self.sim2)
class SimInfo:
    def __init__(self,sim_info):
        self.id = sim_info.id
        self.raw_info = sim_info

        self.fullName = sim_info.first_name+" " +sim_info.last_name
        self.firstName = sim_info.first_name
        self.lastname = sim_info.last_name
        self.age = sim_info.age
        self.pr_want_child = 0

        self.weeklyIncome = 0
        if sim_info.career_tracker is not None:
            careers = sim_info.careers.values()
            if careers:
                for career in careers:

                    careerInfo = CareerInfo(sim_info,career)
                    self.weeklyIncome += careerInfo.weeklyIncome

        self.traits = TraitInfo(sim_info)
        self.aspiration = AspirationInfo(sim_info)
        self.funds = sim_info.family_funds.money
        self.baby_tracker = BabyTracker(self)
        self.household_count = 8 - self.raw_info.household.free_slot_count
    def adopt(self,seeder):
        for coll in services.get_adoption_service()._sim_infos.values():
            for item in coll:

                item = services.get_adoption_service().convert_base_sim_info_to_full(item.sim_id)
                services.get_adoption_service().remove_sim_info(item)
                PregnancyTracker.initialize_sim_info(item,self,seeder)

                return

    @property
    def family(self):
        return FamilyInfo(self.raw_info)

    def impregnate(self,seeder):
        pregnancy_tracker = self.raw_info.pregnancy_tracker
        pregnancy_tracker.start_pregnancy(self.raw_info,seeder.raw_info)
        pregnancy_tracker.complete_pregnancy()
        pregnancy_tracker._create_and_name_offspring()
        pregnancy_tracker._show_npc_dialog()
        pregnancy_tracker.clear_pregnancy()
        pregnancy_tracker.clear_pregnancy_visuals()

    def hasSpouse(self):
        if self.family.spouse is None:
            return False
        return True

    def getSpouse(self):
        if self.hasSpouse():
            return self.family.spouse
        return None

    def eligibleForChild(self):
        return self.hasSpouse()

    def __str__(self):
        returnStr ="===Sim===:\n"
        returnStr +="Name: "+str(self.fullName)+"\n"
        returnStr +="Age: "+str(self.age)+"\n"
        returnStr +="Weekly Income:  "+str(self.weeklyIncome)+"\n"
        returnStr +="Aspiration: "+str(self.aspiration.name)+ "("+str(self.aspiration.actual)+")\n"
        returnStr +="Personality Traits: "+str(self.traits.personality)+"\n"
        returnStr += "Gender Options: " + str(self.traits.genderOptions) + "\n"
        returnStr +="Spouse: "
        if self.family.spouse:
            returnStr+=self.family.spouse.first_name + " "+ self.family.spouse.last_name+"\n"
        else:
            returnStr+= "None\n"
        returnStr +="Children: "
        if (len(self.family.children))>0:
            for child in self.family.children:
                returnStr +=child.first_name+" "+child.last_name+", "
            returnStr +="\n"
        else:
            returnStr +="none\n"
        returnStr+="Funds: "+str(self.funds)+"\n"
        returnStr+= "Baby Tracker: "+str(self.baby_tracker)+"\n"
        return returnStr
class AspirationInfo:
    def __init__(self,sim_info):
        self.name = sim_info.primary_aspiration.__name__
        self.actual = sim_info.primary_aspiration

class TraitInfo:
    def __init__(self,sim_info):
        self.personality = []
        self.genderOptions = []
        traitTracker = sim_info.trait_tracker
        for trait in traitTracker.equipped_traits:
            if trait.trait_type == TraitType.PERSONALITY:
                self.personality.append(trait.__name__)
            if trait.trait_type == TraitType.GENDER_OPTIONS:
                self.genderOptions.append(trait.__name__)


class FamilyInfo:
    def __init__(self,sim_info):
        self.father = None
        self.mother = None
        self.spouse = sim_info.get_significant_other_sim_info()
        self.children = []
        self.siblings = []
        relationships = sim_info.relationship_tracker.get_target_sim_infos()
        for other_sim in relationships:
            relBits = sim_info.relationship_tracker.get_all_bits(other_sim.sim_id)
            for relBit in relBits:
                if RelationshipBitCollectionUid.Family in relBit.collection_ids:
                    if (RelationshipBitCollectionUid.Romance not in relBit.collection_ids
                    and RelationshipBitCollectionUid.Child in relBit.collection_ids):
                        self.children.append(other_sim)
                    if (RelationshipBitCollectionUid.Romance not in relBit.collection_ids
                    and RelationshipBitCollectionUid.Child not in relBit.collection_ids):
                        self.siblings.append(other_sim)




class CareerInfo:
    def __init__(self,simInfo,career):
        self.owner = simInfo
        self.name = type(career).__name__
        self.level = career.user_level
        self.hourlyIncome = career.get_hourly_pay()
        self.dailyHours = self.getDailyHours(career)
        self.weeklyHours = self.getWeeklyHours(career)
        self.weeklyIncome = self.hourlyIncome*self.weeklyHours




    #assumes that work hours always start flat on the hour
    #and flat on end of the hour
    def getDailyHours(self,career):
        if career._work_scheduler is None:
            return 0
        schedules = career._work_scheduler._schedule_entries

        dailyHours = 0
        for sched in schedules:
            if sched.start_time.hour()>sched.end_time.hour():
                dailyHours =24-sched.start_time.hour()+sched.end_time.hour()
            else:
                dailyHours = sched.end_time.hour() - sched.start_time.hour()
            break
        return dailyHours

    def getWeeklyHours(self,career):
        if career._work_scheduler is None:
            return 0
        schedule = career._work_scheduler._schedule_entries
        weeklyHours = 0

        #for each day of the schedule(which is a week),
        #if sim works that day, add to weekly hours
        for sched in schedule:
            for i in range(len(Days)):
                if sched.entry.days_available[Days[i]]:
                    weeklyHours+=self.dailyHours
            break
        return weeklyHours



    def __str__(self):
        return self.name +" - "+self.level

    def testOutput(self):
        returnStr = "TESTING CAREER INFO:\n"
        returnStr+= "Name: "+str(self.name)+"\n"
        returnStr+= "Level: "+str(self.level)+"\n"
        returnStr+= "Daily Hours: "+str(self.dailyHours)+"\n"
        return returnStr

