'''
Main Author: Will LeVine 
Corresponding Email: levinewill@icloud.com
'''
from .progressive_learner import ProgressiveLearner
from .transformers import TreeClassificationTransformer
from .voters import TreeClassificationVoter
from .deciders import SimpleAverage

class LifelongClassificationForest:
    def __init__(self, n_estimators=100, tree_construction_proportion=0.67, finite_sample_correction=False):
        self.n_estimators = n_estimators
        self.tree_construction_proportion=tree_construction_proportion
        self.pl = ProgressiveLearner(
            default_transformer_class=TreeClassificationTransformer,
            default_transformer_kwargs={},
            default_voter_class=TreeClassificationVoter,
            default_voter_kwargs={"finite_sample_correction": finite_sample_correction},
            default_decider_class=SimpleAverage,
            default_decider_kwargs={},
        )

    def add_task(
        self, X, y, task_id=None):
        self.pl.add_task(
            X,
            y,
            task_id=task_id,
            transformer_voter_decider_split=[self.tree_construction_proportion, 1-tree_construction_proportion, 0],
            num_transformers=self.n_estimators,
            decider_kwargs = {"classes" : np.unique(y)}
        )
        return self
    
    def add_transformer(self, X, y, transformer_id=None):
        self.pl.add_transformer(
            X,
            y,
            transformer_id=transformer_id,
            num_transformers=self.n_estimators,
            transformer_data_proportion=self.tree_construction_proportion
        )

        return self

    def predict(self, X, task_id):
        return self.pl.predict(X, task_id)

    def predict_proba(self, X, task_id):
        return self.pl.predict_proba(X, task_id)


class UncertaintyForest:
    def __init__(self, n_estimators=100, finite_sample_correction=False):
        self.n_estimators = n_estimators
        self.finite_sample_correction = finite_sample_correction

    def fit(self, X, y):
        self.lf = LifelongClassificationForest(
            n_estimators=self.n_estimators,
            finite_sample_correction=self.finite_sample_correction,
        )
        self.lf.add_task(X, y, task_id=0, decider_kwargs = {"classes" : np.unique(y)})
        return self

    def predict(self, X):
        return self.lf.predict(X, 0)

    def predict_proba(self, X):
        return self.lf.predict_proba(X, 0)
