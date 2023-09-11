import requests
import pandas as pd
import re

def getDouBanComment(url, header): 
    """
    这个函数的功能是抓取豆瓣电影短评数据
    Args:
        url: 短评页面的URL地址
        header: 请求头
    Return:
        name, comment_time, comment_location, comment
    e.g.:
        >>> url = 'https://movie.douban.com/subject/35267224/comments?status=P'
        >>> header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
}
        >>> getDouBanComment(url, header)
        (['谢明宏',
      '青绿的流水',
      '次等水货',
        ...
        如果改为智斗反派脱难的商业爽片估计更好看'])
    """
    # 发送请求，并获取相应
    response = requests.get(url, headers=header)
    # 解析评论
    comment = re.findall('<span class="short">(.*?)</span>', response.text, flags=re.S)
    # 抓取用户昵称
    name = re.findall('<div class="avatar">\n            <a title="(.*?)" href="', response.text, flags=re.S)
    # 抓取评论时间
    comment_time = re.findall('<span class="comment-time " title="(.*?)">', response.text, flags=re.S)
    # 抓取评论地点
    comment_location = re.findall('<span class="comment-location">(.*?)</span>', response.text, flags=re.S)
    return name, comment_time, comment_location, comment

def saveListStr2DataFrame(saveExcelPath=None, **kwargs):
    """
    保存多个字段到DataFrame并返回
    当saveExcelPath指定具体的Excel路径时，会将结果直接保存到Excel文件中，不返回内容
    Args:
        saveExcelPath: Excel路径， 当saveExcelPath指定具体的Excel路径时，会将结果直接保存到Excel文件中，不返回数据框
        **kwargs: DataFrame字段内容，columnName=columnValues
        
    Return:
        如果saveExcelPath=None(默认)，返回指定的数据框
        如果saveExcelPath!=None，无返回值

    Examples:
        >>> a1 = [1, 2, 3]
        >>> b1 = [4, 5, 6]
        >>> saveListStr2DataFrame(A=a1, B=b1)
            A	B
        0	1	4
        1	2	5
        2	3	6
    """
    data = pd.DataFrame(kwargs.values(), index=kwargs.keys()).T
    if saveExcelPath:
        data.to_excel(saveExcelPath, index=None)
        return 
    return data