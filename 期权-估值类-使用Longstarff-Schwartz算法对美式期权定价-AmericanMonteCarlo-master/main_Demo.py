from amc import *
import pylab
import matplotlib.pyplot as plt
def figsize(w: int, h: int):
    pylab.rcParams['figure.figsize'] = w, h


def linestyle(style, reset_color_counter:bool=True):
    pylab.rcParams['lines.linestyle'] = style
    if reset_color_counter:
        pylab.gca().set_prop_cycle(None)  # Reset Colors Counter

class LogNormalPathGenerator(PathGeneratorBase):
    def __init__(self, timeline, path_count, s0, drift, sigma):
        super().__init__(path_count, timeline)
        s = numpy.ones(path_count) * s0
        self.slices.append(numpy.copy(s))
        for dt in numpy.diff(timeline.ndarray):
            dx = numpy.random.normal(0, 1, path_count) * dt ** .5
            ds = drift * s * dt + sigma * s * dx
            s += ds
            self.slices.append(numpy.copy(s))
            
random.seed(0)
n = 10000     # Number of simulation paths            
s0 = 1000     # Starting share price
rf = 0.02     # Drift, and also risk-free rate
sigma = 0.1   # Volatility
timeline       = TimeLine(numpy.linspace(0, 10, 100 + 1))    
path_generator = LogNormalPathGenerator(timeline, n, s0, rf, sigma)
figsize(8, 6)
plotting.plot_paths(path_generator, 100)
plt.savefig("result/paths.png")
class PutOptionPayoff(PayoffBase):
    strike = 1000
    def get(self, observable, time):
        return numpy.maximum(self.strike - observable, 0)
payoff = PutOptionPayoff()
x = linspace(0, payoff.strike*2, 1000)
figsize(8, 4)
plt.plot(x, payoff.get(x, 0)), plt.title('Payoff for american put option with strike=$1')
plt.savefig('result/Payoff for american put option with strike=$1.png')
interp_factory = lambda x, y, itm_mask : PolynomialInterpolator.Create(x, y, itm_mask, 2)
amc = AmcSimulator(payoff, path_generator, timeline, rf, interp_factory, 
                   ConsoleLogger(LogLevel.WARNING), store_regression_data=True)
amc.run()
plotting.plot_regression(amc, 9.9), plt.legend()
plt.savefig("result/amc_9.9.png")
plt.show()
plotting.plot_regression(amc, 7), plt.legend()
plt.savefig("result/amc_7.png")
plt.show()
plotting.plot_regression(amc, 3), plt.legend()
plt.savefig("result/amc_3.png")
plt.show()
figsize(8, 6)
plotting.plot_quantiles(path_generator, generate_symmetric_quantiles([0.01, 0.025, 0.05, 0.1, 0.25]))
plotting.plot_cashflows(amc.cash_flow_matrix, path_generator, s=1, marker='.', color='black')
plt.savefig("result/cash_flow.png")
plt.plot(path_generator.timeline.ndarray, ones(path_generator.timeline.length) * payoff.strike,
            color='black', linestyle='dashed', alpha=0.5); # Plot strike line
plt.savefig("result/strike line.png")
f = open("result/evaluation.txt","w")
print("NPV : %0.4f" % amc.cash_flow_matrix.calc_npv(rf),file=f)
print("NPV : %0.4f" % amc.cash_flow_matrix.calc_npv(rf))
