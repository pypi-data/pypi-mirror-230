import requests
import pandas as pd
import re
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

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


def getSinaText(url, header={}):
    """
        获取新浪微博博文内容
        Args:
            url: 新浪微博博文数据包地址
            header: 请求头字典
        
        Retuen:
            max_id, screen_name, created_at, text_raw, reposts_count, comments_count, attitudes_count
            max_id: 下一页URL地址中的max_id字段
            screen_name: 博主昵称
            created_at: 博文发布时间
            text_raw: 博文内容
            reposts_count: 转发数
            comments_count: 评论数
            attitudes_count: 点赞数
        
        Examples:
            >>> url = 'https://weibo.com/ajax/feed/hottimeline?since_id=0&refresh=0&group_id=102803&containerid=102803&extparam=discover%7Cnew_feed&max_id=0&count=10'
            >>> getSinaText(url)
            (1,
             ['新华社',
              '捕月少女',
              '大数据查牌员'
              ...
    """
    response = requests.get(url, headers=header)
    response_dict = response.json()

    max_id = response_dict['max_id']
    text_raw = [i['text_raw'] for i in response_dict['statuses']]
    screen_name = [i['user']['screen_name'] for i in response_dict['statuses']]
    created_at = [i['created_at'] for i in response_dict['statuses']]
    reposts_count = [i['reposts_count'] for i in response_dict['statuses']]
    comments_count = [i['comments_count'] for i in response_dict['statuses']]
    attitudes_count = [i['attitudes_count'] for i in response_dict['statuses']]
    return max_id, screen_name, created_at, text_raw, reposts_count, comments_count, attitudes_count

def getSinaComment(url, header={}):
    """
        获取新浪微博博文评论内容
        Args:
            url: 新浪微博博文评论数据包地址
            header: 请求头字典
        
        Retuen:
            max_id, screen_name, created_at, text_raw
            max_id: 下一页URL地址中的max_id字段
            screen_name: 评论人昵称
            created_at: 评论实践
            text_raw: 评论内容
        
        Examples:
            >>> url = 'https://weibo.com/ajax/statuses/buildComments?is_reload=1&id=4940045989970652&is_show_bulletin=2&is_mix=0&count=10&uid=2836883273&fetch_level=0&locale=zh-CN'
            >>> header = {
                    "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
                    "cookie": "XSRF-TOKEN=n360u4rN64m8U_4BorSD8xAv; SUB=_2A25J-gNsDeThGeBM41sT9y7Kyj-IHXVqjnOkrDV8PUNbmtANLUv5kW9NRKwn9pbnmriKVevH_qsT9DFHf631YzOa; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5U7_hCLB2yxZo8QkxYAXSs5JpX5KzhUgL.FoqE1h.ES05ceKe2dJLoIp7LxKML1KBLBKnLxKqL1hnLBoMceon4eoM7So20; ALF=1725933244; SSOLoginState=1694397244; WBPSESS=wi7CfG2VcnaC63Kg8n7kwtsSt9BL87XyXiz2F3wAdeWP4TOIRUKIpv_oqRdHrjaRLCQOnpMk4zpexBxov_b58c8s130uJAsV_dUW1xUNAZvfTx8KcXiu4Q9qUBdgkspD1YVIDsbUuijuTGZ9_RhJJQ=="
                }
            >>> getSinaComment(url, headers=header)
            (138870126847611,
                ['墨客墨客y',
                '等待初心丶',
                '桑凡缇--sunfunty',
                '明天AxA',
                ...
    """
    response = requests.get(url, headers=header)
    response_dict = response.json()
    
    max_id = response_dict['max_id']
    # 获取评论人昵称
    screen_name = [i['user']['screen_name'] for i in response_dict['data']]
    # 评论时间
    created_at = [i['created_at'] for i in response_dict['data']]
    # 评论内容
    text_raw = [i['text_raw'] for i in response_dict['data']]
    return max_id, screen_name, created_at, text_raw

def get_stopword():
    """
        Return:
            返回停用词构成的列表
    """
    with open(os.path.join(ROOT, 'files', 'stopwords.txt'), 'r', encoding='UTF-8') as f:
        stopword = f.readlines()
    stopword = [i.strip() for i in stopword]
    return stopword