import pandas as pd
from src.venn_abers import VennAbersCalibrator
from sklearn.ensemble import RandomForestClassifier

data = {'Name':[7, 6, 5, 2, 5, 7],
        'Age':[20, 21, 19, 18, 7, 12],
        'Height' : [6.1, 5.9, 6.0, 6.1, 5, 23],
        'Gender': ['M','D', 'F', 'F', 'M', 'D']
        }

df = pd.DataFrame(data)
X = df.iloc[:, :-1].values
y = df.Gender.values

clf = RandomForestClassifier()

va = VennAbersCalibrator(estimator=clf, inductive=True, cal_size=0.2, random_state=101)
clf.fit(X,y)
va.fit(X,y)


p_pred = va.predict_proba(X)
y_pred = va.predict(X, one_hot=False)
