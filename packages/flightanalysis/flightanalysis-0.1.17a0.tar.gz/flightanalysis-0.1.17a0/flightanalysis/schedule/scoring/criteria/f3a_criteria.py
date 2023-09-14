from json import loads
from flightanalysis.schedule.scoring.criteria import Criteria, Exponential, Continuous, Comparison, free, Single
from flightanalysis.data import get_json_resource

class F3ASingle:
    track=Single(Exponential(3.8197186342054885,0.9999999999999999), 'absolute')
    roll=Single(Exponential(3.3937161800825275,1.2618595071429148), 'absolute')
    angle=Single(Exponential(3.8197186342054885,0.9999999999999999), 'absolute')
    distance=Single(Exponential(0.02500000000000001,0.9999999999999999), 'absolute')
class F3AIntra:
    track=Continuous(Exponential(3.8197186342054885,0.9999999999999999), 'absolute')
    roll=Continuous(Exponential(3.3937161800825275,1.2618595071429148), 'absolute')
    radius=Continuous(Exponential(0.25,1.2920296742201791), 'ratio')
    speed=Continuous(Exponential(0.15,1.0), 'ratio')
    roll_rate=Continuous(Exponential(0.15,1.0), 'ratio')
class F3AInter:
    radius=Comparison(Exponential(0.5,0.8613531161467861), 'ratio')
    speed=Comparison(Exponential(0.25,0.8613531161467862), 'ratio')
    roll_rate=Comparison(Exponential(0.25,1.1132827525593783), 'ratio')
    length=Comparison(Exponential(0.5,1.1132827525593785), 'ratio')
    free=Comparison(Exponential(0,1), 'ratio')


class F3A:
    inter = F3AInter
    intra = F3AIntra
    single = F3ASingle


if __name__=='__main__':
    print(F3A.inter.radius)
    print(F3A.intra.radius)
    print(F3A.intra.roll)