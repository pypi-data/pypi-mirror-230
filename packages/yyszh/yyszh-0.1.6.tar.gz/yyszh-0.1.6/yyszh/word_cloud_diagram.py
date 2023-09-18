import jieba
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from yyszh.hit_stopwords import stopwords

def word_cloud_diagram(txt_path, diagram_path, stop_words=None):
    """
    生成词云图的函数，将txt中的内容根据关键词生成词云图
    如：
        word_cloud_diagram('test.txt', 'ciyun.png', stop_words=['吃饭', '睡觉', '上班'])
        将本地的test.txt文件生成词云图，并保存到ciyun.png，自己添加了 吃饭、睡觉、上班三个停用词
    :param txt_path: txt文本路径
    :param diagram_path: 词云图保存路径
    :param stop_words: list，自定义停用词，默认已经使用哈工大停用词
    """
    if isinstance(stop_words, list):
        for s in stop_words:
            if s not in stopwords:
                stopwords.append(s)

    text = open(txt_path, encoding="utf-8").read()  # 标明文本路径，打开
    data_cut = jieba.lcut(text, cut_all=False)

    data_result = []
    for i in data_cut:
        if i not in stopwords:
            data_result.append(i)
    text = " ".join(data_result).replace("\n", " ")

    # 生成对象
    wc = WordCloud(font_path = "data/msyh.ttc",width=1500, height=1200, mode="RGBA", background_color=None).generate(text)

    # 保存词云图
    wc.to_file(diagram_path)
    # 显示词云图
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.show()
