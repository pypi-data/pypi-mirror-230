from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.problems import get_problem
from pymoo.optimize import minimize
from pymoo.visualization.scatter import Scatter
from pymoo.operators.crossover.pntx import TwoPointCrossover
from pymoo.operators.mutation.bitflip import BitflipMutation
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.repair.rounding import RoundingRepair
from pymoo.operators.sampling.rnd import IntegerRandomSampling,FloatRandomSampling
import numpy as np
from pymoo.core.problem import Problem
import tqdm
from progressbar import ProgressBar


class NetworkMoltiply(Problem):

    def __init__(self,N_layer_multiply=1,N_variant_multiply=1):
        super().__init__(n_var=N_layer_multiply, n_obj=2, n_ieq_constr=1,
                          xl=0, xu=N_variant_multiply-1, vtype=int)
        self.i=0
    def _evaluate(self, x, out, *args, **kwargs):

        out["F"] = [- np.min(x,axis=1),np.max(x,axis=1)]
        #TODO: capire bene cosa fa G
        out["G"] = x[:, 0] - 10*x[:, 1] - 10
        bar.update(kwargs['algorithm'].n_gen)
        self.i+=1



problem = NetworkMoltiply(10,10)#get_problem("zdt1")

#problem = get_problem("zdt1")

algorithm = NSGA2(pop_size=500,
                  sampling=FloatRandomSampling(),
                  crossover=SBX(prob=1.0, eta=3.0, vtype=float),# repair=RoundingRepair()),
                  mutation=PM(prob=1.0, eta=3.0, vtype=float), #repair=RoundingRepair()),
                  eliminate_duplicates=True)

#TODO: mettere una barra di progresso
bar = ProgressBar(max_value = 200)

res = minimize(problem,
              algorithm,
              ('n_gen', 200),
              seed=1,
              verbose=False,bar=bar)

plot = Scatter()
#plot.add(problem.pareto_front(), plot_type="line", color="black", alpha=0.7)
plot.add(res.F, facecolor="none", edgecolor="red")
#print(res.F)
plot.show()