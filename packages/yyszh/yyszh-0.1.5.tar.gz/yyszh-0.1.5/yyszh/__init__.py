from yyszh.utils import (
    read_config,    # 读取配置文件
    check_and_creat_dir,    # 判断文件目录是否存在，文件目录不存在则创建目录
    getPolygonArea,    # 计算多边形面积
    get_bracketed_content,    # 获取文本中所有小括号中的内容组成的list
    get_email,    # 提取文本中的 E-mail，返回结果为list
    rm_bracketed,    # 去除文本中的括号，包括括号中的内容
    rm_symbol,    # 去除文本中的所有符号
    getLCS,  # 获取最长公共序列
    is_chinese,  # 检查整个字符串是否包含中文，若包含则返回True
    strQ2B,  # 字符串全角转半角
    read_json,      # 读取json文件
    write_json,  # 将json数据写到json文件中，解决了一些数据类型报错问题
    read_csv,    # 读取csv文件， 可以返回为list或者dict，通过isdict=True设置
    write_csv,  # 将数组的内容写到csv中, 支持list或者dict两种数据格式
    read_excel,    # 读取excel文件，可以返回为list或者dict，通过isdict=True设置
    write_excel,    # 将数组的内容写到excel中, 支持list或者dict两种数据格式
    read_txt,       # 读取txt文件，按行作为元素
    write_txt,       # 将文本list写入到txt文件中，每个元素一行内容
    read_word,       # 读取docx文档，读取其中的文本和表格，结果组成一个list
    compute_vecsimilar_one_2_one,    # 计算两个向量的相似度，需要维度相同
    compute_vecsimilar__one_2_many,    # 计算一个向量和多个向量的相似度，返回相似度最大的下标和对应的相似度
    compute_vecsimilar__many_2_many    # 计算多个向量和多个向量的相似度，返回第一个参数中每个相似度最大的下标和对应的相似度

)

from yyszh.word_cloud_diagram import word_cloud_diagram     # 生成词云图