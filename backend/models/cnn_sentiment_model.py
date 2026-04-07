# -*- coding: utf-8 -*-
"""
基于CNN的情感分析模型
"""
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Embedding, Conv1D, MaxPooling1D, Flatten,
    Dense, Dropout, GlobalMaxPooling1D
)
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import jieba
import pickle

class CNNSentimentModel:
    def __init__(self, model_path="models/cnn_sentiment_model"):
        self.model_path = model_path
        self.tokenizer_path = os.path.join(model_path, "tokenizer.pickle")
        self.config_path = os.path.join(model_path, "config.pickle")
        
        # 模型参数
        self.max_features = 10000  # 词汇表大小
        self.max_len = 100        # 序列最大长度
        self.embedding_dim = 128   # 词嵌入维度
        
        # 加载或创建模型
        if os.path.exists(model_path):
            self.model = tf.keras.models.load_model(model_path)
            self.load_tokenizer()
            self.load_config()
            print("✓ 已加载预训练模型")
        else:
            self.model = self.build_model()
            self.tokenizer = Tokenizer(num_words=self.max_features, oov_token="<OOV>")
            print("✓ 已创建新模型")
    
    def build_model(self):
        """构建CNN模型"""
        model = Sequential([
            # 嵌入层
            Embedding(input_dim=self.max_features, 
                      output_dim=self.embedding_dim, 
                      input_length=self.max_len),
            
            # 卷积层
            Conv1D(filters=64, kernel_size=3, activation='relu'),
            MaxPooling1D(pool_size=2),
            Dropout(0.2),
            
            Conv1D(filters=128, kernel_size=3, activation='relu'),
            MaxPooling1D(pool_size=2),
            Dropout(0.2),
            
            # 全局池化层
            GlobalMaxPooling1D(),
            
            # 全连接层
            Dense(64, activation='relu'),
            Dropout(0.5),
            Dense(3, activation='softmax')  # 3分类：正面、负面、中性
        ])
        
        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def preprocess_text(self, text):
        """预处理文本"""
        if not text:
            return ""
        
        # 分词
        words = jieba.lcut(text)
        return " ".join(words)
    
    def train(self, texts, labels, epochs=10, batch_size=32):
        """训练模型"""
        # 预处理文本
        processed_texts = [self.preprocess_text(text) for text in texts]
        
        # 分词和向量化
        self.tokenizer.fit_on_texts(processed_texts)
        sequences = self.tokenizer.texts_to_sequences(processed_texts)
        padded_sequences = pad_sequences(sequences, maxlen=self.max_len, padding='post')
        
        # 训练模型
        history = self.model.fit(
            padded_sequences,
            np.array(labels),
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.2
        )
        
        # 保存模型
        os.makedirs(self.model_path, exist_ok=True)
        self.model.save(self.model_path)
        self.save_tokenizer()
        self.save_config()
        
        return history
    
    def predict(self, text):
        """预测情感"""
        # 预处理文本
        processed_text = self.preprocess_text(text)
        
        # 向量化
        sequence = self.tokenizer.texts_to_sequences([processed_text])
        padded_sequence = pad_sequences(sequence, maxlen=self.max_len, padding='post')
        
        # 预测
        prediction = self.model.predict(padded_sequence)[0]
        sentiment_idx = np.argmax(prediction)
        
        # 映射情感类型
        sentiment_map = {0: "negative", 1: "neutral", 2: "positive"}
        sentiment_type = sentiment_map[sentiment_idx]
        sentiment_score = float(prediction[sentiment_idx])
        
        # 调整情感得分范围为 [-1, 1]
        if sentiment_type == "positive":
            score = sentiment_score
        elif sentiment_type == "negative":
            score = -sentiment_score
        else:
            score = 0.0
        
        return sentiment_type, round(score, 4)
    
    def save_tokenizer(self):
        """保存分词器"""
        with open(self.tokenizer_path, 'wb') as f:
            pickle.dump(self.tokenizer, f)
    
    def load_tokenizer(self):
        """加载分词器"""
        with open(self.tokenizer_path, 'rb') as f:
            self.tokenizer = pickle.load(f)
    
    def save_config(self):
        """保存配置"""
        config = {
            "max_features": self.max_features,
            "max_len": self.max_len,
            "embedding_dim": self.embedding_dim
        }
        with open(self.config_path, 'wb') as f:
            pickle.dump(config, f)
    
    def load_config(self):
        """加载配置"""
        with open(self.config_path, 'rb') as f:
            config = pickle.load(f)
        self.max_features = config.get("max_features", 10000)
        self.max_len = config.get("max_len", 100)
        self.embedding_dim = config.get("embedding_dim", 128)

# 测试代码
if __name__ == "__main__":
    # 创建模型实例
    model = CNNSentimentModel()
    
    # 测试预测
    test_texts = [
        "学校环境很好，老师很负责，学习氛围浓厚",
        "课程安排不合理，作业太多，压力很大",
        "校园活动丰富多彩，社团活动很有趣",
        "食堂饭菜不好吃，价格还贵",
        "图书馆资源丰富，自习室环境舒适"
    ]
    
    print("测试情感分析模型:")
    for text in test_texts:
        sentiment, score = model.predict(text)
        print(f"文本: {text}")
        print(f"情感: {sentiment}, 得分: {score}")
        print("-" * 50)
