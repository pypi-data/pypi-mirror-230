import numpy as np
from cvxopt import matrix
from cvxopt import solvers
from evolufy.information import AvailableInformation

class InvestmentStrategy:
    def optimize(self, information: AvailableInformation):
        return information


class ModernPortfolioTheory:
     def optimize(self, information: AvailableInformation):
        returns = information.valuate()
        self.expected_returns = np.mean(returns, axis=1)
        self.covariance_matrix = np.cov(returns)
        P = matrix(2*self.covariance_matrix, tc="d")
        q = matrix(-information.risk_level*self.expected_returns, tc="d")
        A = matrix(np.ones((1,returns.shape[0])), tc="d")
        b = matrix(1.0)
        self.solution = solvers.qp(P=P,q=q,A=A,b=b)
        for index,entry in enumerate(self.solution['x']):
            information.assets[index].weight = entry
        return information
     def represent_solution(self):
        w_opt = np.array(self.solution['x']).T
        ERp_opt = w_opt@self.expected_returns
        varRp_opt = w_opt@self.covariance_matrix@w_opt.T
        stdevRp_opt = np.sqrt(varRp_opt)
        return varRp_opt-ERp_opt, ERp_opt, varRp_opt, stdevRp_opt