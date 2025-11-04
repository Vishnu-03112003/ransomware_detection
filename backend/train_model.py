import pandas as pd, joblib, os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
csv_path = os.path.join(os.path.dirname(__file__), 'synthetic_dataset.csv')
df = pd.read_csv(csv_path)
X = pd.get_dummies(df.drop(columns=['label'])); y = df['label']
Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=0.2,random_state=42,stratify=y)
clf=RandomForestClassifier(n_estimators=100,random_state=42)
clf.fit(Xtr,ytr); p=clf.predict(Xte)
print('Accuracy:',accuracy_score(yte,p)); print(classification_report(yte,p))
joblib.dump({'model':clf,'columns':X.columns.tolist()}, os.path.join(os.path.dirname(__file__),'model.joblib'))
print('Saved model.joblib')
