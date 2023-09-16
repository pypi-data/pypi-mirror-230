# coding:utf-8
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
import requests
import os

class ConspiracyDetector:
    def __init__(self):
        self.lr_classifier, self.tfidf_vectorizer = self.download_model()

    def download_model(self):
        # 检查本地文件是否存在
        model_file = 'cons_model.pkl'
        tfidf_file = 'tfidf.pkl'
        stopwords_file = 'hit-stopwords.txt'

        if not (os.path.exists(model_file) and os.path.exists(tfidf_file) and os.path.exists(stopwords_file)):
            # 下载模型文件
            url = 'https://raw.githubusercontent.com/mengxiao2000/cospiratory-cn/main/cons_model.pkl'
            r = requests.get(url)
            open(model_file, 'wb').write(r.content)

            url = 'https://raw.githubusercontent.com/mengxiao2000/cospiratory-cn/main/tfidf.pkl'
            r = requests.get(url)
            open(tfidf_file, 'wb').write(r.content)

            url = 'https://raw.githubusercontent.com/mengxiao2000/cospiratory-cn/main/hit-stopwords.txt'
            r = requests.get(url)
            open(stopwords_file, 'wb').write(r.content)

        # 从文件中加载模型
        lr_classifier = joblib.load(model_file)
        tfidf_vectorizer = joblib.load(tfidf_file)
        return lr_classifier, tfidf_vectorizer

    def preprocess_text(self, text):
        # 分词
        segmented_text = ' '.join(jieba.cut(text))
        # 去除停用词（使用与训练时相同的停用词列表）
        stopwords = [l.strip('\n') for l in open('hit-stopwords.txt').readlines()]  # 示例停用词列表
        words = segmented_text.split()
        filtered_words = [word for word in words if word not in stopwords]
        return ' '.join(filtered_words)

    def predict(self, text):
        preprocessed_text = self.preprocess_text(text)

        # 特征工程
        # 使用与训练时相同的 TF-IDF 向量化器
        X_new = self.tfidf_vectorizer.transform([preprocessed_text])

        # 使用模型进行预测
        predicted_label = self.lr_classifier.predict(X_new)
        predicted_proba = self.lr_classifier.predict_proba(X_new)
        
        return {'label': predicted_label, 'proba': predicted_proba}

# 示例用法
if __name__ == "__main__":
    detector = ConspiracyDetector()
    new_text = "我觉得这是政府的阴谋"
    result = detector.predict(new_text)
    print(result)
