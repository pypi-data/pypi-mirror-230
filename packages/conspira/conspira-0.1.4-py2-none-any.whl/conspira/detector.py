#coding:utf-8
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
import requests

# 下载模型文件
url = 'https://raw.githubusercontent.com/mengxiao2000/cospiratory-cn/main/cons_model.pkl'
r = requests.get(url)
open('cons_model.pkl', 'wb').write(r.content)

url = 'https://raw.githubusercontent.com/mengxiao2000/cospiratory-cn/main/tfidf.pkl'
r = requests.get(url)
open('tfidf.pkl', 'wb').write(r.content)

url = 'https://raw.githubusercontent.com/mengxiao2000/cospiratory-cn/main/hit-stopwords.txt'
r = requests.get(url)
open('hit-stopwords.txt', 'wb').write(r.content)

# 从文件中加载模型
lr_classifier = joblib.load('cons_model.pkl')
tfidf_vectorizer = joblib.load('tfidf.pkl')

# 示例新文本
new_text = "我觉得这是政府的阴谋"

# 预处理新文本（分词和去停用词）
def preprocess_text(text):
    # 分词
    segmented_text = ' '.join(jieba.cut(text))
    # 去除停用词（使用与训练时相同的停用词列表）
    stopwords = [l.strip('\n') for l in open('hit-stopwords.txt').readlines()]  # 示例停用词列表
    words = segmented_text.split()
    filtered_words = [word for word in words if word not in stopwords]
    return ' '.join(filtered_words)

def predict(text):
    preprocessed_text = preprocess_text(text)

    # 特征工程
    # 使用与训练时相同的 TF-IDF 向量化器
    # tfidf_vectorizer = TfidfVectorizer(max_features=5000)  # 与训练时相同的配置
    # 注意：在实际情况下，应该保存训练时的tfidf_vectorizer以便在预测时使用相同的词汇表
    X_new = tfidf_vectorizer.transform([preprocessed_text])

    # 使用模型进行预测
    predicted_label = lr_classifier.predict(X_new)
    predicted_proba = lr_classifier.predict_proba(X_new)
    
    return {'label':predicted_label, 'proba':predicted_proba}
    





