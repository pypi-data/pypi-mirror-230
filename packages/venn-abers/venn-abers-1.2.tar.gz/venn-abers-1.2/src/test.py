
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from src.venn_abers import VennAbersCalibrator
import numpy as np
import pandas as pd

X, y = make_classification(n_samples=1000, n_classes=3, n_informative=10)
X_train, X_test, y_train, y_test = train_test_split(X, y)
clf = GaussianNB()
va = VennAbersCalibrator(estimator=clf, inductive=True, cal_size=0.2, random_state=27)
# Inductive Venn-ABERS
va.fit(X_train, y_train)
p_prime = va.predict_proba(X_test)
y_pred = va.predict(X_test, one_hot=False)
# Cross Venn-ABERS
va = VennAbersCalibrator(estimator=clf, inductive=False, n_splits=5, random_state=27)
va.fit(X_train, y_train)
p_prime = va.predict_proba(X_test)
y_pred = va.predict(X_test)
# Manual Venn-ABERS (binary classification only)
X, y = make_classification(n_samples=1000, n_classes=2, n_informative=10)
X_train, X_test, y_train, y_test = train_test_split(X, y)
X_train_proper, X_cal, y_train_proper, y_cal = train_test_split(
X_train, y_train, test_size=0.2, shuffle=False)
clf.fit(X_train_proper, y_train_proper)
p_cal = clf.predict_proba(X_cal)
p_test = clf.predict_proba(X_test)
va = VennAbersCalibrator()
p_prime, p0_p1 = va.predict_proba(p_cal=p_cal, y_cal=y_cal, p_test=p_test, p0_p1_output=True)
y_pred = va.predict(p_cal=p_cal, y_cal=y_cal, p_test=p_test)
# clf.fit(X_train, y_train)
clf = GaussianNB()
clf.fit(X_train, y_train)
p_cal = clf.predict_proba(X_train)
va=VennAbersCalibrator()
opapa, papa = va.predict_proba(p_cal=p_cal, y_cal=y_train, p_test=clf.predict_proba(X_test), p0_p1_output=True)
opa=1